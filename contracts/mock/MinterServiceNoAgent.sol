pragma solidity 0.8.16;

//import "@envelopv1/interfaces/ITrustedWrapper.sol";
//import "@envelopv1/interfaces/ISubscriptionManager.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import '../ServiceProvider.sol';
import '../ServiceAgent.sol';

contract MinterServiceNoAgent is ERC721URIStorage, ServiceProvider, ServiceAgent, Ownable {
	
	constructor(address _subscrRegistry, string memory name_,
        string memory symbol_) 
			ERC721(name_, symbol_)
	        ServiceProvider(_subscrRegistry) {}

	    function registerServiceTariff(Tariff memory _newTariff) 
	        external onlyOwner returns(uint256)
	    {
	        return _registerServiceTariff(_newTariff);
	    }

	    function editServiceTariff(
	        uint256 _tariffIndex, 
	        uint256 _timelockPeriod,
	        uint256 _ticketValidPeriod,
	        uint256 _counter,
	        bool _isAvailable,
	        address _beneficiary
	    )  external onlyOwner 

	    {
	        _editServiceTariff(
	            _tariffIndex, 
	            _timelockPeriod,
	            _ticketValidPeriod,
	            _counter,
	            _isAvailable,
	            _beneficiary
	        );
	    }

	    function addTariffPayOption(
	        uint256 _tariffIndex,
	        address _paymentToken,
	        uint256 _paymentAmount,
	        uint16 _agentFeePercent
	    ) external onlyOwner  returns(uint256)
	    {
	        return _addTariffPayOption(
	            _tariffIndex,
	            _paymentToken,
	            _paymentAmount,
	            _agentFeePercent
	        );
	    }
	    
	    function editTariffPayOption(
	        uint256 _tariffIndex,
	        uint256 _payWithIndex, 
	        address _paymentToken,
	        uint256 _paymentAmount,
	        uint16 _agentFeePercent
	    ) external onlyOwner 
	    {
	        _editTariffPayOption(
	            _tariffIndex,
	            _payWithIndex, 
	            _paymentToken,
	            _paymentAmount,
	            _agentFeePercent
	        );
	    } 

	    function authorizeAgentForService(
	        address _agent,
	        uint256[] memory _serviceTariffIndexes
	    ) external onlyOwner returns (uint256[] memory)
	    {
	        // TODO Check agent
	        return _authorizeAgentForService(
	            _agent,
	            _serviceTariffIndexes
	        );
	    }

	    ////////////////////////////
	    //        Main USAGE      //
	    ////////////////////////////
	    function checkAndFixSubscription(address _user) 
	        external 
	        returns (bool ok) 
	    {
	            ok = _checkAndFixSubscription(_user);
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
	        returns (bool ok, bool needFix)
	    {
	            (ok, needFix) = _checkUserSubscription(
	                _user
	            );
	    }

	    function mint(uint256 tokenId) external {
	    	_checkAndFixSubscription(msg.sender);
	        _mint(msg.sender, tokenId);
	    }

}