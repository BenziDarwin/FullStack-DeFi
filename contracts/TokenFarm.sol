//stake tokens - DONE!
//unstake tokens
//issue tokens - DONE!
//add allowed tokens - DONE!
// get ETH value - DONE!
// check the number of users who have ever used the app. - DONE!
//SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    //What tokens can be staked
    address[] public allowedTokens;
    // Mapping from tokenaddress, to sender to amount.
    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    mapping(address => address) public tokenToPriceFeedAddress;
    address[] public stakers;
    IERC20 public dappToken;

    constructor(address _dappTokenAddress) {
        dappToken = IERC20(_dappTokenAddress);
    }

    function setPriceFeedContract(address _token, address _priceFeed)
        public
        onlyOwner
    {
        tokenToPriceFeedAddress[_token] = _priceFeed;
    }

    function issueTokens() public onlyOwner {
        for (
            uint256 stakersIndex = 0;
            stakersIndex < stakers.length;
            stakersIndex++
        ) {
            address recipient = stakers[stakersIndex];
            uint256 userTotalValue = getUserTotalValue(recipient);
            dappToken.transfer(recipient, userTotalValue / 2);
            //Send them a token reward based on their total value locked.
        }
    }

    function getUserTotalValue(address _userAddress) public returns (uint256) {
        uint256 totalValue = 0;
        require(uniqueTokensStaked[_userAddress] > 0, "No tokens staked.");
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++
        ) {
            totalValue =
                totalValue +
                getSingleTokenValue(
                    _userAddress,
                    allowedTokens[allowedTokensIndex]
                );
        }
        return totalValue;
    }

    function getSingleTokenValue(address _user, address _tokenAddress)
        public
        returns (uint256)
    {
        if (uniqueTokensStaked[_user] <= 0) {
            return 0;
        }
        // price of token * amount staked
        (uint256 valueOfToken, uint256 decimals) = getTokenValue(_tokenAddress);
        uint256 value = stakingBalance[_tokenAddress][_user] * valueOfToken;
        return (value / 10**decimals);
    }

    function getTokenValue(address _tokenAddress)
        internal
        returns (uint256, uint256)
    {
        //pricefeed Address
        address priceFeedAddress = tokenToPriceFeedAddress[_tokenAddress];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        uint256 finalPrice = uint256(price);
        return (finalPrice, decimals);
    }

    function unstakeTokens(address _tokenAddress) public {
        uint256 balance = stakingBalance[_tokenAddress][_msgSender()];
        IERC20 token = IERC20(_tokenAddress);
        token.transfer(_msgSender(), balance);
        stakingBalance[_tokenAddress][_msgSender()] = 0;
        uniqueTokensStaked[_msgSender()] -= 1;
    }

    function stakeTokens(uint256 _amount, address _tokenAddress) public {
        require(_amount > 0, "You have to add an amount greater than 0.");
        require(isAllowed(_tokenAddress), "This token can't be staked.");
        IERC20(_tokenAddress).transferFrom(
            _msgSender(),
            address(this),
            _amount
        );
        stakingBalance[_tokenAddress][_msgSender()] =
            stakingBalance[_tokenAddress][_msgSender()] +
            _amount;
        updateUniqueTokensStaked(_msgSender(), _tokenAddress);
        if (uniqueTokensStaked[_msgSender()] == 1) {
            stakers.push(_msgSender());
        }
    }

    function updateUniqueTokensStaked(address _sender, address _tokenAddress)
        internal
        onlyOwner
    {
        if (stakingBalance[_sender][_tokenAddress] <= 0) {
            uniqueTokensStaked[_sender] += 1;
        }
    }

    function addAllowedTokens(address _tokenAddress) public onlyOwner {
        allowedTokens.push(_tokenAddress);
    }

    function isAllowed(address _tokenAddress) internal returns (bool) {
        for (
            uint256 tokenAddressIndex = 0;
            tokenAddressIndex < allowedTokens.length;
            tokenAddressIndex++
        ) {
            if (allowedTokens[tokenAddressIndex] == _tokenAddress) {
                return true;
            }
        }
        return false;
    }
}
