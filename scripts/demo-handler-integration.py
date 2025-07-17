#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示基类自动Handler调用功能

这个脚本演示了：
1. 基类如何根据get_data_sources()配置自动调用handler方法
2. 新的框架如何减少手工路由注册的需要
3. handler字符串与实际方法的映射关系

Author: chenlei
"""

import sys
import os

# 添加项目根目录到Python路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from api.base_server import BaseStockServer
from flask import jsonify
import json

class DemoHandlerServer(BaseStockServer):
    """演示Handler自动调用的测试服务器"""
    
    def __init__(self):
        super().__init__("Handler自动调用演示服务", 5099)
    
    def get_dashboard_config(self):
        """演示用仪表盘配置"""
        return {
            "title": "Handler自动调用演示",
            "layout": {
                "type": "grid",
                "components": [
                    {
                        "id": "test-table",
                        "type": "table", 
                        "dataSource": "/api/table-data/demo-table",
                        "title": "演示表格",
                        "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
                    },
                    {
                        "id": "test-chart",
                        "type": "chart",
                        "dataSource": "/api/chart-data/demo-chart", 
                        "title": "演示图表",
                        "position": {"row": 0, "col": 1, "rowSpan": 1, "colSpan": 1}
                    }
                ]
            }
        }
    
    def get_data_sources(self):
        """演示用数据源配置"""
        return {
            "/api/table-data/demo-table": {
                "handler": "demo_table_handler",
                "description": "演示表格数据handler",
                "cache_ttl": 30
            },
            "/api/chart-data/demo-chart": {
                "handler": "demo_chart_handler", 
                "description": "演示图表数据handler",
                "cache_ttl": 30
            },
            "/api/table-data/no-handler": {
                "description": "没有handler的静态数据",
                "columns": ["列1", "列2"],
                "data": [["值1", "值2"]]
            },
            "/api/table-data/missing-handler": {
                "handler": "non_existent_handler",
                "description": "handler方法不存在的情况"
            }
        }
    
    def demo_table_handler(self):
        """演示表格数据处理方法"""
        print("📊 调用了 demo_table_handler 方法")
        return jsonify({
            "columns": ["产品", "销量", "收入"],
            "data": [
                ["产品A", 100, 10000],
                ["产品B", 200, 15000], 
                ["产品C", 150, 12000]
            ],
            "metadata": {
                "generated_by": "demo_table_handler",
                "source": "handler自动调用"
            }
        })
    
    def demo_chart_handler(self):
        """演示图表数据处理方法"""
        print("📈 调用了 demo_chart_handler 方法")
        
        # 生成演示数据
        times = ["09:30", "10:00", "10:30", "11:00", "11:30"]
        values = [100, 102, 98, 105, 103]
        
        # 使用基类的图表创建方法
        chart_json = self.create_line_chart(
            times, values, 
            "Handler自动调用演示图表", "时间", "数值"
        )
        
        return chart_json

def test_handler_integration():
    """测试handler集成功能"""
    print("🧪 测试基类Handler自动调用功能")
    print("=" * 60)
    
    # 创建测试服务器实例
    server = DemoHandlerServer()
    
    print("1️⃣ 测试数据源配置")
    data_sources = server.get_data_sources()
    print(f"   配置的数据源: {list(data_sources.keys())}")
    
    print("\n2️⃣ 测试表格handler自动调用")
    print("   请求: /api/table-data/demo-table")
    
    # 模拟Flask上下文
    with server.app.app_context():
        result = server.get_table_data("demo-table")
        if hasattr(result, 'get_json'):
            print(f"   ✅ 成功调用handler，返回数据: {result.get_json()}")
        else:
            print(f"   ❌ 返回类型异常: {type(result)}")
    
    print("\n3️⃣ 测试图表handler自动调用")
    print("   请求: /api/chart-data/demo-chart")
    
    with server.app.app_context():
        result = server.get_chart_data("demo-chart")
        if isinstance(result, str):
            print("   ✅ 成功调用handler，返回Plotly图表JSON")
            # 验证是否为有效JSON
            try:
                chart_data = json.loads(result)
                print(f"   📊 图表标题: {chart_data.get('layout', {}).get('title')}")
            except:
                print("   ⚠️ 返回的不是有效JSON")
        else:
            print(f"   ❌ 返回类型异常: {type(result)}")
    
    print("\n4️⃣ 测试无handler的静态数据")
    print("   请求: /api/table-data/no-handler")
    
    with server.app.app_context():
        result = server.get_table_data("no-handler")
        if hasattr(result, 'get_json'):
            print(f"   ✅ 成功返回静态数据: {result.get_json()}")
        else:
            print(f"   ❌ 返回类型异常: {type(result)}")
    
    print("\n5️⃣ 测试不存在的handler")
    print("   请求: /api/table-data/missing-handler")
    
    with server.app.app_context():
        result = server.get_table_data("missing-handler")
        print(f"   ⚠️ handler不存在时的处理结果: {type(result)}")
    
    print("\n6️⃣ 测试兼容性：调用不存在的数据源")
    print("   请求: /api/table-data/unknown")
    
    with server.app.app_context():
        result = server.get_table_data("unknown")
        if hasattr(result, 'get_json'):
            print(f"   ✅ 降级到默认处理: {result.get_json()}")
        else:
            print(f"   返回类型: {type(result)}")

def demonstrate_method_inspection():
    """演示方法检查机制"""
    print("\n🔍 演示方法检查机制")
    print("=" * 60)
    
    server = DemoHandlerServer()
    
    # 检查各种handler方法是否存在
    handlers_to_check = [
        "demo_table_handler",
        "demo_chart_handler", 
        "non_existent_handler",
        "get_dashboard_config",
        "generate_mock_stock_data"
    ]
    
    for handler in handlers_to_check:
        exists = hasattr(server, handler)
        if exists:
            method = getattr(server, handler)
            print(f"   ✅ {handler}: 存在 ({type(method)})")
        else:
            print(f"   ❌ {handler}: 不存在")

if __name__ == "__main__":
    print("🎯 基类Handler自动调用功能演示")
    print("=" * 80)
    
    try:
        test_handler_integration()
        demonstrate_method_inspection()
        
        print("\n" + "=" * 80)
        print("✅ 演示完成！")
        print("\n💡 关键改进:")
        print("   1. 基类现在支持根据get_data_sources()自动调用handler方法")
        print("   2. 子类只需要定义handler方法，无需手工注册路由")
        print("   3. 支持静态配置和动态handler的混合使用")
        print("   4. 向后兼容原有的路由注册方式")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
