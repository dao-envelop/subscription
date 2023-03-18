// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) Team. Subscription Registry Contract V2
pragma solidity 0.8.16;

import "@openzeppelin/contracts/access/Ownable.sol";
import '../ServiceAgent.sol';

contract AgentForService is Ownable, ServiceAgent  {

	function withdrawEthers(address _feeReceiver) external onlyOwner {
	        withdrawEther(_feeReceiver);
    }

    function withdrawERC20Tokens(address _erc20, address _feeReceiver) external onlyOwner {
	        withdrawTokens(_erc20, _feeReceiver);
    }
}