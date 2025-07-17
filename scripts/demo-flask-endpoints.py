#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask端点名称演示 - 展示端点名称的各种用途
Flask Endpoint Name Demo - Shows various uses of endpoint names

Author: chenlei
"""

from flask import Flask, url_for, jsonify
import json

def demo_endpoint_usage():
    """演示端点名称的用途"""
    
    # 创建Flask应用
    app = Flask(__name__)
    
    # 注册路由 (模拟base_server.py中的注册)
    app.add_url_rule('/health', 'health_check', lambda: "健康检查", methods=['GET'])
    app.add_url_rule('/api/system/info', 'get_system_info', lambda: "系统信息", methods=['GET'])
    app.add_url_rule('/api/dashboard-config', 'get_dashboard_config', lambda: "仪表盘配置", methods=['GET'])
    app.add_url_rule('/api/table-data/<data_type>', 'get_table_data', lambda data_type: f"表格数据: {data_type}", methods=['GET'])
    app.add_url_rule('/api/chart-data/<chart_type>', 'get_chart_data', lambda chart_type: f"图表数据: {chart_type}", methods=['GET'])
    
    with app.app_context():
        print("📋 Flask端点名称演示")
        print("=" * 60)
        
        print("\n1️⃣  所有注册的路由和端点名称:")
        print("-" * 50)
        for rule in app.url_map.iter_rules():
            print(f"   端点名称: {rule.endpoint:20} → 路径: {rule.rule}")
        
        print("\n2️⃣  使用端点名称生成URL:")
        print("-" * 50)
        
        # 静态路由URL生成
        try:
            health_url = url_for('health_check')
            print(f"   health_check        → {health_url}")
            
            system_info_url = url_for('get_system_info') 
            print(f"   get_system_info     → {system_info_url}")
            
            dashboard_url = url_for('get_dashboard_config')
            print(f"   get_dashboard_config → {dashboard_url}")
        except Exception as e:
            print(f"   生成静态URL失败: {e}")
        
        print("\n3️⃣  带参数的URL生成:")
        print("-" * 50)
        
        # 动态路由URL生成
        try:
            # 表格数据URLs
            stock_table_url = url_for('get_table_data', data_type='stock-list')
            print(f"   股票表格数据        → {stock_table_url}")
            
            sector_table_url = url_for('get_table_data', data_type='sector-list')
            print(f"   板块表格数据        → {sector_table_url}")
            
            custom_table_url = url_for('get_table_data', data_type='custom-data')
            print(f"   自定义表格数据      → {custom_table_url}")
            
            # 图表数据URLs
            trend_chart_url = url_for('get_chart_data', chart_type='stock-trend')
            print(f"   股票趋势图表        → {trend_chart_url}")
            
            performance_chart_url = url_for('get_chart_data', chart_type='sector-performance')
            print(f"   板块表现图表        → {performance_chart_url}")
            
        except Exception as e:
            print(f"   生成动态URL失败: {e}")
        
        print("\n4️⃣  端点名称的优势:")
        print("-" * 50)
        print("   ✅ 代码可维护性: 修改URL路径时，只需修改路由注册处")
        print("   ✅ 避免硬编码: 不需要在代码中写死URL字符串")
        print("   ✅ 自动参数处理: Flask自动处理URL参数的编码和验证")
        print("   ✅ 调试友好: 可以通过端点名称快速定位路由")
        
        print("\n5️⃣  端点名称命名规范:")
        print("-" * 50)
        print("   📝 使用描述性名称: 'get_table_data' 比 'table_handler' 更清晰")
        print("   📝 保持一致性: 类似功能使用类似的命名模式")
        print("   📝 避免冲突: 确保端点名称在整个应用中唯一")
        print("   📝 使用下划线: Flask推荐使用下划线分隔单词")

def demo_endpoint_mapping():
    """演示端点名称与函数的映射关系"""
    
    print("\n🔗 端点名称与处理函数的映射关系")
    print("=" * 60)
    
    mappings = [
        {
            "url_pattern": "/api/table-data/<data_type>",
            "endpoint": "get_table_data", 
            "function": "self.get_table_data",
            "example_urls": [
                "/api/table-data/stock-list",
                "/api/table-data/sector-list"
            ]
        },
        {
            "url_pattern": "/api/chart-data/<chart_type>",
            "endpoint": "get_chart_data",
            "function": "self.get_chart_data", 
            "example_urls": [
                "/api/chart-data/stock-trend",
                "/api/chart-data/sector-performance"
            ]
        },
        {
            "url_pattern": "/health",
            "endpoint": "health_check",
            "function": "self.health_check",
            "example_urls": ["/health"]
        }
    ]
    
    for i, mapping in enumerate(mappings, 1):
        print(f"\n{i}️⃣  路由映射 {i}:")
        print(f"   URL模式: {mapping['url_pattern']}")
        print(f"   端点名称: {mapping['endpoint']}")
        print(f"   处理函数: {mapping['function']}")
        print(f"   示例URL: {', '.join(mapping['example_urls'])}")

def demo_practical_usage():
    """演示实际使用场景"""
    
    print("\n💼 实际使用场景演示")
    print("=" * 60)
    
    print("\n📊 场景1: 前端API配置生成")
    print("-" * 40)
    
    # 模拟前端配置生成
    api_config = {
        "endpoints": {
            "healthCheck": "health_check",
            "systemInfo": "get_system_info", 
            "dashboardConfig": "get_dashboard_config",
            "tableData": "get_table_data",
            "chartData": "get_chart_data"
        }
    }
    
    print("   前端可以这样配置API端点:")
    print(f"   {json.dumps(api_config, indent=6, ensure_ascii=False)}")
    
    print("\n🔄 场景2: 动态路由生成")
    print("-" * 40)
    
    # 模拟动态生成API调用
    data_types = ["stock-list", "sector-list", "user-data"]
    chart_types = ["stock-trend", "sector-performance", "volume-analysis"]
    
    print("   后端可以动态生成所有可用的API端点:")
    
    with Flask(__name__).app_context():
        app = Flask(__name__)
        app.add_url_rule('/api/table-data/<data_type>', 'get_table_data', lambda data_type: "", methods=['GET'])
        app.add_url_rule('/api/chart-data/<chart_type>', 'get_chart_data', lambda chart_type: "", methods=['GET'])
        
        with app.app_context():
            print("   表格数据端点:")
            for data_type in data_types:
                try:
                    url = url_for('get_table_data', data_type=data_type)
                    print(f"     {data_type:15} → {url}")
                except:
                    pass
            
            print("   图表数据端点:")
            for chart_type in chart_types:
                try:
                    url = url_for('get_chart_data', chart_type=chart_type)
                    print(f"     {chart_type:15} → {url}")
                except:
                    pass

def main():
    """主函数"""
    demo_endpoint_usage()
    demo_endpoint_mapping()
    demo_practical_usage()
    
    print("\n💡 总结:")
    print("=" * 60)
    print("端点名称 (endpoint) 是Flask路由的唯一标识符，主要用于:")
    print("• URL反向生成 - 通过名称生成URL")
    print("• 路由管理 - Flask内部管理和调试")
    print("• 代码维护 - 避免硬编码URL路径")
    print("• 模板引用 - 在HTML模板中引用路由")
    print("\n在 base_server.py 中，每个路由都有一个对应的端点名称，")
    print("这使得系统更加灵活和易于维护。")

if __name__ == "__main__":
    main()
