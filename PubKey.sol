// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract PubKeyStore {

    struct PubKeyS {
        string public_key;  
        bool isThere;
    }

    mapping(address => PubKeyS) public pubkeyMap;
    
    function registerMyPublicKey(string calldata pubK) public {
        address sender = msg.sender;
        pubkeyMap[sender].public_key = pubK;
        pubkeyMap[sender].isThere = true;
    }

    function getPublicKeyForAddress() public view returns (string memory){
        address sender = msg.sender;
        if(pubkeyMap[sender].isThere){
            return pubkeyMap[sender].public_key;
        }
        else{
            return "Doesn't exist";
        }
    }
}