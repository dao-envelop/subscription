// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) Team. Subscription Registry Contract V2
pragma solidity 0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import '../ServiceAgent.sol';

contract AgentForService is Ownable, ServiceAgent  {

	function withdrawEther(address _feeReceiver) external onlyOwner {
	        _withdrawEther(_feeReceiver);
    }

    function withdrawTokens(address _erc20, address _feeReceiver) external onlyOwner {
	        _withdrawTokens(_erc20, _feeReceiver);
    }
}