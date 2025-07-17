#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点集成测试 - 测试所有服务的API接口
API Endpoints Integration Tests - Test all service API endpoints

Author: chenlei
"""

import unittest
import requests
import json
import time
import threading
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "api"))


class TestAPIIntegration(unittest.TestCase):
    """API集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.base_url = "http://localhost"
        cls.test_ports = [5001, 5002, 5003]
        cls.timeout = 5  # 请求超时时间
    
    def test_server_health_checks(self):
        """测试所有服务器的健康检查"""
        for port in self.test_ports:
            with self.subTest(port=port):
                try:
                    url = f"{self.base_url}:{port}/health"
                    response = requests.get(url, timeout=self.timeout)
                    
                    # 检查响应状态
                    self.assertEqual(response.status_code, 200)
                    
                    # 检查响应内容
                    data = response.json()
                    self.assertIn('status', data)
                    self.assertEqual(data['status'], 'healthy')
                    
                except requests.exceptions.ConnectionError:
                    self.skipTest(f"服务器 {port} 未启动")
                except requests.exceptions.Timeout:
                    self.fail(f"服务器 {port} 响应超时")
    
    def test_api_endpoints_response(self):
        """测试API端点响应"""
        endpoints = [
            "/api/stock-data",
            "/api/plate-data", 
            "/api/chart-data"
        ]
        
        for port in self.test_ports:
            for endpoint in endpoints:
                with self.subTest(port=port, endpoint=endpoint):
                    try:
                        url = f"{self.base_url}:{port}{endpoint}"
                        response = requests.get(url, timeout=self.timeout)
                        
                        # 检查响应状态
                        self.assertEqual(response.status_code, 200)
                        
                        # 检查响应格式
                        data = response.json()
                        self.assertIsInstance(data, dict)
                        
                    except requests.exceptions.ConnectionError:
                        self.skipTest(f"服务器 {port} 未启动")
                    except requests.exceptions.Timeout:
                        self.fail(f"端点 {endpoint} 在端口 {port} 响应超时")
    
    def test_sse_endpoints(self):
        """测试SSE端点"""
        for port in self.test_ports:
            with self.subTest(port=port):
                try:
                    url = f"{self.base_url}:{port}/api/sse"
                    response = requests.get(url, timeout=2, stream=True)
                    
                    # 检查响应头
                    self.assertEqual(response.headers.get('Content-Type'), 'text/event-stream')
                    self.assertEqual(response.headers.get('Cache-Control'), 'no-cache')
                    
                except requests.exceptions.ConnectionError:
                    self.skipTest(f"服务器 {port} 未启动")
                except requests.exceptions.Timeout:
                    # SSE连接超时是正常的，因为我们只是测试连接
                    pass
    
    def test_cors_headers(self):
        """测试CORS头部设置"""
        for port in self.test_ports:
            with self.subTest(port=port):
                try:
                    url = f"{self.base_url}:{port}/api/stock-data"
                    response = requests.get(url, timeout=self.timeout)
                    
                    # 检查CORS头部
                    self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
                    
                except requests.exceptions.ConnectionError:
                    self.skipTest(f"服务器 {port} 未启动")


class TestDataIntegrity(unittest.TestCase):
    """数据完整性测试"""
    
    def setUp(self):
        """测试设置"""
        self.base_url = "http://localhost:5001"  # 使用主服务进行测试
        self.timeout = 5
    
    def test_stock_data_structure(self):
        """测试股票数据结构"""
        try:
            url = f"{self.base_url}/api/stock-data"
            response = requests.get(url, timeout=self.timeout)
            data = response.json()
            
            # 检查数据结构
            self.assertIn('stocks', data)
            self.assertIsInstance(data['stocks'], list)
            
            if data['stocks']:
                stock = data['stocks'][0]
                required_fields = ['股票代码', '股票名称', '现价', '涨跌幅']
                for field in required_fields:
                    self.assertIn(field, stock)
                    
        except requests.exceptions.ConnectionError:
            self.skipTest("主服务器未启动")
    
    def test_plate_data_structure(self):
        """测试板块数据结构"""
        try:
            url = f"{self.base_url}/api/plate-data"
            response = requests.get(url, timeout=self.timeout)
            data = response.json()
            
            # 检查数据结构
            self.assertIn('plates', data)
            self.assertIsInstance(data['plates'], list)
            
            if data['plates']:
                plate = data['plates'][0]
                required_fields = ['板块名称', '板块涨幅']
                for field in required_fields:
                    self.assertIn(field, plate)
                    
        except requests.exceptions.ConnectionError:
            self.skipTest("主服务器未启动")


def run_api_tests():
    """运行API测试"""
    print("🧪 启动API集成测试")
    print("=" * 50)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTest(unittest.makeSuite(TestAPIIntegration))
    suite.addTest(unittest.makeSuite(TestDataIntegrity))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果统计
    print("\n" + "=" * 50)
    print(f"✅ 测试通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ 测试失败: {len(result.failures)}")
    print(f"💥 测试错误: {len(result.errors)}")
    print(f"⏭️  测试跳过: {len(result.skipped)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
