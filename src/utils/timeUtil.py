""" 
def parse_duration(duration_str: str) -> int:
            if not duration_str:
                return None
        
        # 正则表达式匹配时间格式
            import re
            match = re.match(r'^(\d+)([MHD]?)$', duration_str, re.IGNORECASE)
            if not match:
                    return None
            
            value = int(match.group(1))
            unit = match.group(2).upper()
            
            if unit == 'M':
                return value * 60  # 分钟
            elif unit == 'H':
                return value * 3600  # 小时
            elif unit == 'D':
                return value * 86400  # 天
            else:
                return value  # 默认为秒
         """