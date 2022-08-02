import { useState, useRef } from "react";
import { ethers } from "ethers";
import ErrorMessage from "./ErrorMessage";
import { encrypt } from '@metamask/eth-sig-util';

const ascii85 = require('ascii85');

const signMessage = async ({ setError, message }) => {
  try {
    console.log({ message });
    if (!window.ethereum)
      throw new Error("No crypto wallet found. Please install it.");

    await window.ethereum.send("eth_requestAccounts");
    const provider = new ethers.providers.Web3Provider(window.ethereum);
    const signer = provider.getSigner();
    console.log("Account:: ", await signer.getAddress());
    
    encryptData("MCjvEbVM3CZOFu+kqtTYwj7HtWntFbaaOF9YlA/Wpm8=", "hey");
    
    const signature = await signer.signMessage(message);
    const address = await signer.getAddress();
    
    console.log("publicKey:: ", await window.ethereum.request({method: 'eth_getEncryptionPublicKey', params: [address]
    }));

    console.log("decryptedMessage:: ", await window.ethereum.request({method: 'eth_decrypt', params: ["0x53f8d982f679583af2202c36de59d38775b2cca9d38fe3908b6f756bff512a532bd909543119f13ef457f97ebb6814fcaf3a7c34adf3ccdc56f87acd7046ea381b", address]
    }));


    return {
      message,
      signature,
      address
    };
  } catch (err) {
    setError(err.message);
  }
};

function encryptData(publicKey, data){
  // Returned object contains 4 properties: version, ephemPublicKey, nonce, ciphertext
  // Each contains data encoded using base64, version is always the same string
  const enc = encrypt({
    publicKey: publicKey.toString('base64'),
    data: ascii85.encode(data).toString(),
    version: 'x25519-xsalsa20-poly1305',
  });

  console.log("encrypted data: ", enc.ciphertext);
  // We want to store the data in smart contract, therefore we concatenate them
  // into single Buffer
  const buf = Buffer.concat([
    Buffer.from(enc.ephemPublicKey, 'base64'),
    Buffer.from(enc.nonce, 'base64'),
    Buffer.from(enc.ciphertext, 'base64'),
  ]);
  
  // In smart contract we are using `bytes[112]` variable (fixed size byte array)
  // you might need to use `bytes` type for dynamic sized array
  // We are also using ethers.js which requires type `number[]` when passing data
  // for argument of type `bytes` to the smart contract function
  // Next line just converts the buffer to `number[]` required by contract function
  // THIS LINE IS USED IN OUR ORIGINAL CODE:
  // return buf.toJSON().data;
  
  // Return just the Buffer to make the function directly compatible with decryptData function
  return buf;
}

export default function SignMessage() {
  const resultBox = useRef();
  const [signatures, setSignatures] = useState([]);
  const [error, setError] = useState();

  const handleSign = async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    setError();
    const sig = await signMessage({
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
            Sign messages
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
            Sign message
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
                <p>Signer: {sig.address}</p>
                <textarea
                  type="text"
                  readOnly
                  ref={resultBox}
                  className="textarea w-full h-24 textarea-bordered focus:ring focus:outline-none"
                  placeholder="Generated signature"
                  value={sig.signature}
                />
              </div>
            </div>
          );
        })}
      </div>
    </form>
  );
}
