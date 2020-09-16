import time
import sys

# google imports
import google.auth
from google.cloud import bigquery
from google.cloud import bigquery_storage_v1beta1

# pandas
import pandas as pd


class BQClient:
    def __init__(self, data_dir, storage_client):
        # store data dir
        self.data_dir = data_dir
        # this is the queries we use
        self.query_dict = {
            "ProtocolRegistered": """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_ProtocolRegistered`  """,
            "Deposit": """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_Deposit` """,
            "Withdraw": """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_Withdraw`""",
            "RewardDistribution": """SELECT * FROM `blockchain-etl.ethereum_akropolis.SavingsModule_event_RewardDistribution`""",
        }

        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        # bq client init
        self.bq_client = bigquery.Client(
            credentials=credentials,
            project=project_id,
        )
        # init storage client
        self.bq_storage_client = bigquery_storage_v1beta1.BigQueryStorageClient(
            credentials=credentials
        )
        # storage client
        self.storage_client = storage_client
        self.sleep_seconds = 0.2

    # Get bq results as df

    def bq_query_get(self, query):
        df = (
            self.bq_client.query(query)
            .result()
            .to_dataframe(bqstorage_client=self.bq_storage_client)
        )
        return df

    # Get bq data, and update local csv files (this overwrites)

    def update_bq_data(self):
        # Get protocol registered events
        protocolsRegistered = self.bq_query_get(self.query_dict["ProtocolRegistered"])
        protocolsRegistered.to_csv(
            f"{self.data_dir }/protocolsRegistered.csv", index=False
        )

        # get deposit events
        deposits = self.bq_query_get(self.query_dict["Deposit"])
        deposits.to_csv(f"{self.data_dir }/deposits.csv", index=False)

        # get withdrawl events
        withdrawls = self.bq_query_get(self.query_dict["Withdraw"])
        withdrawls.to_csv(f"{self.data_dir }/withdrawls.csv", index=False)

        # get rewards
        rewards = self.bq_query_get(self.query_dict["RewardDistribution"])
        rewards.to_csv(f"{self.data_dir }/rewards.csv", index=False)

    # reads the data from csv
    def read_bq_data_from_csv(self):
        protocolRegistered = pd.read_csv(f"{self.data_dir }/protocolsRegistered.csv")

        deposits = pd.read_csv(
            f"{self.data_dir }/deposits.csv", dtype={"nAmount": float, "nFee": float}
        )

        withdrawls = pd.read_csv(
            f"{self.data_dir }/withdrawls.csv", dtype={"nAmount": float, "nFee": float}
        )

        rewards = pd.read_csv(f"{self.data_dir }/rewards.csv")
        rewards["amount"] = pd.to_numeric(rewards["amount"], errors="coerce")

        return protocolRegistered, deposits, withdrawls, rewards

    # This reads through bigQuery data building out local strorage

    def build_storage_from_bq(self, update, test):
        start = time.time()

        if update:
            print("Grabbing data from Google BigQuery!")
            self.update_bq_data()

        else:
            print("Skipping sync from Google BigQuery!")

        print("Reading stored bq data from csv!")
        # next lets read it as df
        protocolRegistered, deposits, withdrawls, rewards = self.read_bq_data_from_csv()

        print("Registering protocols!")
        # Lets register all our protocolRegistration events first from bq
        for item in protocolRegistered.iterrows():
            event = item[1]
            self.storage_client.handle_protocol_registered(event)

        print("Registering Rewards!")
        # Lets register rewards to storage next
        pools = rewards["poolToken"].unique()
        for pool in pools:
            # get df, and arrange by block_number
            df = rewards.loc[rewards["poolToken"] == pool].sort_values(
                by="block_number", ascending=True
            )
            if test:
                df = df.head()
            for item in df.iterrows():
                event = item[1]
                self.storage_client.handle_reward_distribution(event)
                time.sleep(self.sleep_seconds)
                sys.stdout.write(".")
                sys.stdout.flush()

        print("Registering deposits and withdraws")
        # Now lets fill in pool with deposit/withdraw details

        def deposit(row):
            return "deposit"

        def withdraw(row):
            return "withdraw"

        pools = list(
            set(deposits["protocol"].unique()).union(
                set(withdrawls["protocol"].unique())
            )
        )

        for pool in pools:
            df_dep = deposits.loc[deposits["protocol"] == pool].sort_values(
                by="block_number"
            )
            df_with = withdrawls.loc[withdrawls["protocol"] == pool].sort_values(
                by="block_number"
            )
            df_dep["event"] = df_dep.apply(deposit, axis=1)
            df_with["event"] = df_with.apply(withdraw, axis=1)
            # now add both df together, so we can go step by step to caclulate apr for each period
            df = pd.concat(
                [df_dep, df_with], ignore_index=True, sort=False
            ).sort_values(by="block_number")
            if test:
                df = df.head()

            for item in df.iterrows():
                event = item[1]
                if event.get("event") == "deposit":
                    self.storage_client.handle_deposit(event)
                else:
                    self.storage_client.handle_withdraw(event)
                sys.stdout.write(".")
                sys.stdout.flush()

        self.storage_client.write_storage()
        end = time.time()
        print(f"Sync time: {end-start}")
