from web3 import Web3, HTTPProvider
import json


class MasterContract:

    def __init__(
            self,
            provider_url: str,
            contract_address: str,
    ):
        self.web3 = Web3(HTTPProvider(provider_url))
        self.web3.eth.default_account = self.web3.eth.accounts[0]
        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(contract_address),
            abi=json.load(open('abi.json')),
        )

    def create_instance_contract(self, business_address: str) -> None:
        try:
            self.contract.functions.createInstanceContract(business_address).call()
        except ValueError:
            print('MasterContract/create_instance_contract: revert Instance contract already exists for this business')

    def get_instance_contract(self, business_address: str) -> None:
        return self.contract.functions.instanceContracts(business_address).call()


# master_contract = MasterContract(
#     provider_url='http://127.0.0.1:7545',
#     contract_address='0xc03efC126DB3A9ADFE234a0b8d777628d94A3B53',
# )
#
#
# print(master_contract.get_instance_contract('0x249361110BD3a610aFC4b8609ae773cD0d32737D'))
