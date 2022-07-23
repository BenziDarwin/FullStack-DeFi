from web3 import Web3
from scripts.helpful_scripts import create_contract, get_account, deploy_contracts

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy():
    account = get_account()
    (dappToken, tokenFarm) = deploy_contracts(account)
    tx = dappToken.transfer(
        tokenFarm.address, dappToken.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    weth_token = create_contract("weth_token")
    dai_token = create_contract("fau_token")
    allowedTokensDictionary = {
        dappToken: create_contract("dai_usd_price_feed"),
        dai_token: create_contract("dai_usd_price_feed"),
        weth_token: create_contract("eth_usd_price_feed"),
    }
    addAllowedTokens(tokenFarm, allowedTokensDictionary, account)
    return dappToken, tokenFarm


def addAllowedTokens(tokenFarm, allowedTokensDictionary, account):
    for token in allowedTokensDictionary:
        # dapp_token, weth_token/eth, fau_token/dai
        add_tx = tokenFarm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = tokenFarm.setPriceFeedContract(
            token.address, allowedTokensDictionary[token].address, {"from": account}
        )
        set_tx.wait(1)


def main():
    deploy()
