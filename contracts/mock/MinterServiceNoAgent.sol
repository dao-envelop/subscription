pragma solidity 0.8.16;

//import "@envelopv1/interfaces/ITrustedWrapper.sol";
//import "@envelopv1/interfaces/ISubscriptionManager.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import '../../ServiceProvider.sol';
import '../../ServiceAgent.sol';

contract MinterServiceNoAgent is ERC721URIStorage, ServiceProvider, ServiceAgent, Ownable {
	
	constructor(address _subscrRegistry)
	        ServiceProvider(_subscrRegistry){}

	    /*function buyTicket() external {
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
	    }*/

	    function registerServiceTarif(Tariff memory _newTarif) 
	        external onlyOwner returns(uint256)
	    {
	        return _registerServiceTarif(_newTarif);
	    }

	    function editServiceTarif(
	        uint256 _tarifIndex, 
	        uint256 _timelockPeriod,
	        uint256 _ticketValidPeriod,
	        uint256 _counter,
	        bool _isAvailable,
	        address _beneficiary
	    )  external onlyOwner 

	    {
	        _editServiceTarif(
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
	    ) external onlyOwner  returns(uint256)
	    {
	        return _addTarifPayOption(
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
	    ) external onlyOwner 
	    {
	        _editTarifPayOption(
	            _tarifIndex,
	            _payWithIndex, 
	            _paymentToken,
	            _paymentAmount,
	            _agentFeePercent
	        );
	    } 

	    function authorizeAgentForService(
	        address _agent,
	        uint256[] memory _serviceTarifIndexes
	    ) external onlyOwner returns (uint256[] memory)
	    {
	        // TODO Check agent
	        return _authorizeAgentForService(
	            _agent,
	            _serviceTarifIndexes
	        );
	    }

	    ////////////////////////////
	    //        Main USAGE      //
	    ////////////////////////////
	    function checkAndFixSubscription(address _user) 
	        external 
	        returns (bool ok) 
	    {
	            ok = _checkAndFixSubscription(address _user);
	    }

	    
	    function fixUserSubscription(
	        address _user
	    ) external {
	            _fixUserSubscription(
	                _user
	            );
	    }

	    function checkUserSubscription(address _user) 
	        external 
	        view 
	        returns (bool ok)
	    {
	            ok = _checkUserSubscription(
	                _user,
	                address(this)  
	            );
	    }

	    function mint(uint256 tokenId) external {
	    	_checkAndFixSubscription(msg.sender);
	        _mint(msg.sender, tokenId);
	    }

}