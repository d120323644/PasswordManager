"""
密码管理器 - 数据管理模块
处理数据存储、加载、锁定机制
"""
import json
import os
import time
from datetime import datetime, timedelta
from .crypto import CryptoManager


class PasswordData:
    """密码数据管理"""
    
    def __init__(self, data_file: str = "passwords.dat"):
        self.data_file = data_file
        self.crypto = CryptoManager()
        self.is_unlocked = False
        self.lock_until = None
        self.failed_attempts = 0
        self.max_attempts = 5
        self.lockout_hours = 24
        
    def _get_lock_file(self) -> str:
        """获取锁定状态文件路径"""
        return self.data_file + ".lock"
    
    def check_lock_status(self) -> dict:
        """检查锁定状态"""
        lock_file = self._get_lock_file()
        
        if os.path.exists(lock_file):
            try:
                with open(lock_file, 'r', encoding='utf-8') as f:
                    lock_data = json.load(f)
                    lock_until = datetime.fromisoformat(lock_data['lock_until'])
                    
                    if datetime.now() < lock_until:
                        # 仍在锁定中
                        remaining = lock_until - datetime.now()
                        return {
                            'is_locked': True,
                            'remaining_hours': remaining.total_seconds() / 3600,
                            'remaining_minutes': remaining.total_seconds() / 60
                        }
                    else:
                        # 锁定已过期，清除
                        self.failed_attempts = 0
                        os.remove(lock_file)
            except Exception as e:
                print(f"读取锁定文件失败：{e}")
        
        return {'is_locked': False}
    
    def _save_lock_status(self):
        """保存锁定状态"""
        lock_file = self._get_lock_file()
        lock_until = datetime.now() + timedelta(hours=self.lockout_hours)
        
        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump({
                'failed_attempts': self.failed_attempts,
                'lock_until': lock_until.isoformat(),
                'created_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def verify_master_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """验证主密码"""
        # 先检查是否被锁定
        lock_status = self.check_lock_status()
        if lock_status['is_locked']:
            return False
        
        import base64
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        
        # stored_salt 是 base64 字符串，需要解码成 bytes
        salt = base64.b64decode(stored_salt)
        computed_hash, _ = self.crypto.hash_password(password, salt)
        
        if computed_hash == stored_hash:
            # 密码正确，重置失败计数
            self.failed_attempts = 0
            lock_file = self._get_lock_file()
            if os.path.exists(lock_file):
                os.remove(lock_file)
            return True
        else:
            # 密码错误
            self.failed_attempts += 1
            
            if self.failed_attempts >= self.max_attempts:
                # 达到最大尝试次数，锁定
                self._save_lock_status()
            
            return False
    
    def load_data(self, password: str) -> list:
        """加载加密的密码数据"""
        if not os.path.exists(self.data_file):
            return []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                encrypted = json.load(f)
            
            data = self.crypto.decrypt_data(encrypted, password)
            self.is_unlocked = True
            return data.get('passwords', [])
        except Exception as e:
            raise Exception(f"解密失败：{str(e)}")
    
    def save_data(self, passwords: list, password: str):
        """保存加密的密码数据"""
        encrypted = self.crypto.encrypt_data({'passwords': passwords}, password)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(encrypted, f, ensure_ascii=False, indent=2)
    
    def export_data(self, passwords: list, export_file: str, master_password: str):
        """导出数据（加密格式）"""
        encrypted = self.crypto.encrypt_data({'passwords': passwords}, master_password)
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(encrypted, f, ensure_ascii=False, indent=2)
    
    def import_data(self, import_file: str, master_password: str) -> list:
        """导入数据"""
        with open(import_file, 'r', encoding='utf-8') as f:
            encrypted = json.load(f)
        
        return self.crypto.decrypt_data(encrypted, master_password)
    
    def setup_master_password(self, password: str) -> tuple:
        """设置主密码（首次使用）"""
        hashed, salt = self.crypto.hash_password(password)
        return hashed, base64.b64encode(salt).decode()
