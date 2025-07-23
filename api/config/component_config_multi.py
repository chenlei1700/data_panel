"""
组件配置文件 - 统一管理所有仪表盘组件的配置信息（支持多服务器）
Author: chenlei
Date: 2025-07-22
"""

import os
import json
from typing import Dict, Any, Optional, List

class ComponentConfig:
    """组件配置类"""
    
    def __init__(self, 
                 component_id: str,
                 component_type: str,
                 title: str,
                 api_path: str,
                 handler: str = None,  # 现在是可选的，可以自动推断
                 processor_type: str = None,  # 现在是可选的，用于向后兼容
                 processor_method: str = None,
                 position: Dict[str, int] = None,
                 description: str = "",
                 height: Optional[str] = None,
                 cache_ttl: int = 0,
                 source_data_keys: Optional[List[str]] = None,
                 source_data_logic: Optional[str] = None,
                 **kwargs):
        self.id = component_id
        self.type = component_type
        self.title = title
        self.api_path = api_path
        
        # 如果没有提供 handler，从 api_path 自动推断
        if handler is None:
            # 从 "/api/sector_line_chart_change" 生成 "get_sector_line_chart_change_data"
            if api_path.startswith('/api/'):
                method_name = api_path[5:]  # 去掉 "/api/" 前缀
            else:
                method_name = api_path
            handler = f"get_{method_name}_data"
        
        self.handler = handler
        
        # processor_type 保留用于向后兼容，但不再使用
        self.processor_type = processor_type or "legacy"
        
        # 如果没有提供 processor_method，从 api_path 自动推断
        if processor_method is None:
            # 从 "/api/up_limit_table_data" 提取 "up_limit_table_data"
            if api_path.startswith('/api/'):
                processor_method = api_path[5:]  # 去掉 "/api/" 前缀
            else:
                processor_method = api_path
        
        self.processor_method = processor_method
        self.position = position or {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
        self.description = description
        self.height = height
        self.cache_ttl = cache_ttl
        self.source_data_keys = source_data_keys or []
        self.source_data_logic = source_data_logic
        self.extra_config = kwargs

    def to_dashboard_component(self, dynamic_title: Optional[str] = None) -> Dict[str, Any]:
        """转换为仪表盘组件配置"""
        config = {
            "id": self.id,
            "type": self.type,
            "dataSource": self.api_path,
            "title": dynamic_title or self.title,
            "position": self.position
        }
        
        if self.height:
            config["height"] = self.height
            
        # 添加额外配置
        config.update(self.extra_config)
        
        return config

    def to_data_source_config(self) -> Dict[str, Dict[str, Any]]:
        """转换为数据源配置"""
        return {
            self.api_path: {
                "handler": self.handler,
                "description": self.description,
                "cache_ttl": self.cache_ttl
            }
        }


# 组件配置加载器
class ComponentConfigLoader:
    """组件配置加载器 - 从 JSON 文件加载配置"""
    
    def __init__(self, config_file: str = "components_config.json"):
        self.config_file = config_file
        self.config_path = os.path.join(os.path.dirname(__file__), config_file)
        self._components_configs = None
    
    def load_configs(self) -> Dict[str, Dict[str, Any]]:
        """从 JSON 文件加载组件配置"""
        if self._components_configs is not None:
            return self._components_configs
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 将 JSON 数据转换为 ComponentConfig 对象
            configs = {}
            for server_type, components in json_data.items():
                configs[server_type] = {}
                for comp_id, comp_data in components.items():
                    # 创建 ComponentConfig 对象
                    configs[server_type][comp_id] = ComponentConfig(**comp_data)
            
            self._components_configs = configs
            return configs
            
        except FileNotFoundError:
            print(f"Warning: 配置文件 {self.config_path} 不存在，使用空配置")
            return {"multiplate": {}, "demo": {}, "strong": {}}
        except json.JSONDecodeError as e:
            print(f"Warning: 配置文件 JSON 格式错误: {e}，使用空配置")
            return {"multiplate": {}, "demo": {}, "strong": {}}
        except Exception as e:
            print(f"Warning: 加载配置文件失败: {e}，使用空配置")
            return {"multiplate": {}, "demo": {}, "strong": {}}
    
    def reload_configs(self):
        """重新加载配置"""
        self._components_configs = None
        return self.load_configs()
    
    def save_configs(self, configs: Dict[str, Dict[str, Any]]):
        """保存配置到 JSON 文件"""
        try:
            # 将 ComponentConfig 对象转换为字典
            json_data = {}
            for server_type, components in configs.items():
                json_data[server_type] = {}
                for comp_id, comp_config in components.items():
                    if isinstance(comp_config, ComponentConfig):
                        json_data[server_type][comp_id] = {
                            "component_id": comp_config.id,
                            "component_type": comp_config.type,
                            "title": comp_config.title,
                            "api_path": comp_config.api_path,
                            "handler": comp_config.handler,
                            "processor_type": comp_config.processor_type,
                            "processor_method": comp_config.processor_method,
                            "position": comp_config.position,
                            "description": comp_config.description,
                            "height": comp_config.height,
                            "cache_ttl": comp_config.cache_ttl,
                            "source_data_keys": comp_config.source_data_keys,
                            "source_data_logic": comp_config.source_data_logic,
                            **comp_config.extra_config
                        }
                    else:
                        json_data[server_type][comp_id] = comp_config
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"配置已保存到: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

# 全局配置加载器实例
_config_loader = ComponentConfigLoader()

# 加载组件配置
COMPONENTS_CONFIGS = _config_loader.load_configs()
COMPONENTS_CONFIG = COMPONENTS_CONFIGS.get("multiplate", {})


def get_components_config(server_type: str = "multiplate") -> Dict[str, ComponentConfig]:
    """获取指定服务器类型的组件配置"""
    return COMPONENTS_CONFIGS.get(server_type, {})


def get_all_components_configs() -> Dict[str, Dict[str, ComponentConfig]]:
    """获取所有组件配置"""
    return COMPONENTS_CONFIGS


def reload_components_configs():
    """重新加载组件配置"""
    global COMPONENTS_CONFIGS, COMPONENTS_CONFIG
    COMPONENTS_CONFIGS = _config_loader.reload_configs()
    COMPONENTS_CONFIG = COMPONENTS_CONFIGS.get("multiplate", {})
    return COMPONENTS_CONFIGS


def save_components_configs():
    """保存组件配置"""
    return _config_loader.save_configs(COMPONENTS_CONFIGS)


def add_component_config(server_type: str, component_id: str, component_config: ComponentConfig):
    """动态添加组件配置"""
    if server_type not in COMPONENTS_CONFIGS:
        COMPONENTS_CONFIGS[server_type] = {}
    
    COMPONENTS_CONFIGS[server_type][component_id] = component_config


def remove_component_config(server_type: str, component_id: str):
    """移除组件配置"""
    if server_type in COMPONENTS_CONFIGS and component_id in COMPONENTS_CONFIGS[server_type]:
        del COMPONENTS_CONFIGS[server_type][component_id]


def update_component_config(server_type: str, component_id: str, **kwargs):
    """更新组件配置"""
    if server_type in COMPONENTS_CONFIGS and component_id in COMPONENTS_CONFIGS[server_type]:
        comp_config = COMPONENTS_CONFIGS[server_type][component_id]
        for key, value in kwargs.items():
            if hasattr(comp_config, key):
                setattr(comp_config, key, value)



class ComponentManager:
    """组件管理器 - 支持多服务器"""
    
    def __init__(self, server_instance, server_type: str = "multiplate"):
        self.server = server_instance
        self.server_type = server_type
        self.components = COMPONENTS_CONFIGS.get(server_type, {})
        
    def get_dashboard_config(self) -> Dict[str, Any]:
        """生成仪表盘配置"""
        components = []
        
        for comp_id, comp_config in self.components.items():
            # 检查是否启用该组件
            if comp_config.extra_config.get('enabled', True):
                # 获取动态标题
                dynamic_title = None
                if comp_id == "table12" and hasattr(self.server, 'dynamic_titles'):
                    dynamic_title = self.server.dynamic_titles.get("table12", comp_config.title)
                
                components.append(comp_config.to_dashboard_component(dynamic_title))
        
        return {
            "layout": {
                "rows": 10,
                "cols": 5,
                "components": components
            }
        }
    
    def get_data_sources_config(self) -> Dict[str, Dict[str, Any]]:
        """生成数据源配置"""
        data_sources = {}
        
        for comp_config in self.components.values():
            if comp_config.extra_config.get('enabled', True):
                data_sources.update(comp_config.to_data_source_config())
        
        return data_sources
    
    def get_source_data_logic(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """获取指定端点的源数据逻辑"""
        # 找到对应的组件配置
        for comp_config in self.components.values():
            if comp_config.api_path == endpoint:
                logic_method = comp_config.source_data_logic
                if logic_method and hasattr(self.server, f'_{logic_method}'):
                    # 调用服务器实例的源数据逻辑方法
                    return getattr(self.server, f'_{logic_method}')(endpoint, request_params)
                else:
                    # 使用默认的源数据逻辑
                    return self._default_source_data_logic(comp_config, request_params)
        
        # 未找到配置，使用基类默认实现
        return {}
    
    def _default_source_data_logic(self, comp_config: ComponentConfig, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """默认源数据逻辑"""
        source_data = {
            'endpoint': comp_config.api_path,
            'component_id': comp_config.id,
            'server_type': self.server_type,
            'request_params': request_params,
            'file_timestamps': {}
        }
        
        # 添加依赖的数据文件时间戳
        for data_key in comp_config.source_data_keys:
            if hasattr(self.server, 'data_cache') and hasattr(self.server.data_cache, 'timestamps'):
                source_data['file_timestamps'][data_key] = self.server.data_cache.timestamps.get(data_key, 0)
        
        return source_data
    
    def create_handler_methods(self):
        """为服务器实例动态创建处理方法"""
        for comp_config in self.components.values():
            if comp_config.extra_config.get('enabled', True):
                self._create_handler_method(comp_config)
    
    def _create_handler_method(self, comp_config: ComponentConfig):
        """创建单个处理方法"""
        def handler_method():
            # 使用新的处理器管理器架构，直接调用process方法
            return self.server.processor_manager.process(comp_config.processor_method)
        
        # 设置方法名和文档字符串
        handler_method.__name__ = comp_config.handler
        handler_method.__doc__ = f"获取{comp_config.title}数据"
        
        # 将方法绑定到服务器实例
        setattr(self.server, comp_config.handler, handler_method)
