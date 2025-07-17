#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置初始化脚本 - 创建通用的项目配置
Config Initialization Script - Create universal project configuration

Author: chenlei
"""

import json
import os
import sys
import shutil
import time
from pathlib import Path
import platform

def detect_python_executable():
    """检测Python可执行文件"""
    python_commands = ['python', 'python3', 'py']
    
    for cmd in python_commands:
        try:
            import subprocess
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return cmd
        except:
            continue
    
    return 'python'  # 默认值

def detect_conda_environment():
    """检测当前conda环境"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        # 尝试获取conda环境的Python路径
        try:
            import subprocess
            result = subprocess.run(['conda', 'info', '--envs'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if conda_env in line and '*' in line:
                        path_parts = line.split()
                        if len(path_parts) >= 2:
                            env_path = path_parts[-1]
                            if platform.system() == 'Windows':
                                python_path = os.path.join(env_path, 'python.exe')
                            else:
                                python_path = os.path.join(env_path, 'bin', 'python')
                            
                            if os.path.exists(python_path):
                                return python_path
        except:
            pass
    
    return None

def create_universal_config():
    """创建通用配置文件"""
    # 基于脚本自身位置确定项目根目录
    project_root = Path(__file__).parent.parent
    config_file = project_root / "project-config.json"
    
    print("🚀 配置初始化向导")
    print("=" * 50)
    print()
    
    # 检查是否已存在配置文件
    if config_file.exists():
        print("⚠️  配置文件已存在")
        overwrite = input("是否覆盖现有配置? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ 已取消")
            return
        
        # 备份现有配置
        backup_file = project_root / f"project-config.backup.{int(time.time())}.json"
        shutil.copy2(config_file, backup_file)
        print(f"✅ 已备份现有配置到: {backup_file}")
        print()
    
    # 项目信息
    print("📋 项目信息配置:")
    project_name = input("项目名称 (默认: 股票仪表盘系统): ").strip() or "股票仪表盘系统"
    project_desc = input("项目描述 (默认: 实时股票数据分析与可视化平台): ").strip() or "实时股票数据分析与可视化平台"
    project_version = input("项目版本 (默认: 1.0.0): ").strip() or "1.0.0"
    
    # 端口配置
    print("\n🔌 端口配置:")
    base_port = input("基础端口 (默认: 5001): ").strip() or "5001"
    frontend_port = input("前端端口 (默认: 8080): ").strip() or "8080"
    
    try:
        base_port = int(base_port)
        frontend_port = int(frontend_port)
    except ValueError:
        print("❌ 端口号必须是数字")
        return
    
    # Python环境配置
    print("\n🐍 Python环境配置:")
    
    # 自动检测Python可执行文件
    detected_python = detect_python_executable()
    conda_python = detect_conda_environment()
    
    if conda_python:
        print(f"✅ 检测到conda环境: {conda_python}")
        python_path = input(f"Python可执行文件路径 (默认: {conda_python}): ").strip() or conda_python
    else:
        print(f"✅ 检测到Python命令: {detected_python}")
        python_path = input(f"Python可执行文件路径 (默认: {detected_python}): ").strip() or detected_python
    
    # API路径配置
    print("\n📁 API路径配置:")
    api_base_path = input("API文件路径 (默认: ./api): ").strip() or "./api"
    
    # 开发配置
    print("\n🛠️  开发配置:")
    auto_open_browser = input("自动打开浏览器 (Y/n): ").strip().lower() not in ['n', 'no']
    enable_hot_reload = input("启用热重载 (Y/n): ").strip().lower() not in ['n', 'no']
    
    # 创建配置对象
    config = {
        "projectInfo": {
            "name": project_name,
            "description": project_desc,
            "version": project_version,
            "basePort": base_port,
            "frontendPort": frontend_port,
            "pythonExecutable": detected_python
        },
        "services": [
            {
                "id": "StockDashboard",
                "name": "基础股票分析",
                "description": "查看股票基础数据、价格走势和技术指标",
                "icon": "📈",
                "port": base_port,
                "path": "/stock-dashboard",
                "title": "股票分析仪表盘",
                "serverFile": "show_plate_server.py",
                "component": "StockDashboard",
                "taskLabel": "股票详细信息服务器",
                "enabled": True
            }
        ],
        "apiEndpoints": {
            "dashboardConfig": "/api/dashboard-config",
            "chartData": "/api/chart-data",
            "tableData": "/api/table-data",
            "updates": "/api/dashboard/updates",
            "health": "/health"
        },
        "developmentConfig": {
            "pythonPath": python_path,
            "apiBasePath": api_base_path,
            "autoOpenBrowser": auto_open_browser,
            "enableHotReload": enable_hot_reload
        }
    }
    
    # 确认配置
    print("\n📋 配置确认:")
    print(f"   项目名称: {project_name}")
    print(f"   项目描述: {project_desc}")
    print(f"   版本: {project_version}")
    print(f"   基础端口: {base_port}")
    print(f"   前端端口: {frontend_port}")
    print(f"   Python路径: {python_path}")
    print(f"   API路径: {api_base_path}")
    print(f"   自动打开浏览器: {auto_open_browser}")
    print(f"   启用热重载: {enable_hot_reload}")
    
    confirm = input("\n确认创建配置? (Y/n): ").strip().lower()
    if confirm in ['n', 'no']:
        print("❌ 已取消")
        return
    
    # 写入配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 配置文件已创建: {config_file}")
    
    # 检查API目录
    api_dir = project_root / "api"
    if not api_dir.exists():
        print("⚠️  API目录不存在，正在创建...")
        api_dir.mkdir(parents=True)
        print(f"✅ 已创建API目录: {api_dir}")
    
    # 询问是否生成配置文件
    generate_configs = input("\n是否立即生成所有配置文件? (Y/n): ").strip().lower()
    if generate_configs not in ['n', 'no']:
        print("\n🔄 正在生成配置文件...")
        try:
            import importlib.util
            auto_config_path = project_root / "scripts" / "auto-config-generator.py"
            spec = importlib.util.spec_from_file_location("auto_config_generator", str(auto_config_path))
            auto_config_generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(auto_config_generator)
            
            generator = auto_config_generator.ConfigGenerator()
            generator.generate_all()
            
            print("\n🎉 配置初始化完成!")
            print("\n🚀 下一步:")
            print("   1. 检查生成的配置文件")
            print("   2. 运行 start-all-services.bat (Windows) 或 ./start-all-services.sh (Linux/Mac)")
            print("   3. 访问 http://localhost:8080")
            
        except Exception as e:
            print(f"❌ 生成配置文件时出错: {e}")
            print("请手动运行: python scripts/auto-config-generator.py")
    
    print("\n📚 相关命令:")
    print("   python scripts/auto-config-generator.py  # 生成配置文件")
    print("   python scripts/quick-add-page.py         # 添加新页面")
    print("   python scripts/check-environment.py     # 检查环境")

def main():
    """主函数"""
    import time
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("""
配置初始化脚本使用说明

用法:
  python scripts/init-config.py        # 交互式创建配置
  python scripts/init-config.py --help # 显示帮助信息

功能:
  - 自动检测Python环境
  - 创建通用的项目配置
  - 支持conda环境检测
  - 自动生成配置文件
            """)
            return
    
    create_universal_config()

if __name__ == "__main__":
    main()
