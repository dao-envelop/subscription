// SPDX-License-Identifier: MIT

pragma solidity 0.8.21;

import "@openzeppelin/contracts/access/Ownable.sol";
import '../../ServiceProvider.sol';

contract Service is ServiceProvider, Ownable {
    
    uint256[] public myTariffIndexes;

    event ServiceOK(uint256 param, address _provider);

    constructor(address _subscrRegistry, address _defaultPayToken)
        ServiceProvider(_subscrRegistry)
    {
        
        PayOption[] memory poArray = new PayOption[](1);
        poArray[0] = PayOption(
                _defaultPayToken, // paymentToken
                1e18, // paymentAmount
                1000  // agentFeePercent
        );

        Tariff memory defaultTariff = Tariff(
            SubscriptionType(
                0, // timelockPeriod
                0, // ticketValidPeriod
                1, // counter
                true, // isAvailable
                owner() // beneficiary
            ),
            poArray
        );

        uint256 newTIndex = _registerServiceTariff(defaultTariff);
        myTariffIndexes.push(newTIndex); 
    }

    function setAgent(
        address _agent
    ) external onlyOwner returns(uint256[] memory){
        uint256[] memory idxs = new uint256[](myTariffIndexes.length);
        idxs[0]=myTariffIndexes[0];
        return _authorizeAgentForService(_agent, idxs);
    }

    function getService(uint256 param) external {
        
        // Check ticket
        _checkAndFixSubscription(msg.sender);
        
        // put main service code below
        emit ServiceOK(param, address(this));
    }

     
    
    

}