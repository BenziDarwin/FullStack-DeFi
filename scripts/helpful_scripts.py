from eth_typing import ContractName
from brownie import (
    accounts,
    network,
    config,
    DappToken,
    TokenFarm,
    MockWETH,
    MockDAI,
    MockV3Aggregator,
    Contract,
)


LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-cli"]
FORKED_BLOCKCHAIN_ENVIRONMENTS = ["mainnet-fork-dev"]
decimals = 18
initialValue = 2000000000000000000

type_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "weth_token": MockWETH,
    "fau_token": MockDAI,
}


def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_BLOCKCHAIN_ENVIRONMENTS
    ):
        return accounts[0]
    else:
        account = accounts.add(config["wallet"]["key"])
        return account


def deploy_contracts(_account):
    dappToken = None
    tokenFarm = None
    if len(DappToken) <= 0:
        dappToken = DappToken.deploy({"from": _account})
        if len(TokenFarm) <= 0:
            tokenFarm = TokenFarm.deploy(
                dappToken.address,
                {"from": _account},
                publish_source=config["networks"][network.show_active()]["verify"],
            )
            return (dappToken, tokenFarm)
        else:
            tokenFarm = TokenFarm[-1]
            return (dappToken, tokenFarm)
    else:
        dappToken = DappToken[-1]
        if len(TokenFarm) <= 0:
            tokenFarm = TokenFarm.deploy(dappToken.address, {"from": _account})
            return (dappToken, tokenFarm)
        else:
            tokenFarm = TokenFarm[-1]
            return (dappToken, tokenFarm)


def deploy_mock(name):
    account = get_account()
    if name == "fau_token":
        dai = MockDAI.deploy({"from": account})
        return dai
    if name == "weth_token":
        weth = MockWETH.deploy({"from": account})
        return weth
    if name == "mockV3Aggregator":
        aggregator = MockV3Aggregator.deploy(decimals, initialValue, {"from": account})
        return aggregator


def create_contract(_name):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return deploy_mock(_name)

    contract_type = type_to_mock[_name]
    contract = Contract.from_abi(
        contract_type._name,
        config["networks"][network.show_active()][_name],
        contract_type.abi,
    )
    return contract
