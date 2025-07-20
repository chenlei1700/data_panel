#!/usr/bin/env python3
"""
堆叠面积图功能演示脚本
用于测试和演示新增的堆叠面积图组件功能

使用方法:
python demo-stacked-area-chart.py
"""

import json
import random
import time
from datetime import datetime, timedelta

def generate_stacked_area_demo_data():
    """生成堆叠面积图演示数据"""
    
    # 示例1: 资金流向分析数据
    fund_flow_data = {
        "title": "📈 资金流向分析",
        "description": "展示不同类型资金在交易日内的流入情况",
        "data": generate_fund_flow_data()
    }
    
    # 示例2: 板块表现数据
    sector_performance_data = {
        "title": "🏢 板块表现分析", 
        "description": "展示各板块在不同时间段的表现",
        "data": generate_sector_performance_data()
    }
    
    # 示例3: 成交量分析数据
    volume_analysis_data = {
        "title": "📊 成交量结构分析",
        "description": "展示不同规模订单的成交量分布", 
        "data": generate_volume_analysis_data()
    }
    
    return {
        "fund_flow": fund_flow_data,
        "sector_performance": sector_performance_data, 
        "volume_analysis": volume_analysis_data
    }

def generate_fund_flow_data():
    """生成资金流向数据"""
    # 交易时间点
    time_points = ["09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00"]
    
    # 资金类型（堆叠顺序从下到上）
    fund_types = ["散户资金", "游资", "私募资金", "公募基金", "外资", "国家队"]
    
    # 颜色配置
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F39C12"]
    
    data = {}
    table_data = {}
    
    for time_point in time_points:
        point_data = {}
        total_amount = 0
        
        # 为每种资金类型生成数据
        for i, fund_type in enumerate(fund_types):
            # 基础金额 + 随机波动
            base_amount = [20, 35, 25, 40, 15, 30][i]  # 不同资金类型的基础金额
            
            # 根据时间段调整
            time_factor = get_time_factor(time_point)
            
            # 添加随机性
            random_factor = random.uniform(0.7, 1.3)
            
            amount = round(base_amount * time_factor * random_factor, 1)
            point_data[fund_type] = amount
            total_amount += amount
        
        data[time_point] = point_data
        table_data[time_point] = f"{total_amount:.1f}亿"
    
    return {
        "stackedAreaData": {
            "data": data,
            "keyOrder": fund_types,
            "colors": colors
        },
        "xAxisValues": time_points,
        "tableData": table_data
    }

def generate_sector_performance_data():
    """生成板块表现数据"""
    time_points = ["周一", "周二", "周三", "周四", "周五"]
    sectors = ["科技板块", "金融板块", "消费板块", "医药板块", "新能源"]
    colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]
    
    data = {}
    table_data = {}
    
    for time_point in time_points:
        point_data = {}
        total_performance = 0
        
        for i, sector in enumerate(sectors):
            # 模拟板块表现指数
            performance = round(random.uniform(5, 30), 1)
            point_data[sector] = performance
            total_performance += performance
        
        data[time_point] = point_data
        table_data[time_point] = f"{total_performance:.1f}点"
    
    return {
        "stackedAreaData": {
            "data": data,
            "keyOrder": sectors,
            "colors": colors
        },
        "xAxisValues": time_points,
        "tableData": table_data
    }

def generate_volume_analysis_data():
    """生成成交量分析数据"""
    time_points = ["9:30-10:00", "10:00-10:30", "10:30-11:00", "11:00-11:30", 
                   "14:00-14:30", "14:30-15:00"]
    order_types = ["小单(<5万)", "中单(5-20万)", "大单(20-100万)", "超大单(>100万)"]
    colors = ["#FFD93D", "#6BCF7F", "#4D96FF", "#FF6B6B"]
    
    data = {}
    table_data = {}
    
    for time_point in time_points:
        point_data = {}
        total_volume = 0
        
        for i, order_type in enumerate(order_types):
            # 不同类型订单的基础成交量
            base_volumes = [40, 30, 20, 10]  # 小单占比最高
            volume = round(base_volumes[i] * random.uniform(0.8, 1.4), 1)
            point_data[order_type] = volume
            total_volume += volume
        
        data[time_point] = point_data
        table_data[time_point] = f"{total_volume:.1f}万手"
    
    return {
        "stackedAreaData": {
            "data": data,
            "keyOrder": order_types,
            "colors": colors
        },
        "xAxisValues": time_points,
        "tableData": table_data
    }

def get_time_factor(time_point):
    """根据时间点返回调整因子"""
    factors = {
        "09:30": 1.3,  # 开盘活跃
        "10:00": 1.1,
        "10:30": 1.2,  # 交易活跃时段
        "11:00": 1.0,
        "11:30": 0.9,  # 临近午休
        "14:00": 1.1,  # 午后开盘
        "14:30": 1.3,  # 交易活跃
        "15:00": 1.4   # 收盘前活跃
    }
    return factors.get(time_point, 1.0)

def save_demo_data_to_file():
    """将演示数据保存到文件"""
    demo_data = generate_stacked_area_demo_data()
    
    # 保存为JSON文件
    with open('stacked_area_demo_data.json', 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 演示数据已保存到 stacked_area_demo_data.json")
    
    # 打印数据预览
    print("\n📊 资金流向数据预览:")
    fund_data = demo_data['fund_flow']['data']
    for time_point, values in list(fund_data['stackedAreaData']['data'].items())[:3]:
        print(f"  {time_point}: {values}")
    
    print(f"\n📈 总共生成了 {len(demo_data)} 个演示数据集")

def test_api_format():
    """测试API数据格式的正确性"""
    print("🧪 测试API数据格式...")
    
    demo_data = generate_stacked_area_demo_data()
    
    for name, dataset in demo_data.items():
        data = dataset['data']
        
        # 检查必需字段
        required_fields = ['stackedAreaData', 'xAxisValues']
        for field in required_fields:
            if field not in data:
                print(f"❌ {name}: 缺少字段 {field}")
                continue
        
        # 检查stackedAreaData结构
        stacked_data = data['stackedAreaData']
        if 'data' not in stacked_data or 'keyOrder' not in stacked_data:
            print(f"❌ {name}: stackedAreaData结构不正确")
            continue
            
        # 检查数据一致性
        x_values = data['xAxisValues']
        data_keys = list(stacked_data['data'].keys())
        
        if set(x_values) != set(data_keys):
            print(f"❌ {name}: xAxisValues与data的key不匹配")
            continue
        
        # 检查每个数据点是否包含所有key
        key_order = stacked_data['keyOrder']
        for x_val in x_values:
            point_data = stacked_data['data'][x_val]
            for key in key_order:
                if key not in point_data:
                    print(f"❌ {name}: 数据点 {x_val} 缺少key {key}")
                    break
        
        print(f"✅ {name}: 数据格式正确")

def generate_real_time_data():
    """生成实时更新的数据演示"""
    print("⏱️ 生成实时数据演示 (按Ctrl+C停止)...")
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n🕐 {current_time}")
            
            # 生成一个简化的实时数据点
            data_point = {
                "time": current_time,
                "买盘资金": round(random.uniform(20, 50), 1),
                "卖盘资金": round(random.uniform(15, 45), 1),
                "观望资金": round(random.uniform(10, 30), 1)
            }
            
            total = sum(data_point.values()) - len(data_point) + 1  # 减去time字段
            print(f"  📊 数据: {data_point}")
            print(f"  💰 总计: {total:.1f}亿")
            
            time.sleep(5)  # 每5秒更新一次
            
    except KeyboardInterrupt:
        print("\n⏹️ 实时数据演示已停止")

def main():
    """主函数"""
    print("🚀 堆叠面积图功能演示")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 生成演示数据")
        print("2. 测试API格式")
        print("3. 保存数据到文件")
        print("4. 实时数据演示")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            demo_data = generate_stacked_area_demo_data()
            print(f"\n✅ 已生成 {len(demo_data)} 个数据集:")
            for name, dataset in demo_data.items():
                print(f"  📊 {name}: {dataset['title']}")
                
        elif choice == '2':
            test_api_format()
            
        elif choice == '3':
            save_demo_data_to_file()
            
        elif choice == '4':
            generate_real_time_data()
            
        elif choice == '5':
            print("👋 再见!")
            break
            
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main()
