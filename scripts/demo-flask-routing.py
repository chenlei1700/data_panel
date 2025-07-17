#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 路由演示 - 展示动态路径参数的工作原理
Flask Route Demo - Shows how dynamic path parameters work

Author: chenlei
"""

from flask import Flask, jsonify

def demo_flask_routing():
    """演示Flask路由工作原理"""
    print("🔗 Flask 路由工作原理演示")
    print("=" * 50)
    
    # 创建Flask应用
    app = Flask(__name__)
    
    # 注册路由 - 这就是你看到的那句代码
    @app.route('/api/table-data/<data_type>', methods=['GET'])
    def get_table_data(data_type):
        """处理表格数据请求"""
        print(f"📥 接收到请求，data_type = '{data_type}'")
        
        # 根据不同的data_type返回不同数据
        if data_type == "stock-list":
            return jsonify({
                "type": "stock-list",
                "data": [
                    {"股票代码": "000001", "股票名称": "平安银行", "价格": 12.34},
                    {"股票代码": "000002", "股票名称": "万科A", "价格": 23.45}
                ]
            })
        elif data_type == "sector-list":
            return jsonify({
                "type": "sector-list", 
                "data": [
                    {"板块名称": "科技板块", "涨跌幅": "+2.3%"},
                    {"板块名称": "医药板块", "涨跌幅": "-1.2%"}
                ]
            })
        else:
            return jsonify({"error": f"未知的数据类型: {data_type}"}), 404
    
    print("\n📋 路由注册信息:")
    print("路径模式: /api/table-data/<data_type>")
    print("HTTP方法: GET")
    print("处理函数: get_table_data")
    
    print("\n🎯 可匹配的URL示例:")
    test_urls = [
        "/api/table-data/stock-list",
        "/api/table-data/sector-list", 
        "/api/table-data/user-preferences",
        "/api/table-data/market-summary"
    ]
    
    for url in test_urls:
        data_type = url.split('/')[-1]  # 提取data_type
        print(f"  GET {url} → data_type = '{data_type}'")
    
    print("\n❌ 不会匹配的URL:")
    invalid_urls = [
        "/api/table-data/",                    # 缺少data_type
        "/api/table-data/stock/details",       # 路径层级过多
        "/api/chart-data/stock-list",          # 路径不匹配
        "POST /api/table-data/stock-list"      # HTTP方法不匹配
    ]
    
    for url in invalid_urls:
        print(f"  {url}")

def demo_route_parameter_extraction():
    """演示路径参数提取过程"""
    print("\n🔍 路径参数提取演示")
    print("=" * 50)
    
    # 模拟路由匹配过程
    route_pattern = "/api/table-data/<data_type>"
    
    test_requests = [
        "GET /api/table-data/stock-list",
        "GET /api/table-data/sector-list",
        "GET /api/table-data/financial-reports",
        "GET /api/table-data/123"
    ]
    
    print(f"路由模式: {route_pattern}")
    print("\n请求处理过程:")
    
    for request in test_requests:
        method, url = request.split(' ', 1)
        print(f"\n📨 {request}")
        
        # 检查是否匹配路由模式
        if url.startswith("/api/table-data/") and len(url.split('/')) == 4:
            data_type = url.split('/')[-1]
            print(f"  ✅ 路由匹配成功")
            print(f"  📝 提取参数: data_type = '{data_type}'")
            print(f"  🔧 调用函数: get_table_data('{data_type}')")
            print(f"  📤 函数返回相应的{data_type}数据")
        else:
            print(f"  ❌ 路由匹配失败")

def demo_real_world_usage():
    """演示实际使用场景"""
    print("\n🌍 实际使用场景演示")
    print("=" * 50)
    
    print("在股票仪表盘系统中，这个路由用于:")
    print()
    
    scenarios = [
        {
            "前端需求": "获取股票列表数据",
            "发送请求": "GET /api/table-data/stock-list",
            "后端处理": "data_type='stock-list' → 生成股票数据",
            "返回结果": "股票代码、名称、价格等数据"
        },
        {
            "前端需求": "获取板块列表数据", 
            "发送请求": "GET /api/table-data/sector-list",
            "后端处理": "data_type='sector-list' → 生成板块数据",
            "返回结果": "板块名称、涨跌幅等数据"
        },
        {
            "前端需求": "获取自定义表格数据",
            "发送请求": "GET /api/table-data/custom-metrics",
            "后端处理": "data_type='custom-metrics' → 生成自定义数据",
            "返回结果": "根据配置生成的数据"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"场景 {i}:")
        for key, value in scenario.items():
            print(f"  {key}: {value}")
        print()

def main():
    """主演示函数"""
    print("🚀 Flask 动态路由详解")
    print("=" * 60)
    print()
    
    # 核心语法解释
    print("💡 核心语法:")
    print("app.add_url_rule('/api/table-data/<data_type>', 'get_table_data', self.get_table_data, methods=['GET'])")
    print()
    print("参数说明:")
    print("1. '/api/table-data/<data_type>' - URL路径模式，<data_type>是动态参数")
    print("2. 'get_table_data' - 端点名称，用于URL反向生成")
    print("3. self.get_table_data - 处理函数，接收data_type参数")
    print("4. methods=['GET'] - 只接受GET请求")
    print()
    
    # 运行演示
    demo_flask_routing()
    demo_route_parameter_extraction()
    demo_real_world_usage()
    
    print("🎯 关键理解:")
    print("• <data_type> 是动态参数，可以匹配任何字符串")
    print("• 提取的参数会自动传递给处理函数")
    print("• 一个路由可以处理多种不同类型的数据请求")
    print("• 这种设计提供了API的灵活性和可扩展性")

if __name__ == "__main__":
    main()
