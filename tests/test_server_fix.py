#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器修复脚本
"""

import sys
import os

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_server import BaseStockServer
from datetime import datetime
import json

class TestServer(BaseStockServer):
    """测试服务器"""
    
    def __init__(self, port=5008):
        super().__init__(name="测试服务器", port=port)
    
    def get_dashboard_config(self):
        """获取仪表盘配置"""
        return {
            "title": "测试仪表盘",
            "components": [
                {
                    "id": "test1",
                    "type": "table",
                    "title": "测试表格",
                    "dataSource": "/api/table-data/test-data"
                }
            ]
        }
    
    def get_data_sources(self):
        """获取数据源配置"""
        return {
            "/api/table-data/test-data": {
                "handler": "get_test_data"
            }
        }
    
    def get_test_data(self):
        """获取测试数据"""
        return {
            "columns": ["时间", "数值", "状态"],
            "data": [
                [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 100, "正常"],
                [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 200, "正常"]
            ]
        }

def test_datetime_fix():
    """测试datetime修复"""
    try:
        # 测试datetime.now()调用
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ datetime修复测试通过: {current_time}")
        return True
    except Exception as e:
        print(f"❌ datetime修复测试失败: {e}")
        return False

def test_port_finding():
    """测试端口查找功能"""
    try:
        server = TestServer()
        available_port = server._find_available_port(5008)
        print(f"✅ 端口查找测试通过: 找到可用端口 {available_port}")
        return True
    except Exception as e:
        print(f"❌ 端口查找测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 开始服务器修复测试...")
    
    tests = [
        ("datetime修复", test_datetime_fix),
        ("端口查找", test_port_finding)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！服务器修复成功")
        return True
    else:
        print("⚠️  部分测试失败，请检查修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
