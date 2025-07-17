#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源配置示例演示 - 展示 get_dashboard_config 和 get_data_sources 的配合工作
Data Source Configuration Demo - Shows how get_dashboard_config and get_data_sources work together

Author: chenlei
"""

import json
from typing import Dict, Any

def demo_dashboard_config() -> Dict[str, Any]:
    """演示前端配置 - 定义界面布局和数据获取路径"""
    return {
        "layout": {
            "rows": 3,
            "cols": 2,
            "components": [
                {
                    "id": "stock_chart",
                    "type": "chart",
                    "dataSource": "/api/chart-data/stock-trend",  # ← 前端将调用这个API
                    "title": "股票走势图",
                    "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
                },
                {
                    "id": "sector_chart", 
                    "type": "chart",
                    "dataSource": "/api/chart-data/sector-performance",  # ← 前端将调用这个API
                    "title": "板块表现",
                    "position": {"row": 0, "col": 1, "rowSpan": 1, "colSpan": 1}
                },
                {
                    "id": "stock_table",
                    "type": "table",
                    "dataSource": "/api/table-data/stock-list",  # ← 前端将调用这个API
                    "title": "股票列表",
                    "position": {"row": 1, "col": 0, "rowSpan": 2, "colSpan": 1}
                },
                {
                    "id": "sector_table",
                    "type": "table", 
                    "dataSource": "/api/table-data/sector-list",  # ← 前端将调用这个API
                    "title": "板块列表",
                    "position": {"row": 1, "col": 1, "rowSpan": 2, "colSpan": 1}
                }
            ]
        },
        "title": "数据源配置演示系统",
        "description": "展示前后端数据配置的配合工作"
    }

def demo_data_sources() -> Dict[str, Any]:
    """演示后端配置 - 定义如何生成和处理数据"""
    return {
        "tables": {
            "stock-list": {  # ← 对应 API 路径中的 data_type
                "description": "股票列表数据源",
                "generator_method": "generate_mock_stock_data",
                "params": {"count": 20},
                "refresh_interval": 5000,
                "cache_duration": 30,
                "fields": ["股票代码", "股票名称", "当前价格", "涨跌幅", "成交量"]
            },
            "sector-list": {  # ← 对应 API 路径中的 data_type
                "description": "板块列表数据源",
                "generator_method": "generate_mock_sector_data", 
                "params": {},
                "refresh_interval": 8000,
                "cache_duration": 60,
                "fields": ["板块名称", "涨跌幅", "成交额", "领涨股"]
            }
        },
        "charts": {
            "stock-trend": {  # ← 对应 API 路径中的 chart_type
                "description": "股票走势图数据源",
                "type": "line",
                "generator_method": "generate_mock_time_series",
                "params": {"period": "1d", "interval": "5m"},
                "update_frequency": "realtime",
                "cache_strategy": "no_cache"
            },
            "sector-performance": {  # ← 对应 API 路径中的 chart_type
                "description": "板块表现图数据源",
                "type": "bar",
                "generator_method": "generate_sector_performance_data",
                "params": {"sectors": 10},
                "update_frequency": "medium", 
                "cache_strategy": "short_cache"
            }
        }
    }

def demo_api_flow():
    """演示API调用流程"""
    print("🔄 API调用流程演示")
    print("=" * 60)
    
    dashboard_config = demo_dashboard_config()
    data_sources = demo_data_sources()
    
    print("📊 第一步: 前端获取仪表盘配置")
    print("请求: GET /api/dashboard-config")
    print("返回的配置包含组件布局和数据源URL:")
    
    for component in dashboard_config["layout"]["components"]:
        print(f"  组件 {component['id']}: 将从 {component['dataSource']} 获取数据")
    
    print("\n📡 第二步: 前端根据配置请求具体数据")
    print("基于配置中的 dataSource，前端会调用以下API:")
    
    # 模拟前端调用
    api_calls = []
    for component in dashboard_config["layout"]["components"]:
        data_source = component["dataSource"]
        api_calls.append(data_source)
    
    for api_call in set(api_calls):  # 去重
        print(f"  前端调用: GET {api_call}")
        
        # 解析API路径，确定数据类型
        if "/api/table-data/" in api_call:
            data_type = api_call.split("/api/table-data/")[1]
            if data_type in data_sources["tables"]:
                config = data_sources["tables"][data_type]
                print(f"    后端处理: 使用 {config['generator_method']} 生成表格数据")
                print(f"    参数: {config['params']}")
        
        elif "/api/chart-data/" in api_call:
            chart_type = api_call.split("/api/chart-data/")[1]
            if chart_type in data_sources["charts"]:
                config = data_sources["charts"][chart_type]
                print(f"    后端处理: 使用 {config['generator_method']} 生成图表数据")
                print(f"    图表类型: {config['type']}, 参数: {config['params']}")
    
    print("\n🎯 第三步: 数据生成和返回")
    print("后端根据 get_data_sources() 的配置:")
    print("  1. 调用相应的数据生成方法")
    print("  2. 应用缓存策略和更新频率")
    print("  3. 返回格式化的数据给前端")
    print("  4. 前端接收数据并渲染组件")

def demo_configuration_mapping():
    """演示配置映射关系"""
    print("\n🗺️  配置映射关系演示")
    print("=" * 60)
    
    dashboard_config = demo_dashboard_config()
    data_sources = demo_data_sources()
    
    print("前端配置 (get_dashboard_config) → 后端配置 (get_data_sources)")
    print()
    
    for component in dashboard_config["layout"]["components"]:
        data_source_url = component["dataSource"]
        component_id = component["id"]
        
        print(f"🔗 组件: {component_id}")
        print(f"   前端配置: dataSource = '{data_source_url}'")
        
        # 分析映射关系
        if "/api/table-data/" in data_source_url:
            data_type = data_source_url.split("/api/table-data/")[1]
            if data_type in data_sources["tables"]:
                backend_config = data_sources["tables"][data_type]
                print(f"   ↓ 映射到")
                print(f"   后端配置: tables['{data_type}']")
                print(f"   生成方法: {backend_config['generator_method']}")
                print(f"   刷新间隔: {backend_config['refresh_interval']}ms")
        
        elif "/api/chart-data/" in data_source_url:
            chart_type = data_source_url.split("/api/chart-data/")[1]
            if chart_type in data_sources["charts"]:
                backend_config = data_sources["charts"][chart_type]
                print(f"   ↓ 映射到")
                print(f"   后端配置: charts['{chart_type}']")
                print(f"   图表类型: {backend_config['type']}")
                print(f"   生成方法: {backend_config['generator_method']}")
                print(f"   更新频率: {backend_config['update_frequency']}")
        
        print()

def main():
    """主演示函数"""
    print("📚 数据源配置工作原理演示")
    print("=" * 60)
    print()
    
    print("📋 概念说明:")
    print("• get_dashboard_config(): 定义前端界面布局和数据获取路径")
    print("• get_data_sources(): 定义后端数据生成和处理方式") 
    print("• dataSource (前端): API端点URL，告诉前端从哪里获取数据")
    print("• 配置项 (后端): 数据生成方法和参数，告诉后端如何生成数据")
    print()
    
    # 显示配置内容
    print("🎨 前端配置示例 (get_dashboard_config):")
    print("-" * 50)
    dashboard_config = demo_dashboard_config()
    print(json.dumps(dashboard_config, indent=2, ensure_ascii=False))
    
    print("\n🔧 后端配置示例 (get_data_sources):")
    print("-" * 50)
    data_sources = demo_data_sources()
    print(json.dumps(data_sources, indent=2, ensure_ascii=False))
    
    # 演示工作流程
    demo_api_flow()
    demo_configuration_mapping()
    
    print("\n💡 关键理解:")
    print("1. 前端配置的 dataSource 是 API URL")
    print("2. 后端配置的 key 对应 API URL 中的参数")
    print("3. 两者通过 URL 路径参数建立映射关系")
    print("4. 框架自动处理映射和数据生成")

if __name__ == "__main__":
    main()
