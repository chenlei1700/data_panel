"""
数据处理器基类
提供通用的数据处理功能和接口规范
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
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
    
    @abstractmethod
    def process(self, *args, **kwargs):
        """处理数据的抽象方法，子类必须实现"""
        pass
