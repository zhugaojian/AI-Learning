"""
用户登录认证模块
"""
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import os

class UserAccount:
    """用户账户类"""
    def __init__(self, username: str, password_hash: str, is_locked: bool = False, 
                 lock_until: Optional[float] = None, failed_attempts: int = 0):
        self.username = username
        self.password_hash = password_hash
        self.is_locked = is_locked
        self.lock_until = lock_until
        self.failed_attempts = failed_attempts

class AuthSystem:
    """认证系统类"""
    
    def __init__(self, storage_file: str = "users.json", lock_duration_minutes: int = 10):
        """
        初始化认证系统
        
        Args:
            storage_file: 用户数据存储文件
            lock_duration_minutes: 锁定持续时间（分钟）
        """
        self.storage_file = storage_file
        self.lock_duration = lock_duration_minutes * 60  # 转换为秒
        self.users: Dict[str, UserAccount] = {}
        self.load_users()
    
    def _hash_password(self, password: str) -> str:
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """从文件加载用户数据"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for username, user_data in data.items():
                        self.users[username] = UserAccount(
                            username=username,
                            password_hash=user_data['password_hash'],
                            is_locked=user_data.get('is_locked', False),
                            lock_until=user_data.get('lock_until'),
                            failed_attempts=user_data.get('failed_attempts', 0)
                        )
            except (json.JSONDecodeError, FileNotFoundError):
                # 如果文件损坏或不存在，使用空用户列表
                self.users = {}
        else:
            # 文件不存在，创建默认管理员用户
            self._create_default_users()
    
    def save_users(self):
        """保存用户数据到文件"""
        data = {}
        for username, account in self.users.items():
            data[username] = {
                'password_hash': account.password_hash,
                'is_locked': account.is_locked,
                'lock_until': account.lock_until,
                'failed_attempts': account.failed_attempts
            }
        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _create_default_users(self):
        """创建默认用户（仅用于演示）"""
        default_users = {
            'admin': 'admin123',
            'user1': 'password1',
            'user2': 'password2'
        }
        
        for username, password in default_users.items():
            password_hash = self._hash_password(password)
            self.users[username] = UserAccount(
                username=username,
                password_hash=password_hash,
                is_locked=False,
                lock_until=None,
                failed_attempts=0
            )
        
        self.save_users()
    
    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (成功状态, 消息)
        """
        if username in self.users:
            return False, "用户名已存在"
        
        if len(username) < 3:
            return False, "用户名至少需要3个字符"
        
        if len(password) < 6:
            return False, "密码至少需要6个字符"
        
        password_hash = self._hash_password(password)
        self.users[username] = UserAccount(
            username=username,
            password_hash=password_hash,
            is_locked=False,
            lock_until=None,
            failed_attempts=0
        )
        
        self.save_users()
        return True, "用户注册成功"
    
    def check_lock_status(self, username: str) -> Tuple[bool, Optional[str]]:
        """
        检查用户是否被锁定
        
        Args:
            username: 用户名
            
        Returns:
            (是否被锁定, 解锁时间消息)
        """
        if username not in self.users:
            return False, None
        
        account = self.users[username]
        
        # 如果账户被锁定且锁定期限未过
        if account.is_locked and account.lock_until:
            current_time = time.time()
            if current_time < account.lock_until:
                # 计算剩余时间
                remaining_seconds = int(account.lock_until - current_time)
                remaining_minutes = remaining_seconds // 60
                remaining_seconds %= 60
                
                message = f"账户已被锁定，请在 {remaining_minutes}分{remaining_seconds}秒后重试"
                return True, message
            else:
                # 锁定期已过，解锁账户
                account.is_locked = False
                account.lock_until = None
                account.failed_attempts = 0
                self.save_users()
        
        return False, None
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (登录成功状态, 消息)
        """
        # 检查用户是否存在
        if username not in self.users:
            return False, "用户名或密码错误"
        
        account = self.users[username]
        
        # 检查账户是否被锁定
        is_locked, lock_message = self.check_lock_status(username)
        if is_locked:
            return False, lock_message
        
        # 验证密码
        password_hash = self._hash_password(password)
        if password_hash == account.password_hash:
            # 登录成功，重置失败次数
            account.failed_attempts = 0
            self.save_users()
            return True, "登录成功"
        else:
            # 登录失败，增加失败次数
            account.failed_attempts += 1
            
            # 如果失败次数达到5次，锁定账户
            if account.failed_attempts >= 5:
                account.is_locked = True
                account.lock_until = time.time() + self.lock_duration
                message = f"登录失败次数过多，账户已被锁定10分钟"
            else:
                remaining_attempts = 5 - account.failed_attempts
                message = f"用户名或密码错误，还剩{remaining_attempts}次尝试机会"
            
            self.save_users()
            return False, message
    
    def unlock_account(self, username: str) -> bool:
        """
        解锁用户账户
        
        Args:
            username: 用户名
            
        Returns:
            是否解锁成功
        """
        if username in self.users:
            account = self.users[username]
            account.is_locked = False
            account.lock_until = None
            account.failed_attempts = 0
            self.save_users()
            return True
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            用户信息字典或None
        """
        if username in self.users:
            account = self.users[username]
            is_locked, lock_message = self.check_lock_status(username)
            
            return {
                'username': account.username,
                'is_locked': is_locked,
                'failed_attempts': account.failed_attempts,
                'lock_message': lock_message
            }
        return None


# 创建全局认证系统实例
auth_system = AuthSystem()

if __name__ == "__main__":
    # 简单演示
    auth = AuthSystem()
    
    # 测试登录
    print("测试登录:")
    print(auth.login("admin", "admin123"))  # 应该成功
    print(auth.login("admin", "wrongpass"))  # 应该失败
    
    # 注册新用户
    print("\n测试注册:")
    print(auth.register_user("newuser", "newpass123"))
    print(auth.login("newuser", "newpass123"))