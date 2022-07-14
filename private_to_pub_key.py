from eth_utils import decode_hex, encode_hex
from ethereum.utils import normalize_key, encode_int32
from py_ecc.secp256k1 import privtopub

PRIVATE_KEY_STR = "0xd95d6db65f3e2223703c5d8e205d98e3e6b470f067b0f94f6c6bf73d4301ce48"

def generate_private_key():
    key_bytes = decode_hex(PRIVATE_KEY_STR)
    return key_bytes

private_key_bytes = generate_private_key()
k = normalize_key(private_key_bytes)

pubx, puby = privtopub(k)
pubEx, pubEy = hex(pubx), hex(puby)
print("pub: ", pubEx + pubEy[2:])



# Another method
import eth_keys
privateBytes = decode_hex(PRIVATE_KEY_STR)

signerPrivKey = eth_keys.keys.PrivateKey(privateBytes)
signerPubKey = signerPrivKey.public_key
# print('Public key (uncompressed, 128 hex digits):', signerPubKey)
