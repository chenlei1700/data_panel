#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试堆叠面积图组件的表格显示功能
"""

import requests
import json

def test_table_data():
    """测试表格数据"""
    
    print("🧪 测试堆叠面积图组件表格数据")
    print("=" * 50)
    
    api_url = "http://127.0.0.1:5004/api/chart-data/stacked-area-demo"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API响应成功")
            print(f"📋 数据结构分析:")
            
            # 检查顶级字段
            print(f"   - 顶级字段: {list(data.keys())}")
            
            if 'tableData' in data:
                table_data = data['tableData']
                print(f"   ✅ 找到 tableData 字段")
                print(f"   - 表格数据类型: {type(table_data)}")
                print(f"   - 表格数据内容: {table_data}")
                
                # 检查表格数据是否为空
                if isinstance(table_data, dict) and len(table_data) > 0:
                    print("   ✅ 表格数据不为空，应该能显示表格")
                else:
                    print("   ❌ 表格数据为空或格式错误")
                    
            else:
                print("   ❌ 没有找到 tableData 字段")
            
            if 'stackedAreaData' in data:
                stacked_data = data['stackedAreaData']
                if 'tableData' in stacked_data:
                    print(f"   ⚠️  在 stackedAreaData 内部也找到了 tableData: {stacked_data['tableData']}")
            
            # 完整输出以便调试
            print(f"\n📄 完整响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_table_data()
