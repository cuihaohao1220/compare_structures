"""
compare_structures - 增强版结构对比库

一个用于深度对比两个数据结构（字典/列表）的 Python 库，
支持类型检查、值对比、缺失字段检测、冗余字段检测等功能。

作者: 崔浩浩
"""

try:
    from .compare_structures import compare_structures
except ImportError:
    # 如果相对导入失败，尝试绝对导入（用于直接运行）
    from compare_structures import compare_structures

__version__ = "1.0.0"
__all__ = ["compare_structures"]

