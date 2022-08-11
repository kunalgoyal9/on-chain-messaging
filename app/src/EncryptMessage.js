import { useState, useRef } from "react";
import { ethers } from "ethers";
import ErrorMessage from "./ErrorMessage";
import { encrypt } from '@metamask/eth-sig-util';
const ethUtil = require('ethereumjs-util');
const sigUtil = require('@metamask/eth-sig-util');
import getWeb3 from './getWeb3.js';
const web33 = require('web3');
const {abi} = require('./PubKeyStore.json');

const naclUtil = require('tweetnacl-util');
const nacl = require('tweetnacl');
const ascii85 = require('ascii85');

async function loadContract() {
  let address = "0xC58A32c5fa0c40D885BB2D19B6560d3212d6882F"
  let web3 = await getWeb3();
  return new web3.eth.Contract(abi, address);
}

const encryptMessage = async ({ setError, message }) => {
  try{
    if (!window.ethereum)
      throw new Error("No crypto wallet found. Please install it.");
    
    await window.ethereum.send("eth_requestAccounts");
    
    // Getting address from metamask
    let web3 = await getWeb3();
    const address = (await web3.eth.getAccounts())[0];
    console.log("address", address);

    // Getting public key from contract
    let myContract = await loadContract();
    const pubKeyFromContract = await myContract.methods.getPublicKeyForAddress(address).call();
    console.log("pubKeyFromContract", pubKeyFromContract);

    if(pubKeyFromContract == "Doesn't exist"){
      setError("ask Receiver to register Public key");
    }
    else{
      // const publicKeyFromTxn = "3028ef11b54cdc264e16efa4aad4d8c23ec7b569ed15b69a385f58940fd6a66f";
      console.log("Encrypting message:: ", message);  
      console.log("publickey base64: ", pubKeyFromContract);
      const encryptedData = encryptData(pubKeyFromContract, message);
      return {
        message,
        encryptedData,
        address
      };
    }
    
  }
  catch(err){
    setError(err.message);
  }
}

function encryptData(publicKey, data){
  const encryptedMessage = ethUtil.bufferToHex(
    Buffer.from(
      JSON.stringify(
        sigUtil.encrypt({
          publicKey: publicKey,
          data: data,
          version: 'x25519-xsalsa20-poly1305',
        })
      ),
      'utf8'
    )
  );
  console.log("encrypted data: ", encryptedMessage);

  return encryptedMessage;
}

function hex_to_base64(msgHex){
  const msgBase64 = Buffer.from(msgHex, 'hex').toString('base64');
  return msgBase64;
}

export default function EncryptMessage() {
  const resultBox = useRef();
  const [signatures, setSignatures] = useState([]);
  const [error, setError] = useState();

  const handleSign = async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    setError();
    const sig = await encryptMessage({
      setError,
      message: data.get("message")
    });
    if (sig) {
      setSignatures([...signatures, sig]);
    }
  };

  return (
    <form className="m-4" onSubmit={handleSign}>
      <div className="credit-card w-full shadow-lg mx-auto rounded-xl bg-white">
        <main className="mt-4 p-4">
          <h1 className="text-xl font-semibold text-gray-700 text-center">
            Encrypt messages
          </h1>
          <div className="">
            <div className="my-3">
              <textarea
                required
                type="text"
                name="message"
                className="textarea w-full h-24 textarea-bordered focus:ring focus:outline-none"
                placeholder="Message"
              />
            </div>
          </div>
        </main>
        <footer className="p-4">
          <button
            type="submit"
            className="btn btn-primary submit-button focus:ring focus:outline-none w-full"
          >
            encrypt message
          </button>
          <ErrorMessage message={error} />
        </footer>
        {signatures.map((sig, idx) => {
          return (
            <div className="p-2" key={sig}>
              <div className="my-3">
                <p>
                  Message {idx + 1}: {sig.message}
                </p>
                <p>Encrypter address: {sig.address}</p>
                <textarea
                  type="text"
                  readOnly
                  ref={resultBox}
                  className="textarea w-full h-24 textarea-bordered focus:ring focus:outline-none"
                  placeholder="Generated signature"
                  value={sig.encryptedData}
                />
              </div>
            </div>
          );
        })}
      </div>
    </form>
  );
}
