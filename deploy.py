import asyncio
import configparser
import os
import time
import web3
import ethereum
import time


FEED_PRIVATE_KEY = bytes.fromhex('')
CHAIN_ID = 226
LOCALNET_NODE = 'http://127.0.0.1:7070'
DEVNET_NODE = 'https://rpc-devnet.lachain.io'
TESTNET_NODE = 'https://rpc-testnet.lachain.io'
MAINNET_NODE = 'https://rpc-mainnet.lachain.io'


class Wallet:
    def __init__(self, private_key, connection):
        self.private_key = private_key
        self.address = ethereum.utils.checksum_encode(ethereum.utils.privtoaddr(self.private_key))
        self.connection = connection
        self.nonce = self.connection.eth.getTransactionCount(self.address)

    def send(self, to, amount):
        transaction = {
            'from': self.address,
            'to': to,
            'value': amount,
            'gas': 4000000,
            'gasPrice': 1,
            'nonce': self.nonce,
            'chainId': CHAIN_ID
        }
        signed = web3.eth.Account.signTransaction(transaction, self.private_key)
        txid = self.connection.eth.sendRawTransaction(signed.rawTransaction)
        self.nonce += 1
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt
        return txid

    def tx_info(self, txid):
        return self.connection.eth.getTransactionReceipt(txid)

    def update_nonce(self):
        time.sleep(5)
        self.nonce = self.connection.eth.getTransactionCount(self.address)

    def deploy_contract(self, bytecode, abi):
        print("Entered deploy_contract")
        contract = self.connection.eth.contract(bytecode=bytecode,  abi=abi)
        # print("contract function: ", contract.all_functions())
        tx = contract.constructor("Wrapped OPETH", "wOPETH").buildTransaction({'from': self.address, "nonce": self.nonce, "gasPrice": 1, 'gas': 100000000000})
        signed = web3.eth.Account.signTransaction(tx, self.private_key)
        txid = bytes.hex(self.connection.eth.sendRawTransaction(signed.rawTransaction))
        tx_receipt = self.connection.eth.wait_for_transaction_receipt(txid)
        return tx_receipt.contractAddress

    def call(self, contract_address, abi):
        contract = self.connection.eth.contract(address=contract_address, abi=abi)
        return contract.functions.name().call()
    
if __name__ == '__main__':
    with open("app/src/PubKeyStore.abi", "r") as abifile:
        abi = abifile.read()
    with open("app/src/PubKeyStore.wasm", "rb") as wasmfile:
        bytecode = bytes.hex(wasmfile.read())

    node = web3.Web3(web3.Web3.HTTPProvider(TESTNET_NODE))
    feed_wallet = Wallet(FEED_PRIVATE_KEY, node)

    result = feed_wallet.deploy_contract(bytecode, abi)
    feed_wallet.update_nonce()
    print(result)

# Contract -> LA testnet
# 0xC58A32c5fa0c40D885BB2D19B6560d3212d6882F