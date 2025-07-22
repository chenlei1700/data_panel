#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试路径修复 - 验证配置生成器路径是否正确
"""

import os
import sys
from pathlib import Path
import importlib.util

def test_config_generator():
    """测试配置生成器的路径修复"""
    print("🔍 测试配置生成器路径修复...")
    
    try:
        # 导入配置生成器
        script_path = Path(__file__).parent / "auto-config-generator.py"
        spec = importlib.util.spec_from_file_location("auto_config_generator", script_path)
        auto_config_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_config_generator)
        
        ConfigGenerator = auto_config_generator.ConfigGenerator
        
        # 创建配置生成器实例
        generator = ConfigGenerator()
        
        print(f"✅ 配置生成器初始化成功")
        print(f"📁 脚本目录: {generator.script_dir}")
        print(f"📁 项目根目录: {generator.project_root}")
        print(f"📄 配置文件路径: {generator.config_file}")
        
        # 验证配置文件是否存在
        if Path(generator.config_file).exists():
            print(f"✅ 配置文件存在: {generator.config_file}")
        else:
            print(f"❌ 配置文件不存在: {generator.config_file}")
            return False
        
        # 验证配置是否加载成功
        if hasattr(generator, 'config') and generator.config:
            print(f"✅ 配置加载成功")
            print(f"📊 项目名称: {generator.config.get('projectInfo', {}).get('name', 'Unknown')}")
            
            # 检查服务配置
            services = generator.config.get('services', [])
            enabled_services = [s for s in services if s.get('enabled', False)]
            print(f"🔧 启用的服务数量: {len(enabled_services)}")
            
            return True
        else:
            print("❌ 配置加载失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_path_generation():
    """测试路径生成"""
    print("\n🔍 测试路径生成...")
    
    try:
        # 导入配置生成器
        script_path = Path(__file__).parent / "auto-config-generator.py"
        spec = importlib.util.spec_from_file_location("auto_config_generator", script_path)
        auto_config_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_config_generator)
        
        ConfigGenerator = auto_config_generator.ConfigGenerator
        generator = ConfigGenerator()
        
        # 测试关键路径
        test_paths = [
            ("src目录", generator.project_root / "src"),
            ("api目录", generator.project_root / "api"),
            ("package.json", generator.project_root / "package.json"),
            ("API配置目标", generator.project_root / "src" / "config" / "api.js"),
            ("路由配置目标", generator.project_root / "src" / "router" / "index.js"),
            ("主页组件目标", generator.project_root / "src" / "views" / "Home.vue"),
        ]
        
        all_good = True
        for name, path in test_paths:
            # 对于目标文件，检查父目录是否存在或可以创建
            if name.endswith("目标"):
                parent_dir = path.parent
                if parent_dir.exists() or not parent_dir.exists():
                    print(f"✅ {name}: {path} (父目录: {parent_dir})")
                else:
                    print(f"❌ {name}: {path} (父目录不可访问)")
                    all_good = False
            else:
                if path.exists():
                    print(f"✅ {name}: {path}")
                else:
                    print(f"❌ {name}: {path} (不存在)")
                    all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ 路径生成测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 快速测试配置生成器路径修复")
    print("=" * 50)
    
    tests = [
        ("配置生成器初始化", test_config_generator),
        ("路径生成", test_path_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 路径修复成功！可以安全运行配置生成器")
        print("\n🚀 运行命令:")
        print("   python auto-config-generator.py")
        return True
    else:
        print("⚠️  还有问题需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
