#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器缓存功能脚本
"""

import requests
import time
import json

# 服务器配置
SERVER_URL = "http://localhost:5007"

def test_cache_functionality():
    """测试缓存功能"""
    print("🧪 开始测试服务器缓存功能...")
    
    try:
        # 1. 检查服务器状态
        print("\n1️⃣ 检查服务器状态...")
        health_response = requests.get(f"{SERVER_URL}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print("❌ 服务器状态异常")
            return
        
        # 2. 获取初始缓存状态
        print("\n2️⃣ 获取初始缓存状态...")
        cache_status = requests.get(f"{SERVER_URL}/api/cache/status", timeout=10)
        if cache_status.status_code == 200:
            print("缓存状态:", json.dumps(cache_status.json(), indent=2, ensure_ascii=False))
        else:
            print("❌ 获取缓存状态失败")
            
        # 3. 测试表格数据的缓存 - 第一次请求
        print("\n3️⃣ 第一次请求表格数据（应该从数据源获取）...")
        start_time = time.time()
        table_response1 = requests.get(f"{SERVER_URL}/api/table-data/plate_info", timeout=30)
        first_request_time = time.time() - start_time
        
        if table_response1.status_code == 200:
            print(f"✅ 第一次请求成功，耗时: {first_request_time:.3f}秒")
        else:
            print("❌ 第一次请求失败")
            
        # 4. 测试表格数据的缓存 - 第二次请求（应该使用缓存）
        print("\n4️⃣ 第二次请求表格数据（应该使用缓存）...")
        start_time = time.time()
        table_response2 = requests.get(f"{SERVER_URL}/api/table-data/plate_info", timeout=30)
        second_request_time = time.time() - start_time
        
        if table_response2.status_code == 200:
            print(f"✅ 第二次请求成功，耗时: {second_request_time:.3f}秒")
            if second_request_time < first_request_time * 0.5:
                print("🚀 缓存生效！第二次请求明显更快")
            else:
                print("⚠️ 缓存可能未生效，或数据发生了变化")
        else:
            print("❌ 第二次请求失败")
            
        # 5. 测试股票数据缓存（包含文件依赖检测）
        print("\n5️⃣ 测试股票数据缓存...")
        start_time = time.time()
        stocks_response1 = requests.get(f"{SERVER_URL}/api/table-data/stocks?sectors=航运概念", timeout=30)
        stocks_first_time = time.time() - start_time
        
        if stocks_response1.status_code == 200:
            print(f"✅ 股票数据第一次请求成功，耗时: {stocks_first_time:.3f}秒")
            
            # 立即发起第二次请求
            start_time = time.time()
            stocks_response2 = requests.get(f"{SERVER_URL}/api/table-data/stocks?sectors=航运概念", timeout=30)
            stocks_second_time = time.time() - start_time
            
            if stocks_response2.status_code == 200:
                print(f"✅ 股票数据第二次请求成功，耗时: {stocks_second_time:.3f}秒")
                if stocks_second_time < stocks_first_time * 0.5:
                    print("🚀 股票数据缓存生效！")
                else:
                    print("⚠️ 股票数据缓存可能未生效")
            else:
                print("❌ 股票数据第二次请求失败")
        else:
            print("❌ 股票数据第一次请求失败")
            
        # 6. 测试图表数据的缓存
        print("\n6️⃣ 测试图表数据缓存...")
        start_time = time.time()
        chart_response1 = requests.get(f"{SERVER_URL}/api/chart-data/sector-line-chart_change", timeout=30)
        chart_first_time = time.time() - start_time
        
        if chart_response1.status_code == 200:
            print(f"✅ 图表数据第一次请求成功，耗时: {chart_first_time:.3f}秒")
            
            # 立即发起第二次请求
            start_time = time.time()
            chart_response2 = requests.get(f"{SERVER_URL}/api/chart-data/sector-line-chart_change", timeout=30)
            chart_second_time = time.time() - start_time
            
            if chart_response2.status_code == 200:
                print(f"✅ 图表数据第二次请求成功，耗时: {chart_second_time:.3f}秒")
                if chart_second_time < chart_first_time * 0.5:
                    print("🚀 图表缓存生效！")
                else:
                    print("⚠️ 图表缓存可能未生效")
            else:
                print("❌ 图表数据第二次请求失败")
        else:
            print("❌ 图表数据第一次请求失败")
            
        # 7. 测试涨停数据缓存
        print("\n7️⃣ 测试涨停数据缓存...")
        start_time = time.time()
        uplimit_response1 = requests.get(f"{SERVER_URL}/api/table-data/up_limit", timeout=30)
        uplimit_first_time = time.time() - start_time
        
        if uplimit_response1.status_code == 200:
            print(f"✅ 涨停数据第一次请求成功，耗时: {uplimit_first_time:.3f}秒")
            
            # 立即发起第二次请求
            start_time = time.time()
            uplimit_response2 = requests.get(f"{SERVER_URL}/api/table-data/up_limit", timeout=30)
            uplimit_second_time = time.time() - start_time
            
            if uplimit_response2.status_code == 200:
                print(f"✅ 涨停数据第二次请求成功，耗时: {uplimit_second_time:.3f}秒")
                if uplimit_second_time < uplimit_first_time * 0.5:
                    print("🚀 涨停数据缓存生效！")
                else:
                    print("⚠️ 涨停数据缓存可能未生效")
            else:
                print("❌ 涨停数据第二次请求失败")
        else:
            print("❌ 涨停数据第一次请求失败")
            
        # 8. 查看最终缓存状态
        print("\n8️⃣ 查看最终缓存状态...")
        cache_status_final = requests.get(f"{SERVER_URL}/api/cache/status", timeout=10)
        if cache_status_final.status_code == 200:
            final_stats = cache_status_final.json()
            print("最终缓存状态:", json.dumps(final_stats, indent=2, ensure_ascii=False))
            
            cache_stats = final_stats.get('cache_stats', {})
            cache_size = cache_stats.get('cache_size', 0)
            print(f"📊 缓存中共有 {cache_size} 个条目")
        else:
            print("❌ 获取最终缓存状态失败")
            
        # 9. 测试缓存清理
        print("\n9️⃣ 测试缓存清理...")
        clear_response = requests.post(f"{SERVER_URL}/api/cache/clear", timeout=10)
        if clear_response.status_code == 200:
            print("✅ 缓存清理成功")
            print(clear_response.json().get('message', ''))
        else:
            print("❌ 缓存清理失败")
            
        # 10. 验证缓存清理结果
        print("\n🔟 验证缓存清理结果...")
        cache_status_after_clear = requests.get(f"{SERVER_URL}/api/cache/status", timeout=10)
        if cache_status_after_clear.status_code == 200:
            cleared_stats = cache_status_after_clear.json()
            cache_size_after = cleared_stats.get('cache_stats', {}).get('cache_size', 0)
            print(f"📊 清理后缓存大小: {cache_size_after}")
            if cache_size_after == 0:
                print("✅ 缓存清理成功验证")
            else:
                print("⚠️ 缓存可能未完全清理")
        else:
            print("❌ 获取清理后缓存状态失败")
            
        print("\n🎉 缓存功能测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def performance_comparison_test():
    """性能对比测试"""
    print("\n📈 开始性能对比测试...")
    
    try:
        # 清理缓存
        requests.post(f"{SERVER_URL}/api/cache/clear", timeout=10)
        
        # 测试多次请求的性能差异
        endpoints = [
            "/api/table-data/sector-table",
            "/api/table-data/stocks-table", 
            "/api/chart-data/sector-line-chart_change",
            "/api/chart-data/sector-line-chart_uplimit",
        ]
        
        for endpoint in endpoints:
            print(f"\n🔬 测试端点: {endpoint}")
            times = []
            
            # 连续请求5次
            for i in range(5):
                start_time = time.time()
                response = requests.get(f"{SERVER_URL}{endpoint}", timeout=30)
                request_time = time.time() - start_time
                times.append(request_time)
                
                if response.status_code == 200:
                    print(f"请求 {i+1}: {request_time:.3f}秒")
                else:
                    print(f"请求 {i+1}: 失败 (状态码: {response.status_code})")
                    
                time.sleep(0.5)  # 短暂间隔
                
            if len(times) >= 2:
                print(f"📊 第一次请求: {times[0]:.3f}秒")
                print(f"📊 后续平均: {sum(times[1:])/(len(times)-1):.3f}秒")
                improvement = (times[0] - sum(times[1:])/(len(times)-1)) / times[0] * 100
                print(f"📊 性能提升: {improvement:.1f}%")
                
    except Exception as e:
        print(f"❌ 性能测试过程中出现错误: {e}")

if __name__ == "__main__":
    print("🚀 启动服务器缓存测试工具")
    
    # 基本功能测试
    test_cache_functionality()
    
    # 性能对比测试
    performance_comparison_test()
    
    print("\n✨ 所有测试完成")
