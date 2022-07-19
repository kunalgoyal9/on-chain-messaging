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
from ecies import encrypt

from getPublicKey_from_tx import get_transactions_from_address, get_public_key_from_tx

url = 'https://rpc-testnet.lachain.io'
PRIVATE_KEY_STR = "0xd95d6db65f3e2223703c5d8e205d98e3e6b470f067b0f94f6c6bf73d4301ce48"
TO_ADDRESS = "0x50E90BD4fb314783DB32Fab94BC1Ace448319c08"

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
    
    # Getting Public Key of address
    tx_response = get_transactions_from_address(TO_ADDRESS)
    pubKey = get_public_key_from_tx(tx_response[0]['hash'], chain_id)
    
    print("public key:", pubKey)
    
    # encrypting the message
    encoded_message = message.encode('utf-8')
    encry = encrypt(str(pubKey), encoded_message)
    hex_msg = encode_hex(encry)
   
    # Generating address from private key
    private_key_bytes = generate_private_key()
    address = ethereum.utils.checksum_encode(ethereum.utils.privtoaddr(private_key_bytes))
    
    print(get_balance(address))
    
    print("Address: ", address)
    
    transaction = {
        "from": address,
        "to": TO_ADDRESS,
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


if __name__ == "__main__":    
    chain_id = get_chain_id()
    msg = get_message()
    
    main_fn(msg, chain_id)
    