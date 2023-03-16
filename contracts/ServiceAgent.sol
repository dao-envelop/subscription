// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Service Agent 
// abstract contract implements service agent logic.
// For use in cases with subscription regitry contract

/// @title ServiceAgent abstract contract 
/// @author Envelop project Team
/// @notice Abstract contract implements service agent logic.
/// For use with SubscriptionRegestry
/// @dev Use this code in service agent
/// for tickets selling

pragma solidity 0.8.16;

import {Ticket} from "../contracts/SubscriptionRegistry.sol";
import "../interfaces/IServiceProvider.sol";

abstract contract ServiceAgent{

	//address public serviceProvider;
    //ISubscriptionRegistry public subscriptionRegistry;

	
    function buySubscription(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex,
        address _buyFor,
        address _payer
    ) public payable returns(Ticket memory ticket)
    {
        // get service provider
        IServiceProvider sP = IServiceProvider(_service);
        
        // call SubscriptionRegistry that registered on current
        // service provider
        //return ISubscriptionRegistry(sP.subscriptionRegistry).buySubscription(
        ticket = sP.subscriptionRegistry().buySubscription{value: msg.value}(
            _service,
            _tarifIndex,
            _payWithIndex,
            _buyFor,
            _payer
        );

    }
}