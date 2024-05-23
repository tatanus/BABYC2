import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES


class Encryption:
    def __init__(self, defaultKey: str = b"This is a test key, do not use for real!"):
        self.key = defaultKey
        self.sha = hashlib.sha256()
        self.sha.update(self.key)
        self.encHash = self.sha.digest()

    def encrypt(self, data):
        """ Simple generic encryption code using Crypto.Cipher.AES"""
        paddedData = data + (chr((AES.block_size - len(data) % AES.block_size)) * (
                AES.block_size - len(data) % AES.block_size)).encode('utf-8')
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.encHash, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(paddedData)

    def decrypt(self, data):
        """ Simple generic decryption code using Crypto.Cipher.AES"""
        iv = data[0:AES.block_size]
        cipher = AES.new(self.encHash, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(data[AES.block_size:])
        padChar = decrypted[len(decrypted) - 1]
        if padChar <= AES.block_size:
            decrypted = decrypted[:-padChar]
        return decrypted

    @staticmethod
    def b64encode(data):
        return base64.b64encode(data)

    @staticmethod
    def b64decode(data):
        return base64.b64decode(data)

    @staticmethod
    def splitData(data, datasize=2048):
        """ Small helper function so split something into chunks."""
        output = []
        for i in range(0, len(data), datasize):
            output.append(data[i:i + datasize])
        return output


if __name__ == "__main__":
    enc = Encryption()
    data = b"Hello, this is a test"
    print(f"Original data: {data}")
    encrypted = enc.encrypt(data)
    print(f"Encrypted data: {encrypted}")
    decrypted = enc.decrypt(encrypted)
    print(f"Decrypted data: {decrypted}")
    print(f"Original data: {data}")
    print(f"Original data matches decrypted data: {data == decrypted}")
    print(f"Base64 encoded data: {enc.b64encode(data)}")
    print(f"Base64 decoded data: {enc.b64decode(enc.b64encode(data))}")
    print(f"Split data: {enc.splitData(data)}")
    print(f"Split data: {enc.splitData(data, 5)}")
    print(f"Split data: {enc.splitData(data, 10)}")
