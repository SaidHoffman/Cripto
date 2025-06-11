# records/utils/crypto.py
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


def generate_ed25519_keypair():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return private_bytes, public_bytes


def generate_x25519_keypair():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return private_bytes, public_bytes

############################################################################################


def encrypt_record_aes_cbc(plaintext: bytes, key: bytes) -> tuple[bytes, bytes]:
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext, iv


def decrypt_record_aes_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder() 
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext


############################################################################################


def sign_record(record_text: bytes, private_key_bytes: bytes) -> bytes:
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    signature = private_key.sign(record_text)
    return signature + record_text


def extract_signature_and_plaintext(signed_data: bytes) -> tuple[bytes, bytes]:
    return signed_data[:64], signed_data[64:]


def verify_signature(public_key_bytes: bytes, signed_data: bytes) -> bool:
    try:
        signature, message = extract_signature_and_plaintext(signed_data)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(signature, message)
        return True
    except Exception:
        return False
    
############################################################################################

def wrap_aes_key_with_x25519(receiver_public_bytes: bytes, aes_key: bytes) -> tuple[bytes, bytes, bytes]:
    # Genera una clave efímera
    sender_private_key = x25519.X25519PrivateKey.generate()
    sender_public_key = sender_private_key.public_key()
    sender_public_bytes = sender_public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    receiver_public_key = x25519.X25519PublicKey.from_public_bytes(receiver_public_bytes)
    shared_secret = sender_private_key.exchange(receiver_public_key)

    # Deriva clave temporal con HKDF
    wrapping_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"x25519 key wrapping",
    ).derive(shared_secret)

    aesgcm = AESGCM(wrapping_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, aes_key, associated_data=None)

    return sender_public_bytes, nonce, ciphertext

def unwrap_aes_key_with_x25519(receiver_private_bytes: bytes, sender_public_bytes: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    receiver_private_key = x25519.X25519PrivateKey.from_private_bytes(receiver_private_bytes)
    sender_public_key = x25519.X25519PublicKey.from_public_bytes(sender_public_bytes)
    shared_secret = receiver_private_key.exchange(sender_public_key)

    wrapping_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"x25519 key wrapping",
    ).derive(shared_secret)

    aesgcm = AESGCM(wrapping_key)
    aes_key = aesgcm.decrypt(nonce, ciphertext, associated_data=None)

    return aes_key

