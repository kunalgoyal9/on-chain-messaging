import requests
from eth_account._utils.legacy_transactions import ALLOWED_TRANSACTION_KEYS
from eth_account._utils.signing import extract_chain_id, to_standard_v
from eth_account._utils.legacy_transactions import serializable_unsigned_transaction_from_dict
import web3

url = 'https://rpc-testnet.lachain.io'
PRIVATE_KEY_STR = "0xd95d6db65f3e2223703c5d8e205d98e3e6b470f067b0f94f6c6bf73d4301ce48"
FROM_ADDRESS = "0x6Bc32575ACb8754886dC283c2c8ac54B1Bd93195"

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

def get_chain_id():
    return int(send_api_request([], "eth_chainId"), 16)

w3 = web3.Web3(web3.HTTPProvider('https://rpc-testnet.lachain.io'))

def get_public_key_from_tx(txHash, chain_id):
    
    # 2. choose some tx from this list and request it with web3.eth.getTransaction
    tx = w3.eth.getTransaction(txHash)
    
    # 3. compose valid signature from its r, s and v fields (convert v to [0..3] interval)
    s = w3.eth.account._keys.Signature(vrs=(
                                        to_standard_v(chain_id),
                                        w3.toInt(tx.r),
                                        w3.toInt(tx.s)
                                        ))
    
    # 4. use recover to recover public key from signature and tx hash
    tt = {k:tx[k] for k in ALLOWED_TRANSACTION_KEYS - {'chainId', 'data'}}
    tt['data']=tx.input
    tt['chainId']=chain_id
    
    ut = serializable_unsigned_transaction_from_dict(tt)
    return s.recover_public_key_from_msg_hash(ut.hash())

def get_transactions_from_address(address):
    tx_response = requests.get("https://scan-test.lachain.io/api?module=account&action=txlist&address=" + address + "&offset=10&page=0")
    tx_response = tx_response.json()['result']
    return tx_response

if __name__ == "__main__":    
    chain_id = get_chain_id()
    
    # 1. get transaction list for given address
    tx_response = get_transactions_from_address(FROM_ADDRESS)
    
    for i in range(0,10):
        pubKey = get_public_key_from_tx(tx_response[i]['hash'], chain_id)
        print("tx hash: ", tx_response[i]['hash'])
        print("public key: ", pubKey)
    