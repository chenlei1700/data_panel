#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统性能监控工具 - 监控后端服务的性能指标
System Performance Monitor - Monitor backend service performance metrics

Author: chenlei
"""

import time
import psutil
import json
import threading
import sys
from pathlib import Path
from datetime import datetime
import requests
from collections import deque
import signal


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, services_config=None):
        """初始化监控器"""
        self.services = services_config or {
            5001: "主股票数据服务",
            5002: "强势股票数据服务", 
            5003: "多板块数据服务"
        }
        
        self.monitoring = False
        self.data_history = deque(maxlen=100)  # 保留最近100条记录
        self.monitor_thread = None
        
        # 监控间隔（秒）
        self.interval = 5
        
        # 性能阈值
        self.thresholds = {
            'cpu_warning': 70,     # CPU使用率警告阈值
            'cpu_critical': 90,    # CPU使用率严重阈值
            'memory_warning': 80,  # 内存使用率警告阈值
            'memory_critical': 95, # 内存使用率严重阈值
            'response_warning': 2, # 响应时间警告阈值(秒)
            'response_critical': 5 # 响应时间严重阈值(秒)
        }
    
    def get_system_metrics(self):
        """获取系统指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_total': memory.total,
                'disk_percent': disk.percent,
                'disk_used': disk.used,
                'disk_total': disk.total
            }
        except Exception as e:
            return {'error': f"获取系统指标失败: {e}"}
    
    def get_service_metrics(self, port):
        """获取单个服务的指标"""
        try:
            start_time = time.time()
            
            # 健康检查
            health_response = requests.get(
                f"http://localhost:{port}/health", 
                timeout=10
            )
            health_time = time.time() - start_time
            
            # API响应时间测试
            start_time = time.time()
            api_response = requests.get(
                f"http://localhost:{port}/api/stock-data", 
                timeout=10
            )
            api_time = time.time() - start_time
            
            return {
                'port': port,
                'name': self.services.get(port, f"服务{port}"),
                'status': 'healthy' if health_response.status_code == 200 else 'unhealthy',
                'health_response_time': health_time,
                'api_response_time': api_time,
                'health_status_code': health_response.status_code,
                'api_status_code': api_response.status_code
            }
            
        except requests.exceptions.ConnectionError:
            return {
                'port': port,
                'name': self.services.get(port, f"服务{port}"),
                'status': 'offline',
                'error': '连接失败'
            }
        except requests.exceptions.Timeout:
            return {
                'port': port,
                'name': self.services.get(port, f"服务{port}"),
                'status': 'timeout',
                'error': '响应超时'
            }
        except Exception as e:
            return {
                'port': port,
                'name': self.services.get(port, f"服务{port}"),
                'status': 'error',
                'error': str(e)
            }
    
    def collect_metrics(self):
        """收集所有指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_metrics(),
            'services': []
        }
        
        # 收集所有服务的指标
        for port in self.services.keys():
            service_metrics = self.get_service_metrics(port)
            metrics['services'].append(service_metrics)
        
        return metrics
    
    def analyze_metrics(self, metrics):
        """分析指标并生成警告"""
        alerts = []
        
        # 系统指标分析
        system = metrics.get('system', {})
        if 'cpu_percent' in system:
            cpu = system['cpu_percent']
            if cpu >= self.thresholds['cpu_critical']:
                alerts.append(f"🔴 CPU使用率严重告警: {cpu:.1f}%")
            elif cpu >= self.thresholds['cpu_warning']:
                alerts.append(f"🟡 CPU使用率警告: {cpu:.1f}%")
        
        if 'memory_percent' in system:
            memory = system['memory_percent']
            if memory >= self.thresholds['memory_critical']:
                alerts.append(f"🔴 内存使用率严重告警: {memory:.1f}%")
            elif memory >= self.thresholds['memory_warning']:
                alerts.append(f"🟡 内存使用率警告: {memory:.1f}%")
        
        # 服务指标分析
        for service in metrics.get('services', []):
            name = service.get('name', service.get('port', 'Unknown'))
            
            if service.get('status') == 'offline':
                alerts.append(f"🔴 服务离线: {name}")
            elif service.get('status') == 'timeout':
                alerts.append(f"🟠 服务响应超时: {name}")
            elif service.get('status') == 'error':
                alerts.append(f"❌ 服务错误: {name} - {service.get('error', '')}")
            else:
                # 检查响应时间
                api_time = service.get('api_response_time', 0)
                if api_time >= self.thresholds['response_critical']:
                    alerts.append(f"🔴 API响应时间严重: {name} - {api_time:.2f}s")
                elif api_time >= self.thresholds['response_warning']:
                    alerts.append(f"🟡 API响应时间警告: {name} - {api_time:.2f}s")
        
        return alerts
    
    def display_metrics(self, metrics):
        """显示指标"""
        print(f"\n📊 性能监控报告 - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # 系统指标
        system = metrics.get('system', {})
        if 'error' not in system:
            print(f"🖥️  系统状态:")
            print(f"   CPU使用率: {system.get('cpu_percent', 0):.1f}%")
            print(f"   内存使用率: {system.get('memory_percent', 0):.1f}%")
            print(f"   磁盘使用率: {system.get('disk_percent', 0):.1f}%")
        else:
            print(f"❌ 系统指标获取失败: {system['error']}")
        
        # 服务状态
        print(f"\n🔧 服务状态:")
        for service in metrics.get('services', []):
            name = service.get('name', service.get('port', 'Unknown'))
            status = service.get('status', 'unknown')
            
            if status == 'healthy':
                api_time = service.get('api_response_time', 0)
                health_time = service.get('health_response_time', 0)
                print(f"   ✅ {name}: 健康 (API:{api_time*1000:.0f}ms, Health:{health_time*1000:.0f}ms)")
            elif status == 'offline':
                print(f"   🔴 {name}: 离线")
            elif status == 'timeout':
                print(f"   🟠 {name}: 超时")
            else:
                error_msg = service.get('error', 'Unknown error')
                print(f"   ❌ {name}: 错误 - {error_msg}")
        
        # 显示警告
        alerts = self.analyze_metrics(metrics)
        if alerts:
            print(f"\n⚠️  警告信息:")
            for alert in alerts:
                print(f"   {alert}")
        else:
            print(f"\n✅ 所有指标正常")
    
    def monitor_loop(self):
        """监控循环"""
        print(f"🚀 开始性能监控，监控间隔: {self.interval}秒")
        print("按 Ctrl+C 停止监控")
        
        while self.monitoring:
            try:
                metrics = self.collect_metrics()
                self.data_history.append(metrics)
                
                self.display_metrics(metrics)
                
                # 等待下一次监控
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                time.sleep(self.interval)
    
    def start_monitoring(self):
        """启动监控"""
        if self.monitoring:
            print("⚠️  监控已在运行中")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("\n🛑 监控已停止")
    
    def export_data(self, filename=None):
        """导出监控数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_data_{timestamp}.json"
        
        data = {
            'export_time': datetime.now().isoformat(),
            'data_points': len(self.data_history),
            'monitoring_interval': self.interval,
            'thresholds': self.thresholds,
            'services': self.services,
            'history': list(self.data_history)
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 监控数据已导出到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return None
    
    def generate_summary_report(self):
        """生成摘要报告"""
        if not self.data_history:
            print("📊 暂无监控数据")
            return
        
        print(f"\n📋 性能监控摘要报告")
        print("=" * 50)
        
        # 数据概览
        print(f"📈 数据概览:")
        print(f"   监控时长: {len(self.data_history) * self.interval}秒")
        print(f"   数据点数: {len(self.data_history)}")
        print(f"   监控间隔: {self.interval}秒")
        
        # 系统性能统计
        cpu_values = []
        memory_values = []
        
        for data in self.data_history:
            system = data.get('system', {})
            if 'cpu_percent' in system:
                cpu_values.append(system['cpu_percent'])
            if 'memory_percent' in system:
                memory_values.append(system['memory_percent'])
        
        if cpu_values:
            print(f"\n🖥️  系统性能统计:")
            print(f"   CPU使用率 - 平均:{sum(cpu_values)/len(cpu_values):.1f}% 最高:{max(cpu_values):.1f}% 最低:{min(cpu_values):.1f}%")
        
        if memory_values:
            print(f"   内存使用率 - 平均:{sum(memory_values)/len(memory_values):.1f}% 最高:{max(memory_values):.1f}% 最低:{min(memory_values):.1f}%")
        
        # 服务可用性统计
        service_stats = {}
        for data in self.data_history:
            for service in data.get('services', []):
                port = service.get('port')
                name = service.get('name', f"服务{port}")
                
                if name not in service_stats:
                    service_stats[name] = {'total': 0, 'healthy': 0, 'response_times': []}
                
                service_stats[name]['total'] += 1
                if service.get('status') == 'healthy':
                    service_stats[name]['healthy'] += 1
                    api_time = service.get('api_response_time')
                    if api_time is not None:
                        service_stats[name]['response_times'].append(api_time)
        
        if service_stats:
            print(f"\n🔧 服务可用性统计:")
            for name, stats in service_stats.items():
                availability = (stats['healthy'] / stats['total']) * 100
                avg_response = sum(stats['response_times']) / len(stats['response_times']) if stats['response_times'] else 0
                print(f"   {name}: 可用性{availability:.1f}% 平均响应{avg_response*1000:.0f}ms")


def signal_handler(signum, frame):
    """信号处理器"""
    print("\n\n🛑 收到停止信号，正在优雅关闭...")
    sys.exit(0)


def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("📊 系统性能监控工具")
    print("=" * 50)
    
    # 创建监控器
    monitor = PerformanceMonitor()
    
    try:
        # 显示初始选项
        print("\n选择操作:")
        print("1. 实时监控")
        print("2. 单次检查") 
        print("3. 配置监控参数")
        print()
        
        choice = input("请输入选择 (1-3, 默认1): ").strip() or "1"
        
        if choice == "1":
            # 实时监控
            monitor.start_monitoring()
            
            try:
                # 保持主线程运行
                while monitor.monitoring:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                monitor.stop_monitoring()
                monitor.generate_summary_report()
                
                # 询问是否导出数据
                export = input("\n是否导出监控数据? (y/N): ").strip().lower()
                if export == 'y':
                    monitor.export_data()
        
        elif choice == "2":
            # 单次检查
            print("\n🔍 执行单次性能检查...")
            metrics = monitor.collect_metrics()
            monitor.display_metrics(metrics)
            
            alerts = monitor.analyze_metrics(metrics)
            if alerts:
                print(f"\n⚠️  发现 {len(alerts)} 个警告")
            else:
                print(f"\n✅ 系统状态良好")
        
        elif choice == "3":
            # 配置参数
            print("\n⚙️  监控参数配置:")
            print(f"当前监控间隔: {monitor.interval}秒")
            
            new_interval = input("新的监控间隔 (秒, 默认不修改): ").strip()
            if new_interval.isdigit():
                monitor.interval = int(new_interval)
                print(f"✅ 监控间隔已设置为 {monitor.interval}秒")
            
            print("\n配置完成，可以重新运行程序使用新配置。")
        
        else:
            print("❌ 无效选择")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 监控程序异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
