# Envelop On-Chain Subscription Platform
The subscription platform operates with the following role model (it is assumed that the actor with the role is implemented as a contract):
- **Service Provider** is a contract whose services are sold by subscription.
- **Agent** - a contract that sells a subscription on behalf ofservice provider. May receive sales commission
- **Platform** - SubscriptionRegistry contract that performs processingsubscriptions, fares, tickets

## Usage with eth-brownie framework
1. Install package
```bash
brownie pm install dao-envelop/subscription@0.0.2		
```
2. Edit `brownie-config.yaml`, something like
```yaml
dotenv: .env
compiler:
    solc:
        remappings:
          - "@envelop-subscription=dao-envelop/subscription@0.0.2"
```
3. Then you can use @substitution in your Solidity code:
```solidity
import '@envelop/contracts/ServiceAgent.sol';
```

## Development
We use Brownie framework for developing and unit test. For run tests
first please [install it](https://eth-brownie.readthedocs.io/en/stable/install.html)  
To run long tests you must rename test files in tests folder before running (delete "long_").

So just clone https://github.com/dao-envelop/subscription , install dependencies and good luck!
