from .delphiClient import StorageClient
from .delphiClient import BQClient
from .delphiClient import EventListener
from .delphiClient import EthClient

from dotenv import load_dotenv
import os

load_dotenv()

# Don't set this env var for dev , local redis
REDIS_URL = os.getenv("REDIS_URL")

# all args are bool


def main(rebuild_storage, update_bq, store_csv, test):
    print(
        f"""Delphi Event Listener + BQ Sync \n
Rebuild Storage: {rebuild_storage}
Grab BQ Data: {update_bq}
Test Run: {test}\n"""
    )
    # Lets first connect to web3
    eth = EthClient()
    eth.setup()

    # Lets first init a storage client
    if REDIS_URL:
        store = StorageClient(eth, REDIS_URL)
    else:
        store = StorageClient(eth)
    store.setup_w3()
    if update_bq:

        # Init big query client
        bq = BQClient("/home/rex/Documents/final/delphi-api/delphi_api/data", store)

        if rebuild_storage:
            bq.build_storage_from_bq(update_bq, store_csv, test)

    # Read the store to update state
    store.read_storage()

    # Get last seen block
    last_seen_block = store.get_last_block()
    print(f"\nLast seen block in storage: {last_seen_block}")
    # setup listen client
    lc = EventListener(eth, store)

    # run filters
    lc.create_and_watch_filters(eth.get_savings(), last_seen_block + 1)
