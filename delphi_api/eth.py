from web3 import Web3
import os 
import json 

#Infura web3 ws url 
INFURA_WS_URL = os.environ.get("INFURA_WS_URL")
# Archive node http url 
ARCHIVE_NODE = os.environ.get("ARCHIVE_NODE")
# Idefi contract abi
IDEFI_MODULE_ABI_FILENAME = os.environ.get("IDEFI_MODULE_ABI_FILENAME")
# Saving contract abi
SAVINGS_MODULE_ABI_FILENAME = os.environ.get("SAVINGS_MODULE_ABI_FILENAME")
# Savings contract address 
SAVINGS_MODULE_ADDRESS = os.environ.get("SAVINGS_MODULE_ADDRESS")



def read_json(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data 

def init_web3_archive():
    w3 = Web3(Web3.HTTPProvider(ARCHIVE_NODE))
    print(f"web3 archive node connection status: {w3.isConnected()}")
    print(f"Current Block {w3.eth.blockNumber}")
    return w3 

def init_web3():
    w3 = Web3(Web3.WebsocketProvider(INFURA_WS_URL))
    print(f"web3 ws infura node connection status: {w3.isConnected()}")
    print(f"Current Block {w3.eth.blockNumber}")
    return w3 

def init_idefi_contract(w3, address):
    address = Web3.toChecksumAddress(address)
    ContractAbi = read_json(IDEFI_MODULE_ABI_FILENAME)
    contract = w3.eth.contract(address =address, abi=ContractAbi)
    return contract

def init_savings_contract(w3):
    savingsContractAbi = read_json(SAVINGS_MODULE_ABI_FILENAME)
    savings = w3.eth.contract(address =SAVINGS_MODULE_ADDRESS, abi=savingsContractAbi)
    return savings