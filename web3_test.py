import json
from web3 import Web3, HTTPProvider
from smart_contracts.EscrowContract.config import ESCROW_CONTRACT_ADDRESS
from smart_contracts.InstanceContract.config import INSTANCE_CONTRACT_ADDRESS
from smart_contracts.MasterContract.config import MASTER_CONTRACT_ADDRESS

PROVIDER_URL = 'http://127.0.0.1:7545'
ADMIN_ADDRESS = ''
OWNERS_ADDRESSES = {}
SUBSCRIBERS = {}


web3 = Web3(HTTPProvider(PROVIDER_URL))
web3.eth.default_account = web3.eth.accounts[0]

# ESCROW_CONTRACT = web3.eth.contract(
#     address=web3.to_checksum_address(ESCROW_CONTRACT_ADDRESS),
#     abi=json.load(open('smart_contracts/EscrowContract/abi.json')),
# )

# INSTANCE_CONTRACT = web3.contract(
#     address=web3.to_checksum_address(INSTANCE_CONTRACT_ADDRESS),
#     abi=json.load(open('InstanceContract/abi.json')),
# )

MASTER_CONTRACT = web3.eth.contract(
    address=web3.to_checksum_address(MASTER_CONTRACT_ADDRESS),
    abi=json.load(open('smart_contracts/MasterContract/abi.json')),
)


a = MASTER_CONTRACT.functions.instanceContracts('0xb350dA6F2CE2Ed9Fac7Fc8F238330529Af3329BF').call()
print(a)


