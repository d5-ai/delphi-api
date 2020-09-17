from .delphiClient import StorageClient
from .delphiClient import EventListener
from .delphiClient import EthClient

from dotenv import load_dotenv
import os

load_dotenv()

# Don't set this env var for dev , local redis
REDIS_URL = os.getenv("REDIS_URL")
BQ_STORAGE_URL = os.getenv("BQ_STORAGE_URL")


def main():
    print("Delphi Event Listener")
    # Lets first connect to web3
    eth = EthClient()
    eth.setup()

    # Lets first init a storage client
    store = StorageClient(eth, REDIS_URL)
    store.connect_to_storage()
    store.setup_w3()
    # Read the store to update state
    store.read_storage()
    # Get last seen block
    last_seen_block = store.get_last_block()
    print(f"\nLast seen block in storage: {last_seen_block}")
    # setup listen client
    lc = EventListener(eth, store)

    # run filters
    lc.create_and_watch_filters(eth.get_savings(), last_seen_block + 1)
