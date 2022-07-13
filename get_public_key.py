from curses import raw
from inspect import signature
from itertools import chain
from sys import byteorder
from time import time
from sqlalchemy import null
import web3
from eth_utils import decode_hex, encode_hex
import requests
from eth_keys import keys
from eth_account.messages import encode_defunct
import ethereum

url = 'https://rpc-testnet.lachain.io'
PRIVATE_KEY_STR = "0xd95d6db65f3e2223703c5d8e205d98e3e6b470f067b0f94f6c6bf73d4301ce48"

session = requests.Session()

def send_api_request_to_address(address, params , method):
    payload = { "jsonrpc":"2.0",
                "method":method,
                "params":params,
                "id":0
                }
    
    headers = {'Content-type': 'application/json'}
    response = session.post(address, json=payload, headers=headers)
    try:
        res = response.json()['result']
        return res
    except Exception as eer:
        print("-"*10, "Error in response", "-"*10)
        print(response.json())
        print("-"*10, "Error in response", "-"*10)
        
        print("exception: " + format(eer))
        return eer

def send_api_request(params , method):
    return send_api_request_to_address(url, params, method)

def send_raw_tx(raw_tx):
    return send_api_request([raw_tx], "eth_sendRawTransaction")

def get_chain_id():
    return int(send_api_request([], "eth_chainId"), 16)

def get_balance(address):
    return int(send_api_request([address, "latest"], "eth_getBalance"), 16)

def get_message():
    return "Hey lachain!"

def generate_private_key():
    key_bytes = decode_hex(PRIVATE_KEY_STR)
    return key_bytes

def update_nonce(address):
    method = "eth_getTransactionCount"
    params = [
        address,
        "latest"
    ]
    nonce = send_api_request(params , method)
    int_nonce = nonce
    params = [
        address,
        "pending"
    ]
    nonce = send_api_request(params , method)
    int_nonce = max(int_nonce , nonce)
    return int_nonce

def main_fn(message, chain_id):
    # Serializing transaction 
    encoded_message = message.encode('utf-8')
    
    hex_msg = encode_hex(encoded_message)
   
    # Generating address from private key
    private_key_bytes = generate_private_key()
    address = ethereum.utils.checksum_encode(ethereum.utils.privtoaddr(private_key_bytes))
    
    print(get_balance(address))
    
    print("Address: ", address)
    
    transaction = {
        "from": address,
        "to": "0xc2d3E141F0Ab45B53451B118E5c02A85C010Ed91",
        "value": 2,
        "gas": 100000000,
        "gasPrice": 1,
        "nonce": update_nonce(address),
        "chainId": chain_id,
        "data": hex_msg,
    }
    signed_tx = web3.eth.Account.signTransaction(transaction, private_key_bytes)
    
    # sending signed transaction
    raw_tx = web3.Web3.toHex(signed_tx.rawTransaction)
    tx_hash = send_raw_tx(raw_tx)
    print("Sent tx hash:", tx_hash)
    
    # Creating signature from signed_tx
    print(signed_tx)
    r = signed_tx.r
    s = signed_tx.s
    v = signed_tx.v
    r_bytes = r.to_bytes(length=32,byteorder='big')
    s_bytes = s.to_bytes(length=32,byteorder='big')
    v_bytes = v.to_bytes(length=2,byteorder='big')
    if (chain_id <= 109):
        v_bytes = v.to_bytes(length=1,byteorder='big')
    signature = r_bytes + s_bytes + v_bytes

    encoded_sig = encode_hex(signature)
    
    return null

from eth_account._utils.legacy_transactions import ALLOWED_TRANSACTION_KEYS
from eth_account._utils.signing import extract_chain_id, to_standard_v

if __name__ == "__main__":    
    chain_id = get_chain_id()
    
    # 1. get transaction list for given address
    
    
    # 2. choose some tx from this list and request it with web3.eth.getTransaction
    tx = send_api_request(["0x5ee0eb7a8e867c72752e9965904b5bd71e023b83c6a0506a0ddbc91502316995"], "eth_getTransactionByHash")  
    # print("tx: ", tx)
   
    # 3. compose valid signature from its r, s and v fields (convert v to [0..3] interval)
    s = w3.eth.account._keys.Signature(vrs=(
    to_standard_v(extract_chain_id(chain_id)[1]),
    w3.toInt(tx['r']),
    w3.toInt(tx['s'])
    ))
    print("signature: ", s)
    
    # 4. use recover to recover public key from signature and tx hash
    
    # recovered_message = web3.eth.Account.recover();
    
    tt = {k:tx[k] for k in ALLOWED_TRANSACTION_KEYS - {'chainId', 'data'}}
    tt['data']=tx['input']
    tt['chainId']=extract_chain_id(chain_id)[0]
    
    print("tt: ", tt)
    
    print(ALLOWED_TRANSACTION_KEYS)
        
    # main_fn(msg, chain_id)
    