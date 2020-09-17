import requests


class ApiHelper:
    def __init__(self, storage_client):
        self.url = "https://api.coingecko.com/api/v3/simple/"
        self.storage_client = storage_client
        self.pool_names = {
            "0x051e3a47724740d47042edc71c0ae81a35fdede9": "Delphi Aave BUSD",
            "0x08ddb58d31c08242cd444bb5b43f7d2c6bca0396": "Delphi Compound DAI",
            "0x7967ada2a32a633d5c055e2e075a83023b632b4e": "Delphi Curve yPool",
            "0x91d7b9a8d2314110d4018c88dbfdcf5e2ba4772e": "Delphi Curve sUSD",
            "0x9984d588ef2112894a0513663ba815310d383e3c": "Delphi Compound USDC",
            "0xbed50f08b8e68293bd7db742c4207f2f6e520cd2": "Delphi Aave sUSD",
            "0xeae1a8206f68a7ef629e85fc69e82cfd36e83ba4": "Delphi Curve BUSD",
        }

    def get_usd_price(self, coin_id):
        url = f"{self.url}price?ids={coin_id}&vs_currencies=usd"
        print(url)
        resp = requests.get(url)
        price = resp.json().get(coin_id, {}).get("usd", None)
        return price

    def get_rewards(self):
        self.storage_client.read_storage()
        rewards = self.storage_client.parse_rewards()
        # for pool in rewards:
        #     print(f"{self.pool_names[pool]}")
        #     print(rewards[pool])
        return rewards

    def get_apy(self):
        self.storage_client.read_storage()
        apy = self.storage_client.parse_apy()
        # for pool in apy:
        #     print(f"{self.pool_names[pool]} : {apy[pool]}")
        return apy

    def get_liquidity_total(self):
        storage = self.storage_client.read_storage()
        liquidity = {}
        for pool in storage:
            bal = storage[pool]["balance"]["amount"]
            # print(f"{self.pool_names[pool]} : {bal/10**18}")
            liquidity[pool] = bal / 10 ** 18
        return liquidity

    def get_stats(self):
        rewards = self.get_rewards()
        apy = self.get_apy()
        liquidity = self.get_liquidity_total()

        stats = {}
        for pool in apy:
            pool_stats = {}
            pool_stats["apy"] = apy[pool]
            pool_stats["rewards"] = rewards[pool]
            pool_stats["liquidity"] = liquidity[pool]
            stats[pool] = pool_stats
        return stats
