import pytest
from brownie import network, accounts, exceptions
from scripts.deploy import deploy
from scripts.helpful_scripts import create_contract, get_account, initialValue

LOCAL_BLOCKCHAIN_NETWORKS = ["ganache", "development"]
FORKED_BLOCKCHAIN_NETWORKS = ["mainnet-fork-dev"]


def test_set_price_feed_contract():
    account = get_account()
    non_owner = accounts[1]
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip("Only for local testing!")
    else:
        dappToken, tokenFarm = deploy()
        dappPriceFeed = create_contract("dai_usd_price_feed")
        set_tx = tokenFarm.setPriceFeedContract(
            dappToken.address, dappPriceFeed.address, {"from": account}
        )
        set_tx.wait(1)
        assert (
            tokenFarm.tokenToPriceFeedAddress(dappToken.address)
            == dappPriceFeed.address
        )
        with pytest.raises(exceptions.VirtualMachineError):
            set_tx = tokenFarm.setPriceFeedContract(
                dappToken.address, dappPriceFeed.address, {"from": non_owner}
            )
            set_tx.wait(1)
            assert (
                tokenFarm.tokenToPriceFeedAddress(dappToken.address)
                == dappPriceFeed.address
            )


def test_stake_tokens(amount_staked):
    # Arrange
    account = get_account()
    non_owner = accounts[1]
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip("Only for local testing!")
    else:
        # Act
        dappToken, tokenFarm = deploy()
        tx = dappToken.approve(tokenFarm.address, amount_staked, {"from": account})
        tx.wait(1)
        add_tx = tokenFarm.addAllowedTokens(dappToken.address, {"from": account})
        add_tx.wait(1)
        st_tx = tokenFarm.stakeTokens(
            amount_staked, dappToken.address, {"from": account}
        )
        st_tx.wait(1)
        # Assert
        assert (
            tokenFarm.stakingBalance(dappToken.address, account.address)
            == amount_staked
        )
        assert tokenFarm.uniqueTokensStaked(account.address) == 1
        assert tokenFarm.stakers(0) == account.address
    return tokenFarm, dappToken


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip("Only for local testing!")
    else:
        account = get_account()
        non_owner = accounts[1]
        tokenFarm, dappToken = test_stake_tokens(amount_staked)
        starting_balance = dappToken.balanceOf(account.address)
        # Act
        tx = tokenFarm.issueTokens({"from": account})
        tx.wait(1)
        # Assert
        assert (
            dappToken.balanceOf(account.address) == starting_balance + initialValue * 2
        )
