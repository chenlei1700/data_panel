# -*- coding: utf-8 -*-
"""
API服务包初始化文件
API Services Package Initialization

包含各种Flask服务器实现：
- 基础服务器框架 (base_server.py)
- 演示服务器 (show_plate_server_demo.py)
- 多板块服务器 (show_plate_server_multiplate_v2.py)
- 强势板块服务器 (show_plate_server_strong.py)
- 高级功能服务器 (show_plate_server_v2.py)

Author: chenlei
"""

__version__ = "1.0.0"
__author__ = "chenlei"

# 可以在这里定义包级别的常量或配置
DEFAULT_HOST = "0.0.0.0"
DEFAULT_DEBUG = True

# 导出主要的服务器类或函数（如果需要）
__all__ = [
    "DEFAULT_HOST",
    "DEFAULT_DEBUG",
]
