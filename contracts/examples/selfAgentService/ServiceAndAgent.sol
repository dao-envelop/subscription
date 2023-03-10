// SPDX-License-Identifier: MIT

pragma solidity 0.8.16;

import "@openzeppelin/contracts/access/Ownable.sol";
import '../../ServiceProvider.sol';
import '../../ServiceAgent.sol';

contract ServicAndAgent is ServiceProvider, ServiceAgent, Ownable {
    
    uint256[] public myTarifIndexes;

    event ServiceOK(uint256 param, address _provider);
    event TicketSold(address indexed buyer, address indexed service, Ticket ticket);

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
        myTarifIndexes.push(newTIndex); 
    }

    function setAgent() external onlyOwner returns(uint256[] memory){
        uint256[] memory idxs = new uint256[](myTarifIndexes.length);
        idxs[0]=myTarifIndexes[0];
        return _authorizeAgentForService(address(this), idxs);
    }

    function buyTicket() external {
        Ticket memory t;
        t = buySubscription(
            address(this),
            0, //  _tarifIndex,
            0, // _payWithIndex,
            msg.sender, // _buyFor,
            msg.sender  // _payer
        );
        
        // put additional code below
        emit TicketSold(msg.sender, address(this), t);
    }

    function getService(uint256 param) external {
        
        // Check ticket
        _checkAndFixSubscription(msg.sender);
        
        // put main service code below
        emit ServiceOK(param, address(this));
    }

     
    
    

}