# -*- coding: utf-8 -*-
"""
后端测试包初始化文件
Backend Tests Package Initialization

包含后端相关测试：
- API集成测试 (test_api_integration.py)
- 基础服务器测试 (test_base_server.py)

Author: chenlei
"""

__version__ = "1.0.0"
__author__ = "chenlei"

# 测试配置常量
TEST_HOST = "localhost"
TEST_TIMEOUT = 30

__all__ = [
    "TEST_HOST",
    "TEST_TIMEOUT",
]
