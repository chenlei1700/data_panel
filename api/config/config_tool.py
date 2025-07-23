#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具 - 统一管理服务器和组件配置
Configuration Management Tool - Unified Server and Component Configuration

Author: chenlei
Date: 2025-07-23

使用方法:
    python config_tool.py list                     # 列出所有配置
    python config_tool.py server list              # 列出服务器配置
    python config_tool.py components list          # 列出组件配置
    python config_tool.py components list multiplate    # 列出指定服务器的组件
    python config_tool.py validate                 # 验证所有配置
    python config_tool.py reload                   # 重新加载配置
"""

import sys
import os
import json
from typing import Dict, Any

# 添加路径
sys.path.append(os.path.dirname(__file__))

from server_config import ServerConfigManager
from component_config_multi import (
    get_components_config,
    get_all_components_configs,
    reload_components_configs,
    save_components_configs,
    COMPONENTS_CONFIGS
)

class UnifiedConfigManager:
    """统一配置管理器"""
    
    def __init__(self):
        self.server_manager = ServerConfigManager()
    
    def list_all_configs(self):
        """列出所有配置"""
        print("🔧 配置概览")
        print("=" * 60)
        
        # 服务器配置
        servers = self.server_manager.get_all_servers_config()
        print(f"\n🖥️  服务器配置 ({len(servers)} 个)")
        for server_name, config in servers.items():
            port = config.get('port', 'N/A')
            name = config.get('name', 'N/A')
            auto_update = config.get('auto_update', {}).get('enabled', False)
            status = "✅" if auto_update else "❌"
            print(f"   {status} {server_name:12} | 端口:{port:4} | {name}")
        
        # 组件配置
        components_configs = get_all_components_configs()
        total_components = sum(len(comps) for comps in components_configs.values())
        print(f"\n📊 组件配置 ({total_components} 个)")
        for server_type, components in components_configs.items():
            enabled_count = sum(1 for comp in components.values() 
                              if comp.extra_config.get('enabled', True))
            print(f"   📋 {server_type:12} | {enabled_count}/{len(components)} 个启用")
    
    def list_server_configs(self):
        """列出服务器配置详情"""
        print("🖥️  服务器配置详情")
        print("=" * 80)
        
        servers = self.server_manager.get_all_servers_config()
        
        if not servers:
            print("❌ 没有找到服务器配置")
            return
        
        print(f"{'服务器':^12} | {'端口':^6} | {'自动更新':^8} | {'间隔':^6} | {'最大客户端':^8} | {'名称'}")
        print("-" * 80)
        
        for server_name, config in servers.items():
            port = config.get('port', 'N/A')
            name = config.get('name', 'N/A')
            auto_update = config.get('auto_update', {})
            enabled = "✅" if auto_update.get('enabled', False) else "❌"
            interval = auto_update.get('interval', 'N/A')
            max_clients = auto_update.get('max_clients', 'N/A')
            
            print(f"{server_name:^12} | {port:^6} | {enabled:^8} | {interval:^6} | {max_clients:^8} | {name}")
    
    def list_component_configs(self, server_type: str = None):
        """列出组件配置"""
        if server_type:
            configs = get_components_config(server_type)
            if not configs:
                print(f"❌ 服务器类型 '{server_type}' 不存在或没有配置")
                return
            
            print(f"📊 {server_type} 组件配置")
            print("-" * 70)
            print(f"{'状态':^4} | {'ID':^15} | {'类型':^12} | {'端口':^6} | {'标题'}")
            print("-" * 70)
            
            for comp_id, comp_config in configs.items():
                enabled = comp_config.extra_config.get('enabled', True)
                status = "✅" if enabled else "❌"
                # 从API路径提取端口信息
                api_parts = comp_config.api_path.split('/')
                endpoint = api_parts[-1] if api_parts else comp_config.api_path
                
                print(f"{status:^4} | {comp_id:^15} | {comp_config.type:^12} | {endpoint:^6} | {comp_config.title}")
        else:
            print("📊 所有组件配置")
            print("=" * 60)
            
            configs = get_all_components_configs()
            for server_name, components in configs.items():
                enabled_count = sum(1 for comp in components.values() 
                                  if comp.extra_config.get('enabled', True))
                print(f"\n🖥️  {server_name} ({enabled_count}/{len(components)} 启用)")
                
                for comp_id, comp_config in components.items():
                    enabled = comp_config.extra_config.get('enabled', True)
                    status = "✅" if enabled else "❌"
                    print(f"   {status} {comp_id:15} | {comp_config.type:10} | {comp_config.title}")
    
    def validate_all_configs(self):
        """验证所有配置"""
        print("🔍 验证配置完整性...")
        errors = []
        warnings = []
        
        # 验证服务器配置
        print("\n📋 验证服务器配置...")
        servers = self.server_manager.get_all_servers_config()
        
        if not servers:
            warnings.append("没有配置任何服务器")
        else:
            ports = {}
            for server_name, config in servers.items():
                port = config.get('port')
                if not port:
                    errors.append(f"服务器 {server_name} 缺少端口配置")
                elif port in ports:
                    errors.append(f"端口冲突: {port} - {ports[port]} vs {server_name}")
                else:
                    ports[port] = server_name
                
                if not config.get('name'):
                    warnings.append(f"服务器 {server_name} 缺少名称")
        
        # 验证组件配置
        print("📋 验证组件配置...")
        configs = get_all_components_configs()
        
        for server_type, components in configs.items():
            if not components:
                warnings.append(f"服务器 {server_type} 没有配置任何组件")
                continue
            
            # 检查位置冲突
            positions = {}
            api_paths = {}
            
            for comp_id, comp_config in components.items():
                # 检查必要属性
                required_attrs = ['id', 'type', 'title', 'api_path', 'handler', 'position']
                missing_attrs = [attr for attr in required_attrs if not hasattr(comp_config, attr)]
                if missing_attrs:
                    errors.append(f"{server_type}.{comp_id}: 缺少属性 {missing_attrs}")
                
                # 检查位置冲突
                pos_key = f"{comp_config.position['row']},{comp_config.position['col']}"
                if pos_key in positions:
                    errors.append(f"{server_type}: 位置冲突 {pos_key} - {positions[pos_key]} vs {comp_id}")
                else:
                    positions[pos_key] = comp_id
                
                # 检查API路径重复
                if comp_config.api_path in api_paths:
                    warnings.append(f"{server_type}: API路径重复 {comp_config.api_path} - {api_paths[comp_config.api_path]} vs {comp_id}")
                else:
                    api_paths[comp_config.api_path] = comp_id
        
        # 输出结果
        if not errors and not warnings:
            print("✅ 所有配置验证通过！")
        else:
            if errors:
                print(f"\n❌ 发现 {len(errors)} 个错误:")
                for error in errors:
                    print(f"   • {error}")
            
            if warnings:
                print(f"\n⚠️  发现 {len(warnings)} 个警告:")
                for warning in warnings:
                    print(f"   • {warning}")
        
        return len(errors) == 0
    
    def reload_all_configs(self):
        """重新加载所有配置"""
        print("🔄 重新加载所有配置...")
        try:
            # 重新加载服务器配置
            self.server_manager._load_config()
            print("✅ 服务器配置重新加载成功")
            
            # 重新加载组件配置
            reload_components_configs()
            print("✅ 组件配置重新加载成功")
            
            print("✅ 所有配置重新加载完成")
        except Exception as e:
            print(f"❌ 重新加载失败: {e}")
    
    def show_config_summary(self):
        """显示配置摘要"""
        print("📊 配置摘要")
        print("=" * 50)
        
        # 服务器统计
        servers = self.server_manager.get_all_servers_config()
        server_count = len(servers)
        active_servers = sum(1 for s in servers.values() 
                           if s.get('auto_update', {}).get('enabled', False))
        
        print(f"🖥️  服务器: {active_servers}/{server_count} 启用自动更新")
        
        # 组件统计
        configs = get_all_components_configs()
        total_components = sum(len(comps) for comps in configs.values())
        enabled_components = sum(
            sum(1 for comp in comps.values() if comp.extra_config.get('enabled', True))
            for comps in configs.values()
        )
        
        print(f"📊 组件: {enabled_components}/{total_components} 启用")
        
        # 配置文件状态
        config_dir = os.path.dirname(__file__)
        server_config_path = os.path.join(config_dir, "server_config.json")
        components_config_path = os.path.join(config_dir, "components_config.json")
        
        server_exists = "✅" if os.path.exists(server_config_path) else "❌"
        components_exists = "✅" if os.path.exists(components_config_path) else "❌"
        
        print(f"📁 配置文件:")
        print(f"   {server_exists} server_config.json")
        print(f"   {components_exists} components_config.json")


def main():
    """主函数"""
    manager = UnifiedConfigManager()
    
    if len(sys.argv) < 2:
        print("🔧 统一配置管理工具")
        print("\n使用方法:")
        print("  python config_tool.py list                          # 配置概览")
        print("  python config_tool.py summary                       # 配置摘要")
        print("  python config_tool.py server list                   # 服务器配置详情")
        print("  python config_tool.py components list [server_type] # 组件配置")
        print("  python config_tool.py validate                      # 验证配置")
        print("  python config_tool.py reload                        # 重新加载配置")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        manager.list_all_configs()
    
    elif command == "summary":
        manager.show_config_summary()
    
    elif command == "server":
        if len(sys.argv) > 2 and sys.argv[2] == "list":
            manager.list_server_configs()
        else:
            print("❌ 用法: server list")
    
    elif command == "components":
        if len(sys.argv) > 2 and sys.argv[2] == "list":
            server_type = sys.argv[3] if len(sys.argv) > 3 else None
            manager.list_component_configs(server_type)
        else:
            print("❌ 用法: components list [server_type]")
    
    elif command == "validate":
        manager.validate_all_configs()
    
    elif command == "reload":
        manager.reload_all_configs()
    
    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()
