import pytest

from scripts.deploy import deploy, add_operators, stake


def test_mev_reception(accounts, Lido, NodeOperatorsRegistry, DepositContractMock, LidoMevDistributor):
    deployer = accounts[0]
    treasury = accounts[1]
    oracle = deployer

    # deploy Lido and distributor
    (lido, registry, distributor) = deploy(
        Lido,
        NodeOperatorsRegistry,
        DepositContractMock,
        LidoMevDistributor,
        deployer,
        treasury
    )

    # register three node operators
    operators = accounts[2:5]
    add_operators(registry, operators, deployer)

    # submit ETH to Lido from three addresses, minting stETH
    stakers = [(accounts[5], 1 * 10**18), (accounts[6], 32 * 10**18), (accounts[7], 64 * 10**18)]
    stake(lido, stakers, oracle)

    # print balances
    ops_balances_prev = [ lido.balanceOf(op) for op in operators ]
    stakers_balances_prev = [ lido.balanceOf(addr[0]) for addr in stakers ]

    print('pre-MEV ops stETH balances:', [ bal / 10**18 for bal in ops_balances_prev ])
    print('pre-MEV stakers stETH balances:', [ bal / 10**18 for bal in stakers_balances_prev ])

    # distribute MEV to node operators and stakers
    total_mev = 10 * 10**18
    print(f'distributing MEV, total {total_mev / 10**18} ETH')

    mev_extractor = accounts[9]
    tx = distributor.distribureMev({'from': mev_extractor, 'value': total_mev})
    # tx.info()

    ops_balances_post = [ lido.balanceOf(op) for op in operators ]
    stakers_balances_post = [ lido.balanceOf(addr[0]) for addr in stakers ]

    print('post-MEV ops stETH balances:', [ bal / 10**18 for bal in ops_balances_post ])
    print('post-MEV stakers stETH balances:', [ bal / 10**18 for bal in stakers_balances_post ])

    ops_balances_inc = [
        ops_balances_post[i] - ops_balances_prev[i]
        for i in range(len(ops_balances_post))
    ]

    stakers_balances_inc = [
        stakers_balances_post[i] - stakers_balances_prev[i]
        for i in range(len(stakers_balances_post))
    ]

    print(
        f'ops stETH balances increase (total {sum(ops_balances_inc) / 10**18} stETH):',
        [ bal / 10**18 for bal in ops_balances_inc ]
    )

    print(
        f'stakers stETH balances increase (total {sum(stakers_balances_inc) / 10**18} stETH):',
        [ bal / 10**18 for bal in stakers_balances_inc ]
    )

    assert abs(sum(ops_balances_inc) - sum(stakers_balances_inc)) < 100

    total_balances_inc = sum(ops_balances_inc) + sum(stakers_balances_inc)

    assert total_balances_inc < total_mev
    assert total_mev - total_balances_inc < 100
