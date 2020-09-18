import asyncio
from datetime import datetime
import time


class EventListener:
    def __init__(self, eth_client, storage_client):
        self.eth_client = eth_client
        self.storage_client = storage_client
        self.run = True
        self.block_sleep = 10
        self.last_debug_msg = time.time()

    def handle_event(self, event):
        w3 = self.eth_client.get_w3()

        args = event.get("args")
        args = dict(args)
        name = event.get("event")
        block_number = event.get("blockNumber")
        # we also need to pass block_number to handle functions
        args["block_number"] = block_number
        block_details = w3.eth.getBlock(block_number)
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
            print("Deposit Registered to Redis!")
        if name == "Withdraw":
            print("Submitting a withdraw!")
            self.storage_client.handle_withdraw(args)
            self.storage_client.write_storage()
            print("Withdraw registered to Redis!")
        if name == "RewardDistribution":
            print("Submitting a RewardDistribution!")
            self.storage_client.handle_reward_distribution(args)
            self.storage_client.write_storage()
            print("Withdraw registered to Redis!")
        elif name == "ProtocolRegistered":
            print("Submitting a ProtocolRegistered!")
            self.storage_client.handle_protocol_registered(args)
            self.storage_client.write_storage()
            print("ProtocolRegistered to Redis!")
        else:
            print("Event type not found!")
            print(event)

    def create_filter_by_event_name(
        self, savings_contract, event_filter, last_seen_block
    ):
        if event_filter == "Deposit":
            filter = savings_contract.events.Deposit.createFilter(
                fromBlock=last_seen_block
            )
        elif event_filter == "Withdraw":
            filter = savings_contract.events.Withdraw.createFilter(
                fromBlock=last_seen_block
            )
        elif event_filter == "RewardDistribution":
            filter = savings_contract.events.RewardDistribution.createFilter(
                fromBlock=last_seen_block
            )
        elif event_filter == "ProtocolRegistered":
            filter = savings_contract.events.ProtocolRegistered.createFilter(
                fromBlock=last_seen_block
            )
        else:
            filter = None

        return filter

    # polling loop, this polls the filter checking for new entries

    async def polling_loop(
        self, savings_contract, event_filter, last_seen_block, poll_interval
    ):

        while True:
            print(f"Setting up {event_filter} event listening filters..")
            # Connect to a new filter
            filter = self.create_filter_by_event_name(
                savings_contract, event_filter, last_seen_block
            )
            self.run = True
            print("Listening.....")
            while self.run:
                try:
                    new = filter.get_new_entries()
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
                    if (time.time() - self.last_debug_msg) > 60:
                        self.last_debug_msg = time.time()
                        print(f"Listening..")
                except Exception as e:
                    print(f"Exception in polling loop: {e}")
                    self.run = False

    def create_and_watch_filters(self, savings_contract, last_seen_block):

        filters = ["Deposit", "Withdraw", "RewardDistribution", "ProtocolRegistered"]

        loop = asyncio.get_event_loop()

        loop.run_until_complete(
            asyncio.gather(
                self.polling_loop(savings_contract, filters[0], last_seen_block, 6),
                self.polling_loop(savings_contract, filters[1], last_seen_block, 6),
                self.polling_loop(savings_contract, filters[2], last_seen_block, 12),
                self.polling_loop(savings_contract, filters[3], last_seen_block, 12),
                return_exceptions=True,
            )
        )
