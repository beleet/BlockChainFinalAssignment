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
        self.web3.eth.default_account = self.web3.eth.accounts[0]
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

    def get_instance_contract(self, business_address: str) -> None:
        return self.contract.functions.instanceContracts(business_address).call()


# master_contract = MasterContract(
#     provider_url='http://127.0.0.1:7545',
#     contract_address='0x8295d6111Ae421656870024a344dFAdc839B9190',
# )


# print(master_contract.create_instance_contract('0x567963c579dd24422aCC548e58A7DF838bD1205F'))
# print(master_contract.get_instance_contract('0x8295d6111Ae421656870024a344dFAdc839B9190'))
