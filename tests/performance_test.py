#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能和负载测试脚本 - 测试系统在高负载下的表现
Performance and Load Testing - Test system performance under high load

Author: chenlei
"""

import asyncio
import aiohttp
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path


class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self, base_url="http://localhost", ports=[5001, 5002, 5003]):
        self.base_url = base_url
        self.ports = ports
        self.results = {}
    
    async def single_request(self, session, url, endpoint):
        """单个请求测试"""
        start_time = time.time()
        try:
            async with session.get(f"{url}{endpoint}", timeout=10) as response:
                await response.text()
                end_time = time.time()
                return {
                    'success': response.status == 200,
                    'response_time': end_time - start_time,
                    'status_code': response.status
                }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'response_time': end_time - start_time,
                'error': str(e)
            }
    
    async def load_test(self, url, endpoint, concurrent_users=10, requests_per_user=5):
        """负载测试"""
        print(f"🚀 开始负载测试: {url}{endpoint}")
        print(f"   并发用户: {concurrent_users}, 每用户请求: {requests_per_user}")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # 创建并发请求任务
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    task = self.single_request(session, url, endpoint)
                    tasks.append(task)
            
            # 执行所有请求
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # 分析结果
            return self.analyze_results(results, end_time - start_time, concurrent_users, requests_per_user)
    
    def analyze_results(self, results, total_time, concurrent_users, requests_per_user):
        """分析测试结果"""
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_requests]
        
        analysis = {
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(results) * 100,
            'total_time': total_time,
            'requests_per_second': len(results) / total_time,
            'concurrent_users': concurrent_users,
            'requests_per_user': requests_per_user
        }
        
        if response_times:
            analysis.update({
                'avg_response_time': statistics.mean(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'median_response_time': statistics.median(response_times)
            })
            
            if len(response_times) > 1:
                analysis['std_response_time'] = statistics.stdev(response_times)
        
        return analysis
    
    def print_results(self, endpoint, analysis):
        """打印测试结果"""
        print(f"\n📊 {endpoint} 测试结果:")
        print(f"   总请求数: {analysis['total_requests']}")
        print(f"   成功请求: {analysis['successful_requests']}")
        print(f"   失败请求: {analysis['failed_requests']}")
        print(f"   成功率: {analysis['success_rate']:.2f}%")
        print(f"   总耗时: {analysis['total_time']:.2f}秒")
        print(f"   请求/秒: {analysis['requests_per_second']:.2f}")
        
        if 'avg_response_time' in analysis:
            print(f"   平均响应时间: {analysis['avg_response_time']*1000:.2f}ms")
            print(f"   最快响应时间: {analysis['min_response_time']*1000:.2f}ms")
            print(f"   最慢响应时间: {analysis['max_response_time']*1000:.2f}ms")
            print(f"   中位响应时间: {analysis['median_response_time']*1000:.2f}ms")


class EndpointStressTest:
    """端点压力测试"""
    
    def __init__(self):
        self.test_endpoints = [
            "/api/stock-data",
            "/api/plate-data",
            "/api/chart-data",
            "/health"
        ]
    
    async def run_stress_test(self, base_url, port):
        """运行单个服务的压力测试"""
        print(f"\n🔥 压力测试 - 端口 {port}")
        print("=" * 40)
        
        performance_suite = PerformanceTestSuite()
        url = f"{base_url}:{port}"
        
        results = {}
        
        for endpoint in self.test_endpoints:
            try:
                # 轻负载测试
                light_result = await performance_suite.load_test(
                    url, endpoint, concurrent_users=5, requests_per_user=3
                )
                
                # 中等负载测试
                medium_result = await performance_suite.load_test(
                    url, endpoint, concurrent_users=10, requests_per_user=5
                )
                
                # 高负载测试
                heavy_result = await performance_suite.load_test(
                    url, endpoint, concurrent_users=20, requests_per_user=10
                )
                
                results[endpoint] = {
                    'light_load': light_result,
                    'medium_load': medium_result,
                    'heavy_load': heavy_result
                }
                
                # 打印结果
                performance_suite.print_results(f"{endpoint} (轻负载)", light_result)
                performance_suite.print_results(f"{endpoint} (中负载)", medium_result)
                performance_suite.print_results(f"{endpoint} (重负载)", heavy_result)
                
                # 短暂休息避免过载
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ 端点 {endpoint} 测试失败: {e}")
                results[endpoint] = {'error': str(e)}
        
        return results


async def run_performance_tests():
    """运行完整的性能测试套件"""
    print("⚡ 性能和负载测试套件")
    print("=" * 50)
    print()
    
    stress_tester = EndpointStressTest()
    all_results = {}
    
    # 测试所有服务端口
    ports = [5001, 5002, 5003]
    base_url = "http://localhost"
    
    for port in ports:
        try:
            # 首先检查服务是否可用
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{base_url}:{port}/health", timeout=5) as response:
                        if response.status != 200:
                            print(f"⚠️  端口 {port} 服务健康检查失败")
                            continue
                except:
                    print(f"❌ 端口 {port} 服务不可用，跳过测试")
                    continue
            
            # 运行压力测试
            results = await stress_tester.run_stress_test(base_url, port)
            all_results[port] = results
            
        except Exception as e:
            print(f"❌ 端口 {port} 测试失败: {e}")
            all_results[port] = {'error': str(e)}
    
    # 生成测试报告
    generate_performance_report(all_results)
    
    return all_results


def generate_performance_report(results):
    """生成性能测试报告"""
    print("\n📋 性能测试报告摘要")
    print("=" * 50)
    
    for port, port_results in results.items():
        if 'error' in port_results:
            print(f"❌ 端口 {port}: 测试失败 - {port_results['error']}")
            continue
        
        print(f"\n🔌 端口 {port} 性能摘要:")
        
        for endpoint, endpoint_results in port_results.items():
            if 'error' in endpoint_results:
                print(f"   ❌ {endpoint}: 测试失败")
                continue
            
            heavy_load = endpoint_results.get('heavy_load', {})
            if 'success_rate' in heavy_load:
                print(f"   📊 {endpoint}:")
                print(f"      成功率: {heavy_load['success_rate']:.1f}%")
                print(f"      RPS: {heavy_load['requests_per_second']:.1f}")
                if 'avg_response_time' in heavy_load:
                    print(f"      平均响应: {heavy_load['avg_response_time']*1000:.1f}ms")
    
    # 保存详细报告到文件
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"performance_report_{timestamp}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"⚠️  保存报告失败: {e}")


def main():
    """主函数"""
    print("🚀 启动性能测试...")
    print()
    
    try:
        # 运行异步性能测试
        results = asyncio.run(run_performance_tests())
        
        print("\n✅ 性能测试完成")
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
