// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;


// IERC20.sol:
//      ERC20 functions.
// ReentrancyGuard.sol:
//      contract to prevent re-entrancy attacks
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract InstanceContract is ReentrancyGuard {
    address public businessOwner;
    address public escrowContract;
    uint256 public serviceFeePercent;
    address public feeManagementContract;

    // Event to emit when a subscription payment is received
    event SubscriptionPaymentReceived(address indexed subscriber, uint256 amount, address token);

    constructor(address _businessOwner, address _escrowContract, address _feeManagementContract, uint256 _serviceFeePercent) {
        require(_businessOwner != address(0), "Business owner address cannot be zero");
        require(_escrowContract != address(0), "Escrow contract address cannot be zero");
        require(_feeManagementContract != address(0), "Fee Management contract address cannot be zero");

        businessOwner = _businessOwner;
        escrowContract = _escrowContract;
        feeManagementContract = _feeManagementContract;
        serviceFeePercent = _serviceFeePercent;
    }

    /**
     * @dev Function to handle subscription payments
     * @param amount The amount of tokens to be paid
     * @param token The ERC20 token address in which payment is made
     */
    function paySubscription(uint256 amount, address token) external nonReentrant {
        require(amount > 0, "Amount must be greater than 0");
        require(token != address(0), "Token address cannot be zero");

        uint256 feeAmount = (amount * serviceFeePercent) / 100;
        uint256 amountAfterFee = amount - feeAmount;

        // Transfer the fee to the fee management contract
        IERC20(token).transferFrom(msg.sender, feeManagementContract, feeAmount);

        // Transfer the rest to the escrow contract
        IERC20(token).transferFrom(msg.sender, escrowContract, amountAfterFee);

        emit SubscriptionPaymentReceived(msg.sender, amount, token);
    }

}