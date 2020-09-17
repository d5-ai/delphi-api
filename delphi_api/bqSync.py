from .delphiClient import StorageClient
from .delphiClient import BQClient
from .delphiClient import EthClient


from dotenv import load_dotenv
import os

load_dotenv()
# Don't set this env var for dev , local redis
REDIS_URL = os.getenv("REDIS_URL")
BQ_STORAGE_URL = os.getenv("BQ_STORAGE_URL")


def main(get_bq_data, test):
    print("BigQuery Sync + Redis Storage Populate")
    print(f"Grab BQ Data: {get_bq_data}")
    print(f"TestRun: {test}")
    # connect to web3
    eth = EthClient()
    eth.setup()
    # Lets first init a storage client
    if REDIS_URL:
        store = StorageClient(eth, REDIS_URL)
    else:
        store = StorageClient(eth)

    store.connect_to_storage()
    store.setup_w3()

    # Init big query client
    bq = BQClient(BQ_STORAGE_URL, store)

    bq.build_storage_from_bq(get_bq_data, test)
