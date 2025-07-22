#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
堆叠面积图组件测试脚本
测试新创建的堆叠面积图组件的API和数据格式
"""

import requests
import json
from typing import Dict, Any

def test_stacked_area_api():
    """测试堆叠面积图API端点"""
    
    print("🧪 堆叠面积图组件测试")
    print("=" * 50)
    
    # API端点
    api_url = "http://127.0.0.1:5004/api/chart-data/stacked-area-demo"
    
    try:
        # 发送请求
        print(f"📡 测试API端点: {api_url}")
        response = requests.get(api_url, timeout=10)
        
        # 检查状态码
        print(f"📊 HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 解析JSON数据
            data = response.json()
            
            print("✅ API响应成功!")
            print(f"📋 响应数据结构:")
            
            if 'stackedAreaData' in data:
                stacked_data = data['stackedAreaData']
                
                # 检查数据结构
                if 'data' in stacked_data:
                    print(f"   - 数据点数量: {len(stacked_data['data'])}")
                    print(f"   - X轴时间点: {list(stacked_data['data'].keys())}")
                    
                    # 检查第一个数据点
                    first_key = list(stacked_data['data'].keys())[0]
                    first_data = stacked_data['data'][first_key]
                    print(f"   - 第一个数据点 ({first_key}): {first_data}")
                
                if 'colors' in stacked_data:
                    print(f"   - 颜色配置: {stacked_data['colors']}")
                
                if 'tableData' in stacked_data:
                    print(f"   - 表格数据: {stacked_data['tableData']}")
                
                print("\n📈 测试数据有效性:")
                validate_data_structure(stacked_data)
                
            else:
                print("❌ 响应数据中缺少 'stackedAreaData' 字段")
                
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 请确保后端服务器(端口5004)正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 服务器响应时间过长")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def validate_data_structure(stacked_data: Dict[str, Any]):
    """验证堆叠面积图数据结构的有效性"""
    
    validation_results = []
    
    # 检查必要字段
    required_fields = ['data', 'colors']
    for field in required_fields:
        if field in stacked_data:
            validation_results.append(f"✅ {field}: 存在")
        else:
            validation_results.append(f"❌ {field}: 缺失")
    
    # 检查数据格式
    if 'data' in stacked_data:
        data_dict = stacked_data['data']
        
        # 检查是否有数据
        if len(data_dict) > 0:
            validation_results.append(f"✅ 数据点数量: {len(data_dict)}")
            
            # 检查数据结构一致性
            first_key = list(data_dict.keys())[0]
            first_value = data_dict[first_key]
            
            if isinstance(first_value, dict):
                validation_results.append("✅ 数据格式: 字典结构")
                validation_results.append(f"✅ 系列数量: {len(first_value)}")
                validation_results.append(f"✅ 系列名称: {list(first_value.keys())}")
            else:
                validation_results.append("❌ 数据格式: 不是字典结构")
        else:
            validation_results.append("❌ 数据点数量: 0")
    
    # 检查颜色配置
    if 'colors' in stacked_data:
        colors = stacked_data['colors']
        if isinstance(colors, list) and len(colors) > 0:
            validation_results.append(f"✅ 颜色配置: {len(colors)} 个颜色")
        else:
            validation_results.append("❌ 颜色配置: 格式错误或为空")
    
    # 输出验证结果
    for result in validation_results:
        print(f"   {result}")

def test_frontend_accessibility():
    """测试前端页面可访问性"""
    
    print("\n🌐 前端页面测试")
    print("=" * 30)
    
    pages_to_test = [
        ("主页", "http://localhost:8082/"),
        ("堆叠面积图演示", "http://localhost:8082/stacked-area-demo"),
    ]
    
    for page_name, url in pages_to_test:
        try:
            print(f"🔗 测试页面: {page_name}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ 页面可访问 ({response.status_code})")
            else:
                print(f"   ❌ 页面不可访问 ({response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 连接错误: 请确保前端服务器(端口8082)正在运行")
        except Exception as e:
            print(f"   ❌ 错误: {e}")

def print_test_summary():
    """打印测试总结"""
    
    print("\n📝 测试总结")
    print("=" * 40)
    print("本测试验证了以下功能:")
    print("1. ✅ 堆叠面积图API端点响应")
    print("2. ✅ 数据格式和结构验证") 
    print("3. ✅ 前端页面可访问性")
    print("\n如果所有测试通过，说明堆叠面积图组件已成功集成!")
    print("\n🎯 下一步操作:")
    print("- 在浏览器中访问 http://localhost:8082/stacked-area-demo")
    print("- 检查图表渲染和交互功能")
    print("- 测试不同数据配置和颜色主题")

if __name__ == "__main__":
    test_stacked_area_api()
    test_frontend_accessibility()
    print_test_summary()
