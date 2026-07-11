"""
统一工具类 - 直接模块引用版本
使用方式:
    ut.str.is_blank("hello")
    ut.file.clone("src.txt", "dst.txt")
"""

# 直接导入模块并重命名
import string_utils as str
import file_utils as file

# 可以继续添加其他工具模块
# import json_utils as json
# import io_utils as io

# 可选：提供版本信息
__version__ = "1.0.0"
__all__ = ['str', 'file']  # 定义公开的接口