#!/usr/bin/env python3
"""
测试动态标题功能的脚本
"""

import requests
import json
import time

def test_dynamic_titles():
    """测试动态标题功能"""
    base_url = "http://127.0.0.1:5003"
    
    print("🧪 开始测试动态标题功能...")
    
    # 1. 测试获取仪表盘配置
    print("\n1️⃣ 测试获取仪表盘配置...")
    try:
        response = requests.get(f"{base_url}/api/dashboard-config")
        if response.status_code == 200:
            config = response.json()
            print("✅ 仪表盘配置获取成功")
            
            # 检查动态标题
            components = config['layout']['components']
            for comp in components:
                if comp['id'] in ['table2', 'table21', 'table22']:
                    print(f"📋 {comp['id']}: {comp['title']}")
        else:
            print(f"❌ 获取配置失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取配置出错: {e}")
    
    # 2. 测试手动刷新标题
    print("\n2️⃣ 测试手动刷新标题...")
    try:
        response = requests.post(f"{base_url}/api/dashboard/refresh-titles")
        if response.status_code == 200:
            result = response.json()
            print("✅ 标题刷新成功")
            print(f"📊 涨幅前3板块: {result.get('top_sectors', [])}")
            print(f"🏷️ 动态标题: {result.get('titles', {})}")
        else:
            print(f"❌ 标题刷新失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 标题刷新出错: {e}")
    
    # 3. 再次获取配置验证标题是否更新
    print("\n3️⃣ 验证标题是否更新...")
    try:
        response = requests.get(f"{base_url}/api/dashboard-config")
        if response.status_code == 200:
            config = response.json()
            print("✅ 验证配置获取成功")
            
            # 检查更新后的动态标题
            components = config['layout']['components']
            for comp in components:
                if comp['id'] in ['table2', 'table21', 'table22']:
                    print(f"📋 {comp['id']}: {comp['title']}")
        else:
            print(f"❌ 验证配置失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 验证配置出错: {e}")
    
    # 4. 测试API参数
    print("\n4️⃣ 测试API参数支持...")
    test_params = [
        ("table2", "航运概念"),
        ("table21", "可控核聚变"),
        ("table22", "军工")
    ]
    
    for component_id, sector_name in test_params:
        try:
            url = f"{base_url}/api/table-data/stocks"
            params = {
                "componentId": component_id,
                "sector_name": sector_name
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {component_id} ({sector_name}): 获取到 {len(data.get('data', []))} 条数据")
            else:
                print(f"❌ {component_id} ({sector_name}): 获取失败 {response.status_code}")
        except Exception as e:
            print(f"❌ {component_id} ({sector_name}): 出错 {e}")
    
    print("\n🎉 动态标题功能测试完成！")

if __name__ == "__main__":
    test_dynamic_titles()
