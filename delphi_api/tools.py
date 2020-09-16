import eth 
from web3 import Web3
import time
from datetime import date, timedelta, datetime
import numpy as np 
import json 

# Constants 
APR_DECIMALS = 10**8 
SLEEP= 0.2 


# global storage 
storage = {}


# Load w3
w3 = eth.init_web3()
w3_archive = eth.init_web3_archive()
savings = eth.init_savings_contract(w3)

def get_w3_connection():
    return w3, w3_archive, savings 
def get_storage():
    global storage 
    return storage 


def write_storage():
    global storage 
    with open('storage.json', 'w') as outfile:
        json.dump(storage, outfile, indent=4)

def read_storage():
    global storage
    with open('storage.json') as json_file:
        storage = json.load(json_file)
    return storage 

def get_last_block():
    storage = read_storage()

    pools = list(storage.keys())
    last_seen_block = 0

    for pool in pools:
        last_block= storage[pool]['aprHistory'][-1]['block']
        if last_block >last_seen_block:
            last_seen_block = last_block

    return last_seen_block

# Handles the event where a protocol is registered 
def handle_protocol_registered(event):
    # Create or update the savings pool 
    create_or_update_savings_pool(event, event.get("protocol"), event.get("poolToken"))

# Hanges the event where reward is distributed 
def handle_reward_distribution(event):   
    pool_token = event.get("poolToken")
    pool_address = savings.functions.protocolByPoolToken(Web3.toChecksumAddress(pool_token)).call()
    reward = create_s_pool_reward(event, pool_address)
    global storage 
    storage[pool_address.lower()]['rewards'].append(reward)

def handle_deposit(event):
    user = event.get("user")
    #TODO add user 
    update_pool_balance_and_apy(event, event.get('protocol'), (event.get('nAmount') - event.get('nFee')))

def handle_withdraw(event):
    # TODO check user balance and exclude from protocol if zero 
    update_pool_balance_and_apy(event, event.get('protocol'), (event.get('nAmount')*(-1)))







def calc_apy(duration, fromAmount, toAmount, aprDecimals):
    seconds_in_year = 365*24 * 60 *60.0 
    if (fromAmount == 0) or (duration==0.0):
        apy = 0 
    else:
        apy = (((toAmount - fromAmount)*((aprDecimals))*(seconds_in_year))/(fromAmount))/duration
    return apy
    
    

def update_pool_balance_and_apy(event, poolAddress, currentBalanceCorrection):
    global storage 
    contract_idefi = eth.init_idefi_contract(w3_archive, Web3.toChecksumAddress(poolAddress))
    prev_balance = storage.get(poolAddress, {}).get('balance')
    block = event.get('block_number')
    normalized_balance =  contract_idefi.functions.normalizedBalance().call(block_identifier=block)
    current_balance = create_s_pool_balance(event, normalized_balance, poolAddress )
    # follow rate limits
    time.sleep(SLEEP)
    accumalated_yield = current_balance.get("amount") - currentBalanceCorrection - prev_balance.get('amount') 
    if  not ( prev_balance['amount'] == 0) or not ( accumalated_yield  == 0 ):
     
        end = datetime.strptime(current_balance['date'][:-6],'%Y-%m-%d %H:%M:%S')   
        start = datetime.strptime(prev_balance['date'][:-6],'%Y-%m-%d %H:%M:%S')   
        duration = (end - start).total_seconds()
     
        apy = calc_apy(duration, prev_balance['amount'], (current_balance['amount'] - currentBalanceCorrection),APR_DECIMALS )
        if (apy > 0):
            apr = create_s_pool_apr(event, duration, apy, poolAddress)
            storage[poolAddress]['apr'] = apr  
            storage[poolAddress]['aprHistory'].append(apr)
        
    storage[poolAddress]['balance'] = current_balance 
    storage[poolAddress]['balanceHistory'].append(current_balance)




def create_or_update_savings_pool(event, protocol, poolToken):
    # load pools
    global storage 
    # check if pool exists
    pool = storage.get("protocol", None);
    # if it doesnt we create the entry in storage 
    if not pool:
        data = { 
              "poolToken": poolToken,
              "rewards": [],
              "aprHistory": [],
              "balanceHistory": [],
              "users": [],
              "distributions": []}
        
        apr = create_s_pool_apr(event, 0, 0, protocol)
        data['apr'] = apr
        data['aprHistory'].append(apr)
        
        bal = create_s_pool_balance(event, 0, protocol)
        
        
        data['balance'] = bal
        data['balanceHistory'].append(bal)
        
        # update storage 
        storage[protocol] = data 
        
def create_s_pool_apr(event, duration, amount, pool_id):
    apr = {'amount': amount, 
           'duration': duration,
            'date': event.get("block_timestamp"),
          'pool': pool_id,
          'block': event.get("block_number")}
    return apr 

def create_s_pool_balance(event, amount, pool_id):
    balance = {'amount': amount,
                'date': event.get('block_timestamp'),
                'pool': pool_id,
                'block': event.get('block_number')}
    return balance    

def create_s_pool_reward(event, pool_address):
    reward = {'pool': pool_address,
               'token': event.get("rewardToken"),
             'amount': event.get('amount'),
             'date': event.get("block_timestamp"),
             'block': event.get("block_number")}
    return reward 

def parse_rewards(storage):
    # this will store each pool, and rewards 
    pool_dict = {}
    # get unique pools 
    pools = list(storage.keys())
    # for each pool 
    for pool in pools:   
        rewards = storage[pool]['rewards']

        
        today = datetime.now()
        # time one week ago 
        week_prior =  today - timedelta(weeks=1)
        reward_dict = {}
        for reward in rewards:
            date = datetime.strptime(reward['date'][:-6],'%Y-%m-%d %H:%M:%S')  
            if date > week_prior: 
                entry = reward_dict.get(reward['token'], None)
                if entry:
                    reward_dict[reward['token']] += reward['amount']/(10**18)
                    
                else:
                    reward_dict[reward['token']] = (reward['amount'])/(10**18)
    
        pool_dict[pool] = reward_dict
    
    return pool_dict 

def parse_apy(storage):
    # this will store each pool, and apy 
    pool_dict = {}
    # get unique pools 
    pools = list(storage.keys())
    # for each pool 
    for pool in pools:   
        aprHistory = storage[pool]['aprHistory'][-10:]
        sum = 0
        weights = 0   
        for item in aprHistory:
            sum += (item['amount'])*(item['duration'])
            weights += item['duration']
        
        pool_dict[pool] = (sum/weights)*100/(APR_DECIMALS)
    return pool_dict

    