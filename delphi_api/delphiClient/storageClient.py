import time
import json
from datetime import datetime, timedelta
from web3 import Web3
import redis


class StorageClient:
    def __init__(self, eth_client, url=False):
        # TODO: add redis config as env
        if url:
            print("Production Redis connecting..")
            self.r = redis.Redis.from_url(url)
        else:
            print("Dev Redis connecting...")
            self.r = redis.Redis("localhost")
        self.storage = {}
        self.eth_client = eth_client
        self.w3 = None
        self.w3_archive = None
        self.savings = None
        self.sleep_seconds = 0.2
        self.apr_decimals = 10 ** 12

    def setup_w3(self):
        self.w3 = self.eth_client.get_w3()
        self.w3_archive = self.eth_client.get_w3_archive()
        self.savings = self.eth_client.get_savings()

    def get_storage(self):
        return self.storage

    # Call this periodically to write state to file
    def write_storage(self):
        if bool(self.storage):
            self.r.mset({"Store": json.dumps(self.storage)})

    # call this when you want to read storage at start of program

    def read_storage(self):
        data = self.r.get("Store")
        try:
            self.storage = json.loads(data)

        except Exception as e:
            print(e)
            self.storage = {}
        return self.storage

    # finds the last block the current storage has info about
    def get_last_block(self):
        pools = list(self.storage.keys())
        last_seen_block = 0
        for pool in pools:
            last_block = self.storage[pool]["aprHistory"][-1]["block"]
            if last_block > last_seen_block:
                last_seen_block = last_block
            last_block = self.storage[pool]["rewards"][-1]["block"]
            if last_block > last_seen_block:
                last_seen_block = last_block
        return last_seen_block

    # Event Handleers

    # Handles the event where a protocol is registered

    def handle_protocol_registered(self, event):
        # Create or update the savings pool
        self.create_or_update_savings_pool(
            event, event.get("protocol"), event.get("poolToken")
        )

    # Handles the event where reward is distributed
    def handle_reward_distribution(self, event):
        pool_token = event.get("poolToken")
        pool_address = self.savings.functions.protocolByPoolToken(
            Web3.toChecksumAddress(pool_token)
        ).call()
        reward = self.create_s_pool_reward(event, pool_address)
        self.storage[pool_address.lower()]["rewards"].append(reward)

    def handle_deposit(self, event):
        # user = event.get("user")
        # TODO add user
        self.update_pool_balance_and_apy(
            event, event.get("protocol"), (event.get("nAmount") - event.get("nFee"))
        )

    def handle_withdraw(self, event):
        # TODO check user balance and exclude from protocol if zero
        self.update_pool_balance_and_apy(
            event, event.get("protocol"), (event.get("nAmount") * (-1))
        )

    ##############

    # Create / Update methods

    def create_or_update_savings_pool(self, event, protocol, poolToken):
        # check if pool exists
        pool = self.storage.get("protocol", None)
        # if it doesn't we create the entry in storage
        if not pool:
            data = {
                "poolToken": poolToken,
                "rewards": [],
                "aprHistory": [],
                "balanceHistory": [],
                "users": [],
                "distributions": [],
            }

            apr = self.create_s_pool_apr(event, 0, 0, protocol)
            data["apr"] = apr
            data["aprHistory"].append(apr)

            bal = self.create_s_pool_balance(event, 0, protocol)
            data["balance"] = bal
            data["balanceHistory"].append(bal)
            # update storage
            self.storage[protocol] = data

    def create_s_pool_apr(self, event, duration, amount, pool_id):
        apr = {
            "amount": amount,
            "duration": duration,
            "date": event.get("block_timestamp"),
            "pool": pool_id,
            "block": event.get("block_number"),
        }
        return apr

    def create_s_pool_balance(self, event, amount, pool_id):
        balance = {
            "amount": amount,
            "date": event.get("block_timestamp"),
            "pool": pool_id,
            "block": event.get("block_number"),
        }
        return balance

    def create_s_pool_reward(self, event, pool_address):
        reward = {
            "pool": pool_address,
            "token": event.get("rewardToken"),
            "amount": event.get("amount"),
            "date": event.get("block_timestamp"),
            "block": event.get("block_number"),
        }
        return reward

    # Helper Functions

    def calc_apy(self, duration, fromAmount, toAmount, aprDecimals):
        seconds_in_year = 365 * 24 * 60 * 60.0
        if (fromAmount == 0) or (duration == 0.0):
            apy = 0
        else:
            diff = (toAmount - fromAmount) * aprDecimals
            apy = (diff * seconds_in_year) / fromAmount / duration
        return apy

    def update_pool_balance_and_apy(self, event, poolAddress, currentBalanceCorrection):
        contract_idefi = self.eth_client.return_idefi_contract(
            self.w3_archive, Web3.toChecksumAddress(poolAddress)
        )
        prev_balance = self.storage.get(poolAddress, {}).get("balance")
        block = event.get("block_number")
        normalized_balance = contract_idefi.functions.normalizedBalance().call(
            block_identifier=block
        )
        current_balance = self.create_s_pool_balance(
            event, normalized_balance, poolAddress
        )
        # follow rate limits
        time.sleep(self.sleep_seconds)
        accumulated_yield = (
            current_balance.get("amount")
            - currentBalanceCorrection
            - prev_balance.get("amount")
        )

        if not (prev_balance["amount"] == 0) or not (accumulated_yield == 0):

            end = datetime.strptime(current_balance["date"][:-6], "%Y-%m-%d %H:%M:%S")
            start = datetime.strptime(prev_balance["date"][:-6], "%Y-%m-%d %H:%M:%S")
            duration = (end - start).total_seconds()

            apy = self.calc_apy(
                duration,
                prev_balance["amount"],
                (current_balance["amount"] - currentBalanceCorrection),
                self.apr_decimals,
            )
            if apy > 0:
                apr = self.create_s_pool_apr(event, duration, apy, poolAddress)
                self.storage[poolAddress]["apr"] = apr
                self.storage[poolAddress]["aprHistory"].append(apr)

        self.storage[poolAddress]["balance"] = current_balance
        self.storage[poolAddress]["balanceHistory"].append(current_balance)

    def parse_rewards(self):
        # this will store each pool, and rewards
        pool_dict = {}
        # get unique pools
        pools = list(self.storage.keys())
        # for each pool
        for pool in pools:
            rewards = self.storage[pool]["rewards"]

            today = datetime.now()
            # time one week ago
            week_prior = today - timedelta(weeks=1)
            reward_dict = {}
            for reward in rewards:
                date = datetime.strptime(reward["date"][:-6], "%Y-%m-%d %H:%M:%S")
                if date > week_prior:
                    entry = reward_dict.get(reward["token"], None)
                    if entry:
                        reward_dict[reward["token"]] += reward["amount"] / (10 ** 18)

                    else:
                        reward_dict[reward["token"]] = (reward["amount"]) / (10 ** 18)

            pool_dict[pool] = reward_dict

        return pool_dict

    def parse_apy(self):
        # this will store each pool, and apy
        pool_dict = {}
        # get unique pools
        pools = list(self.storage.keys())
        # for each pool
        for pool in pools:
            aprHistory = self.storage[pool]["aprHistory"][-10:]
            sum = 0
            weights = 0
            for item in aprHistory:
                sum += (item["amount"]) * (item["duration"])
                weights += item["duration"]

            pool_dict[pool] = (sum / weights) * 100 / (self.apr_decimals)
        return pool_dict
