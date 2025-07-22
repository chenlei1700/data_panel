#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器配置文件
Server Configuration - 管理所有股票仪表盘服务器的配置

Author: chenlei
"""

import os
import json
from typing import Dict, Any, Optional


class ServerConfigManager:
    """服务器配置管理器"""
    
    def __init__(self, config_file: str = "server_config.json"):
        self.config_file = config_file
        self.config_path = os.path.join(os.path.dirname(__file__), config_file)
        self._load_config()
    
    def _load_config(self):
        """从文件加载配置"""
        default_config = {
            "auto_update": {
                "enabled": True,
                "interval": 30,
                "components": ["chart1", "chart2", "table1", "table2"],
                "random_selection": True,
                "max_clients": 50,
                "heartbeat_interval": 30
            },
            "servers": {
                "multiplate": {
                    "port": 5008,
                    "name": "多板块股票仪表盘",
                    "auto_update": {
                        "enabled": True,
                        "interval": 25,
                        "components": ["chart1", "chart2", "table1", "table2", "table12", "table21", "table22"],
                        "random_selection": True,
                        "max_clients": 30,
                        "heartbeat_interval": 30
                    }
                },
                "demo": {
                    "port": 5004,
                    "name": "演示股票仪表盘",
                    "auto_update": {
                        "enabled": True,
                        "interval": 45,
                        "components": ["chart1", "table1"],
                        "random_selection": False,
                        "max_clients": 20,
                        "heartbeat_interval": 60
                    }
                },
                "strong": {
                    "port": 5002,
                    "name": "强势股票仪表盘",
                    "auto_update": {
                        "enabled": True,
                        "interval": 20,
                        "components": ["chart1", "chart2", "table1", "upLimitTable"],
                        "random_selection": True,
                        "max_clients": 40,
                        "heartbeat_interval": 30
                    }
                }
            },
            "global": {
                "debug": True,
                "host": "0.0.0.0",
                "max_cache_size": 100,
                "enable_cors": True,
                "log_level": "INFO"
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 递归合并配置
                    self.config = self._merge_configs(default_config, loaded_config)
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            self.config = default_config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """递归合并配置字典"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_server_config(self, server_name: str) -> Dict[str, Any]:
        """获取特定服务器的配置"""
        server_config = self.config.get("servers", {}).get(server_name, {})
        
        # 合并全局自动更新配置和服务器特定配置
        auto_update_config = self.config.get("auto_update", {}).copy()
        if "auto_update" in server_config:
            auto_update_config.update(server_config["auto_update"])
        
        return {
            "port": server_config.get("port", 5004),
            "name": server_config.get("name", "股票仪表盘"),
            "auto_update_config": auto_update_config,
            "global_config": self.config.get("global", {})
        }
    
    def update_server_config(self, server_name: str, new_config: Dict[str, Any]):
        """更新特定服务器的配置"""
        if "servers" not in self.config:
            self.config["servers"] = {}
        
        if server_name not in self.config["servers"]:
            self.config["servers"][server_name] = {}
        
        self.config["servers"][server_name].update(new_config)
        self.save_config()
    
    def update_global_auto_update_config(self, new_config: Dict[str, Any]):
        """更新全局自动更新配置"""
        self.config["auto_update"].update(new_config)
        self.save_config()
    
    def get_all_servers_config(self) -> Dict[str, Any]:
        """获取所有服务器配置"""
        return self.config.get("servers", {})
    
    def is_auto_update_enabled(self, server_name: str) -> bool:
        """检查指定服务器是否启用自动更新"""
        server_config = self.get_server_config(server_name)
        return server_config.get("auto_update_config", {}).get("enabled", True)
    
    def toggle_server_auto_update(self, server_name: str) -> bool:
        """切换服务器自动更新状态"""
        current_status = self.is_auto_update_enabled(server_name)
        new_status = not current_status
        
        if server_name not in self.config.get("servers", {}):
            self.config.setdefault("servers", {})[server_name] = {}
        
        self.config["servers"][server_name].setdefault("auto_update", {})["enabled"] = new_status
        self.save_config()
        
        return new_status


# 全局配置管理器实例
config_manager = ServerConfigManager()


def get_server_config(server_name: str) -> Dict[str, Any]:
    """便捷函数：获取服务器配置"""
    return config_manager.get_server_config(server_name)


def create_auto_update_config(server_name: str, **overrides) -> Dict[str, Any]:
    """便捷函数：创建自动更新配置"""
    server_config = get_server_config(server_name)
    auto_update_config = server_config.get("auto_update_config", {}).copy()
    auto_update_config.update(overrides)
    return auto_update_config


# 预定义的配置模板
QUICK_CONFIGS = {
    "high_frequency": {  # 高频更新模式
        "enabled": True,
        "interval": 10,
        "random_selection": True,
        "max_clients": 30
    },
    "normal": {  # 正常模式
        "enabled": True,
        "interval": 30,
        "random_selection": True,
        "max_clients": 50
    },
    "low_frequency": {  # 低频更新模式
        "enabled": True,
        "interval": 60,
        "random_selection": False,
        "max_clients": 100
    },
    "disabled": {  # 禁用模式
        "enabled": False,
        "interval": 30,
        "random_selection": True,
        "max_clients": 50
    },
    "demo": {  # 演示模式
        "enabled": True,
        "interval": 15,
        "components": ["chart1", "table1"],
        "random_selection": False,
        "max_clients": 10
    }
}


def apply_quick_config(server_name: str, config_name: str):
    """应用预定义配置模板"""
    if config_name not in QUICK_CONFIGS:
        raise ValueError(f"未知的配置模板: {config_name}")
    
    config_manager.update_server_config(server_name, {
        "auto_update": QUICK_CONFIGS[config_name]
    })
    
    print(f"已为服务器 '{server_name}' 应用配置模板 '{config_name}'")


if __name__ == "__main__":
    # 测试配置管理器
    print("=== 服务器配置管理器测试 ===")
    
    # 获取多板块服务器配置
    multiplate_config = get_server_config("multiplate")
    print(f"多板块服务器配置: {json.dumps(multiplate_config, indent=2, ensure_ascii=False)}")
    
    # 创建自定义自动更新配置
    custom_config = create_auto_update_config("multiplate", interval=15, enabled=False)
    print(f"自定义自动更新配置: {json.dumps(custom_config, indent=2, ensure_ascii=False)}")
    
    # 应用快速配置
    apply_quick_config("demo", "high_frequency")
    
    print("配置管理器测试完成")
