import { useState, useRef } from "react";
import { ethers } from "ethers";
import ErrorMessage from "./ErrorMessage";
import SuccessMessage from "./SuccessMessage";

const decryptMessage = async ({ encryptedMessage}) => {
  try {
    
    // const address = await window.web3.currentProvider;
    const address = await window.ethereum.request({method: 'eth_accounts', params: []})
    // const address = "0x6Bc32575ACb8754886dC283c2c8ac54B1Bd93195";

    console.log("address: ", address[0]);
    console.log("encrypted message: ", encryptedMessage);

    const decryptedMessage = await window.ethereum.request({method: 'eth_decrypt', params: [encryptedMessage, address[0]]})

    // const signerAddr = await ethers.utils.verifyMessage(message, signature);
    
    return decryptedMessage;

  } catch (err) {
    console.log(err);
    return "Error";
  }
};

export default function DecryptMessage() {
  const [error, setError] = useState();
  const [successMsg, setSuccessMsg] = useState();

  const handleVerification = async (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    setSuccessMsg();
    setError();
    const decryptedMessage = await decryptMessage({
      setError,
      encryptedMessage: data.get("message"),
      // address: data.get("address"),
      // signature: data.get("signature")
    });

    if (decryptedMessage) {
      setSuccessMsg(decryptedMessage);
    } else {
      setError("Invalid signature");
    }
  };

  return (
    <form className="m-4" onSubmit={handleVerification}>
      <div className="credit-card w-full shadow-lg mx-auto rounded-xl bg-white">
        <main className="mt-4 p-4">
          <h1 className="text-xl font-semibold text-gray-700 text-center">
          Decrypt Message
          </h1>
          <div className="">
            <div className="my-3">
              <textarea
                required
                type="text"
                name="message"
                className="textarea w-full h-24 textarea-bordered focus:ring focus:outline-none"
                placeholder="Encrypted Message"
              />
            </div>
          </div>
        </main>
        <footer className="p-4">
          <button
            type="submit"
            className="btn btn-primary submit-button focus:ring focus:outline-none w-full"
          >
            Decrypt Message
          </button>
        </footer>
        <div className="p-4 mt-4">
          <ErrorMessage message={error} />
          <SuccessMessage message={successMsg} />
        </div>
      </div>
    </form>
  );
}
