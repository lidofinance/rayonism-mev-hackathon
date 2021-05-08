# Rayonism MEV hackathon

This repo contains only a demo/mock code, don't use it in production!


## Lido MEV distributor

The main contract in this repo is [`LidoMevDistributor.sol`](./contracts/LidoMevDistributor.sol). Upon ETH reception by the `distribureMev()` function, it does the following:

1. Converts the received ETH to stETH.
2. Burns part of the just-minted stETH, effectively distributing this stETH amount between other stETH holders, proportional to their pool's share.
3. Sends the rest of stETH to validator operators, with each operator receiving the amount proportional to the number of validators it runs.

The split of MEV between stakers (stETH holders) and validator operators is defined by the `_validatorsMevShare` constructor argument which defines the percentage of MEV that goes to validators, `10**18` corresponding to 100%.


## Playing with it

To see how the distribution works, run:

```
brownie test -s
```

This will execute the test scenario defined in [test_mev_distribution.py](./tests/test_mev_distribution.py).
