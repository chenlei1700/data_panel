"""
启动缓存模块 - 支持启动时只执行一次的缓存策略
Author: data_panel开发团队
Date: 2025-08-01
"""
import time
import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from flask import jsonify


class StartupOnceCache:
    """启动时只执行一次的缓存类"""
    
    def __init__(self):
        self.startup_cache = {}  # 存储启动时计算的数据
        self.startup_flags = {}  # 标记哪些端点已经计算过
        self.startup_time = time.time()  # 服务器启动时间
        
    def is_startup_cached(self, endpoint: str, params: Optional[Dict] = None) -> bool:
        """检查是否已在启动时缓存"""
        cache_key = self._generate_startup_key(endpoint, params)
        return cache_key in self.startup_cache
    
    def get_startup_cache(self, endpoint: str, params: Optional[Dict] = None):
        """获取启动时的缓存数据"""
        cache_key = self._generate_startup_key(endpoint, params)
        cached_data = self.startup_cache.get(cache_key)
        
        if cached_data:
            print(f"🔒 使用启动时缓存: {endpoint}")
            # 添加缓存标识
            if hasattr(cached_data, 'json') and cached_data.json:
                data = cached_data.json.copy()
                if isinstance(data, dict) and 'metadata' in data:
                    data['metadata']['cached'] = True
                    data['metadata']['cache_type'] = 'startup_once'
                    data['metadata']['cached_at'] = self.startup_time
                return jsonify(data)
        
        return cached_data
    
    def set_startup_cache(self, endpoint: str, params: Optional[Dict] = None, response_data=None):
        """设置启动时缓存"""
        cache_key = self._generate_startup_key(endpoint, params)
        self.startup_cache[cache_key] = response_data
        self.startup_flags[cache_key] = True
        print(f"💾 已设置启动时缓存: {endpoint}")
    
    def _generate_startup_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """生成启动缓存键"""
        if params:
            param_str = json.dumps(params, sort_keys=True, default=str)
            return f"startup:{endpoint}:{hashlib.md5(param_str.encode()).hexdigest()[:8]}"
        return f"startup:{endpoint}"
    
    def clear_startup_cache(self):
        """清除所有启动缓存"""
        cleared_count = len(self.startup_cache)
        self.startup_cache.clear()
        self.startup_flags.clear()
        print(f"🗑️ 已清除 {cleared_count} 个启动缓存项")
        return cleared_count
    
    def get_startup_cache_stats(self) -> Dict[str, Any]:
        """获取启动缓存统计信息"""
        return {
            'cached_endpoints': len(self.startup_cache),
            'startup_time': self.startup_time,
            'cache_age_seconds': time.time() - self.startup_time,
            'cache_keys': list(self.startup_cache.keys())
        }
