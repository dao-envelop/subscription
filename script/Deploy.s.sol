// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.21;

import {Script, console2} from "forge-std/Script.sol";
import "../lib/forge-std/src/StdJson.sol";
import {SubscriptionRegistry} from "../contracts/SubscriptionRegistry.sol";
import {EnvelopAgentWithRegistry} from "../contracts/examples/envelopAgent/EnvelopAgentWithRegistry.sol";

contract DeployScript is Script {
    using stdJson for string;

    function run() public {
        console2.log("Chain id: %s", vm.toString(block.chainid));
        console2.log("Deployer address: %s, %s", msg.sender, msg.sender.balance);

        // Load json with chain params
        string memory root = vm.projectRoot();
        string memory params_path = string.concat(root, "/script/chain_params.json");
        string memory params_json_file = vm.readFile(params_path);
        string memory key;

        // Define constructor params
        address plOwner;   
        key = string.concat(".", vm.toString(block.chainid),".platform_owner");
        if (vm.keyExists(params_json_file, key)) 
        {
            plOwner = params_json_file.readAddress(key);
        } else {
            plOwner = msg.sender;
        }
        console2.log("plOwner: %s", plOwner); 
        
        key = string.concat(".", vm.toString(block.chainid), ".wl_assets");
        console2.log("current key is: %s", key); 
        console2.log("key exist: %s", vm.keyExists(params_json_file, key)); 
        address[] memory wlAssets;
        if (vm.keyExists(params_json_file, key)) {
            wlAssets = params_json_file.readAddressArray(key);
            console2.log("wlAssets.length: %s", wlAssets.length); 
            for (uint256 i = 0; i < wlAssets.length; ++ i) {
                console2.log("wlAsset[%s]: %s", i, wlAssets[i]);
            }
        }

        key = string.concat(".", vm.toString(block.chainid),".wrapperTrustedV2_address");
        address wrapperTrusted;
        if (vm.keyExists(params_json_file, key)) {
            wrapperTrusted = params_json_file.readAddress(key);
        }
        console2.log("wrapper: %s", wrapperTrusted); 
        
        //////////   Deploy   //////////////
        vm.startBroadcast();
        SubscriptionRegistry sub_reg = new SubscriptionRegistry(plOwner);
        EnvelopAgentWithRegistry agent = new EnvelopAgentWithRegistry();
        vm.stopBroadcast();
        
        ///////// Pretty printing ////////////////
        
        string memory path = string.concat(root, "/script/explorers.json");
        string memory json = vm.readFile(path);
        console2.log("Chain id: %s", vm.toString(block.chainid));
        string memory explorer_url = json.readString(
            string.concat(".", vm.toString(block.chainid))
        );
        
        console2.log("**SubscriptionRegistry**");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(sub_reg));
        console2.log("**EnvelopAgentWithRegistry**");
        console2.log("https://%s/address/%s#code\n", explorer_url, address(agent));

        console2.log("```python");
        console2.log("sub_reg = SubscriptionRegistry.at('%s')", address(sub_reg));
        console2.log("agent = EnvelopAgentWithRegistry.at('%s')", address(agent));
        console2.log("```");

        ///////// End of pretty printing ////////////////

        ///  Init ///
        vm.startBroadcast();
        if (wrapperTrusted != address(0)) {
            console2.log("setMainWrapper: %s", wrapperTrusted);
            sub_reg.setMainWrapper(wrapperTrusted);
        }

        for (uint256 i = 0; i < wlAssets.length; ++ i) {
            console2.log("Adding to white list: %s", wlAssets[i]);
            sub_reg.setAssetForPaymentState(wlAssets[i], true);
        }
        
        vm.stopBroadcast();

    }
}
