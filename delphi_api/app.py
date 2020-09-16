import bq
import tools
from dotenv import load_dotenv
import time
import json
import pandas as pd
import sys
from timeit import default_timer as timer
import asyncio
import os
import etherscan
from datetime import datetime, timezone


load_dotenv()
# State
run = True

# Data extracted from bigQuery
DATA_DIR = 'data'
# Apr config decimals
APR_DECIMALS = 10**8
SLEEP = 0.2
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
# Savings contract address
SAVINGS_MODULE_ADDRESS = os.environ.get("SAVINGS_MODULE_ADDRESS")


# get w3 , w3 archive and savings contract
w3, w3_archive, savings = tools.get_w3_connection()


def build_storage(bq_update, head):
    """[builds storage object from big query]

    Args:
        bq_update ([bool]): [update date from big query]
        head ([bool]): [run only updates for first 5 rows]

    """
    start = time.time()
    # first lets fgrab bq data
    if bq_update:
        print("Grabbing data from BQ!")
        bq.update_bq_data()

    print("Reading stored bq data from csv!")
    # next lets read it as df
    protocolRegistered, deposits, withdrawls, rewards = bq.read_bq_data_from_csv()

    print("Registering protocols!")
    # Lets register all our protocolRegistration events first from bq
    for item in protocolRegistered.iterrows():
        event = item[1]
        tools.handle_protocol_registered(event)

    print("Registering Rewards!")
    # Lets register rewards to storage next
    pools = rewards['poolToken'].unique()
    for pool in pools:
        # get df, and arrange by block_number
        df = rewards.loc[rewards['poolToken'] == pool].sort_values(
            by='block_number', ascending=True)
        if head:
            df = df.head()
        for item in df.iterrows():
            event = item[1]
            tools.handle_reward_distribution(event)
            time.sleep(SLEEP)
            sys.stdout.write('.')
            sys.stdout.flush()

    print("Registering deposits and withdraws")
    # Now lets fill in pool with deposit/withdraw details

    def deposit(row):
        return 'deposit'

    def withdraw(row):
        return 'withdraw'

    pools = list(set(deposits['protocol'].unique()).union(
        set(withdrawls['protocol'].unique())))
    for pool in pools:
        df_dep = deposits.loc[deposits['protocol']
                              == pool].sort_values(by='block_number')
        df_with = withdrawls.loc[withdrawls['protocol']
                                 == pool].sort_values(by='block_number')
        df_dep['event'] = df_dep.apply(deposit, axis=1)
        df_with['event'] = df_with.apply(withdraw, axis=1)
        # now add both df together, so we can go step by step to caclulate apr for each period
        df = pd.concat([df_dep, df_with], ignore_index=True,
                       sort=False).sort_values(by='block_number')
        if head:
            df = df.head()

        for item in df.iterrows():
            event = item[1]
            if event.get("event") == "deposit":
                tools.handle_deposit(event)
            else:
                tools.handle_withdraw(event)
            sys.stdout.write('.')
            sys.stdout.flush()

    tools.write_storage()
    end = time.time()
    print(f"Sync time: {end-start}")


def handle_event(event):
    global w3

    args = event.get("args")
    args = dict(args)
    name = event.get("event")
    block_number = event.get('blockNumber')
    # we also need to pass block_number to handle functions
    args['block_number'] = event.get("blockNumber")
    block_details = w3.eth.getBlock(event.get("blockNumber"))
    timestamp = block_details.get("timestamp")
    date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    date = f"{date}+00:00"
    args['block_timestamp'] = date
    # rewardToken is mispelled in actual rewardDistribution event :(
    args['rewardToken'] = args.get("rewardRoken", None)
    print("EventDetails")

    print(args)

    # txid = Web3.toHex(event.get("transactionHash"))
    print(f"{name}:  Block:{block_number}")
    if name == 'Deposit':
        print("Submitting a deposit!")
        tools.handle_deposit(args)
        tools.write_storage()
    if name == 'Withdraw':
        print("Submitting a withdraw!")
        tools.handle_withdraw(args)
        tools.write_storage()
    if name == 'RewardDistribution':
        print("Submitting a RewardDistribution!")
        tools.handle_reward_distribution(args)
        tools.write_storage()
    else:
        print("Submitting a ProtocolRegistered!")
        tools.handle_protocol_registered(args)
        tools.write_storage()


# polling loop, this polls the filter checking for new entries
async def polling_loop(event_filter, poll_interval):
    # if run is set to false (during exception, stop)
    global run
    while run:
        for event in event_filter.get_new_entries():
            handle_event(event)
        # print("Sleeping")
        await asyncio.sleep(poll_interval)
        #print("Woke up")
    event_filter.close()


def create_and_watch_filters(savings_contract, last_seen_block):
    global run
    global savings
    # Create filters
    deposit_event_filter = savings_contract.events.Deposit.createFilter(
        fromBlock=last_seen_block)
    withdraw_event_filter = savings_contract.events.Withdraw.createFilter(
        fromBlock=last_seen_block)
    reward_distribution_event_filter = savings_contract.events.RewardDistribution.createFilter(
        fromBlock=last_seen_block)
    protocol_registered_event_filter = savings_contract.events.ProtocolRegistered.createFilter(
        fromBlock=last_seen_block)

    loop = asyncio.get_event_loop()
    print("Listening....")
    # Run polling loop for each filter
    try:
        loop.run_until_complete(asyncio.gather(
            polling_loop(deposit_event_filter, 6),
            polling_loop(withdraw_event_filter, 6),
            polling_loop(reward_distribution_event_filter, 12),
            polling_loop(protocol_registered_event_filter, 12)
        ))

    except Exception as e:
        loop.close()
        run = False


def main():
    global run

    # incase start from scratch
    #build_storage(True, False)
    #print("Sync finished!")
    # read storage
    storage = tools.read_storage()

    # get last sen block from local storage
    last_seen_block = tools.get_last_block()
    print(f"Last seen block: {last_seen_block}")

    # import pprint

    # # lets resync from last seen block
    # ethscan = etherscan.Etherscan(ETHERSCAN_API_KEY, SAVINGS_MODULE_ADDRESS )

    # result = ethscan.get_event_logs(last_seen_block+1, 'latest')
    # for item in (result['result']):
    #     tx = ethscan.get_tx_reciepts(item['transactionHash'])
    #     logs = (tx['result']['logs'])
    #     for i in logs:
    #         if i['topics'][0] == '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c':
    #             print(i)
    #     # pprint.pprint(a)
    #     # # if a['topics'][0] == '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c':
    #     #     pass

    # loop
    while True:
        if run:
            # run filters
            create_and_watch_filters(savings, last_seen_block+1)
        else:
            print("Restarting! Something went wrong!")
            run = True


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
