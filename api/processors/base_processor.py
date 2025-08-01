"""
数据处理器基类
提供通用的数据处理功能和接口规范
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time
from flask import jsonify, request


class BaseDataProcessor(ABC):
    """数据处理器基类"""
    
    def __init__(self, server_instance):
        """
        初始化处理器
        
        Args:
            server_instance: 服务器实例，用于访问数据缓存和其他资源
        """
        self.server = server_instance
        self.data_cache = server_instance.data_cache
        self.response_cache = server_instance.response_cache
        self.logger = server_instance.logger
    
    def get_request_params(self) -> Dict[str, Any]:
        """获取请求参数"""
        return dict(request.args) if hasattr(request, 'args') else {}
    
    def build_cache_params(self, **kwargs) -> Dict[str, Any]:
        """构建缓存参数"""
        params = self.get_request_params()
        params.update(kwargs)
        return params
    
    def should_use_cache(self, endpoint: str, cache_params: Optional[Dict] = None, 
                        source_data: Optional[Dict] = None):
        """检查是否应该使用缓存"""
        return self.response_cache.should_use_cache(endpoint, cache_params, source_data)
    
    def store_cache(self, endpoint: str, cache_params: Optional[Dict] = None, 
                   source_data: Optional[Dict] = None, response_data=None):
        """存储缓存"""
        self.response_cache.store_response(endpoint, cache_params, source_data, response_data)
    
    def error_response(self, message: str, status_code: int = 500):
        """返回错误响应"""
        self.logger.error(message)
        return jsonify({"error": message}), status_code
    
    def _process_with_startup_cache(self, endpoint: str, original_method):
        """
        启动缓存包装器
        为原有的处理方法添加启动缓存功能
        
        Args:
            endpoint: API端点路径
            original_method: 原始的数据处理方法
            
        Returns:
            处理后的响应数据
        """
        try:
            # 对于启动缓存，我们简化参数处理，只使用endpoint作为key
            # 因为启动缓存主要用于不依赖请求参数的静态数据
            cache_params = None  # 启动缓存不使用参数
            
            # 🔍 添加详细的调试信息
            print(f"🔍 启动缓存检查: {endpoint}")
            print(f"  - cache_params: {cache_params}")
            
            # 检查启动缓存
            if hasattr(self.server, 'startup_cache') and self.server.startup_cache.is_startup_cached(endpoint, cache_params):
                self.logger.info(f"🔒 使用启动时缓存数据: {endpoint}")
                return self.server.startup_cache.get_startup_cache(endpoint, cache_params)
            
            # 如果有启动缓存对象但没有缓存，显示详细信息
            if hasattr(self.server, 'startup_cache'):
                cache_key = self.server.startup_cache._generate_startup_key(endpoint, cache_params)
                available_keys = list(self.server.startup_cache.startup_cache.keys())
                print(f"  - generated_key: {cache_key}")
                print(f"  - available_keys: {available_keys}")
                print(f"  - cache_exists: {cache_key in self.server.startup_cache.startup_cache}")
            
            # 没有缓存，执行原始方法
            self.logger.info(f"🔄 启动缓存未命中，执行计算: {endpoint}")
            
            # 记录开始时间
            start_time = time.time()
            
            # 调用原始处理方法
            response_data = original_method()
            
            # 记录计算时间
            duration = time.time() - start_time
            self.logger.info(f"⏱️ 计算完成，耗时: {duration:.2f}秒")
            
            # 如果响应是 JSON 格式，添加缓存元数据
            if hasattr(response_data, 'json') and response_data.json:
                data = response_data.json.copy()
                if isinstance(data, dict):
                    if 'metadata' not in data:
                        data['metadata'] = {}
                    data['metadata'].update({
                        'cached': False,
                        'cache_type': 'startup_once',
                        'calculatedAt': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'calculation_duration': duration
                    })
                    response_data = jsonify(data)
            
            # 存储到启动缓存
            if hasattr(self.server, 'startup_cache'):
                # 使用相同的参数策略：启动缓存不使用参数
                self.server.startup_cache.set_startup_cache(endpoint, None, response_data)
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"启动缓存处理失败 {endpoint}: {e}")
            return self.error_response(f"处理失败: {e}")
    
    def _process_with_response_cache(self, endpoint: str, original_method, cache_params: Optional[Dict] = None, 
                                   source_data: Optional[Dict] = None):
        """
        响应缓存包装器
        为原有的处理方法添加响应缓存功能
        
        Args:
            endpoint: API端点路径
            original_method: 原始的数据处理方法
            cache_params: 缓存参数
            source_data: 源数据用于缓存检查
            
        Returns:
            处理后的响应数据
        """
        try:
            if cache_params is None:
                cache_params = self.build_cache_params()
            
            # 检查响应缓存
            if self.should_use_cache(endpoint, cache_params, source_data):
                cached_response = self.response_cache.get_response(endpoint, cache_params)
                if cached_response:
                    self.logger.info(f"🔒 使用响应缓存数据: {endpoint}")
                    return cached_response
            
            # 没有缓存，执行原始方法
            self.logger.info(f"🔄 响应缓存未命中，执行计算: {endpoint}")
            
            # 记录开始时间
            start_time = time.time()
            
            # 调用原始处理方法
            response_data = original_method()
            
            # 记录计算时间
            duration = time.time() - start_time
            self.logger.info(f"⏱️ 计算完成，耗时: {duration:.2f}秒")
            
            # 存储到响应缓存
            self.store_cache(endpoint, cache_params, source_data, response_data)
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"响应缓存处理失败 {endpoint}: {e}")
            return self.error_response(f"处理失败: {e}")
    
    @abstractmethod
    def process(self, *args, **kwargs):
        """处理数据的抽象方法，子类必须实现"""
        pass
