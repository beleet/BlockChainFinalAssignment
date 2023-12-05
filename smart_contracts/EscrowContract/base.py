from web3 import Web3, HTTPProvider
import json

import config


class EscrowContract:

    def __init__(
            self,
            provider_url: str,
            contract_address: str,
    ):
        self.web3 = Web3(HTTPProvider(provider_url))
        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(contract_address),
            abi=json.load(open('abi.json')),
        )

    def get_business_owner(self) -> str:
        return self.contract.functions.businessOwner().call()

    def get_events(self):
        return self.contract.events


# escrow_contract = EscrowContract(
#     provider_url=config.PROVIDER_MUMBAI_URL,
#     contract_address='0x22DF0E966d3C1e063a0e7381De0b6c02A0573C0B',
# )
#
# print(escrow_contract.get_events())
