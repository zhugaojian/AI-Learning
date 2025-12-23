import re

def is_valid_ip(ip):
    """
    IP地址验证函数，支持IPv4和IPv6地址验证，支持单个IP验证和批量验证
    
    参数:
        ip (str/list/tuple): 要验证的IP地址，可以是单个字符串，也可以是包含多个IP地址的列表或元组
    
    返回:
        tuple/dict: 如果是单个IP地址，返回元组 (bool, str)，其中第一个元素是验证结果(True表示有效，False表示无效)，第二个元素是验证消息
                   如果是批量验证，返回字典，键为输入的IP地址，值为对应的验证结果元组
    """
    # 批量验证处理
    if isinstance(ip, (list, tuple)):
        results = {}
        for i in ip:
            results[i] = is_valid_ip(i)
        return results
    
    # 类型检查
    if not isinstance(ip, str):
        return False, "输入参数类型错误，必须是字符串"
    
    # 检查是否为IPv4地址
    if "." in ip:
        return _is_valid_ipv4(ip)
    # 检查是否为IPv6地址
    elif ":" in ip:
        return _is_valid_ipv6(ip)
    # 既不是IPv4也不是IPv6
    else:
        return False, "IP地址格式错误，必须是IPv4或IPv6格式"

def _is_valid_ipv4(ip):
    """
    IPv4地址验证函数
    
    参数:
        ip (str): 要验证的IPv4地址
    
    返回:
        tuple: (bool, str) 验证结果元组
    """
    # IPv4地址正则表达式：匹配4个0-255的数字段，每个段之间用点分隔
    # 每个数字段不能以0开头（除非该段本身就是0）
    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    # 先检查是否符合基本格式
    if not re.fullmatch(ipv4_pattern, ip):
        return False, "IPv4地址格式错误，必须是4个0-255的数字段，用点分隔"
    
    # 检查是否有前导零（除了单个0的情况）
    parts = ip.split('.')
    for i, part in enumerate(parts):
        if len(part) > 1 and part.startswith('0'):
            return False, f"IPv4地址第{i+1}部分不能有前导零"
    
    return True, "IP验证正确"

def _is_valid_ipv6(ip):
    """
    IPv6地址验证函数
    
    参数:
        ip (str): 要验证的IPv6地址
    
    返回:
        tuple: (bool, str) 验证结果元组
    """
    # 检查是否包含多个::压缩标记
    if ip.count("::") > 1:
        return False, "IPv6地址只能有一个::压缩标记"
    
    # IPv6地址正则表达式
    # 支持标准格式和压缩格式
    ipv6_pattern = r'^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$'
    
    # 检查是否符合IPv6格式
    if not re.fullmatch(ipv6_pattern, ip):
        return False, "IPv6地址格式错误，必须是8个16进制段，用冒号分隔，支持压缩格式::"
    
    # 检查压缩后的部分数量是否合法
    if "::" in ip:
        non_empty_parts = [p for p in ip.split(":") if p]
        if len(non_empty_parts) > 7:
            return False, "IPv6地址压缩格式错误，压缩后部分数量必须在0-7之间"
    # 非压缩格式必须有8个部分
    else:
        parts = ip.split(":")
        if len(parts) != 8:
            return False, "IPv6地址必须包含8个16进制段"
    
    return True, "IP验证正确"