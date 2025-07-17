#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检查脚本 - 检查运行环境是否满足要求
Environment Check Script - Check if the environment meets requirements
"""

import sys
import subprocess
import importlib
import json
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("🐍 检查 Python 版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}")
        print("   需要 Python 3.7 或更高版本")
        return False
    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_required_packages():
    """检查必需的 Python 包"""
    print("\n📦 检查 Python 依赖包...")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS', 
        'pandas': 'pandas',
        'numpy': 'numpy',
        'plotly': 'plotly'
    }
    
    missing_packages = []
    
    for package, display_name in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - 未安装")
            missing_packages.append(display_name)
    
    if missing_packages:
        print(f"\n⚠️  缺少 {len(missing_packages)} 个必需包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n安装命令:")
        print("pip install flask flask-cors pandas numpy plotly")
        return False
    
    return True

def check_node_environment():
    """检查 Node.js 环境"""
    print("\n🟢 检查 Node.js 环境...")
    
    try:
        # 检查 node
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"✅ Node.js: {node_version}")
        
        # 检查 npm
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, check=True)
        npm_version = result.stdout.strip()
        print(f"✅ npm: {npm_version}")
        
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js 未安装或不在 PATH 中")
        print("   请访问 https://nodejs.org 下载安装")
        return False

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        'package.json',
        'src/main.js',
        'src/App.vue',
        'src/router/index.js',
        'src/config/api.js',
        'api/show_plate_server.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少 {len(missing_files)} 个关键文件")
        return False
    
    return True

def check_npm_dependencies():
    """检查 npm 依赖"""
    print("\n📦 检查 npm 依赖...")
    
    if not Path('package.json').exists():
        print("❌ package.json 不存在")
        return False
    
    if not Path('node_modules').exists():
        print("⚠️  node_modules 不存在，需要运行 npm install")
        return False
    
    print("✅ npm 依赖已安装")
    return True

def check_port_availability():
    """检查端口可用性"""
    print("\n🔌 检查端口可用性...")
    
    import socket
    
    required_ports = [5001, 5002, 5003, 8080]
    occupied_ports = []
    
    for port in required_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  端口 {port} 已被占用")
            occupied_ports.append(port)
        else:
            print(f"✅ 端口 {port} 可用")
    
    if occupied_ports:
        print(f"\n⚠️  {len(occupied_ports)} 个端口被占用，可能影响服务启动")
        return False
    
    return True

def generate_setup_guide():
    """生成安装指南"""
    guide = """
## 🛠️ 环境配置指南

### Python 环境
1. 安装 Python 3.7+: https://www.python.org/downloads/
2. 安装依赖包:
   ```bash
   pip install flask flask-cors pandas numpy plotly
   ```

### Node.js 环境  
1. 安装 Node.js: https://nodejs.org
2. 安装项目依赖:
   ```bash
   npm install
   ```

### 启动服务
1. Windows 用户: 双击 `start-all-services.bat`
2. Linux/Mac 用户: 运行 `./start-all-services.sh`
3. 手动启动: 参考 README.md

### 验证安装
运行环境检查脚本:
```bash
python check-environment.py
```
"""
    
    with open('SETUP_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("\n📝 已生成安装指南: SETUP_GUIDE.md")

def main():
    """主检查函数"""
    print("="*50)
    print("🔍 股票仪表盘系统 - 环境检查")
    print("="*50)
    
    checks = [
        check_python_version(),
        check_required_packages(),
        check_node_environment(), 
        check_project_structure(),
        check_npm_dependencies(),
        check_port_availability()
    ]
    
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    print("\n" + "="*50)
    print(f"📊 检查结果: {passed_checks}/{total_checks} 项通过")
    
    if passed_checks == total_checks:
        print("✅ 恭喜! 环境配置完整，可以启动系统")
        print("\n🚀 启动系统:")
        print("   Windows: start-all-services.bat")
        print("   Linux/Mac: ./start-all-services.sh")
    else:
        print(f"❌ 有 {total_checks - passed_checks} 项检查未通过")
        print("   请按照上述提示解决问题后重新检查")
        generate_setup_guide()
    
    print("="*50)

if __name__ == "__main__":
    main()
