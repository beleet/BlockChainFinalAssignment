// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Ownable.sol:
//      provides basic authorization control functions for implementing user permissions.
//      in this project ownership ensures that only the owner can release funds.
// IERC20.sol:
//      ERC20 functions.
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

// Onwable also allows us to transfer ownership
contract EscrowContract is Ownable {
    // constructor:
    //      initializes contract with the address of the buiseness owner (channel handler).
    // releaseFunds:
    //      allows to withdraw funds
    address public businessOwner;

    constructor(address _businessOwner) Ownable(_businessOwner) {
        require(_businessOwner != address(0), "Business owner address cannot be zero");
        businessOwner = _businessOwner;
    }

    function releaseFunds(address token, uint256 amount) public onlyOwner {
        require(amount > 0, "Amount must be greater than 0");
        IERC20(token).transfer(businessOwner, amount);
    }

}