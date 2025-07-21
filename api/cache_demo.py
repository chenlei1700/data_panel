#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基类防重复缓存机制演示

展示了如何在子类中使用基类的缓存功能，无需外部依赖
"""

import time
import hashlib
import json
from typing import Dict, Any, Optional, Tuple


class BaseResponseCache:
    """基础响应缓存类演示"""
    
    def __init__(self, max_cache_size=100):
        self.cache = {}
        self.hash_cache = {}  
        self.access_times = {}
        self.max_cache_size = max_cache_size
        
    def _generate_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """生成缓存键"""
        if params:
            param_str = json.dumps(params, sort_keys=True, default=str)
            return f"{endpoint}:{param_str}"
        return endpoint
        
    def _calculate_data_hash(self, data: Any) -> str:
        """计算数据的哈希值"""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode('utf-8')).hexdigest()
        except Exception as e:
            print(f"计算哈希失败: {e}")
            return str(time.time())
            
    def should_use_cache(self, endpoint: str, params: Optional[Dict] = None, 
                        current_data: Optional[Any] = None) -> Tuple[bool, Optional[Any]]:
        """检查是否应该使用缓存的响应"""
        cache_key = self._generate_cache_key(endpoint, params)
        
        if cache_key not in self.cache:
            return False, None
            
        if current_data is None:
            self.access_times[cache_key] = time.time()
            return True, self.cache[cache_key]
            
        current_hash = self._calculate_data_hash(current_data)
        cached_hash = self.hash_cache.get(cache_key)
        
        if current_hash == cached_hash:
            print(f"✅ 数据未变化，使用缓存: {endpoint}")
            self.access_times[cache_key] = time.time()
            return True, self.cache[cache_key]
        else:
            print(f"🔄 数据已变化，需要重新计算: {endpoint}")
            return False, None
            
    def store_response(self, endpoint: str, params: Optional[Dict] = None,
                      source_data: Optional[Any] = None, response_data: Optional[Any] = None):
        """存储响应到缓存"""
        cache_key = self._generate_cache_key(endpoint, params)
        
        if source_data is not None:
            data_hash = self._calculate_data_hash(source_data)
            self.hash_cache[cache_key] = data_hash
            
        if response_data is not None:
            self.cache[cache_key] = response_data
            self.access_times[cache_key] = time.time()
            print(f"💾 响应已缓存: {endpoint}")


class DemoStockServer:
    """演示股票服务器"""
    
    def __init__(self):
        self.response_cache = BaseResponseCache()
        self.data_timestamps = {}
        
        # 模拟数据
        self.mock_data = {
            'plate_df': {
                'timestamp': time.time(),
                'data': [
                    {'板块名': '科技板块', '涨幅': 2.5, '时间': '09:30'},
                    {'板块名': '医药板块', '涨幅': -1.2, '时间': '09:30'},
                    {'板块名': '新能源', '涨幅': 3.8, '时间': '09:30'}
                ]
            }
        }
    
    def with_cache_protection(self, endpoint: str, handler_func, source_data_func=None):
        """缓存保护装饰器"""
        def wrapper():
            # 获取源数据用于比较
            source_data = None
            if source_data_func:
                source_data = source_data_func()
            
            # 检查缓存
            should_cache, cached_response = self.response_cache.should_use_cache(
                endpoint, None, source_data
            )
            
            if should_cache and cached_response:
                return cached_response
            
            # 执行实际处理
            print(f"🔧 执行数据处理: {endpoint}")
            response_data = handler_func()
            
            # 存储到缓存
            self.response_cache.store_response(endpoint, None, source_data, response_data)
            
            return response_data
        
        return wrapper
    
    def get_source_data_for_plate_info(self):
        """获取板块信息的源数据"""
        return {
            'timestamp': self.mock_data['plate_df']['timestamp'],
            'data_count': len(self.mock_data['plate_df']['data']),
            'data_hash': str(hash(str(self.mock_data['plate_df']['data'])))
        }
    
    def _get_plate_info_raw(self):
        """原始的板块信息获取方法"""
        # 模拟耗时操作
        print("⏳ 模拟数据处理...")
        time.sleep(0.5)
        
        return {
            'columns': ['板块名', '涨幅', '时间'],
            'data': self.mock_data['plate_df']['data'],
            'processed_at': time.time()
        }
    
    def get_plate_info_with_cache(self):
        """带缓存保护的板块信息获取"""
        protected_handler = self.with_cache_protection(
            "/api/table-data/plate_info",
            self._get_plate_info_raw,
            self.get_source_data_for_plate_info
        )
        return protected_handler()
    
    def get_plate_info_without_cache(self):
        """不带缓存的板块信息获取"""
        return self._get_plate_info_raw()
    
    def simulate_data_change(self):
        """模拟数据变化"""
        self.mock_data['plate_df']['timestamp'] = time.time()
        self.mock_data['plate_df']['data'][0]['涨幅'] = round(
            self.mock_data['plate_df']['data'][0]['涨幅'] + 0.1, 1
        )
        print("📊 模拟数据已更新")


def demo():
    """演示缓存机制"""
    print("🚀 基类防重复缓存机制演示")
    print("=" * 50)
    
    server = DemoStockServer()
    
    print("\n1. 首次请求（无缓存）")
    start_time = time.time()
    result1 = server.get_plate_info_with_cache()
    print(f"⏱️ 耗时: {time.time() - start_time:.2f}秒")
    print(f"📋 结果: {result1['data']}")
    
    print("\n2. 再次请求（使用缓存）")
    start_time = time.time()
    result2 = server.get_plate_info_with_cache()
    print(f"⏱️ 耗时: {time.time() - start_time:.2f}秒")
    print(f"📋 结果: {result2['data']}")
    
    print("\n3. 模拟数据变化")
    server.simulate_data_change()
    
    print("\n4. 数据变化后请求（重新计算）")
    start_time = time.time()
    result3 = server.get_plate_info_with_cache()
    print(f"⏱️ 耗时: {time.time() - start_time:.2f}秒")
    print(f"📋 结果: {result3['data']}")
    
    print("\n5. 再次请求变化后数据（使用新缓存）")
    start_time = time.time()
    result4 = server.get_plate_info_with_cache()
    print(f"⏱️ 耗时: {time.time() - start_time:.2f}秒")
    print(f"📋 结果: {result4['data']}")
    
    print("\n6. 对比：不使用缓存的请求")
    start_time = time.time()
    result5 = server.get_plate_info_without_cache()
    print(f"⏱️ 耗时: {time.time() - start_time:.2f}秒")
    print(f"📋 结果: {result5['data']}")
    
    print("\n=" * 50)
    print("✨ 演示总结:")
    print("- 首次请求: 需要执行完整处理")
    print("- 重复请求: 使用缓存，响应更快")
    print("- 数据变化: 自动检测并重新计算")
    print("- 缓存命中: 避免重复计算，提高性能")


if __name__ == '__main__':
    demo()
