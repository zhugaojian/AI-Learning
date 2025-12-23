"""
用户登录模块的单元测试
"""
import unittest
import time
import os
import tempfile
from unittest.mock import patch
from auth import AuthSystem, UserAccount

class TestAuthSystem(unittest.TestCase):
    """AuthSystem测试类"""
    
    def setUp(self):
        """每个测试前的准备工作"""
        # 创建临时文件用于存储测试数据
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        # 创建认证系统实例，使用临时文件
        self.auth = AuthSystem(storage_file=self.temp_file.name, lock_duration_minutes=10)
    
    def tearDown(self):
        """每个测试后的清理工作"""
        # 删除临时文件
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_hash_password(self):
        """测试密码哈希函数"""
        auth = AuthSystem()
        hash1 = auth._hash_password("testpassword")
        hash2 = auth._hash_password("testpassword")
        
        # 相同的密码应该生成相同的哈希值
        self.assertEqual(hash1, hash2)
        
        # 不同的密码应该生成不同的哈希值
        hash3 = auth._hash_password("different")
        self.assertNotEqual(hash1, hash3)
    
    def test_register_user(self):
        """测试用户注册"""
        # 成功注册
        success, message = self.auth.register_user("testuser", "testpass123")
        self.assertTrue(success)
        self.assertEqual(message, "用户注册成功")
        self.assertIn("testuser", self.auth.users)
        
        # 注册已存在的用户
        success, message = self.auth.register_user("testuser", "anotherpass")
        self.assertFalse(success)
        self.assertEqual(message, "用户名已存在")
        
        # 用户名太短
        success, message = self.auth.register_user("ab", "password123")
        self.assertFalse(success)
        self.assertEqual(message, "用户名至少需要3个字符")
        
        # 密码太短
        success, message = self.auth.register_user("validuser", "123")
        self.assertFalse(success)
        self.assertEqual(message, "密码至少需要6个字符")
    
    def test_login_success(self):
        """测试登录成功"""
        # 先注册用户
        self.auth.register_user("testuser", "testpass123")
        
        # 登录成功
        success, message = self.auth.login("testuser", "testpass123")
        self.assertTrue(success)
        self.assertEqual(message, "登录成功")
        
        # 验证失败次数已重置
        account = self.auth.users["testuser"]
        self.assertEqual(account.failed_attempts, 0)
    
    def test_login_user_not_exist(self):
        """测试不存在的用户登录"""
        success, message = self.auth.login("nonexistent", "password")
        self.assertFalse(success)
        self.assertEqual(message, "用户名或密码错误")
    
    def test_login_wrong_password(self):
        """测试密码错误"""
        # 先注册用户
        self.auth.register_user("testuser", "testpass123")
        
        # 密码错误
        success, message = self.auth.login("testuser", "wrongpass")
        self.assertFalse(success)
        self.assertEqual(message, "用户名或密码错误，还剩4次尝试机会")
        
        # 验证失败次数增加
        account = self.auth.users["testuser"]
        self.assertEqual(account.failed_attempts, 1)
    
    def test_account_lock_after_five_failures(self):
        """测试5次失败后账户锁定"""
        # 先注册用户
        self.auth.register_user("testuser", "testpass123")
        
        # 连续5次错误密码登录
        for i in range(5):
            success, message = self.auth.login("testuser", "wrongpass")
            if i < 4:
                remaining = 4 - i
                expected_message = f"用户名或密码错误，还剩{remaining}次尝试机会"
                self.assertEqual(message, expected_message)
            else:
                # 第5次应该触发锁定
                self.assertIn("账户已被锁定10分钟", message)
        
        # 验证账户状态
        account = self.auth.users["testuser"]
        self.assertTrue(account.is_locked)
        self.assertIsNotNone(account.lock_until)
        self.assertEqual(account.failed_attempts, 5)
        
        # 尝试用正确密码登录，应该失败（账户被锁定）
        success, message = self.auth.login("testuser", "testpass123")
        self.assertFalse(success)
        self.assertIn("账户已被锁定", message)
    
    def test_check_lock_status(self):
        """测试锁定状态检查"""
        # 注册并锁定用户
        self.auth.register_user("testuser", "testpass123")
        account = self.auth.users["testuser"]
        account.is_locked = True
        account.lock_until = time.time() + 600  # 锁定10分钟
        
        # 检查锁定状态
        is_locked, message = self.auth.check_lock_status("testuser")
        self.assertTrue(is_locked)
        self.assertIn("账户已被锁定", message)
        
        # 测试已过期的锁定
        account.lock_until = time.time() - 100  # 锁定已过期
        is_locked, message = self.auth.check_lock_status("testuser")
        self.assertFalse(is_locked)
        self.assertIsNone(message)
        
        # 验证账户已自动解锁
        self.assertFalse(account.is_locked)
        self.assertEqual(account.failed_attempts, 0)
    
    def test_unlock_account(self):
        """测试解锁账户"""
        # 注册并锁定用户
        self.auth.register_user("testuser", "testpass123")
        account = self.auth.users["testuser"]
        account.is_locked = True
        account.lock_until = time.time() + 600
        account.failed_attempts = 5
        
        # 解锁账户
        result = self.auth.unlock_account("testuser")
        self.assertTrue(result)
        
        # 验证账户状态
        self.assertFalse(account.is_locked)
        self.assertIsNone(account.lock_until)
        self.assertEqual(account.failed_attempts, 0)
        
        # 尝试解锁不存在的用户
        result = self.auth.unlock_account("nonexistent")
        self.assertFalse(result)
    
    def test_get_user_info(self):
        """测试获取用户信息"""
        # 注册用户
        self.auth.register_user("testuser", "testpass123")
        
        # 获取用户信息
        user_info = self.auth.get_user_info("testuser")
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], "testuser")
        self.assertFalse(user_info['is_locked'])
        self.assertEqual(user_info['failed_attempts'], 0)
        
        # 获取不存在的用户信息
        user_info = self.auth.get_user_info("nonexistent")
        self.assertIsNone(user_info)
    
    @patch('time.time')
    def test_lock_expiration(self, mock_time):
        """测试锁定过期"""
        # 设置初始时间
        current_time = 1000
        mock_time.return_value = current_time
        
        # 注册并锁定用户
        self.auth.register_user("testuser", "testpass123")
        account = self.auth.users["testuser"]
        account.is_locked = True
        account.lock_until = current_time + 300  # 锁定5分钟
        
        # 模拟时间过去6分钟
        mock_time.return_value = current_time + 360
        
        # 检查锁定状态，应该自动解锁
        is_locked, _ = self.auth.check_lock_status("testuser")
        self.assertFalse(is_locked)
        self.assertFalse(account.is_locked)
        self.assertIsNone(account.lock_until)
        self.assertEqual(account.failed_attempts, 0)
    
    def test_save_and_load_users(self):
        """测试用户数据的保存和加载"""
        # 注册几个用户
        self.auth.register_user("user1", "pass123")
        self.auth.register_user("user2", "pass123")
        
        # 修改一些状态
        account = self.auth.users["user1"]
        account.failed_attempts = 3
        
        # 保存数据
        self.auth.save_users()
        
        # 创建新的AuthSystem实例加载数据
        new_auth = AuthSystem(storage_file=self.temp_file.name)
        
        # 验证数据正确加载
        self.assertIn("user1", new_auth.users)
        self.assertIn("user2", new_auth.users)
        
        account1 = new_auth.users["user1"]
        self.assertEqual(account1.failed_attempts, 3)


class TestUserAccount(unittest.TestCase):
    """UserAccount测试类"""
    
    def test_user_account_creation(self):
        """测试UserAccount创建"""
        account = UserAccount(
            username="testuser",
            password_hash="abc123",
            is_locked=True,
            lock_until=1234567890.0,
            failed_attempts=3
        )
        
        self.assertEqual(account.username, "testuser")
        self.assertEqual(account.password_hash, "abc123")
        self.assertTrue(account.is_locked)
        self.assertEqual(account.lock_until, 1234567890.0)
        self.assertEqual(account.failed_attempts, 3)
    
    def test_user_account_default_values(self):
        """测试UserAccount默认值"""
        account = UserAccount(
            username="testuser",
            password_hash="abc123"
        )
        
        self.assertEqual(account.username, "testuser")
        self.assertEqual(account.password_hash, "abc123")
        self.assertFalse(account.is_locked)
        self.assertIsNone(account.lock_until)
        self.assertEqual(account.failed_attempts, 0)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAuthSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestUserAccount))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("运行用户登录模块单元测试...")
    run_tests()