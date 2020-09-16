from web3 import Web3
import os
import json


class EthClient:
    def __init__(self):
        self.infura_ws_url = os.environ.get("INFURA_WS_URL")
        self.archive_node_url = os.environ.get("ARCHIVE_NODE")
        self.idefi_module_abi_filename = os.environ.get("IDEFI_MODULE_ABI_FILENAME")
        self.savings_module_abi_filename = os.environ.get("SAVINGS_MODULE_ABI_FILENAME")
        self.savings_module_address = os.environ.get("SAVINGS_MODULE_ADDRESS")
        self.w3 = None
        self.w3_archive = None
        self.savings = None

    def read_json(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data

    def init_web3_archive(self):
        self.w3_archive = Web3(Web3.HTTPProvider(self.archive_node_url))
        print(f"web3 archive node connection status: {self.w3_archive.isConnected()}")
        print(f"Current Block {self.w3_archive.eth.blockNumber}")

    def init_web3(self):
        self.w3 = Web3(Web3.WebsocketProvider(self.infura_ws_url))
        print(f"web3 ws infura node connection status: {self.w3.isConnected()}")
        print(f"Current Block {self.w3.eth.blockNumber}")

    # w3 is selectable so you can choose between the nodes

    def init_savings_contract(self, w3):
        savingsContractAbi = self.read_json(self.savings_module_abi_filename)
        self.savings = w3.eth.contract(
            address=self.savings_module_address, abi=savingsContractAbi
        )

    def return_idefi_contract(self, w3, address):
        address = Web3.toChecksumAddress(address)
        ContractAbi = self.read_json(self.idefi_module_abi_filename)
        contract = w3.eth.contract(address=address, abi=ContractAbi)
        return contract

    def setup(self):
        self.init_web3_archive()
        self.init_web3()
        self.init_savings_contract(self.w3)

    def get_w3(self):
        return self.w3

    def get_w3_archive(self):
        return self.w3_archive

    def get_savings(self):
        return self.savings
