//SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DappToken is ERC20 {
    constructor() ERC20("Dapp", "DAT") {
        _mint(_msgSender(), 1000000000000000000000000);
    }
}
