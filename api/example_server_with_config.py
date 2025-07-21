#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：如何在现有服务器中集成自动更新配置系统
Example: How to integrate auto-update configuration system in existing servers

Author: chenlei
"""

import sys
import os
from flask import jsonify

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from base_server import BaseStockServer
from server_config import get_server_config, create_auto_update_config


class ExampleStockServer(BaseStockServer):
    """示例股票服务器 - 展示如何集成配置系统"""
    
    def __init__(self, port=None, auto_update_config=None):
        """
        初始化示例服务器
        
        Args:
            port: 服务器端口，如果为None则从配置文件读取
            auto_update_config: 自动更新配置，如果为None则从配置文件读取
        """
        # 1. 从配置文件获取服务器配置
        server_config = get_server_config("example")  # 使用 "example" 作为服务器名称
        
        # 2. 处理端口配置
        if port is None:
            port = server_config.get("port", 5009)  # 默认端口5009
        
        # 3. 处理自动更新配置
        if auto_update_config is None:
            auto_update_config = server_config.get("auto_update_config", {})
        else:
            # 合并配置文件配置和参数配置
            file_config = server_config.get("auto_update_config", {})
            file_config.update(auto_update_config)
            auto_update_config = file_config
        
        # 4. 获取服务器名称
        server_name = server_config.get("name", "示例股票仪表盘")
        
        # 5. 调用基类初始化
        super().__init__(port=port, name=server_name, auto_update_config=auto_update_config)
        
        # 6. 初始化服务器特定的数据
        self.example_data = {
            "stocks": [
                {"code": "000001", "name": "平安银行", "price": 12.34, "change": 0.12},
                {"code": "000002", "name": "万科A", "price": 23.45, "change": -0.23},
                {"code": "600000", "name": "浦发银行", "price": 9.87, "change": 0.05},
            ]
        }
        
        print(f"✅ {server_name} 初始化完成")
        print(f"   - 端口: {self.port}")
        print(f"   - 自动更新: {'启用' if self.auto_update_config['enabled'] else '禁用'}")
        if self.auto_update_config['enabled']:
            print(f"   - 更新间隔: {self.auto_update_config['interval']}秒")
    
    def get_dashboard_config(self):
        """实现抽象方法：获取仪表盘配置"""
        return {
            "title": self.name,
            "components": [
                {
                    "id": "table1",
                    "type": "table",
                    "title": "股票数据表",
                    "dataSource": f"http://localhost:{self.port}/api/table-data/stocks"
                },
                {
                    "id": "chart1", 
                    "type": "chart",
                    "title": "股票价格图表",
                    "dataSource": f"http://localhost:{self.port}/api/chart-data/prices"
                }
            ],
            "layout": {
                "rows": 2,
                "cols": 1
            },
            "auto_update": self.auto_update_config
        }
    
    def get_data_sources(self):
        """实现抽象方法：获取数据源配置"""
        return {
            "stocks": {
                "type": "json",
                "url": f"/api/table-data/stocks",
                "refresh_interval": self.auto_update_config.get('interval', 30)
            },
            "prices": {
                "type": "json", 
                "url": f"/api/chart-data/prices",
                "refresh_interval": self.auto_update_config.get('interval', 30)
            }
        }
    
    def register_custom_routes(self):
        """注册自定义路由"""
        # 添加示例数据API端点
        self.app.add_url_rule('/api/table-data/stocks', 'get_stocks_data', 
                             self.get_stocks_data, methods=['GET'])
        self.app.add_url_rule('/api/chart-data/prices', 'get_prices_data', 
                             self.get_prices_data, methods=['GET'])
        
        print("✅ 自定义路由注册完成")
    
    def get_stocks_data(self):
        """获取股票表格数据"""
        try:
            # 模拟实时价格变化
            import random
            for stock in self.example_data["stocks"]:
                # 随机变化 ±5%
                change_pct = random.uniform(-0.05, 0.05)
                stock["price"] = round(stock["price"] * (1 + change_pct), 2)
                stock["change"] = round(stock["price"] - stock["price"] / (1 + change_pct), 2)
            
            return jsonify({
                "status": "success",
                "data": {
                    "rows": self.example_data["stocks"],
                    "columns": [
                        {"field": "code", "header": "股票代码"},
                        {"field": "name", "header": "股票名称"},
                        {"field": "price", "header": "当前价格"},
                        {"field": "change", "header": "涨跌额"}
                    ]
                }
            })
        except Exception as e:
            self.logger.error(f"获取股票数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_prices_data(self):
        """获取价格图表数据"""
        try:
            import random
            import time
            
            # 生成模拟的时间序列数据
            timestamps = []
            prices = []
            base_time = int(time.time()) - 3600  # 1小时前开始
            
            for i in range(60):  # 60个数据点
                timestamps.append(base_time + i * 60)  # 每分钟一个点
                price = 12 + random.uniform(-2, 2) + 0.1 * i  # 基础价格12，有随机波动和微弱趋势
                prices.append(round(price, 2))
            
            chart_data = {
                "type": "line",
                "data": {
                    "labels": [f"{i//60:02d}:{i%60:02d}" for i in range(60)],
                    "datasets": [{
                        "label": "股票价格",
                        "data": prices,
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "tension": 0.1
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": "股票价格走势"
                        }
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": False
                        }
                    }
                }
            }
            
            return jsonify({
                "status": "success",
                "data": chart_data
            })
        except Exception as e:
            self.logger.error(f"获取价格图表数据失败: {e}")
            return jsonify({"error": str(e)}), 500


def main():
    """主函数 - 展示不同的启动方式"""
    print("📚 示例：集成自动更新配置系统")
    print("=" * 40)
    
    import argparse
    
    parser = argparse.ArgumentParser(description='示例股票仪表盘服务器')
    parser.add_argument('--mode', choices=['default', 'custom', 'disabled'], 
                       default='default', help='启动模式')
    parser.add_argument('--port', type=int, help='服务器端口')
    
    args = parser.parse_args()
    
    if args.mode == 'default':
        print("🔧 使用默认配置启动...")
        # 最简单的方式：完全使用配置文件
        server = ExampleStockServer()
        
    elif args.mode == 'custom':
        print("⚙️ 使用自定义配置启动...")
        # 自定义配置方式
        custom_config = create_auto_update_config("example",
                                                 enabled=True,
                                                 interval=15,  # 15秒更新
                                                 max_clients=20)
        server = ExampleStockServer(port=args.port, auto_update_config=custom_config)
        
    elif args.mode == 'disabled':
        print("🚫 禁用自动更新模式启动...")
        # 禁用自动更新
        disabled_config = {"enabled": False}
        server = ExampleStockServer(port=args.port, auto_update_config=disabled_config)
    
    print("\n🌐 可用的API端点:")
    print(f"   - 健康检查: http://localhost:{server.port}/health")
    print(f"   - 股票数据: http://localhost:{server.port}/api/table-data/stocks")
    print(f"   - 价格图表: http://localhost:{server.port}/api/chart-data/prices")
    print(f"   - 配置管理: http://localhost:{server.port}/config")
    print(f"   - 自动更新状态: http://localhost:{server.port}/api/auto-update/status")
    print(f"   - SSE事件流: http://localhost:{server.port}/api/dashboard/updates")
    
    print(f"\n🚀 启动服务器...")
    try:
        server.run(debug=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")


if __name__ == '__main__':
    main()
