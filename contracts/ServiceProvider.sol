// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Service Provider 
// abstract contract implements subscribing features.
// For use in cases with subscription

/// @title ServiceProvider abstract contract 
/// @author Envelop project Team
/// @notice Abstract contract implements subscribing features.
/// For use with SubscriptionRegestry
/// @dev Use this code in service provider contract that
/// want use subscription. One contract = one servie

pragma solidity 0.8.16;

import "../interfaces/ISubscriptionRegistry.sol";

abstract contract ServiceProvider {

	address public serviceProvider;
    ISubscriptionRegistry public subscriptionRegistry;

	constructor(address _subscrRegistry) {
        require(_subscrRegistry != address(0), 'Non zero only');
	 	serviceProvider = address(this);
        subscriptionRegistry = ISubscriptionRegistry(_subscrRegistry);
	}

    function registerServiceTarif(Tariff calldata _newTarif) 
        public virtual returns(uint256)
    {
        return subscriptionRegistry.registerServiceTarif(_newTarif);
    }

    
    function editServiceTarif(
        uint256 _tarifIndex, 
        uint256 _timelockPeriod,
        uint256 _ticketValidPeriod,
        uint256 _counter,
        bool _isAvailable,
        address _beneficiary
    ) public virtual 
    {
        subscriptionRegistry.editServiceTarif(
            _tarifIndex, 
            _timelockPeriod,
            _ticketValidPeriod,
            _counter,
            _isAvailable,
            _beneficiary
        );
    }

    function addTarifPayOption(
        uint256 _tarifIndex,
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) external virtual returns(uint256)
    {
        return subscriptionRegistry.addTarifPayOption(
            _tarifIndex,
            _paymentToken,
            _paymentAmount,
            _agentFeePercent
        );
    }
    
    function editTarifPayOption(
        uint256 _tarifIndex,
        uint256 _payWithIndex, 
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) external virtual 
    {
        subscriptionRegistry.editTarifPayOption(
            _tarifIndex,
            _payWithIndex, 
            _paymentToken,
            _paymentAmount,
            _agentFeePercent
        );
    } 

    function authorizeAgentForService(
        address _agent,
        uint256[] calldata _serviceTarifIndexes
    ) external virtual returns (uint256[] memory)
    {
        // TODO Check agent
        return subscriptionRegistry.authorizeAgentForService(
            _agent,
            _serviceTarifIndexes
        );
    }

    ////////////////////////////
    //        Main USAGE      //
    ////////////////////////////
    function _checkAndFixSubscription(address _user) 
        internal 
        returns (bool ok) 
    {
            ok = subscriptionRegistry.checkAndFixUserSubscription(
                _user
            );
    }

    
    function _fixUserSubscription(
        address _user
    ) internal {
            subscriptionRegistry.fixUserSubscription(
                _user
            );
    }

    function _checkUserSubscription(address _user) 
        internal 
        view 
        returns (bool ok)
    {
            ok = subscriptionRegistry.checkUserSubscription(
                _user,
                address(this)  
            );
    }
}