import re

def is_valid_email(email):
    """
    检查邮箱地址的有效性
    
    参数:
    email (str or list or tuple): 要检查的邮箱地址，可以是单个字符串或多个邮箱组成的列表/元组
    
    返回:
    tuple or dict: 如果是单个邮箱，返回(True, "邮箱验证正确")或(False, "错误原因")；如果是多个邮箱，返回字典{邮箱: 验证结果元组}
    """
    # 如果输入是列表或元组，进行批量验证
    if isinstance(email, (list, tuple)):
        results = {}
        for e in email:
            results[e] = is_valid_email(e)
        return results
    
    # 1. 类型检查：确保输入是字符串类型
    #    如果输入不是字符串（如None、数字、列表等），直接返回错误原因
    if not isinstance(email, str):
        return False, "输入参数类型错误"
    
    # 邮箱验证的正则表达式
    # 正则表达式分解说明：
    # ^                    - 字符串开头
    # [a-zA-Z0-9._%+-]*    - 用户名前缀部分：允许字母、数字、下划线、点、百分号、加号、减号，0次或多次出现
    # [a-zA-Z0-9._%+-]     - 用户名最后一个字符：必须是字母、数字、下划线、点、百分号、加号或减号
    #                       （确保用户名不以点结尾）
    # @                    - 必须包含@符号作为用户名和域名的分隔符
    # [a-zA-Z0-9.-]*       - 域名前缀部分：允许字母、数字、点、减号，0次或多次出现
    # [a-zA-Z0-9.-]        - 域名最后一个字符：必须是字母、数字、点或减号
    #                       （确保域名不以点结尾）
    # \.                   - 必须包含一个点来分隔域名主体和顶级域名
    # [a-zA-Z]{2,6}        - 顶级域名：必须是2-6个字母（如com、org、net、info等）
    # $                    - 字符串结尾
    pattern = r'^[a-zA-Z0-9._%+-]*[a-zA-Z0-9._%+-]@[a-zA-Z0-9.-]*[a-zA-Z0-9.-]\.[a-zA-Z]{2,6}$'
    
    # 2. @符号检查：确保邮箱包含且只包含一个@符号
    #    缺少@符号或有多个@符号的邮箱都是无效的
    if '@' not in email:
        return False, "邮箱地址必须包含@符号"
    if email.count('@') > 1:
        return False, "邮箱地址只能包含一个@符号"
    
    # 3. 连续点检查：确保邮箱中没有连续的点
    #    连续的点（如"user..name@example.com"）是无效的邮箱格式
    if '..' in email:
        return False, "邮箱地址中不能包含连续的点"
    
    # 4. 用户名格式检查：确保用户名不以点开头或结尾
    #    将邮箱按@符号分割，获取用户名部分
    username = email.split('@')[0]
    #    以点开头或结尾的用户名是无效的
    if username.startswith('.'):
        return False, "用户名不能以点开头"
    if username.endswith('.'):
        return False, "用户名不能以点结尾"
    
    # 5. 域名格式检查：确保域名不以点或减号开头或结尾
    #    将邮箱按@符号分割，获取域名部分
    domain = email.split('@')[1]
    #    以点或减号开头/结尾的域名是无效的
    if domain.startswith('.'):
        return False, "域名不能以点开头"
    if domain.endswith('.'):
        return False, "域名不能以点结尾"
    if domain.startswith('-'):
        return False, "域名不能以减号开头"
    if domain.endswith('-'):
        return False, "域名不能以减号结尾"
    
    # 6. 域名部分检查：确保域名的每个部分都不以减号开头或结尾
    #    将域名按点分割成各个部分（如example.com分割为["example", "com"]）
    domain_parts = domain.split('.')
    for part in domain_parts:
        #    域名的任何一个部分都不能以减号开头或结尾
        if part.startswith('-'):
            return False, "域名的部分不能以减号开头"
        if part.endswith('-'):
            return False, "域名的部分不能以减号结尾"
    
    # 8. 连续减号检查：确保域名部分不包含连续的减号
    if '--' in domain:
        return False, "域名部分不能包含连续的减号"
    
    # 9. 最终正则匹配检查：使用完整的正则表达式验证邮箱格式
    #    虽然前面已经进行了多步检查，但最终的正则匹配可以确保整体格式正确
    if not re.fullmatch(pattern, email):
        return False, "邮箱格式不符合标准规范"
    
    return True, "邮箱验证正确"

