import unittest
from email_validator import is_valid_email

class TestEmailValidator(unittest.TestCase):
    """
    邮箱验证函数的单元测试类
    """
    
    def test_valid_emails(self):
        """
        测试有效的邮箱地址
        """
        valid_emails = [
            "user@example.com",      # 基本格式
            "user.name@example.com", # 用户名包含点
            "user+tag@example.com",  # 用户名包含加号
            "user-name@example.com", # 用户名包含减号
            "user_name@example.com", # 用户名包含下划线
            "user@sub.example.com",  # 多级域名
            "user@example.co.uk",    # 多级顶级域名
            "user@123.com",          # 数字域名
            "user123@example.com",   # 用户名包含数字
            "user.name+tag@example.com", # 用户名同时包含点和加号
            "user%name@example.com", # 用户名包含百分号
            "user@example.museum",   # 顶级域名长度为6个字符
            "user@sub-example.com",  # 域名部分包含减号
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                result, message = is_valid_email(email)
                self.assertTrue(result, f"邮箱 {email} 应该被认为是有效的")
                self.assertEqual(message, "邮箱验证正确", f"邮箱 {email} 的验证消息应该是'邮箱验证正确'")
    
    def test_invalid_emails(self):
        """
        测试无效的邮箱地址
        """
        invalid_emails = [
            "user",                  # 缺少@和域名
            "user@",                 # 缺少域名
            "@example.com",          # 缺少用户名
            "user@.com",             # 缺少域名部分
            "user@example.",         # 缺少顶级域名
            "user@example.c",        # 顶级域名太短
            "user@example.com.",     # 尾部有多余的点
            "user..name@example.com",# 用户名有连续的点
            "user@example..com",     # 域名有连续的点
            "user@-example.com",     # 域名以减号开头
            "user@example-.com",     # 域名以减号结尾
            "user@.example.com",     # 域名以点开头
            "user@example.com.",     # 域名以点结尾
            "user name@example.com", # 用户名有空格
            "user@example com",      # 域名有空格
            r"user@exa\mple.com",    # 无效的转义字符
            12345,                   # 非字符串类型
            None,                    # None值
            ".user@example.com",     # 用户名以点开头
            "user.@example.com",     # 用户名以点结尾
            "user@-example-.com",    # 域名以减号开头和结尾
            "user@@example.com",     # 多个@符号
            "user@sub--example.com", # 域名部分包含连续减号
            "user@sub-example-.com", # 域名部分以减号结尾
            "user@example.toolong",  # 顶级域名超过6个字符
            "",                      # 空字符串
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                result, message = is_valid_email(email)
                self.assertFalse(result, f"邮箱 {email} 应该被认为是无效的")
                self.assertIsInstance(message, str, f"邮箱 {email} 的错误消息应该是字符串类型")
                self.assertNotEqual(message, "邮箱验证正确", f"邮箱 {email} 的错误消息不应该是'邮箱验证正确'")
    
    def test_batch_validation(self):
        """
        测试批量验证功能
        """
        emails = [
            "user@example.com",      # 有效
            "user",                  # 无效
            "user.name@example.com", # 有效
            "user@.com",             # 无效
        ]
        
        results = is_valid_email(emails)
        self.assertIsInstance(results, dict, "批量验证应该返回字典类型")
        
        for email, (result, message) in results.items():
            with self.subTest(email=email):
                self.assertIsInstance(result, bool, f"邮箱 {email} 的验证结果应该是布尔类型")
                self.assertIsInstance(message, str, f"邮箱 {email} 的验证消息应该是字符串类型")
                if email in ["user@example.com", "user.name@example.com"]:
                    self.assertTrue(result, f"邮箱 {email} 应该被认为是有效的")
                    self.assertEqual(message, "邮箱验证正确")
                else:
                    self.assertFalse(result, f"邮箱 {email} 应该被认为是无效的")
                    self.assertNotEqual(message, "邮箱验证正确")

if __name__ == "__main__":
    unittest.main()
