import { useState, useRef } from "react";
import ErrorMessage from "./ErrorMessage";
import getWeb3 from './getWeb3.js';
const {abi} = require('./PubKeyStore.json');

async function loadContract() {
  let address = "0xC58A32c5fa0c40D885BB2D19B6560d3212d6882F"
  let web3 = await getWeb3();
  return new web3.eth.Contract(abi, address);
}

const registerPublicKey = async ({setError}) => {
  try{
    // Getting address from metamask
    let web3 = await getWeb3();
    const address = (await web3.eth.getAccounts())[0];
    console.log("address", address);

    // Getting public key from metamask
    const publicKey = await window.ethereum.request({method: 'eth_getEncryptionPublicKey', params: [address]});

    let myContract = await loadContract();
    await myContract.methods.registerMyPublicKey(publicKey).send({from: address});
    const done = true;
    return {
            done,
            address
            };
  }
  catch(err){
    setError(err.message);
  }
}

export default function RegisterPublicKey() {
  const [signatures, setSignatures] = useState([]);
  const [error, setError] = useState();

  const handleSign = async (e) => {
    e.preventDefault();
    setError();
    const sig = await registerPublicKey({
      setError
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
            Register Public Key
          </h1>
        </main>
        <footer className="p-4">
          <button
            type="submit"
            className="btn btn-primary submit-button focus:ring focus:outline-none w-full"
          >
            Register My Public Key
          </button>
          <ErrorMessage message={error} />
        </footer>
        {signatures.map((sig, idx) => {
          return (
            <div className="p-2" key={sig}>
              <div className="my-3">
                <p>
                  Done: {idx + 1}: {sig.done}
                </p>
                <p>Address: {sig.address}</p>
              </div>
            </div>
          );
        })}
      </div>
    </form>
  );
}
