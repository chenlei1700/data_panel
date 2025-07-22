#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票仪表盘服务器启动脚本
Server Launcher - 统一管理和启动多个服务器

Author: chenlei
"""

import os
import sys
import argparse
import json
from typing import Dict, List

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from config.server_config import config_manager, apply_quick_config, QUICK_CONFIGS
from show_plate_server_multiplate_v2 import MultiPlateStockServer


def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🚀 股票仪表盘服务器管理工具")
    print("   Stock Dashboard Server Management Tool")
    print("=" * 60)


def list_available_configs():
    """列出可用的配置模板"""
    print("\n📋 可用的配置模板:")
    print("-" * 30)
    for name, config in QUICK_CONFIGS.items():
        status = "启用" if config.get('enabled', True) else "禁用"
        interval = config.get('interval', 'N/A')
        print(f"  • {name:15} - {status}, 间隔: {interval}秒")
    print()


def show_server_status():
    """显示所有服务器状态"""
    print("\n🖥️  服务器状态:")
    print("-" * 40)
    
    servers = config_manager.get_all_servers_config()
    for name, config in servers.items():
        port = config.get('port', 'N/A')
        auto_update = config.get('auto_update', {})
        status = "启用" if auto_update.get('enabled', True) else "禁用"
        interval = auto_update.get('interval', 'N/A')
        
        print(f"  • {name:12} (端口: {port:4}) - 自动更新: {status}, 间隔: {interval}秒")
    print()


def configure_server_interactive():
    """交互式配置服务器"""
    print("\n⚙️  交互式配置向导")
    print("-" * 25)
    
    # 选择服务器
    servers = list(config_manager.get_all_servers_config().keys())
    print("选择要配置的服务器:")
    for i, server in enumerate(servers, 1):
        print(f"  {i}. {server}")
    
    try:
        choice = int(input("\n请输入选择 (1-{}): ".format(len(servers)))) - 1
        if choice < 0 or choice >= len(servers):
            print("❌ 无效选择")
            return
        
        server_name = servers[choice]
        print(f"\n正在配置服务器: {server_name}")
        
        # 配置选项
        print("\n1. 使用快速配置模板")
        print("2. 自定义配置")
        config_choice = input("请选择配置方式 (1/2): ")
        
        if config_choice == "1":
            # 快速配置
            list_available_configs()
            template_name = input("请输入模板名称: ").strip()
            if template_name in QUICK_CONFIGS:
                apply_quick_config(server_name, template_name)
                print(f"✅ 已为 {server_name} 应用配置模板 '{template_name}'")
            else:
                print("❌ 无效的模板名称")
        
        elif config_choice == "2":
            # 自定义配置
            print("\n自定义配置:")
            enabled = input("启用自动更新? (y/n): ").lower() == 'y'
            interval = int(input("更新间隔 (秒): ") or "30")
            max_clients = int(input("最大客户端数: ") or "50")
            
            custom_config = {
                "auto_update": {
                    "enabled": enabled,
                    "interval": interval,
                    "max_clients": max_clients
                }
            }
            
            config_manager.update_server_config(server_name, custom_config)
            print(f"✅ 已保存 {server_name} 的自定义配置")
        
        else:
            print("❌ 无效选择")
    
    except (ValueError, KeyboardInterrupt):
        print("\n❌ 配置已取消")


def start_server(server_name: str, **kwargs):
    """启动指定服务器"""
    print(f"\n🚀 启动服务器: {server_name}")
    
    if server_name == "multiplate":
        server = MultiPlateStockServer(**kwargs)
        print(f"📱 配置管理界面: http://localhost:{server.port}/config")
        server.run(debug=kwargs.get('debug', True))
    else:
        print(f"❌ 未支持的服务器: {server_name}")


def main():
    """主函数"""
    print_banner()
    
    parser = argparse.ArgumentParser(description='股票仪表盘服务器管理工具')
    
    # 主要操作
    parser.add_argument('action', nargs='?', choices=['start', 'config', 'status', 'list-configs'], 
                       default='start', help='执行的操作')
    
    # 服务器选择
    parser.add_argument('--server', '-s', default='multiplate', 
                       help='服务器名称 (multiplate, demo, strong)')
    
    # 配置选项
    parser.add_argument('--port', type=int, help='服务器端口')
    parser.add_argument('--config-template', choices=list(QUICK_CONFIGS.keys()),
                       help='应用配置模板')
    parser.add_argument('--auto-update', action='store_true', help='启用自动更新')
    parser.add_argument('--no-auto-update', action='store_true', help='禁用自动更新')
    parser.add_argument('--interval', type=int, help='自动更新间隔（秒）')
    parser.add_argument('--max-clients', type=int, help='最大SSE客户端数')
    
    # 运行选项
    parser.add_argument('--debug', action='store_true', default=True, help='启用调试模式')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式配置')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'status':
            show_server_status()
            
        elif args.action == 'list-configs':
            list_available_configs()
            
        elif args.action == 'config':
            if args.interactive:
                configure_server_interactive()
            else:
                print("请使用 --interactive 选项进行配置")
                
        elif args.action == 'start':
            # 应用配置模板（如果指定）
            if args.config_template:
                apply_quick_config(args.server, args.config_template)
                print(f"✅ 已为 {args.server} 应用配置模板 '{args.config_template}'")
            
            # 构建启动参数
            start_kwargs = {
                'debug': args.debug
            }
            
            if args.port:
                start_kwargs['port'] = args.port
            
            # 构建自动更新配置
            auto_update_config = {}
            if args.auto_update:
                auto_update_config['enabled'] = True
            elif args.no_auto_update:
                auto_update_config['enabled'] = False
            
            if args.interval:
                auto_update_config['interval'] = args.interval
            
            if args.max_clients:
                auto_update_config['max_clients'] = args.max_clients
            
            if auto_update_config:
                start_kwargs['auto_update_config'] = auto_update_config
            
            # 启动服务器
            start_server(args.server, **start_kwargs)
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
