import asyncio
import sys
from datetime import datetime


class EventListener:
    def __init__(self, eth_client, storage_client):
        self.eth_client = eth_client
        self.storage_client = storage_client
        self.run = True
        self.block_sleep = 10

    def handle_event(self, event):
        w3 = self.eth_client.get_w3()

        args = event.get("args")
        args = dict(args)
        name = event.get("event")
        block_number = event.get("blockNumber")
        # we also need to pass block_number to handle functions
        args["block_number"] = event.get("blockNumber")
        block_details = w3.eth.getBlock(event.get("blockNumber"))
        timestamp = block_details.get("timestamp")
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        date = f"{date}+00:00"
        args["block_timestamp"] = date
        # rewardToken is misspelled in actual rewardDistribution event :(
        args["rewardToken"] = args.get("rewardRoken", None)
        print("EventDetails")

        print(args)

        # txid = Web3.toHex(event.get("transactionHash"))
        print(f"{name}:  Block:{block_number}")
        if name == "Deposit":
            print("Submitting a deposit!")
            self.storage_client.handle_deposit(args)
            self.storage_client.write_storage()
        if name == "Withdraw":
            print("Submitting a withdraw!")
            self.storage_client.handle_withdraw(args)
            self.storage_client.write_storage()
        if name == "RewardDistribution":
            print("Submitting a RewardDistribution!")
            self.storage_client.handle_reward_distribution(args)
            self.storage_client.write_storage()
        else:
            print("Submitting a ProtocolRegistered!")
            self.storage_client.handle_protocol_registered(args)
            self.storage_client.write_storage()

    # polling loop, this polls the filter checking for new entries

    async def polling_loop(self, event_filter, poll_interval):
        while self.run:
            try:
                new = event_filter.get_new_entries()
                # sleep a bit here so the blocks can sync
                # we need to get block timestamp from node, this may fail if node hasn't synced
                if len(new) > 0:
                    print(
                        f"New events found! Waiting {self.block_sleep} blocks so node can catch up"
                    )
                    # let 10 more blocks go by
                    await asyncio.sleep(10 * 6)
                    for event in new:
                        self.handle_event(event)
                # print(f"{event_filter.filter_id} Sleeping")
                await asyncio.sleep(poll_interval)
                # print(f"{event_filter.filter_id} Woke up")
                print(".")
            except Exception as e:
                print(e)

    def create_and_watch_filters(self, savings_contract, last_seen_block):
        print("Setting up Contract Event Listening Filters..")
        # Create filters
        deposit_event_filter = savings_contract.events.Deposit.createFilter(
            fromBlock=last_seen_block
        )
        withdraw_event_filter = savings_contract.events.Withdraw.createFilter(
            fromBlock=last_seen_block
        )
        reward_distribution_event_filter = (
            savings_contract.events.RewardDistribution.createFilter(
                fromBlock=last_seen_block
            )
        )
        protocol_registered_event_filter = (
            savings_contract.events.ProtocolRegistered.createFilter(
                fromBlock=last_seen_block
            )
        )
        print("Created filters! Starting asyncio event loop...")

        loop = asyncio.get_event_loop()
        print("Listening")
        # sys.stdout.write("\nListening")
        # sys.stdout.flush()
        # Run polling loop for each filter
        try:
            loop.run_until_complete(
                asyncio.gather(
                    self.polling_loop(deposit_event_filter, 6),
                    self.polling_loop(withdraw_event_filter, 6),
                    self.polling_loop(reward_distribution_event_filter, 12),
                    self.polling_loop(protocol_registered_event_filter, 12),
                    return_exceptions=True,
                )
            )

        except Exception as e:
            try:
                loop.close()
                self.run = False
            except Exception as e2:
                print(e, e2)
