"""
使用示例
"""
from auth import AuthSystem
import time

def main():
    # 创建认证系统实例
    auth = AuthSystem()
    
    print("=== 用户登录系统演示 ===\n")
    
    # 1. 注册新用户
    print("1. 注册新用户: demo_user")
    success, message = auth.register_user("demo_user", "Demo1234")
    print(f"   注册结果: {success}, 消息: {message}")
    
    # 2. 登录成功测试，使用demo_user登录
    print("\n2. 登录成功测试，使用demo_user登录")
    success, message = auth.login("demo_user", "Demo1234")
    print(f"   登录结果: {success}, 消息: {message}")
    
    # 3. 登录失败（密码错误）
    print("\n3. 登录失败测试，使用错误密码登录demo_user")
    success, message = auth.login("demo_user", "Wrong1234")
    print(f"   登录结果: {success}, 消息: {message}")
    
    # 4. 获取用户信息，测试锁定状态
    print("\n4. 获取用户信息，测试demo_user是否被锁定")
    user_info = auth.get_user_info("demo_user")
    if user_info:
        print(f"   用户名: {user_info['username']}")
        print(f"   是否锁定: {user_info['is_locked']}")
        print(f"   失败次数: {user_info['failed_attempts']}")
    
    # 5. 模拟多次失败导致锁定
    print("\n5. 模拟多次登录失败导致账户锁定")
    
    # 先解锁账户（以防之前已被锁定）
    auth.unlock_account("demo_user")
    
    # 故意失败5次
    print("   故意用错误密码登录5次: 用户demo_user")
    for i in range(5):
        success, message = auth.login("demo_user", f"Wrong123{i}")
        print(f"   第{i+1}次: {message}")
    
    # 6. 尝试登录被锁定的账户
    print("\n6. 尝试登录被锁定的账户：用户demo_user")
    success, message = auth.login("demo_user", "Demo1234")
    print(f"   登录结果: {success}, 消息: {message}")
    
    # 7. 解锁账户
    print("\n7. 解锁账户：用户demo_user")
    if auth.unlock_account("demo_user"):
        print("   账户解锁成功")
        
        # 8. 再次尝试登录
        print("\n8. 解锁后再次登录，用户demo_user")
        success, message = auth.login("demo_user", "Demo1234")
        print(f"   登录结果: {success}, 消息: {message}")
    
    print("\n=== 演示结束 ===")

if __name__ == "__main__":
    main()