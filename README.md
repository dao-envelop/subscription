## Foundry

**Foundry is a blazing fast, portable and modular toolkit for Ethereum application development written in Rust.**

Foundry consists of:

-   **Forge**: Ethereum testing framework (like Truffle, Hardhat and DappTools).
-   **Cast**: Swiss army knife for interacting with EVM smart contracts, sending transactions and getting chain data.
-   **Anvil**: Local Ethereum node, akin to Ganache, Hardhat Network.
-   **Chisel**: Fast, utilitarian, and verbose solidity REPL.

## Documentation

https://book.getfoundry.sh/

## Usage

### Build

```shell
$ forge build
```

### Test

```shell
$ forge test
```

### Format

```shell
$ forge fmt
```

### Gas Snapshots

```shell
$ forge snapshot
```

### Anvil

```shell
$ anvil
```

### Deploy

```shell
$ forge script script/Deploy.s.sol:DeployScript --rpc-url blast_sepolia --verifier blockscout --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --account ttwo --sender 0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3 --broadcast
```

### Verify

```shell
$ forge verify-contract <deployed address>  ./contracts/SubscriptionRegistry.sol:SubscriptionRegistry --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(address param1)" 0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3)

$ forge verify-contract <deployed address>  ./contracts/examples/envelopAgent/EnvelopAgentWithRegistry.sol:EnvelopAgentWithRegistry --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 
```

### Cast

```shell
$ cast <subcommand>
```

### Help

```shell
$ forge --help
$ anvil --help
$ cast --help
```

### Add forge to existing Brownie project
```shell
$ forge init --force
$ forge install OpenZeppelin/openzeppelin-contracts@v4.9.3
$ forge install dao-envelop/envelop-protocol-v1@1.3.0
$ forge buld
```
### First build
```shell
git clone git@gitlab.com:ubd2/ubd-market-adapters.git
git submodule update --init --recursive
```