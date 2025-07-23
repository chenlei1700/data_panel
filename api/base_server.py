#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用股票仪表盘服务器基类
Base Stock Dashboard Server - 可重用的服务器框架

Author: chenlei
"""

from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
import logging
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly
import time
import threading
import queue
import hashlib
from datetime import datetime, timedelta
import random
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple


class BaseDataCache:
    """基础数据缓存类 - 用于数据文件的缓存管理"""
    
    def __init__(self, file_paths: Optional[Dict[str, str]] = None):
        self.cache = {}
        self.timestamps = {}
        self.file_paths = file_paths or {}
        
    def get_file_path(self, file_key: str) -> Optional[str]:
        """获取文件路径"""
        return self.file_paths.get(file_key)
        
    def get_file_timestamp(self, file_path: str) -> float:
        """获取文件的修改时间戳"""
        try:
            return os.path.getmtime(file_path)
        except OSError:
            return 0
            
    def should_reload(self, file_key: str) -> bool:
        """检查是否需要重新加载文件"""
        file_path = self.get_file_path(file_key)
        if not file_path or not os.path.exists(file_path):
            return False
            
        current_timestamp = self.get_file_timestamp(file_path)
        cached_timestamp = self.timestamps.get(file_key, 0)
        
        return current_timestamp > cached_timestamp
        
    def load_data(self, key: str):
        """加载数据，支持从文件路径自动加载"""
        # 如果有配置的文件路径，使用文件加载逻辑
        if key in self.file_paths:
            return self._load_from_file(key)
        
        # 否则返回缓存中的数据
        return self.cache.get(key, pd.DataFrame())
    
    def _load_from_file(self, file_key: str):
        """从文件加载数据"""
        if file_key not in self.cache or self.should_reload(file_key):
            file_path = self.get_file_path(file_key)
            if not file_path or not os.path.exists(file_path):
                print(f"警告: 文件不存在 {file_path}")
                return pd.DataFrame()
                
            try:
                print(f"重新加载文件: {file_path}")
                df = pd.read_csv(file_path)
                self.cache[file_key] = df
                self.timestamps[file_key] = self.get_file_timestamp(file_path)
                return df.copy()
            except Exception as e:
                print(f"加载文件失败 {file_path}: {e}")
                return pd.DataFrame()
        else:
            print(f"使用缓存数据: {file_key}")
            return self.cache[file_key].copy()
    
    def update_data(self, key: str, data: Any):
        """更新缓存数据"""
        self.cache[key] = data
        self.timestamps[key] = time.time()
        
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
    
    def add_file_path(self, key: str, path: str):
        """添加文件路径映射"""
        self.file_paths[key] = path
    
    def update_file_paths(self, paths: Dict[str, str]):
        """批量更新文件路径映射"""
        self.file_paths.update(paths)


class BaseResponseCache:
    """基础响应缓存类 - 用于缓存API响应数据"""
    
    def __init__(self, max_cache_size=100):
        self.cache = {}  # 存储实际响应数据
        self.hash_cache = {}  # 存储数据哈希值
        self.access_times = {}  # 存储访问时间，用于LRU清理
        self.max_cache_size = max_cache_size
        
    def _generate_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """生成缓存键"""
        if params:
            # 对参数进行排序，确保键的一致性
            param_str = json.dumps(params, sort_keys=True, default=str)
            return f"{endpoint}:{param_str}"
        return endpoint
        
    def _calculate_data_hash(self, data: Any) -> str:
        """计算数据的哈希值"""
        try:
            # 将数据转换为JSON字符串再计算哈希
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode('utf-8')).hexdigest()
        except Exception as e:
            print(f"计算哈希失败: {e}")
            return str(time.time())  # 如果哈希失败，使用时间戳
            
    def _cleanup_cache(self):
        """清理缓存，保持在最大大小限制内"""
        if len(self.cache) <= self.max_cache_size:
            return
            
        # 按访问时间排序，移除最旧的条目
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        keys_to_remove = [key for key, _ in sorted_keys[:len(sorted_keys) - self.max_cache_size + 10]]
        
        for key in keys_to_remove:
            self.cache.pop(key, None)
            self.hash_cache.pop(key, None)
            self.access_times.pop(key, None)
            
        print(f"缓存清理完成，移除 {len(keys_to_remove)} 个条目")
        
    def should_use_cache(self, endpoint: str, params: Optional[Dict] = None, current_data: Optional[Any] = None) -> Tuple[bool, Optional[Any]]:
        """检查是否应该使用缓存的响应"""
        cache_key = self._generate_cache_key(endpoint, params)
        
        # 如果没有缓存，直接返回False
        if cache_key not in self.cache:
            return False, None
            
        # 如果没有提供当前数据，无法比较，使用缓存
        if current_data is None:
            self.access_times[cache_key] = time.time()
            return True, self.cache[cache_key]
            
        # 计算当前数据的哈希值
        current_hash = self._calculate_data_hash(current_data)
        cached_hash = self.hash_cache.get(cache_key)
        
        # 比较哈希值
        if current_hash == cached_hash:
            print(f"数据未变化，使用缓存响应: {endpoint}")
            self.access_times[cache_key] = time.time()
            return True, self.cache[cache_key]
        else:
            print(f"数据已变化，需要重新计算: {endpoint}")
            return False, None
            
    def store_response(self, endpoint: str, params: Optional[Dict] = None, 
                      source_data: Optional[Any] = None, response_data: Optional[Any] = None):
        """存储响应到缓存"""
        cache_key = self._generate_cache_key(endpoint, params)
        
        if source_data is not None:
            # 计算源数据的哈希值
            data_hash = self._calculate_data_hash(source_data)
            self.hash_cache[cache_key] = data_hash
            
        if response_data is not None:
            # 存储响应数据
            self.cache[cache_key] = response_data
            self.access_times[cache_key] = time.time()
            
            # 清理缓存
            self._cleanup_cache()
            
            print(f"响应已缓存: {endpoint}")
            
    def clear_cache(self):
        """清空所有缓存"""
        self.cache.clear()
        self.hash_cache.clear()
        self.access_times.clear()
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "cache_size": len(self.cache),
            "hash_cache_size": len(self.hash_cache),
            "max_cache_size": self.max_cache_size,
            "oldest_access": min(self.access_times.values()) if self.access_times else None,
            "newest_access": max(self.access_times.values()) if self.access_times else None
        }


class BaseStockServer(ABC):
    """股票仪表盘服务器基类"""
    
    def __init__(self, name: str = "股票仪表盘服务", port: int = 5004, auto_update_config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 自动更新配置
        self.auto_update_config = auto_update_config or {
            'enabled': True,           # 是否启用自动更新
            'interval': 30,            # 更新间隔（秒）
            'components': ["chart1", "chart2", "table1", "table2"],  # 参与自动更新的组件
            'random_selection': True,  # 是否随机选择组件更新
            'max_clients': 50,         # 最大SSE客户端数
            'heartbeat_interval': 30   # 心跳间隔（秒）
        }
        
        # 初始化缓存系统
        self.data_cache = BaseDataCache(self.get_data_cache_file_paths())
        self.response_cache = BaseResponseCache()
        
        # SSE相关
        self.sse_clients = []
        self.latest_update = {"componentId": None, "params": {}}
        
        # 注册通用路由
        self._register_routes()
        
        # 启动后台更新线程（仅在启用时）
        if self.auto_update_config['enabled']:
            self.update_thread = threading.Thread(target=self._background_data_update, daemon=True)
            self.update_thread.start()
            self.logger.info(f"自动更新线程已启动，间隔: {self.auto_update_config['interval']}秒")
        else:
            self.logger.info("自动更新功能已禁用")
    
    def get_data_cache_file_paths(self) -> Dict[str, str]:
        """获取数据缓存文件路径配置 - 子类可以重写此方法"""
        return {}
    
    def _register_routes(self):
        """注册所有路由"""
        # 通用路由
        self.app.add_url_rule('/health', 'health_check', self.health_check, methods=['GET'])
        self.app.add_url_rule('/api/system/info', 'get_system_info', self.get_system_info, methods=['GET'])
        self.app.add_url_rule('/api/dashboard-config', 'get_dashboard_config', self.get_dashboard_config, methods=['GET'])
        
        # 数据路由
        self.app.add_url_rule('/api/table-data/<data_type>', 'get_table_data', self.get_table_data, methods=['GET'])
        self.app.add_url_rule('/api/chart-data/<chart_type>', 'get_chart_data', self.get_chart_data, methods=['GET'])
        
        # SSE路由
        self.app.add_url_rule('/api/dashboard/update', 'update_dashboard', self.update_dashboard, methods=['POST'])
        self.app.add_url_rule('/api/dashboard/updates', 'dashboard_updates', self.dashboard_updates, methods=['GET'])
        
        # 缓存管理路由
        self.app.add_url_rule('/api/cache/status', 'get_cache_status', self.get_cache_status, methods=['GET'])
        self.app.add_url_rule('/api/cache/clear', 'clear_cache', self.clear_cache, methods=['POST'])
        
        # 自动更新配置路由
        self.app.add_url_rule('/api/auto-update/config', 'get_auto_update_config', self.get_auto_update_config, methods=['GET'])
        self.app.add_url_rule('/api/auto-update/config', 'update_auto_update_config', self.update_auto_update_config, methods=['PUT'])
        self.app.add_url_rule('/api/auto-update/status', 'get_auto_update_status', self.get_auto_update_status, methods=['GET'])
        self.app.add_url_rule('/api/auto-update/toggle', 'toggle_auto_update', self.toggle_auto_update, methods=['POST'])
        
        # 静态文件服务路由（配置管理界面）
        self.app.add_url_rule('/config', 'config_page', self.serve_config_page, methods=['GET'])
        self.app.add_url_rule('/static/<path:filename>', 'static_files', self.serve_static_files, methods=['GET'])
        
        # 允许子类注册自定义路由
        self.register_custom_routes()
        
        # 兼容旧方法名
        if hasattr(self, 'register_routes') and self.register_routes != self.register_custom_routes:
            self.register_routes()
    
    def register_custom_routes(self):
        """子类可以重写此方法注册自定义路由"""
        pass
    
    @abstractmethod
    def get_dashboard_config(self) -> Dict[str, Any]:
        """获取仪表盘配置 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_data_sources(self) -> Dict[str, Any]:
        """获取数据源配置 - 子类必须实现"""
        pass
    
    def get_cache_observables(self) -> Dict[str, Dict[str, Any]]:
        """
        定义需要观察的数据源，用于防重复缓存
        子类可以重写此方法来指定哪些数据需要被观察
        
        返回格式:
        {
            "endpoint_pattern": {
                "data_keys": ["data_key1", "data_key2"],  # 需要观察的数据键
                "params_keys": ["param1", "param2"],      # 需要观察的参数键
                "custom_hash_func": function,             # 可选：自定义哈希函数
                "ttl": 300                                # 可选：缓存TTL（秒）
            }
        }
        """
        return {
            # 默认观察配置，子类可以重写
            "table-data": {
                "data_keys": ["data_time", "data_count"],
                "params_keys": ["sector_name", "component_id"]
            },
            "chart-data": {
                "data_keys": ["data_time", "data_count"],
                "params_keys": ["sector_name", "component_id"]
            }
        }
    
    def with_cache_protection(self, endpoint: str, handler_func: callable, 
                             source_data_func: Optional[callable] = None,
                             params_extractor: Optional[callable] = None):
        """
        通用的缓存保护装饰器方法
        
        Args:
            endpoint: API端点路径
            handler_func: 实际的处理函数
            source_data_func: 获取源数据的函数（用于哈希比较）
            params_extractor: 从request中提取参数的函数
        """
        def wrapper(*args, **kwargs):
            try:
                # 提取参数
                params = {}
                if params_extractor:
                    params = params_extractor()
                else:
                    # 默认参数提取
                    if hasattr(request, 'args'):
                        params = dict(request.args)
                
                # 获取源数据
                source_data = None
                if source_data_func:
                    source_data = source_data_func()
                
                # 检查缓存
                should_cache, cached_response = self.response_cache.should_use_cache(
                    endpoint, params, source_data
                )
                
                if should_cache and cached_response:
                    self.logger.info(f"使用缓存响应: {endpoint}")
                    return cached_response
                
                # 执行实际处理
                self.logger.info(f"执行数据处理: {endpoint}")
                response_data = handler_func(*args, **kwargs)
                
                # 存储到缓存
                self.response_cache.store_response(endpoint, params, source_data, response_data)
                
                return response_data
                
            except Exception as e:
                self.logger.error(f"缓存保护装饰器失败 {endpoint}: {e}")
                # 失败时直接调用原函数
                return handler_func(*args, **kwargs)
        
        return wrapper
    
    def get_cache_status(self):
        """获取缓存状态信息"""
        try:
            cache_stats = self.response_cache.get_cache_stats()
            data_cache_info = {
                "data_cache_size": len(self.data_cache.cache),
                "data_timestamps": len(self.data_cache.timestamps)
            }
            
            return jsonify({
                "status": "success",
                "response_cache": cache_stats,
                "data_cache": data_cache_info,
                "server_info": {
                    "name": self.name,
                    "connected_clients": len(self.sse_clients)
                }
            })
        except Exception as e:
            self.logger.error(f"获取缓存状态失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def clear_cache(self):
        """清理所有缓存"""
        try:
            # 清理响应缓存
            response_initial_size = len(self.response_cache.cache)
            self.response_cache.clear_cache()
            
            # 清理数据缓存
            data_initial_size = len(self.data_cache.cache)
            self.data_cache.clear_cache()
            
            message = f"缓存已清理，移除响应缓存 {response_initial_size} 个条目，数据缓存 {data_initial_size} 个条目"
            self.logger.info(message)
            return jsonify({
                "status": "success", 
                "message": message
            })
        except Exception as e:
            self.logger.error(f"清理缓存失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    # === 自动更新配置管理方法 ===
    
    def get_auto_update_config(self):
        """获取自动更新配置"""
        try:
            return jsonify({
                "status": "success",
                "config": self.auto_update_config.copy(),
                "server_info": {
                    "name": self.name,
                    "port": self.port,
                    "sse_clients": len(self.sse_clients)
                }
            })
        except Exception as e:
            self.logger.error(f"获取自动更新配置失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def update_auto_update_config(self):
        """更新自动更新配置"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "缺少配置数据"}), 400
            
            old_enabled = self.auto_update_config['enabled']
            
            # 更新配置
            for key, value in data.items():
                if key in self.auto_update_config:
                    self.auto_update_config[key] = value
            
            # 如果启用状态发生变化，需要重启或停止后台线程
            new_enabled = self.auto_update_config['enabled']
            if old_enabled != new_enabled:
                if new_enabled and not hasattr(self, 'update_thread') or not self.update_thread.is_alive():
                    # 启动新的后台线程
                    self.update_thread = threading.Thread(target=self._background_data_update, daemon=True)
                    self.update_thread.start()
                    self.logger.info("自动更新线程已重新启动")
                elif not new_enabled:
                    self.logger.info("自动更新已禁用（现有线程将在下一次检查时退出）")
            
            self.logger.info(f"自动更新配置已更新: {data}")
            return jsonify({
                "status": "success",
                "message": "配置更新成功",
                "config": self.auto_update_config.copy()
            })
        except Exception as e:
            self.logger.error(f"更新自动更新配置失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_auto_update_status(self):
        """获取自动更新状态"""
        try:
            thread_alive = hasattr(self, 'update_thread') and self.update_thread.is_alive()
            
            # 从 ComponentManager 获取组件列表
            available_components = []
            if hasattr(self, 'component_manager'):
                available_components = list(self.component_manager.components.keys())
            
            return jsonify({
                "status": "success",
                "auto_update": {
                    "enabled": self.auto_update_config['enabled'],
                    "thread_running": thread_alive,
                    "interval": self.auto_update_config['interval'],
                    "components": available_components,
                    "sse_clients": len(self.sse_clients),
                    "max_clients": self.auto_update_config['max_clients']
                }
            })
        except Exception as e:
            self.logger.error(f"获取自动更新状态失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def toggle_auto_update(self):
        """切换自动更新开关"""
        try:
            current_status = self.auto_update_config['enabled']
            new_status = not current_status
            
            self.auto_update_config['enabled'] = new_status
            
            if new_status and (not hasattr(self, 'update_thread') or not self.update_thread.is_alive()):
                # 启动后台线程
                self.update_thread = threading.Thread(target=self._background_data_update, daemon=True)
                self.update_thread.start()
                message = "自动更新已启用，后台线程已启动"
            elif not new_status:
                message = "自动更新已禁用（后台线程将在下一次检查时退出）"
            else:
                message = f"自动更新状态已切换为: {'启用' if new_status else '禁用'}"
                
            self.logger.info(message)
            return jsonify({
                "status": "success",
                "message": message,
                "enabled": new_status,
                "thread_running": hasattr(self, 'update_thread') and self.update_thread.is_alive()
            })
        except Exception as e:
            self.logger.error(f"切换自动更新状态失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def _cleanup_sse_clients(self):
        """清理无效的SSE客户端连接"""
        try:
            initial_count = len(self.sse_clients)
            # 这里可以添加更复杂的客户端有效性检查逻辑
            # 目前简单地假设所有客户端都有效，但在实际应用中可能需要ping检查
            
            # 如果客户端数量过多，移除一些较旧的连接
            if len(self.sse_clients) > self.auto_update_config['max_clients']:
                remove_count = len(self.sse_clients) - self.auto_update_config['max_clients']
                self.sse_clients = self.sse_clients[remove_count:]
                self.logger.info(f"清理了 {remove_count} 个SSE客户端连接")
            
            return initial_count - len(self.sse_clients)
        except Exception as e:
            self.logger.error(f"清理SSE客户端失败: {e}")
            return 0
    
    # === 静态文件服务方法 ===
    
    def serve_config_page(self):
        """提供配置管理页面"""
        try:
            static_dir = os.path.join(os.path.dirname(__file__), 'static')
            return send_from_directory(static_dir, 'config.html')
        except Exception as e:
            self.logger.error(f"提供配置页面失败: {e}")
            return jsonify({"error": "配置页面不可用"}), 404
    
    def serve_static_files(self, filename):
        """提供静态文件服务"""
        try:
            static_dir = os.path.join(os.path.dirname(__file__), 'static')
            return send_from_directory(static_dir, filename)
        except Exception as e:
            self.logger.error(f"提供静态文件失败: {e}")
            return jsonify({"error": "文件未找到"}), 404
    
    # === 通用数据生成方法 ===
    
    def generate_mock_stock_data(self, count: int = 20) -> List[Dict[str, Any]]:
        """生成模拟股票数据"""
        stock_codes = [f"{1000 + i:04d}" for i in range(count)]
        stock_names = [
            "平安银行", "万科A", "招商银行", "中国平安", "美的集团",
            "五粮液", "贵州茅台", "恒瑞医药", "迈瑞医疗", "宁德时代",
            "比亚迪", "海康威视", "立讯精密", "药明康德", "爱尔眼科",
            "东方财富", "海尔智家", "格力电器", "洋河股份", "三安光电"
        ]
        
        data = []
        for i in range(count):
            price = round(random.uniform(5, 150), 2)
            change_pct = round(random.uniform(-10, 10), 2)
            volume = random.randint(1000, 50000)
            
            data.append({
                "股票代码": stock_codes[i],
                "股票名称": stock_names[i % len(stock_names)],
                "当前价格": price,
                "涨跌幅": f"{change_pct:+.2f}%",
                "成交量": volume,
                "市值": round(price * volume / 100, 2)
            })
        
        return data
    
    def generate_mock_sector_data(self) -> List[Dict[str, Any]]:
        """生成模拟板块数据"""
        sectors = [
            "科技板块", "医药板块", "新能源", "金融板块", "消费板块",
            "军工板块", "地产板块", "汽车板块", "钢铁板块", "化工板块"
        ]
        
        data = []
        for sector in sectors:
            change_pct = round(random.uniform(-5, 5), 2)
            data.append({
                "板块名称": sector,
                "涨跌幅": f"{change_pct:+.2f}%",
                "成交额": round(random.uniform(100, 1000), 2),
                "领涨股": random.choice(["股票A", "股票B", "股票C"]),
                "活跃度": random.choice(["高", "中", "低"])
            })
        
        return data
    
    def generate_mock_time_series(self) -> Tuple[List[str], List[float]]:
        """生成模拟时间序列数据"""
        base_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        times = []
        values = []
        
        current_time = base_time
        current_value = 100
        
        while current_time.hour < 15:
            times.append(current_time.strftime("%H:%M"))
            
            change = random.uniform(-2, 2)
            current_value += change
            values.append(round(current_value, 2))
            
            current_time += timedelta(minutes=5)
            
            if current_time.hour == 11 and current_time.minute == 30:
                current_time = current_time.replace(hour=13, minute=0)
        
        return times, values
    
    # === 通用图表生成方法 ===
    
    def create_line_chart(self, x_data: List, y_data: List, title: str = "线性图", 
                         x_title: str = "X轴", y_title: str = "Y轴") -> str:
        """创建线性图"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name=title,
            line=dict(color='#2196F3', width=2)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white',
            height=300
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_bar_chart(self, x_data: List, y_data: List, title: str = "柱状图",
                        x_title: str = "X轴", y_title: str = "Y轴", colors: Optional[List] = None) -> str:
        """创建柱状图"""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_data,
            y=y_data,
            marker_color=colors or 'lightblue',
            name=title
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white',
            height=300
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # === 通用路由处理方法 ===
    
    def get_table_data(self, data_type: str):
        """获取表格数据 - 支持缓存防重复机制"""
        try:
            data_sources = self.get_data_sources()
            
            # 检查数据源配置（支持完整路径匹配）
            table_path = f"/api/table-data/{data_type}"
            if table_path in data_sources:
                config = data_sources[table_path]
                
                # 如果配置中有 handler，尝试调用对应的方法
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        
                        # 检查是否需要缓存保护
                        cache_ttl = config.get('cache_ttl', None)
                        if cache_ttl is not None and cache_ttl > 0:
                            # 使用缓存保护机制
                            def source_data_extractor():
                                # 子类可以重写此方法来提供更精确的源数据
                                return self._get_source_data_for_endpoint(table_path)
                                
                            protected_handler = self.with_cache_protection(
                                table_path, 
                                handler_method,
                                source_data_extractor
                            )
                            return protected_handler()
                        else:
                            # 直接调用handler
                            return handler_method()
                    else:
                        self.logger.warning(f"Handler方法 {handler_name} 不存在，使用默认处理")
                else:
                    # 如果没有handler，直接返回配置数据
                    return jsonify(config)
            
            # 兼容旧的配置格式 (tables 字典)
            if data_type in data_sources.get('tables', {}):
                config = data_sources['tables'][data_type]
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        return handler_method()
                return jsonify(config)
            
            # 默认处理
            return self._handle_default_table_data(data_type)
            
        except Exception as e:
            self.logger.error(f"获取表格数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def _handle_default_table_data(self, data_type: str):
        """处理默认的表格数据"""
        if data_type == "stock-list":
            stock_data = self.generate_mock_stock_data(20)
            return jsonify({
                "columns": ["股票代码", "股票名称", "当前价格", "涨跌幅", "成交量", "市值"],
                "data": [[item[col] for col in ["股票代码", "股票名称", "当前价格", "涨跌幅", "成交量", "市值"]] 
                        for item in stock_data]
            })
        elif data_type == "sector-list":
            sector_data = self.generate_mock_sector_data()
            return jsonify({
                "columns": ["板块名称", "涨跌幅", "成交额", "领涨股", "活跃度"],
                "data": [[item[col] for col in ["板块名称", "涨跌幅", "成交额", "领涨股", "活跃度"]] 
                        for item in sector_data]
            })
        
        return jsonify({"columns": [], "data": []})
    
    def _get_source_data_for_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """
        获取端点的源数据，用于缓存哈希比较
        子类可以重写此方法来提供更精确的源数据
        """
        # 默认实现：返回基本信息
        return {
            "timestamp": time.time(),
            "endpoint": endpoint,
            "data_cache_timestamps": self.data_cache.timestamps.copy()
        }
    
    def get_chart_data(self, chart_type: str):
        """获取图表数据 - 可被子类重写"""
        try:
            data_sources = self.get_data_sources()
            
            # 检查数据源配置（支持完整路径匹配）
            chart_path = f"/api/chart-data/{chart_type}"
            if chart_path in data_sources:
                config = data_sources[chart_path]
                
                # 如果配置中有 handler，尝试调用对应的方法
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        return handler_method()
                    else:
                        self.logger.warning(f"Handler方法 {handler_name} 不存在，使用默认处理")
                else:
                    # 如果没有handler，直接返回配置数据
                    return config
            
            # 兼容旧的配置格式 (charts 字典)
            if chart_type in data_sources.get('charts', {}):
                config = data_sources['charts'][chart_type]
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        return handler_method()
                return config
            
            # 默认处理
            if chart_type == "stock-trend":
                times, values = self.generate_mock_time_series()
                return self.create_line_chart(times, values, '股票价格走势', '时间', '价格 (元)')
            
            elif chart_type == "sector-performance":
                sector_data = self.generate_mock_sector_data()
                sector_names = [item["板块名称"] for item in sector_data]
                sector_changes = [float(item["涨跌幅"].replace("%", "").replace("+", "")) for item in sector_data]
                colors = ['red' if x < 0 else 'green' for x in sector_changes]
                return self.create_bar_chart(sector_names, sector_changes, '板块表现', '板块', '涨跌幅 (%)', colors)
            
            elif chart_type == "volume-analysis":
                stock_data = self.generate_mock_stock_data(10)
                stock_names = [item["股票名称"] for item in stock_data]
                volumes = [item["成交量"] for item in stock_data]
                return self.create_bar_chart(stock_names, volumes, '成交量分析', '股票', '成交量')
            
            return jsonify({"error": "未知图表类型"})
            
        except Exception as e:
            self.logger.error(f"获取图表数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    # === SSE相关方法 ===
    
    def send_update_to_clients(self, data: Dict[str, Any]):
        """向所有客户端发送更新"""
        message = f"data: {json.dumps(data)}\n\n"
        clients_to_remove = []
        
        for client in list(self.sse_clients):
            try:
                client.put(message)
            except Exception as e:
                self.logger.error(f"发送更新失败: {e}")
                clients_to_remove.append(client)
        
        for client in clients_to_remove:
            try:
                self.sse_clients.remove(client)
            except ValueError:
                pass
    
    def update_dashboard(self):
        """接收仪表盘更新请求"""
        try:
            data = request.json
            component_id = data.get('componentId')
            params = data.get('params', {})
            
            self.logger.info(f"接收到更新请求: componentId={component_id}, params={params}")
            
            self.latest_update = {
                "componentId": component_id,
                "params": params,
                "timestamp": int(time.time() * 1000)
            }
            
            self.send_update_to_clients(self.latest_update)
            
            return jsonify({"status": "success", "message": "更新已发送"})
            
        except Exception as e:
            self.logger.error(f"处理更新请求失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def dashboard_updates(self):
        """SSE端点，向前端推送实时更新"""
        def event_stream():
            client_queue = queue.Queue()
            self.sse_clients.append(client_queue)
            
            try:
                if self.latest_update["componentId"]:
                    yield f"data: {json.dumps(self.latest_update)}\n\n"
                
                while True:
                    try:
                        message = client_queue.get(block=True, timeout=30)
                        yield message
                    except queue.Empty:
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': int(time.time() * 1000)})}\n\n"
                        
            except Exception as e:
                self.logger.error(f"SSE连接错误: {e}")
            finally:
                try:
                    self.sse_clients.remove(client_queue)
                except ValueError:
                    pass
        
        return Response(event_stream(), mimetype='text/event-stream')
    
    def health_check(self):
        """健康检查端点"""
        return jsonify({
            "status": "healthy",
            "service": self.name,
            "version": "1.0.0",
            "timestamp": int(time.time() * 1000),
            "connected_clients": len(self.sse_clients)
        })
    
    def get_system_info(self):
        """获取系统信息"""
        return jsonify({
            "name": self.name,
            "version": "1.0.0",
            "description": "基于通用框架的股票仪表盘服务",
            "features": [
                "实时数据模拟",
                "多种图表类型", 
                "交互式仪表盘",
                "SSE实时更新"
            ],
            "endpoints": {
                "dashboard-config": "/api/dashboard-config",
                "table-data": "/api/table-data/<data_type>",
                "chart-data": "/api/chart-data/<chart_type>",
                "dashboard-updates": "/api/dashboard/updates",
                "health": "/health"
            }
        })
    
    def _background_data_update(self):
        """后台定期更新数据"""
        if not self.auto_update_config['enabled']:
            self.logger.info("自动更新已禁用，后台更新线程退出")
            return
            
        self.logger.info("自动更新后台线程开始运行")
        
        while True:
            try:
                # 使用配置的更新间隔
                time.sleep(self.auto_update_config['interval'])
                
                # 检查是否有SSE客户端连接
                if not self.sse_clients:
                    continue
                
                # 检查是否超过最大客户端数限制
                if len(self.sse_clients) > self.auto_update_config['max_clients']:
                    self.logger.warning(f"SSE客户端数量 ({len(self.sse_clients)}) 超过限制 ({self.auto_update_config['max_clients']})")
                    # 清理无效连接
                    self._cleanup_sse_clients()
                
                # 获取参与自动更新的组件列表
                components = []
                if hasattr(self, 'component_manager'):
                    # 从 ComponentManager 获取启用的组件
                    components = [comp_id for comp_id, comp_config in self.component_manager.components.items() 
                                if comp_config.extra_config.get('enabled', True)]
                
                if not components:
                    self.logger.warning("自动更新组件列表为空")
                    continue
                
                # 根据配置选择组件
                if self.auto_update_config['random_selection']:
                    selected_component = random.choice(components)
                else:
                    # 按顺序选择（可以添加更复杂的逻辑）
                    current_time = int(time.time())
                    index = (current_time // self.auto_update_config['interval']) % len(components)
                    selected_component = components[index]
                
                update_data = {
                    "componentId": selected_component,
                    "params": {"auto_refresh": True},
                    "timestamp": int(time.time() * 1000),
                    "type": "auto_update",
                    "server_config": {
                        "interval": self.auto_update_config['interval'],
                        "random_mode": self.auto_update_config['random_selection']
                    }
                }
                
                # 发送更新到客户端
                if self.sse_clients:
                    self.send_update_to_clients(update_data)
                    self.logger.info(f"自动更新推送: {selected_component} (客户端数: {len(self.sse_clients)})")
                    
            except Exception as e:
                self.logger.error(f"自动更新线程异常: {e}")
                # 出现异常时等待一段时间再继续，避免快速失败循环
                time.sleep(min(self.auto_update_config['interval'], 10))
    
    def _find_available_port(self, start_port: int) -> int:
        """查找可用端口"""
        import socket
        for port in range(start_port, start_port + 100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except OSError:
                continue
        raise RuntimeError("无法找到可用端口")
    
    def run(self, debug: bool = True, host: str = '0.0.0.0'):
        """启动服务器"""
        self.logger.info(f"启动{self.name}，端口: {self.port}")
        
        try:
            # 检查端口是否可用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, self.port))
            sock.close()
            
            if result == 0:
                self.logger.warning(f"端口 {self.port} 已被占用，尝试自动寻找可用端口")
                self.port = self._find_available_port(self.port)
                self.logger.info(f"使用新端口: {self.port}")
            
            # 配置Flask应用以减少重载问题
            self.app.config.update(
                ENV='development' if debug else 'production',
                DEBUG=debug,
                TESTING=False,
                PROPAGATE_EXCEPTIONS=True
            )
            
            # 启动服务器
            self.app.run(
                debug=debug, 
                host=host, 
                port=self.port,
                use_reloader=False,  # 禁用自动重载以避免套接字问题
                threaded=True
            )
            
        except KeyboardInterrupt:
            self.logger.info("服务器被用户中断")
        except OSError as e:
            if hasattr(e, 'winerror') and e.winerror == 10038:  # WinError 10038
                self.logger.error("套接字错误，可能是端口冲突或重载问题")
                self.logger.info("建议重启程序或使用不同端口")
            else:
                self.logger.error(f"网络错误: {e}")
            sys.exit(3)
        except Exception as e:
            self.logger.error(f"服务器启动失败: {e}")
            sys.exit(1)


def parse_command_line_args() -> int:
    """解析命令行参数获取端口"""
    port = 5004  # 默认端口
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ 端口参数必须是数字")
            sys.exit(1)
    
    # 从环境变量获取端口
    if 'SERVER_PORT' in os.environ:
        try:
            port = int(os.environ['SERVER_PORT'])
        except ValueError:
            pass
    
    return port
