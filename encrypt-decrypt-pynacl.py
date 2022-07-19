"""Module for encryption and decryption compatible with MetaMask."""
from base64 import a85decode, a85encode

# PyNaCl==1.5.0
from nacl.public import Box, PrivateKey, PublicKey


def _hex_to_bytes(hex: str) -> bytes:
    return bytes.fromhex(hex[2:] if hex[:2] == "0x" else hex)


def export_public_key(private_key_hex: str) -> bytes:
    """Export public key for contract join request.
    Args:
        private_key: hex string representing private key
    Returns:
        32 bytes representing public key
    """
    pub_key = PrivateKey(_hex_to_bytes(private_key_hex)).public_key
    print("pub: ", pub_key._public_key.hex())
    
    return bytes(pub_key)


def encrypt_nacl(public_key: bytes, data: bytes) -> bytes:
    """Encryption function using NaCl box compatible with MetaMask
    For implementation used in MetaMask look into: https://github.com/MetaMask/eth-sig-util
    Args:
        public_key: public key of recipient (32 bytes)
        data: message data
    Returns:
        encrypted data
    """
    emph_key = PrivateKey.generate()
    
    print("prv key: ", emph_key)
    
    enc_box = Box(emph_key, PublicKey(public_key))
    # Encryption must work with MetaMask decryption (requires valid utf-8)
    data = a85encode(data)
    ciphertext = enc_box.encrypt(data)
    return bytes(emph_key.public_key) + ciphertext


def decrypt_nacl(private_key: bytes, data: bytes) -> bytes:
    """Decryption function using NaCl box compatible with MetaMask
    For implementation used in MetaMask look into: https://github.com/MetaMask/eth-sig-util
    Args:
        private_key: private key to decrypt with
        data: encrypted message data
    Returns:
        decrypted data
    """
    emph_key, ciphertext = data[:32], data[32:]
    box = Box(PrivateKey(private_key), PublicKey(emph_key))
    return a85decode(box.decrypt(ciphertext))

PRIVATE_KEY_STR = "0xd95d6db65f3e2223703c5d8e205d98e3e6b470f067b0f94f6c6bf73d4301ce48"

pub_key = export_public_key(PRIVATE_KEY_STR)

print("export_public_key: ", pub_key.hex())

encrypted_txt = encrypt_nacl(pub_key, b"Kunal Goyal")

print(decrypt_nacl(_hex_to_bytes(PRIVATE_KEY_STR), encrypted_txt))