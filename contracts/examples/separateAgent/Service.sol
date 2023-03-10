// SPDX-License-Identifier: MIT

pragma solidity 0.8.16;

import "@openzeppelin/contracts/access/Ownable.sol";
import '../../ServiceProvider.sol';

contract Service is ServiceProvider, Ownable {
    
    uint256[] public myTarifIndex;

    constructor(address _subscrRegistry, address _defaultPayToken)
        ServiceProvider(_subscrRegistry)
    {
        
        PayOption[] memory poArray = new PayOption[](1);
        poArray[0] = PayOption(
                _defaultPayToken, // paymentToken
                1e18, // paymentAmount
                1000  // agentFeePercent
        );

        Tariff memory defaultTarif = Tariff(
            SubscriptionType(
                0, // timelockPeriod
                0, // ticketValidPeriod
                1, // counter
                true, // isAvailable
                owner() // beneficiary
            ),
            poArray
        );

        uint256 newTIndex = _registerServiceTarif(defaultTarif);
        myTarifIndex.push(newTIndex); 

    }

     
    
    

}