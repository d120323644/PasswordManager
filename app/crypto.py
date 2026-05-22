"""
密码管理器 - 加密模块
使用 AES-256-GCM 加密
"""
import base64
import json
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets


class CryptoManager:
    """加密管理器"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def derive_key(self, password: str, salt: bytes) -> bytes:
        """从密码派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=self.backend
        )
        return kdf.derive(password.encode())
    
    def encrypt_data(self, data: dict, password: str) -> dict:
        """加密数据"""
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        key = self.derive_key(password, salt)
        
        aesgcm = AESGCM(key)
        data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
        
        return {
            'salt': base64.b64encode(salt).decode(),
            'nonce': base64.b64encode(nonce).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode()
        }
    
    def decrypt_data(self, encrypted: dict, password: str) -> dict:
        """解密数据"""
        salt = base64.b64decode(encrypted['salt'])
        nonce = base64.b64decode(encrypted['nonce'])
        ciphertext = base64.b64decode(encrypted['ciphertext'])
        
        key = self.derive_key(password, salt)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return json.loads(plaintext.decode('utf-8'))
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple:
        """哈希密码（用于验证主密码）"""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=self.backend
        )
        # 如果传入的是 bytes，返回时也保持 bytes（用于内部验证）
        # 如果是新生成的，返回 base64 字符串（用于存储）
        salt_return = salt if isinstance(salt, bytes) else base64.b64encode(salt).decode()
        return base64.b64encode(kdf.derive(password.encode())).decode(), salt_return
