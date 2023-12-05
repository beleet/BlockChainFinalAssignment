from web3 import Web3, HTTPProvider
import json
import os


class InstanceContract:

    def __init__(
            self,
            provider_url: str,
            contract_address: str,
    ):
        self.web3 = Web3(HTTPProvider(provider_url))
        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(contract_address),
            abi=json.load(open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'abi.json'
                )
            ))
        )

    def get_business_owner(self) -> str:
        return self.contract.functions.businessOwner().call()

    def get_escrow_contract(self) -> str:
        return self.contract.functions.escrowContract().call()

    def get_fee_management_contract(self) -> str:
        return self.contract.functions.feeManagementContract().call()

    def get_service_fee_percent(self) -> float:
        return self.contract.functions.serviceFeePercent().call()

    def pay_subscription(self, amount, token) -> None:
        self.contract.functions.paySubscription(amount, token).call()

#
# instance_contract = InstanceContract(
#     provider_url='https://rpc-mumbai.maticvigil.com/',
#     contract_address='0x403391D6c95393B8c390caDf1e42d49A350c4a5D',
# )

# print(instance_contract.get_business_owner())
# print(instance_contract.get_escrow_contract())
# print(instance_contract.get_fee_management_contract())
# print(instance_contract.get_service_fee_percent())


# event_filter = instance_contract.contract.events.SubscriptionPaymentReceived.get_logs(
#     fromBlock=instance_contract.web3.eth.block_number - 1000
# )
# print(instance_contract.web3.eth.block_number)
