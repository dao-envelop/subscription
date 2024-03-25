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

### Deploy Blast Sepolia

```shell
$ forge script script/Deploy.s.sol:DeployScript --rpc-url blast_sepolia  --account ttwo --sender 0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3 --broadcast
```

#### Verify

```shell
$ forge verify-contract <deployed address>  ./contracts/SubscriptionRegistry.sol:SubscriptionRegistry --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(address param1)" 0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3)

$ forge verify-contract <deployed address>  ./contracts/examples/envelopAgent/EnvelopAgentWithRegistry.sol:EnvelopAgentWithRegistry --verifier-url 'https://api.routescan.io/v2/network/testnet/evm/168587773/etherscan' --etherscan-api-key "verifyContract" --num-of-optimizations 200 --compiler-version 0.8.21 
```

### Deploy Blast Mainnet 2024-03-03

```shell
$ forge script script/Deploy.s.sol:DeployScript --rpc-url blast_mainnet  --account envdeployer --sender 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B --broadcast
```

#### Verify

```shell
$ forge verify-contract 0x68247DF83d594af6332bF901a5fF8c3448622774  ./contracts/SubscriptionRegistry.sol:SubscriptionRegistry --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 --constructor-args $(cast abi-encode "constructor(address param1)" 0xE1a8F0a249A87FDB9D8B912E11B198a2709D6d9B)

$ forge verify-contract 0xD5E1cDfCf6A9fdc68997a90E8B5ee962e536a0D8  ./contracts/examples/envelopAgent/EnvelopAgentWithRegistry.sol:EnvelopAgentWithRegistry --verifier-url 'https://api.blastscan.io/api' --etherscan-api-key $BLASTSCAN_TOKEN --num-of-optimizations 200 --compiler-version 0.8.21 
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
git clone git@gitlab.com:envelop/subscription.git
git submodule update --init --recursive
```