from web3 import Web3, HTTPProvider
import json


class EscrowContract:

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

    def get_business_owner(self) -> str:
        return self.contract.functions.businessOwner().call()

    def release_funds(self, token, amount) -> None:
        pass


escrow_contract = EscrowContract(
    provider_url='http://127.0.0.1:7545',
    contract_address='0x1F6eC9c46201E5E8dC863bAaFeD6d021170544ac',
)

print(escrow_contract.get_business_owner())
