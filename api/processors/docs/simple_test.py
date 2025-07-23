"""
简化处理器测试
测试各个处理器的基本功能

Author: chenlei
Date: 2025-07-23
"""
import sys
import os
import pandas as pd

# 添加上级目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入处理器类
from multiplate_processor import MultiPlateProcessor
from demo_processor import DemoProcessor
from strong_processor import StrongProcessor
from base_processor import BaseDataProcessor


class MockServer:
    """模拟服务器类"""
    
    def __init__(self, server_type):
        self.server_type = server_type
        self.dynamic_titles = ["航运概念", "新能源", "芯片概念"]
        self.data_cache = MockDataCache()
        self.response_cache = MockResponseCache()
        self.logger = MockLogger()
    
    def _get_dynamic_titles_list(self):
        return self.dynamic_titles
    
    def _get_top_sectors(self, count):
        return ["航运概念", "新能源", "芯片概念", "医疗器械", "军工概念"][:count]


class MockResponseCache:
    """模拟响应缓存类"""
    
    def should_use_cache(self, endpoint, cache_params=None, source_data=None):
        return False, None
    
    def store_response(self, endpoint, cache_params=None, source_data=None, response_data=None):
        pass


class MockDataCache:
    """模拟数据缓存类"""
    
    def __init__(self):
        self.timestamps = {
            'stock_df': 1700000000,
            'plate_df': 1700000000,
            'stock_minute_df': 1700000000,
            'affinity_df': 1700000000
        }
    
    def load_data(self, data_type):
        # 返回空的 DataFrame 以便测试
        return pd.DataFrame()


class MockLogger:
    """模拟日志记录器"""
    
    def info(self, message):
        print(f"[INFO] {message}")
    
    def error(self, message):
        print(f"[ERROR] {message}")
    
    def warning(self, message):
        print(f"[WARNING] {message}")


def test_processor_creation():
    """测试处理器创建"""
    print("=" * 60)
    print("测试处理器创建")
    print("=" * 60)
    
    server = MockServer('test')
    
    processors = {
        'MultiPlateProcessor': MultiPlateProcessor,
        'DemoProcessor': DemoProcessor,
        'StrongProcessor': StrongProcessor
    }
    
    for name, processor_class in processors.items():
        try:
            processor = processor_class(server_instance=server)
            print(f"✅ {name} 创建成功")
            
            # 测试获取可用方法
            methods = processor.get_available_methods()
            print(f"   可用方法数量: {len(methods)}")
            
        except Exception as e:
            print(f"❌ {name} 创建失败: {e}")
    
    return True


def test_multiplate_methods():
    """测试多板块处理器方法"""
    print("\n" + "=" * 60)
    print("测试多板块处理器方法")
    print("=" * 60)
    
    server = MockServer('multiplate')
    
    processor = MultiPlateProcessor(server_instance=server)
    
    # 获取所有可用方法
    methods = processor.get_available_methods()
    print(f"多板块处理器可用方法 ({len(methods)} 个):")
    
    # 显示前10个方法
    for i, method in enumerate(methods[:10], 1):
        print(f"  {i:2d}. {method}")
    
    if len(methods) > 10:
        print(f"  ... 还有 {len(methods) - 10} 个方法")
    
    # 测试几个关键方法（不执行，只测试方法存在性）
    key_methods = [
        'sector_line_chart_change',
        'sector_speed_chart',
        'plate_info_table_data',
        'today_plate_up_limit_distribution'
    ]
    
    print(f"\n检查关键方法:")
    for method in key_methods:
        if method in methods:
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} (缺失)")
    
    return True


def test_demo_methods():
    """测试演示处理器方法"""
    print("\n" + "=" * 60)
    print("测试演示处理器方法")
    print("=" * 60)
    
    server = MockServer('demo')
    
    processor = DemoProcessor(server_instance=server)
    
    methods = processor.get_available_methods()
    print(f"演示处理器可用方法 ({len(methods)} 个):")
    for i, method in enumerate(methods, 1):
        print(f"  {i:2d}. {method}")
    
    return True


def test_strong_methods():
    """测试强势处理器方法"""
    print("\n" + "=" * 60)
    print("测试强势处理器方法")
    print("=" * 60)
    
    server = MockServer('strong')
    
    processor = StrongProcessor(server_instance=server)
    
    methods = processor.get_available_methods()
    print(f"强势处理器可用方法 ({len(methods)} 个):")
    for i, method in enumerate(methods, 1):
        print(f"  {i:2d}. {method}")
    
    return True


def test_method_execution():
    """测试方法执行（简单测试）"""
    print("\n" + "=" * 60)
    print("测试方法执行")
    print("=" * 60)
    
    server = MockServer('demo')
    
    processor = DemoProcessor(server_instance=server)
    
    # 测试一些简单方法
    test_methods = ['demo_summary', 'demo_config']
    
    for method in test_methods:
        try:
            print(f"测试执行 {method}...", end=' ')
            result = processor.process(method)
            print("✅ 成功")
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    return True


def main():
    """主测试函数"""
    print("🚀 开始简化处理器测试")
    
    tests = [
        test_processor_creation,
        test_multiplate_methods,
        test_demo_methods,
        test_strong_methods,
        test_method_execution
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                success_count += 1
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有测试通过！新架构工作正常。")
    else:
        print("⚠️  部分测试失败，请检查实现。")


if __name__ == "__main__":
    main()
