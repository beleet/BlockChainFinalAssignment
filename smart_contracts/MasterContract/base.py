from web3 import Web3, HTTPProvider
import json
import os


class MasterContract:

    def __init__(
            self,
            provider_url: str,
            contract_address: str,
    ):
        self.web3 = Web3(HTTPProvider(provider_url))
        # self.web3.eth.default_account = self.web3.eth.accounts[0]
        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(contract_address),
            abi=json.load(open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'abi.json'
                )
            ))
        )

    def create_instance_contract(self, business_address: str):
        self.contract.functions.createInstanceContract(business_address).transact()

        return self.get_instance_contract(business_address=business_address)

    def get_instance_contract(self, business_address: str) -> str:
        return self.contract.functions.instanceContracts(business_address).call()


# master_contract = MasterContract(
#     provider_url='https://rpc-mumbai.maticvigil.com/',
#     contract_address='0xb76616eb1d39688169eB029D21034dA885d04132',
# )
#
#
# print(master_contract.create_instance_contract('0x6C7e833e95134b498982433cec6c8E1bE8c96643'))
