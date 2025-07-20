#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
堆叠面积图组件数据格式验证脚本
验证后端API数据格式与前端组件的兼容性
"""

import requests
import json

def test_api_data_format():
    """测试API数据格式"""
    
    print("🔍 验证堆叠面积图API数据格式")
    print("=" * 50)
    
    api_url = "http://127.0.0.1:5004/api/chart-data/stacked-area-demo"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API响应成功")
            print(f"📋 返回的数据结构:")
            
            # 验证顶级结构
            if 'stackedAreaData' in data:
                print("   ✅ 包含 stackedAreaData 字段")
                
                stacked_data = data['stackedAreaData']
                
                # 验证数据字段
                if 'data' in stacked_data:
                    print("   ✅ 包含 data 字段")
                    data_dict = stacked_data['data']
                    
                    if len(data_dict) > 0:
                        print(f"   ✅ 数据点数量: {len(data_dict)}")
                        
                        # 获取X轴值
                        x_values = list(data_dict.keys())
                        print(f"   ✅ X轴时间点: {x_values}")
                        
                        # 获取第一个数据点的key顺序
                        first_point = data_dict[x_values[0]]
                        key_order = list(first_point.keys())
                        print(f"   ✅ 数据系列: {key_order}")
                        
                        # 验证数据完整性
                        print("\n🔬 数据完整性检查:")
                        all_complete = True
                        for x_val in x_values:
                            point_data = data_dict[x_val]
                            missing_keys = [k for k in key_order if k not in point_data]
                            if missing_keys:
                                print(f"   ❌ {x_val} 缺少字段: {missing_keys}")
                                all_complete = False
                        
                        if all_complete:
                            print("   ✅ 所有数据点都包含完整的字段")
                            
                    else:
                        print("   ❌ 数据为空")
                        
                else:
                    print("   ❌ 缺少 data 字段")
                
                # 验证颜色字段
                if 'colors' in stacked_data:
                    print("   ✅ 包含 colors 字段")
                    colors = stacked_data['colors']
                    print(f"   ✅ 颜色数量: {len(colors)}")
                else:
                    print("   ⚠️  缺少 colors 字段（将使用默认颜色）")
                
            else:
                print("   ❌ 缺少 stackedAreaData 字段")
                
            print(f"\n📄 完整数据结构预览:")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:500] + "...")
            
        else:
            print(f"❌ API请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def simulate_frontend_parsing():
    """模拟前端组件的数据解析过程"""
    
    print("\n🎭 模拟前端组件数据解析")
    print("=" * 40)
    
    try:
        response = requests.get("http://127.0.0.1:5004/api/chart-data/stacked-area-demo")
        data = response.json()
        
        # 模拟前端组件的解析逻辑
        if data.get('stackedAreaData') and data['stackedAreaData'].get('data'):
            stacked_data = data['stackedAreaData']
            chart_data = stacked_data
            
            # 提取 X 轴值
            x_axis_values = sorted(stacked_data['data'].keys())
            print(f"✅ X轴值提取成功: {x_axis_values}")
            
            # 提取 key 顺序
            if x_axis_values:
                first_data_point = stacked_data['data'][x_axis_values[0]]
                key_order = list(first_data_point.keys())
                print(f"✅ 系列顺序提取成功: {key_order}")
                
                # 添加到 chart_data
                chart_data['keyOrder'] = key_order
                
                print("✅ 数据解析完成，组件应该能够正常渲染")
                
                # 验证累积计算
                print("\n📊 累积计算验证:")
                for i, x_val in enumerate(x_axis_values[:2]):  # 只显示前两个点
                    data_point = stacked_data['data'][x_val]
                    cumulative = 0
                    print(f"   {x_val}:")
                    for key in key_order:
                        value = data_point.get(key, 0)
                        cumulative += value
                        print(f"     {key}: {value} (累积: {cumulative})")
                    
            else:
                print("❌ 没有找到数据点")
        else:
            print("❌ 数据格式不符合预期")
            
    except Exception as e:
        print(f"❌ 模拟解析失败: {e}")

if __name__ == "__main__":
    test_api_data_format()
    simulate_frontend_parsing()
    
    print("\n🎯 结论:")
    print("- 修复后的组件应该能够正确解析API数据")
    print("- 组件会自动提取X轴值和系列顺序")
    print("- 请刷新浏览器页面查看图表显示效果")
