import unittest
from ip_validator import is_valid_ip

class TestIPValidator(unittest.TestCase):
    """IP验证器单元测试类"""
    
    def test_valid_ipv4(self):
        """测试有效的IPv4地址"""
        valid_ipv4_list = [
            "192.168.1.1",
            "10.0.0.1",
            "255.255.255.255",
            "0.0.0.0",
            "127.0.0.1",
            "1.1.1.1",
            "192.168.0.255"
        ]
        
        for ip in valid_ipv4_list:
            with self.subTest(ip=ip):
                result, message = is_valid_ip(ip)
                self.assertTrue(result, f"有效IPv4地址 {ip} 验证失败: {message}")
                self.assertEqual(message, "IP验证正确")
    
    def test_invalid_ipv4(self):
        """测试无效的IPv4地址"""
        invalid_ipv4_list = [
            "192.168.01.1",  # 前导零
            "192.168.1.001",  # 前导零
            "192.168.1.",  # 缺少最后一段
            "192.168..1",  # 空段
            ".192.168.1.1",  # 开头有.符号
            "192.168.1.256",  # 超出范围
            "192.168.1.300",  # 超出范围
            "192.168.1.1.1",  # 太多段
            "192.168.1",  # 太少段
            "256.0.0.1",  # 第一段超出范围
            "192.168.1.abc",  # 非数字
            "192 168 1 1"  # 空格分隔
        ]
        
        for ip in invalid_ipv4_list:
            with self.subTest(ip=ip):
                result, message = is_valid_ip(ip)
                self.assertFalse(result, f"无效IPv4地址 {ip} 验证失败: {message}")
    
    def test_valid_ipv6(self):
        """测试有效的IPv6地址"""
        valid_ipv6_list = [
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",  # 完整格式
            "2001:db8:85a3:0:0:8a2e:370:7334",  # 省略前导零
            "2001:db8:85a3::8a2e:370:7334",  # 压缩格式
            "::1",  # 本地环回地址
            "::",  # 未指定地址
            "fe80::1ff:fe23:4567:890a",  # 链路本地地址
            "2001:0db8:1234:5678:9abc:def0:1234:5678",  # 标准格式
            "2001:0db8::1234:5678"  # 压缩格式
        ]
        
        for ip in valid_ipv6_list:
            with self.subTest(ip=ip):
                result, message = is_valid_ip(ip)
                self.assertTrue(result, f"有效IPv6地址 {ip} 验证失败: {message}")
                self.assertEqual(message, "IP验证正确")
    
    def test_invalid_ipv6(self):
        """测试无效的IPv6地址"""
        invalid_ipv6_list = [
            "2001:0db8:85a3::8a2e::7334",  # 多个压缩标记
            "2001:0db8:85a3:0000:0000:8a2e:0370",  # 段数不足
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334:8888",  # 段数过多
            "2001:0db8:85a3:0000:0000:8a2e:0370:zzzz",  # 非十六进制字符
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334:8888:9999",  # 段数过多
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334:8888:9999:0000",  # 段数过多
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334:8888:9999:0000:1111",  # 段数过多
            "2001:0db8:85a3:0000:0000:8a2e:0370:733g",  # 无效字符
            "2001:0db8:85a3:::8a2e:0370:7334",  # 多个连续冒号
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334x",  # 结尾有无效字符
            "x2001:0db8:85a3:0000:0000:8a2e:0370:7334"  # 开头有无效字符
        ]
        
        for ip in invalid_ipv6_list:
            with self.subTest(ip=ip):
                result, message = is_valid_ip(ip)
                self.assertFalse(result, f"无效IPv6地址 {ip} 验证失败: {message}")
    
    def test_batch_validation(self):
        """测试批量IP验证"""
        # 单个IP列表测试
        ip_list = ["192.168.1.1", "192.168.01.1", "2001:db8::1", "2001:db8:::1"]
        results = is_valid_ip(ip_list)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), len(ip_list))
        
        # 验证结果
        self.assertTrue(results["192.168.1.1"][0])
        self.assertFalse(results["192.168.01.1"][0])
        self.assertTrue(results["2001:db8::1"][0])
        self.assertFalse(results["2001:db8:::1"][0])
        
        # 元组类型测试
        ip_tuple = ("10.0.0.1", "invalid_ip")
        results_tuple = is_valid_ip(ip_tuple)
        self.assertIsInstance(results_tuple, dict)
        self.assertEqual(len(results_tuple), len(ip_tuple))
    
    def test_invalid_types(self):
        """测试无效的输入类型"""
        invalid_types = [
            123,  # 整数
            123.456,  # 浮点数
            True,  # 布尔值
            [],  # 空列表
            {},  # 空字典
            None  # None值
        ]
        
        for invalid_input in invalid_types:
            with self.subTest(input=invalid_input):
                # 确保非批量验证的处理
                if isinstance(invalid_input, (list, tuple)):
                    results = is_valid_ip(invalid_input)
                    self.assertIsInstance(results, dict)
                else:
                    result, message = is_valid_ip(invalid_input)
                    self.assertFalse(result)
                    self.assertEqual(message, "输入参数类型错误，必须是字符串")
    
    def test_other_formats(self):
        """测试既不是IPv4也不是IPv6的地址格式"""
        other_formats = [
            "example.com",  # 域名
            "user@example.com",  # 邮箱
            "192.168.1.1:8080",  # IP带端口
            "http://192.168.1.1",  # URL
            "",  # 空字符串
            "   ",  # 空白字符串
            "abc",  # 普通字符串
            "1234567890"  # 纯数字
        ]
        
        for ip in other_formats:
            with self.subTest(ip=ip):
                result, message = is_valid_ip(ip)
                self.assertFalse(result, f"非IP格式 {ip} 验证失败: {message}")
    
    def test_ipv4_boundary_cases(self):
        """测试IPv4边界情况"""
        # 测试边缘数值
        boundary_cases = [
            "0.0.0.0",  # 最小值
            "255.255.255.255",  # 最大值
            "1.0.0.0",
            "0.1.0.0",
            "0.0.1.0",
            "0.0.0.1",
            "255.0.0.0",
            "0.255.0.0",
            "0.0.255.0",
            "0.0.0.255"
        ]
        
        for ip in boundary_cases:
            with self.subTest(ip=ip):
                result, message = is_valid_ip(ip)
                self.assertTrue(result, f"IPv4边界情况 {ip} 验证失败: {message}")
    
    def test_ipv6_boundary_cases(self):
        """测试IPv6边界情况"""
        # 测试各种压缩格式
        boundary_cases = [
            "::",  # 全压缩
            "::1",  # 末尾压缩
            "1::",  # 开头压缩
            "1::2",  # 中间压缩
            "1:2::3:4",  # 中间压缩
            "2001:db8:85a3::8a2e:370:7334",  # 标准压缩
        ]
        
        for ip in boundary_cases:
            with self.subTest(ip=ip):
                result, message = is_valid_ip(ip)
                self.assertTrue(result, f"IPv6边界情况 {ip} 验证失败: {message}")

if __name__ == "__main__":
    unittest.main()