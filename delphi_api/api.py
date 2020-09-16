import storageClient
import pprint


POOL_NAMES = {
    "0x051e3a47724740d47042edc71c0ae81a35fdede9": "Delphi Aave BUSD",
    "0x08ddb58d31c08242cd444bb5b43f7d2c6bca0396": "Delphi Compound DAI",
    "0x7967ada2a32a633d5c055e2e075a83023b632b4e": "Delphi Curve yPool",
    "0x91d7b9a8d2314110d4018c88dbfdcf5e2ba4772e": "Delphi Curve sUSD",
    "0x9984d588ef2112894a0513663ba815310d383e3c": "Delphi Compound USDC",
    "0xbed50f08b8e68293bd7db742c4207f2f6e520cd2": "Delphi Aave sUSD",
    "0xeae1a8206f68a7ef629e85fc69e82cfd36e83ba4": "Delphi Curve BUSD",
}


tools = storageClient.StorageClient(None)
storage = tools.read_storage()


def get_rewards():

    rewards = tools.parse_rewards()
    for pool in rewards:
        print(f"{POOL_NAMES[pool]}")
        pprint.pprint(rewards[pool])
    return rewards


def get_apy():
    apy = tools.parse_apy()
    for pool in apy:
        print(f"{POOL_NAMES[pool]} : {apy[pool]}")
    return apy


def get_liquidity_total():
    storage = tools.read_storage()
    for pool in storage:
        bal = storage[pool]["balance"]["amount"]
        print(f"{POOL_NAMES[pool]} : {bal/10**18}")


get_apy()
get_rewards()
get_liquidity_total()
