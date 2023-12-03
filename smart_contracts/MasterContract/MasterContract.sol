// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./InstanceContract.sol";
import "./EscrowContract.sol";

contract MasterContract is Ownable {
    mapping(address => address) public instanceContracts;
    address public feeManagementContract;
    uint256 public serviceFeePercent;

    event InstanceContractCreated(address indexed business, address instanceContract);

    constructor(address _feeManagementContract, uint256 _serviceFeePercent, address initialOwner)
        Ownable(initialOwner)
    {
        feeManagementContract = _feeManagementContract;
        serviceFeePercent = _serviceFeePercent;
    }

    function createInstanceContract(address business) public onlyOwner {
        require(instanceContracts[business] == address(0), "Instance contract already exists for this business");
        require(business != address(0), "Business address cannot be zero");

        // Create and deploy a new Escrow Contract for the business
        EscrowContract newEscrowContract = new EscrowContract(business);

        // Deploy a new Instance Contract with the business's Escrow Contract and the shared Fee Management Contract
        InstanceContract newInstanceContract = new InstanceContract(
            business,
            address(newEscrowContract),
            feeManagementContract,
            serviceFeePercent
        );

        instanceContracts[business] = address(newInstanceContract);
        emit InstanceContractCreated(business, address(newInstanceContract));
    }

}