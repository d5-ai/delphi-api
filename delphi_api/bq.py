# google imports
import google.auth
from google.cloud import bigquery
from google.cloud import bigquery_storage_v1beta1
# pandas
import pandas as pd
import numpy as np


# Data extracted from bigQuery
DATA_DIR = 'data'

# Queries
QUERY_DICT = {"ProtocolRegistered":
              """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_ProtocolRegistered`  """,
              "Deposit":
              """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_Deposit` """,
              "Withdraw":
                  """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_Withdraw`""",
              "RewardDistribution":
              """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_RewardDistribution`"""}


# get google creds
credentials, your_project_id = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# Make clients.
bqclient = bigquery.Client(
    credentials=credentials,
    project=your_project_id,
)
bqstorageclient = bigquery_storage_v1beta1.BigQueryStorageClient(
    credentials=credentials
)


# Get bq results as df
def bq_query_get(query):
    df = (
        bqclient.query(query)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient))
    return df

# Get bq data, and update local csv files


def update_bq_data():
    # Get protocol registered events
    protocolsRegistered = bq_query_get(QUERY_DICT['ProtocolRegistered'])
    protocolsRegistered.to_csv(
        f'{DATA_DIR}/protocolsRegistered.csv', index=False)

    # get deposit events
    deposits = bq_query_get(QUERY_DICT['Deposit'])
    deposits.to_csv(f'{DATA_DIR}/deposits.csv', index=False)

    # get withdrawl events
    withdrawls = bq_query_get(QUERY_DICT['Withdraw'])
    withdrawls.to_csv(f'{DATA_DIR}/withdrawls.csv', index=False)

    # get rewards
    rewards = bq_query_get(self.query_dict['RewardDistribution'])
    rewards.to_csv(f'{DATA_DIR}/rewards.csv', index=False)


def read_bq_data_from_csv():
    protocolRegistered = pd.read_csv(f"{DATA_DIR}/protocolsRegistered.csv")

    deposits = pd.read_csv(f"{DATA_DIR}/deposits.csv",
                           dtype={'nAmount': float, 'nFee': float})

    withdrawls = pd.read_csv(
        f"{DATA_DIR}/withdrawls.csv", dtype={'nAmount': float, 'nFee': float})

    rewards = pd.read_csv(f"{DATA_DIR}/rewards.csv")
    rewards['amount'] = pd.to_numeric(rewards['amount'], errors='coerce')

    return protocolRegistered, deposits, withdrawls, rewards
