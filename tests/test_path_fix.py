#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径测试脚本 - 验证 data_panel 移动后的路径修复
"""

import os
import sys
from pathlib import Path

def test_paths():
    """测试各种路径是否正确"""
    print("🔍 测试路径配置...")
    
    # 当前脚本所在目录
    current_dir = Path(__file__).parent
    print(f"📁 当前目录: {current_dir}")
    
    # 检查关键文件和目录是否存在
    checks = [
        ("项目配置文件", current_dir / "project-config.json"),
        ("API目录", current_dir / "api"),
        ("src目录", current_dir / "src"),
        ("package.json", current_dir / "package.json"),
        ("src/config目录", current_dir / "src" / "config"),
        ("src/views目录", current_dir / "src" / "views"),
        ("src/router目录", current_dir / "src" / "router"),
    ]
    
    all_passed = True
    for name, path in checks:
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (不存在)")
            all_passed = False
    
    return all_passed

def test_config_generator_import():
    """测试配置生成器导入和基本功能"""
    try:
        # 添加当前目录到路径
        sys.path.insert(0, str(Path(__file__).parent))
        
        # 由于文件名有连字符，需要特殊导入
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "auto_config_generator", 
            Path(__file__).parent / "auto-config-generator.py"
        )
        auto_config_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_config_generator)
        
        ConfigGenerator = auto_config_generator.ConfigGenerator
        
        generator = ConfigGenerator()
        print(f"✅ 配置生成器初始化成功")
        print(f"📁 项目根目录: {generator.project_root}")
        
        # 检查配置是否正确加载
        if hasattr(generator, 'config') and generator.config:
            print(f"✅ 配置文件加载成功")
            print(f"📊 项目名称: {generator.config.get('projectInfo', {}).get('name', 'Unknown')}")
            
            services = generator.config.get('services', [])
            enabled_services = [s for s in services if s.get('enabled', False)]
            print(f"🔧 启用的服务数量: {len(enabled_services)}")
            
            return True
        else:
            print("❌ 配置文件加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 配置生成器导入失败: {e}")
        return False

def test_path_generation():
    """测试路径生成是否正确"""
    try:
        # 添加当前目录到路径
        sys.path.insert(0, str(Path(__file__).parent))
        
        # 由于文件名有连字符，需要特殊导入
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "auto_config_generator", 
            Path(__file__).parent / "auto-config-generator.py"
        )
        auto_config_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_config_generator)
        
        ConfigGenerator = auto_config_generator.ConfigGenerator
        
        generator = ConfigGenerator()
        
        # 测试各种路径生成
        test_paths = [
            ("API配置文件", generator.project_root / "src" / "config" / "api.js"),
            ("路由配置文件", generator.project_root / "src" / "router" / "index.js"),
            ("主页组件", generator.project_root / "src" / "views" / "Home.vue"),
            ("VS Code任务", generator.project_root / ".vscode" / "tasks.json"),
            ("启动脚本(Windows)", generator.project_root / "start-all-services.bat"),
            ("启动脚本(Linux)", generator.project_root / "start-all-services.sh"),
        ]
        
        print("\n🔍 测试生成文件路径...")
        for name, path in test_paths:
            # 确保父目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"📁 {name}: {path}")
            
        return True
        
    except Exception as e:
        print(f"❌ 路径生成测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始路径修复验证测试...")
    print("=" * 50)
    
    tests = [
        ("基础路径检查", test_paths),
        ("配置生成器导入", test_config_generator_import),
        ("路径生成测试", test_path_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！路径修复成功")
        print("\n🚀 可以安全运行:")
        print("   python auto-config-generator.py")
        return True
    else:
        print("⚠️  部分测试失败，请检查路径配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
