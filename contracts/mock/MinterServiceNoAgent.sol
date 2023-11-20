// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import '../ServiceProviderOwnable.sol';
import '../ServiceAgent.sol';

contract MinterServiceNoAgent is ERC721URIStorage, ServiceProviderOwnable, ServiceAgent {
	
	constructor(address _subscrRegistry, string memory name_,
        string memory symbol_) 
			ERC721(name_, symbol_)
	        ServiceProviderOwnable(_subscrRegistry) {}


	    ////////////////////////////
	    //        Main USAGE      //
	    ////////////////////////////
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

	    function changeSubscriptionRegistry(address _subscrRegistry) external onlyOwner {
	    	subscriptionRegistry = ISubscriptionRegistry(_subscrRegistry);
	    }

}