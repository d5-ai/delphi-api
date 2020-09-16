import bqClient
import ethClient
import listenClient
import storageClient
from dotenv import load_dotenv
import os

load_dotenv()

# Don't set this env var for dev , local redis
REDIS_URL = os.getenv("REDISCLOUD_URL")

# all args are bool


def main(rebuild_storage, update_bq, test):
    print(
        f"""Delphi Event Listener + BQ Sync \n
Rebuild Storage: {rebuild_storage}
Grab BQ Data: {update_bq}
Test Run: {test}\n"""
    )
    # Lets first connect to web3
    eth = ethClient.EthClient()
    eth.setup()

    # Lets first init a storage client
    if REDIS_URL:
        store = storageClient.StorageClient(eth, REDIS_URL)
    else:
        store = storageClient.StorageClient(eth)
    store.setup_w3()

    # Init big query client
    bq = bqClient.BQClient("./data", store)

    if rebuild_storage:
        bq.build_storage_from_bq(update_bq, test)

    # Read the store to update state
    store.read_storage()

    # Get last seen block
    last_seen_block = store.get_last_block()
    print(f"\nLast seen block in storage: {last_seen_block}")
    # setup listen client
    lc = listenClient.EventListener(eth, store)

    # run filters
    lc.create_and_watch_filters(eth.get_savings(), last_seen_block + 1)


if __name__ == "__main__":
    try:
        main(False, False, False)
    except Exception as e:
        print(e)
