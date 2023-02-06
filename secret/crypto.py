import os

from cryptography.fernet import Fernet


def create_key():
    key = Fernet.generate_key()
    with open('crypto.key', 'wb') as crypto_key:
        crypto_key.write(key)

def get_cipher():
    dir_path = os.path.dirname(__file__)
    key = open(dir_path + '/crypto.key', 'rb').read()
    return Fernet(key)

def encrypt_text(text):
    byte_text = bytes(text, 'utf-8')
    encrypted_byte_text = get_cipher().encrypt(byte_text)
    encrypted_text = encrypted_byte_text.decode()
    return encrypted_text

def decrypt_text(encrypted_text):
    encrypted_byte_text = bytes(encrypted_text, 'utf-8')
    decrypted_byte_text = get_cipher().decrypt(encrypted_byte_text)
    decrypted_text = decrypted_byte_text.decode()
    return decrypted_text



from datetime import datetime, timedelta

a = datetime.now()

b = 60

c = a + timedelta(seconds=b)

print(a < c)