// SPDX-License-Identifier: MIT

pragma solidity 0.8.16;

//import "@openzeppelin/contracts/access/Ownable.sol";
import '../../ServiceAgent.sol';

contract Agent is ServiceAgent {
    
    event TicketSold(address indexed buyer, address indexed service, Ticket ticket);
    
    function buyTicket(address _service) external payable {
        Ticket memory t;
        t = buySubscription(
            _service,
            0, //  _tarifIndex,
            0, // _payWithIndex,
            msg.sender, // _buyFor,
            msg.sender  // _payer
        );
        
        // put additional code below
        emit TicketSold(msg.sender, _service, t);
    }

     
    
    

}