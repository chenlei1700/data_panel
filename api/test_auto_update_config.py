#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新配置系统测试脚本
Auto Update Configuration System Test

Author: chenlei
"""

import os
import sys
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import threading

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from server_config import config_manager, apply_quick_config, QUICK_CONFIGS


class ConfigSystemTester:
    """配置系统测试器"""
    
    def __init__(self):
        self.test_results = []
        self.server_port = 5008
        self.base_url = f"http://localhost:{self.server_port}"
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name} {message}")
    
    def test_config_manager(self):
        """测试配置管理器"""
        print("\n🔧 测试配置管理器")
        print("-" * 30)
        
        try:
            # 测试获取服务器配置
            config = config_manager.get_server_config("multiplate")
            self.log_test("获取服务器配置", bool(config))
            
            # 测试更新配置
            original_interval = config.get("auto_update_config", {}).get("interval", 30)
            new_interval = 45
            
            config_manager.update_server_config("multiplate", {
                "auto_update": {"interval": new_interval}
            })
            
            updated_config = config_manager.get_server_config("multiplate")
            actual_interval = updated_config.get("auto_update_config", {}).get("interval", 30)
            
            self.log_test("更新配置", actual_interval == new_interval, 
                         f"期望间隔: {new_interval}, 实际间隔: {actual_interval}")
            
            # 恢复原始配置
            config_manager.update_server_config("multiplate", {
                "auto_update": {"interval": original_interval}
            })
            
            # 测试切换自动更新状态
            original_status = config_manager.is_auto_update_enabled("multiplate")
            new_status = config_manager.toggle_server_auto_update("multiplate")
            restored_status = config_manager.toggle_server_auto_update("multiplate")
            
            self.log_test("切换自动更新状态", 
                         new_status != original_status and restored_status == original_status)
            
            # 测试快速配置
            apply_quick_config("multiplate", "demo")
            demo_config = config_manager.get_server_config("multiplate")
            demo_interval = demo_config.get("auto_update_config", {}).get("interval")
            
            self.log_test("应用快速配置", demo_interval == 15, 
                         f"演示模式间隔应为15秒，实际: {demo_interval}")
            
            # 恢复正常配置
            apply_quick_config("multiplate", "normal")
            
        except Exception as e:
            self.log_test("配置管理器测试", False, f"异常: {e}")
    
    def test_server_api(self):
        """测试服务器API"""
        print("\n🌐 测试服务器API")
        print("-" * 20)
        
        # 等待一下确保服务器启动
        time.sleep(2)
        
        try:
            # 测试健康检查
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.log_test("健康检查API", response.status_code == 200)
            
            # 测试自动更新状态API
            response = requests.get(f"{self.base_url}/api/auto-update/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("自动更新状态API", data.get("status") == "success")
            else:
                self.log_test("自动更新状态API", False, f"HTTP {response.status_code}")
            
            # 测试自动更新配置API
            response = requests.get(f"{self.base_url}/api/auto-update/config", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("自动更新配置API", data.get("status") == "success")
            else:
                self.log_test("自动更新配置API", False, f"HTTP {response.status_code}")
            
            # 测试配置更新API
            test_config = {"interval": 20, "max_clients": 25}
            response = requests.put(f"{self.base_url}/api/auto-update/config", 
                                  json=test_config, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("配置更新API", data.get("status") == "success")
                
                # 验证配置是否生效
                time.sleep(1)
                verify_response = requests.get(f"{self.base_url}/api/auto-update/config", timeout=5)
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    config_data = verify_data.get("config", {})
                    self.log_test("配置更新验证", 
                                config_data.get("interval") == 20 and 
                                config_data.get("max_clients") == 25)
            else:
                self.log_test("配置更新API", False, f"HTTP {response.status_code}")
            
            # 测试开关切换API
            response = requests.post(f"{self.base_url}/api/auto-update/toggle", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("开关切换API", data.get("status") == "success")
            else:
                self.log_test("开关切换API", False, f"HTTP {response.status_code}")
            
            # 测试缓存状态API
            response = requests.get(f"{self.base_url}/api/cache/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("缓存状态API", data.get("status") == "success")
            else:
                self.log_test("缓存状态API", False, f"HTTP {response.status_code}")
            
            # 测试缓存清理API
            response = requests.post(f"{self.base_url}/api/cache/clear", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("缓存清理API", data.get("status") == "success")
            else:
                self.log_test("缓存清理API", False, f"HTTP {response.status_code}")
                
        except requests.ConnectionError:
            self.log_test("服务器连接", False, "无法连接到服务器，请确认服务器已启动")
        except Exception as e:
            self.log_test("API测试", False, f"异常: {e}")
    
    def test_sse_connection(self):
        """测试SSE连接"""
        print("\n📡 测试SSE连接")
        print("-" * 15)
        
        try:
            import sseclient
            
            # 创建SSE客户端
            response = requests.get(f"{self.base_url}/api/dashboard/updates", 
                                  stream=True, timeout=10)
            
            if response.status_code == 200:
                self.log_test("SSE连接建立", True)
                
                # 读取几个事件
                client = sseclient.SSEClient(response)
                events_received = 0
                
                for event in client.events():
                    events_received += 1
                    if events_received >= 3:  # 接收3个事件就停止
                        break
                
                self.log_test("SSE事件接收", events_received > 0, 
                            f"收到 {events_received} 个事件")
            else:
                self.log_test("SSE连接建立", False, f"HTTP {response.status_code}")
                
        except ImportError:
            self.log_test("SSE测试", False, "需要安装 sseclient 库: pip install sseclient-py")
        except Exception as e:
            self.log_test("SSE测试", False, f"异常: {e}")
    
    def test_config_templates(self):
        """测试配置模板"""
        print("\n📋 测试配置模板")
        print("-" * 18)
        
        try:
            # 测试所有预定义配置模板
            for template_name, expected_config in QUICK_CONFIGS.items():
                apply_quick_config("multiplate", template_name)
                
                # 获取应用后的配置
                applied_config = config_manager.get_server_config("multiplate")
                auto_update_config = applied_config.get("auto_update_config", {})
                
                # 验证关键配置是否匹配
                expected_enabled = expected_config.get("enabled", True)
                actual_enabled = auto_update_config.get("enabled", True)
                
                expected_interval = expected_config.get("interval")
                actual_interval = auto_update_config.get("interval")
                
                template_ok = (expected_enabled == actual_enabled and
                             (expected_interval is None or expected_interval == actual_interval))
                
                self.log_test(f"配置模板 {template_name}", template_ok,
                            f"启用: {actual_enabled}, 间隔: {actual_interval}")
            
            # 恢复正常配置
            apply_quick_config("multiplate", "normal")
            
        except Exception as e:
            self.log_test("配置模板测试", False, f"异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始自动更新配置系统测试")
        print("=" * 50)
        
        self.test_config_manager()
        self.test_config_templates()
        self.test_server_api()
        self.test_sse_connection()
        
        # 输出测试总结
        print("\n📊 测试总结")
        print("=" * 20)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"通过率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过！配置系统工作正常。")
        else:
            print("\n⚠️ 部分测试失败，请检查相关功能。")
            
            print("\n失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed == total


def main():
    """主函数"""
    print("🔧 自动更新配置系统测试工具")
    
    import argparse
    parser = argparse.ArgumentParser(description='测试自动更新配置系统')
    parser.add_argument('--port', type=int, default=5008, help='服务器端口')
    parser.add_argument('--skip-server', action='store_true', help='跳过服务器API测试')
    parser.add_argument('--skip-sse', action='store_true', help='跳过SSE测试')
    
    args = parser.parse_args()
    
    tester = ConfigSystemTester()
    tester.server_port = args.port
    tester.base_url = f"http://localhost:{args.port}"
    
    # 运行配置管理器和模板测试（不需要服务器运行）
    tester.test_config_manager()
    tester.test_config_templates()
    
    if not args.skip_server:
        print("\n📌 注意: 服务器API测试需要服务器运行在端口", args.port)
        print("请在另一个终端运行:")
        print(f"python server_launcher.py start --server multiplate --port {args.port}")
        
        input("按回车键继续服务器测试...")
        
        tester.test_server_api()
        
        if not args.skip_sse:
            tester.test_sse_connection()
    
    # 输出最终结果
    passed = sum(1 for result in tester.test_results if result["success"])
    total = len(tester.test_results)
    
    print(f"\n📊 最终测试结果: {passed}/{total} 通过")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
