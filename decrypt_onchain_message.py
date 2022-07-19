from ecies import decrypt
from eth_utils import decode_hex
import eth_keys

priv = "0x27a4efc920b24deb68f6376c1d4a8aee4dd1ab985247c8de6770be2890210baa"
privateBytes = decode_hex(priv)
signerPrivKey = eth_keys.keys.PrivateKey(privateBytes)

sk_hex = signerPrivKey.to_hex()  # hex string

encry = "0x048aa849fde0fbb9cd0625408ca2f8e4d3e83de90f5f806c0472c88e559b81482423002ba0f4fcaf32d8e5d71d0591a9cdd0a84f9da3e6d7234be4f7c0a5cdc87e6e04d2b68ca7f1b15b0059177c836dbab688173e349fb8730fbe2a742f1eb0a4fdeb86db0450b3397f423573"
decoded_encry = decode_hex(encry)

dec = decrypt(sk_hex, decoded_encry)
print("dec: ", dec)