import os
from brownie import ZERO_ADDRESS


def deploy(Lido, NodeOperatorsRegistry, DepositContractMock, LidoMevDistributor, deployer, treasury):
    deposit_contract = DepositContractMock.deploy({'from': deployer})
    registry = NodeOperatorsRegistry.deploy({'from': deployer})

    print(f'registry: {registry.address}')

    lido = Lido.deploy(
        deposit_contract,
        deployer,
        registry,
        treasury,
        treasury,
        {'from': deployer}
    )

    print(f'lido: {lido.address}')

    registry.setLido(lido, {'from': deployer})

    lido.setWithdrawalCredentials(os.urandom(32), {'from': deployer})
    lido.resume({'from': deployer})

    # 50% of the received MEV goes to validators, 50% to stakers
    distributor = LidoMevDistributor.deploy(lido, 5 * 10**17, {'from': deployer})

    return (lido, registry, distributor)


def add_operators(registry, operators, deployer, keys_per_operator = 20):
    for i in range(len(operators)):
        registry.addNodeOperator(str(i), operators[i], keys_per_operator, {'from': deployer})
        registry.addSigningKeys(
            i,
            keys_per_operator,
            os.urandom(48 * keys_per_operator),
            os.urandom(96 * keys_per_operator),
            {'from': deployer}
        )
        print(f'added node operator {i}')
        print(dict(registry.getNodeOperator(i, True)))


def stake(lido, stakers, oracle):
    total_ether = 0

    for (staker, amount) in stakers:
        total_ether += amount
        lido.submit(ZERO_ADDRESS, {'value': amount, 'from': staker})
        balance = lido.balanceOf(staker)
        print(f'balance of {staker}: {balance / 10**18} stETH')

    lido.depositBufferedEther({'from': stakers[0][0]})
    (deposited_validators, _, _) = lido.getBeaconStat()

    print('reporting staking rewards...')

    lido.pushBeacon(deposited_validators, (deposited_validators * 32 + 1) * 10**18, {'from': oracle})

    print('beacon stat:', dict(lido.getBeaconStat()))
