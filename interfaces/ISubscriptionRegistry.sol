// SPDX-License-Identifier: MIT

pragma solidity 0.8.16;

import {SubscriptionType, PayOption, Tariff, Ticket} from "../contracts/SubscriptionRegistry.sol";
interface ISubscriptionRegistry   {

    
    function registerServiceTarif(Tariff calldata _newTarif) external returns(uint256);
    
    function authorizeAgentForService(
        address _agent,
        uint256[] calldata _serviceTarifIndexes
    ) external virtual returns (uint256[] memory);

    function buySubscription(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex,
        address _buyFor,
        address _payer
    ) external returns(Ticket memory ticket);

    function editServiceTarif(
        uint256 _tarifIndex, 
        uint256 _timelockPeriod,
        uint256 _ticketValidPeriod,
        uint256 _counter,
        bool _isAvailable,
        address _beneficiary
    ) external;

    function addTarifPayOption(
        uint256 _tarifIndex,
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) external returns(uint256);
    
    function editTarifPayOption(
        uint256 _tarifIndex,
        uint256 _payWithIndex, 
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) external; 
    
    function checkUserSubscription(
        address _user, 
        address _service
    ) external view returns (bool ok);


    function checkAndFixUserSubscription(address _user) external returns (bool ok);

    function fixUserSubscription(address _user) external;


    function getUserTicketForService(
        address _service,
        address _user
    ) external view returns(Ticket memory); 
    
    function getTariffsForService(address _service) external view returns (Tariff[] memory);

    function getTicketPrice(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex
    ) external view returns (address, uint256);

    function getAvailableAgentsTarifForService(
        address _agent, 
        address _service
    ) external view returns(Tariff[] memory); 
}