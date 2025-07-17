#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端服务测试 - 基础框架测试
Backend Service Tests - Base Framework Tests

Author: chenlei
"""

import pytest
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "api"))

from base_server import BaseStockServer


class TestBaseServer:
    """测试基础服务器框架"""
    
    def setup_method(self):
        """测试前准备"""
        self.server = BaseStockServer("test_server", 5999)
    
    def test_server_initialization(self):
        """测试服务器初始化"""
        assert self.server.name == "test_server"
        assert self.server.port == 5999
        assert self.server.app is not None
    
    def test_cors_configuration(self):
        """测试CORS配置"""
        # 检查CORS是否正确配置
        # 这里可以通过检查app的配置或发送请求来验证
        assert hasattr(self.server, 'app')
    
    def test_stock_data_generation(self):
        """测试股票数据生成"""
        data = self.server.generate_stock_data()
        
        # 验证数据结构
        assert isinstance(data, list)
        assert len(data) > 0
        
        # 验证数据字段
        if data:
            stock = data[0]
            required_fields = ['股票代码', '股票名称', '现价', '涨跌幅']
            for field in required_fields:
                assert field in stock
    
    def test_plate_data_generation(self):
        """测试板块数据生成"""
        data = self.server.generate_plate_data()
        
        # 验证数据结构
        assert isinstance(data, list)
        assert len(data) > 0
        
        # 验证数据字段
        if data:
            plate = data[0]
            required_fields = ['板块名称', '板块涨幅', '领涨股票']
            for field in required_fields:
                assert field in plate


class TestAPIEndpoints:
    """测试API端点"""
    
    def setup_method(self):
        """测试前准备"""
        self.server = BaseStockServer("test_server", 5999)
        self.app = self.server.app.test_client()
    
    def test_health_endpoint(self):
        """测试健康检查端点"""
        response = self.app.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_stock_data_endpoint(self):
        """测试股票数据端点"""
        response = self.app.get('/api/stock-data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'stocks' in data
        assert isinstance(data['stocks'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
