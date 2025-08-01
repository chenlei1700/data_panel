#!/usr/bin/env python3
"""
自动处理器生成器（增强版）
根据server_config.json和components_config.json自动生成对应的处理器文件并更新processor_factory.py
支持基于组件配置的动态处理器生成，包含启动缓存集成
Author: chenlei  
Date: 2025-07-26 (更新: 2025-08-01)
"""

import json
import os
import sys
import datetime
from pathlib import Path
from typing import Dict, List, Any


class ProcessorGenerator:
    """处理器自动生成器（增强版）"""
    
    def __init__(self, config_dir="conf", processors_dir="processors", servers_dir="server"):
        """
        初始化生成器
        
        Args:
            config_dir: 配置文件目录
            processors_dir: 处理器文件目录
            servers_dir: 服务器文件目录
        """
        # 获取脚本所在目录作为基础路径
        base_dir = Path(__file__).parent

        self.config_dir = base_dir / config_dir
        self.processors_dir = base_dir / processors_dir
        self.servers_dir = base_dir / "server"
        self.api_dir = base_dir / "server"  # 为了兼容性，保持api_dir指向server目录
        self.server_config_file = self.config_dir / "server_config.json"
        self.components_config_file = self.config_dir / "components_config.json"
        self.processor_factory_file = self.processors_dir / "processor_factory.py"
        self.processor_template_file = self.processors_dir / "processor_template.txt"
        self.server_template_file = self.servers_dir / "server_template.txt"
        
    def load_server_config(self):
        """加载服务器配置"""
        try:
            with open(self.server_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误: 配置文件 {self.server_config_file} 不存在")
            return None
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件JSON格式错误: {e}")
            return None
    
    def load_components_config(self):
        """加载组件配置"""
        try:
            with open(self.components_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误: 组件配置文件 {self.components_config_file} 不存在")
            return None
        except json.JSONDecodeError as e:
            print(f"错误: 组件配置文件JSON格式错误: {e}")
            return None
    
    def load_server_template(self):
        """加载服务器模板"""
        try:
            with open(self.server_template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"错误: 服务器模板文件 {self.server_template_file} 不存在")
            return None
    
    def generate_processor_class_name(self, server_key):
        """
        根据服务器key生成处理器类名
        
        Args:
            server_key: 服务器配置key
            
        Returns:
            处理器类名 (首字母大写的驼峰命名)
        """
        # 将下划线分割的名称转换为驼峰命名
        parts = server_key.split('_')
        class_name = ''.join(word.capitalize() for word in parts)
        return class_name
    
    def _generate_method_with_cache(self, method_name: str, api_path: str, title: str, 
                                  description: str, component_type: str, cache_strategy: str) -> str:
        """生成带缓存的方法代码"""
        
        if cache_strategy == "startup_once":
            method_code = f'''    def process_{method_name}(self):
        """{title} - 带启动缓存"""
        return self._process_with_startup_cache('{api_path}', self._original_{method_name})
    
    def _original_{method_name}(self):
        """{description}"""
        try:
            # TODO: 实现{title}的数据处理逻辑
            # 组件类型: {component_type}
            # API路径: {api_path}
            
            # 示例返回数据
            result_data = {{
                "title": "{title}",
                "data": [],  # TODO: 填充实际数据
                "metadata": {{
                    "component_type": "{component_type}",
                    "description": "{description}",
                    "api_path": "{api_path}",
                    "cache_strategy": "startup_once"
                }}
            }}
            
            return jsonify(result_data)
            
        except Exception as e:
            return self.error_response(f"获取{title}数据失败: {{str(e)}}")

'''
        elif cache_strategy == "response_cache":
            method_code = f'''    def process_{method_name}(self):
        """{title} - 带响应缓存"""
        return self._process_with_response_cache('{api_path}', self._original_{method_name})
    
    def _original_{method_name}(self):
        """{description}"""
        try:
            # TODO: 实现{title}的数据处理逻辑
            # 组件类型: {component_type}
            # API路径: {api_path}
            
            # 示例返回数据
            result_data = {{
                "title": "{title}",
                "data": [],  # TODO: 填充实际数据
                "metadata": {{
                    "component_type": "{component_type}",
                    "description": "{description}",
                    "api_path": "{api_path}",
                    "cache_strategy": "response_cache"
                }}
            }}
            
            return jsonify(result_data)
            
        except Exception as e:
            return self.error_response(f"获取{title}数据失败: {{str(e)}}")

'''
        else:
            method_code = f'''    def process_{method_name}(self):
        """{title} - 无缓存"""
        try:
            # TODO: 实现{title}的数据处理逻辑
            # 组件类型: {component_type}
            # API路径: {api_path}
            
            # 示例返回数据
            result_data = {{
                "title": "{title}",
                "data": [],  # TODO: 填充实际数据
                "metadata": {{
                    "component_type": "{component_type}",
                    "description": "{description}",
                    "api_path": "{api_path}",
                    "cache_strategy": "none"
                }}
            }}
            
            return jsonify(result_data)
            
        except Exception as e:
            return self.error_response(f"获取{title}数据失败: {{str(e)}}")

'''
        
        return method_code

    def _generate_core_methods(self):
        """生成核心必要方法：process, config, get_available_methods"""
        return '''
    def process(self, method_name: str, *args, **kwargs):
        """处理数据请求的统一入口方法"""
        try:
            # 获取原始方法名（移除process_前缀）
            original_method = method_name.replace('process_', '') if method_name.startswith('process_') else method_name
            
            # 查找对应的方法
            method_to_call = None
            for attr_name in dir(self):
                if not attr_name.startswith('_') and attr_name != 'process':
                    if attr_name == f"process_{original_method}" or attr_name == original_method:
                        method_to_call = getattr(self, attr_name)
                        break
            
            if method_to_call and callable(method_to_call):
                return method_to_call(*args, **kwargs)
            else:
                return self.error_response(f"未找到方法: {method_name}")
                
        except Exception as e:
            return self.error_response(f"处理请求时发生错误: {str(e)}")

    def config(self):
        """获取处理器配置信息"""
        try:
            available_methods = self.get_available_methods()
            return jsonify({
                "processor_name": self.__class__.__name__,
                "available_methods": available_methods,
                "description": "自动生成的数据处理器",
                "version": "1.0.0"
            })
        except Exception as e:
            return self.error_response(f"获取配置信息失败: {str(e)}")

    def get_available_methods(self):
        """获取所有可用的处理方法"""
        try:
            methods = []
            for attr_name in dir(self):
                if not attr_name.startswith('_') and attr_name not in ['process', 'config', 'get_available_methods', 'error_response']:
                    attr = getattr(self, attr_name)
                    if callable(attr):
                        methods.append(attr_name)
            return methods
        except Exception as e:
            return []
'''
    
    def generate_processor_with_components(self, server_key: str, server_config: Dict[str, Any]) -> str:
        """基于组件配置生成处理器代码"""
        
        # 加载组件配置
        components_config = self.load_components_config()
        if not components_config or server_key not in components_config:
            print(f"❌ 未找到 {server_key} 的组件配置")
            return None
        
        server_components = components_config[server_key]
        
        # 生成类名
        class_name = self.generate_processor_class_name(server_key)
        
        # 获取组件列表（处理两种可能的结构）
        components = []
        if isinstance(server_components, dict):
            if 'components' in server_components:
                # 如果有components字段，使用它
                components = server_components['components']
            else:
                # 否则直接遍历字典中的组件
                for comp_key, comp_value in server_components.items():
                    if isinstance(comp_value, dict) and 'api_path' in comp_value:
                        components.append(comp_value)
        
        # 文件头
        header = f'''"""
{server_key}处理器
根据components_config.json和server_config.json自动生成
Author: Auto-generated
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from flask import jsonify
from .base_processor import BaseDataProcessor

class {class_name}Processor(BaseDataProcessor):
    """
    {server_key}数据处理器
    
    基于components_config.json中的{server_key}配置自动生成
    包含以下组件的处理方法:
'''
        
        # 添加组件列表到docstring
        for component in components:
            title = component.get('title', 'Unknown')
            description = component.get('description', 'No description')
            header += f"    - {title}: {description}\n"
        
        header += '    """\n\n'
        
        # 生成所有方法
        methods = ""
        for component in components:
            api_path = component.get('api_path', '')
            title = component.get('title', 'Unknown')
            description = component.get('description', 'No description')
            component_type = component.get('component_type', 'unknown')
            cache_strategy = component.get('cache_strategy', 'startup_once')  # 默认使用启动缓存
            
            # 从API路径生成方法名
            method_name = api_path.strip('/').replace('/', '_').replace('-', '_')
            if method_name.startswith('api_'):
                method_name = method_name[4:]  # 移除api_前缀
            if not method_name:
                method_name = title.lower().replace(' ', '_').replace('-', '_')
            
            method_code = self._generate_method_with_cache(
                method_name, api_path, title, description, 
                component_type, cache_strategy
            )
            methods += method_code
        
        # 生成核心方法
        core_methods = self._generate_core_methods()
        
        # 组合完整的代码
        full_code = header + methods + core_methods
        
        return full_code
    
    def generate_processor_file(self, server_key, server_config, use_components=True):
        """
        生成单个处理器文件
        
        Args:
            server_key: 服务器配置key
            server_config: 服务器配置
            use_components: 是否使用组件配置生成（默认True）
        """
        
        # 优先尝试使用组件配置生成
        if use_components:
            processor_content = self.generate_processor_with_components(server_key, server_config)
            if processor_content:
                # 生成文件名
                processor_filename = f"{server_key}_processor.py"
                processor_file_path = self.processors_dir / processor_filename
                
                # 如果文件已存在，询问是否覆盖
                if processor_file_path.exists():
                    print(f"⚠️ 处理器文件 {processor_filename} 已存在，跳过生成")
                    return True
                
                # 写入文件
                try:
                    with open(processor_file_path, 'w', encoding='utf-8') as f:
                        f.write(processor_content)
                    print(f"✅ 成功生成组件化处理器: {processor_filename}")
                    return True
                except Exception as e:
                    print(f"❌ 生成处理器 {processor_filename} 失败: {e}")
                    return False
        
        # 回退到模板生成
        template = self.load_processor_template()
        if not template:
            return False
        
        # 生成类名和文件名
        class_name = self.generate_processor_class_name(server_key)
        processor_filename = f"{server_key}_processor.py"
        processor_file_path = self.processors_dir / processor_filename
        
        # 如果文件已存在，询问是否覆盖
        if processor_file_path.exists():
            print(f"⚠️ 处理器文件 {processor_filename} 已存在，跳过生成")
            return True
        
        # 替换模板中的占位符
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        description = server_config.get('name', f'{server_key}服务器')
        
        processor_content = template.format(
            processor_name=server_key,
            class_name=class_name,
            date=current_date,
            description=description
        )
        
        # 写入文件
        try:
            with open(processor_file_path, 'w', encoding='utf-8') as f:
                f.write(processor_content)
            print(f"✅ 成功生成模板处理器: {processor_filename}")
            return True
        except Exception as e:
            print(f"❌ 生成处理器 {processor_filename} 失败: {e}")
            return False
    
    def generate_server_file(self, server_key, server_config):
        """
        生成单个服务器文件
        
        Args:
            server_key: 服务器配置key
            server_config: 服务器配置
        """
        template = self.load_server_template()
        if not template:
            return False
        
        # 生成类名和文件名
        class_name = self.generate_processor_class_name(server_key)
        server_filename = f"{server_key}_server.py"
        server_file_path = self.servers_dir / server_filename
        
        # 如果文件已存在，询问是否覆盖
        if server_file_path.exists():
            print(f"⚠️ 服务器文件 {server_filename} 已存在，跳过生成")
            return True
        
        # 替换模板中的占位符
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        description = server_config.get('name', f'{server_key}服务器')
        default_port = server_config.get('port', 5000)
        
        server_content = template.format(
            server_type=server_key,
            class_name=class_name,
            date=current_date,
            description=description,
            default_port=default_port
        )
        
        # 写入文件
        try:
            with open(server_file_path, 'w', encoding='utf-8') as f:
                f.write(server_content)
            print(f"✅ 成功生成服务器: {server_filename}")
            return True
        except Exception as e:
            print(f"❌ 生成服务器 {server_filename} 失败: {e}")
            return False
    
    def get_existing_processors(self):
        """获取现有的处理器文件列表"""
        processors = []
        for file_path in self.processors_dir.glob("*_processor.py"):
            if file_path.name != "processor_template.py":
                processor_name = file_path.stem.replace("_processor", "")
                processors.append(processor_name)
        return processors
    
    def update_processor_factory(self, server_keys):
        """
        更新processor_factory.py文件 - 现在使用动态导入，无需修改文件
        
        Args:
            server_keys: 服务器配置keys列表
        """
        print("✅ processor_factory.py 支持动态导入，无需更新")
        return True
    
    def list_components_for_server(self, server_type: str = None):
        """列出指定服务器类型的组件信息"""
        
        components_config = self.load_components_config()
        if not components_config:
            return
        
        if server_type:
            if server_type not in components_config:
                print(f"❌ 找不到服务器类型: {server_type}")
                return
            
            server_configs = {server_type: components_config[server_type]}
        else:
            server_configs = components_config
        
        for srv_type, config in server_configs.items():
            # 获取组件列表（处理两种可能的结构）
            components = []
            if isinstance(config, dict):
                if 'components' in config:
                    # 如果有components字段，使用它
                    components = config['components']
                else:
                    # 否则直接遍历字典中的组件
                    for comp_key, comp_value in config.items():
                        if isinstance(comp_value, dict) and 'api_path' in comp_value:
                            components.append(comp_value)
            
            print(f"\n📋 {srv_type} 组件列表:")
            print(f"   总数: {len(components)}")
            
            for i, component in enumerate(components, 1):
                api_path = component.get('api_path', 'N/A')
                title = component.get('title', 'Unknown')
                cache_strategy = component.get('cache_strategy', 'startup_once')
                method_name = api_path.strip('/').replace('/', '_').replace('-', '_')
                if method_name.startswith('api_'):
                    method_name = method_name[4:]
                
                print(f"   {i:2d}. {title}")
                print(f"       方法: process_{method_name}()")
                print(f"       路径: {api_path}")
                print(f"       缓存: {cache_strategy}")
    
    def generate_all_processors_with_components(self):
        """生成所有基于组件配置的处理器"""
        config = self.load_server_config()
        components_config = self.load_components_config()
        
        if not config:
            return False
        
        if not components_config:
            print("❌ 未找到组件配置文件，无法生成处理器")
            return False
        
        servers = config.get('servers', {})
        if not servers:
            print("警告: 配置中没有找到服务器定义")
            return False
        
        print(f"🔍 发现 {len(servers)} 个服务器配置:")
        for key, server_config in servers.items():
            name = server_config.get('name', key)
            port = server_config.get('port', 'N/A')
            has_components = key in components_config
            print(f"  - {key}: {name} (端口: {port}) {'✅有组件配置' if has_components else '❌无组件配置'}")
        
        print("\n🚀 开始生成组件化处理器...")
        
        success_count = 0
        server_keys = list(servers.keys())
        
        # 生成每个处理器文件
        for server_key, server_config in servers.items():
            if self.generate_processor_file(server_key, server_config, use_components=True):
                success_count += 1
        
        print(f"\n✅ 生成完成: {success_count}/{len(servers)} 个处理器文件")
        
        # 更新processor_factory.py
        if success_count > 0:
            print("\n🔧 更新processor_factory.py...")
            self.update_processor_factory(server_keys)
        
        return success_count == len(servers)
    
    def generate_all_servers(self):
        """生成所有服务器文件"""
        config = self.load_server_config()
        if not config:
            return False
        
        servers = config.get('servers', {})
        if not servers:
            print("警告: 配置中没有找到服务器定义")
            return False
        
        print(f"\n开始生成服务器文件...")
        
        success_count = 0
        
        # 生成每个服务器文件
        for server_key, server_config in servers.items():
            if self.generate_server_file(server_key, server_config):
                success_count += 1
        
        print(f"\n服务器文件生成完成: {success_count}/{len(servers)} 个")
        
        return success_count == len(servers)
    
    def add_new_server_processor(self, server_key, server_name, port):
        """
        添加新的服务器处理器
        
        Args:
            server_key: 服务器key
            server_name: 服务器名称  
            port: 端口号
        """
        # 1. 更新server_config.json
        config = self.load_server_config()
        if not config:
            return False
        
        if 'servers' not in config:
            config['servers'] = {}
        
        # 添加新服务器配置
        config['servers'][server_key] = {
            "port": port,
            "name": server_name,
            "auto_update": {
                "enabled": True,
                "interval": 30,
                "random_selection": True,
                "max_clients": 30,
                "heartbeat_interval": 30
            }
        }
        
        # 保存配置文件
        try:
            with open(self.server_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ 已更新server_config.json，添加服务器: {server_key}")
        except Exception as e:
            print(f"❌ 更新server_config.json失败: {e}")
            return False
        
        # 2. 生成处理器文件
        server_config = config['servers'][server_key]
        if not self.generate_processor_file(server_key, server_config):
            return False
        
        # 3. 生成服务器文件
        if not self.generate_server_file(server_key, server_config):
            return False
        
        # 4. 更新processor_factory.py
        server_keys = list(config['servers'].keys())
        return self.update_processor_factory(server_keys)


def main():
    """主函数"""
    print("🤖 处理器和服务器自动生成器（增强版）")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"当前目录: {current_dir}")
    
    # 初始化生成器
    generator = ProcessorGenerator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "generate":
            # 生成所有处理器（基础模板）
            print("\n📋 模式: 生成所有处理器（基础模板）")
            generator.generate_all_processors()
            
        elif command == "generate-with-components":
            # 生成所有处理器（基于组件配置）
            print("\n🧩 模式: 生成所有处理器（基于组件配置）")
            generator.generate_all_processors_with_components()
            
        elif command == "generate-servers":
            # 生成所有服务器文件
            print("\n🖥️ 模式: 生成所有服务器文件")
            generator.generate_all_servers()
            
        elif command == "generate-all":
            # 生成所有文件
            print("\n🚀 模式: 生成所有文件")
            generator.generate_all_files()
            
        elif command == "generate-all-with-components":
            # 生成所有文件（基于组件配置）
            print("\n🚀 模式: 生成所有文件（基于组件配置）")
            print("\n🧩 生成组件化处理器...")
            processor_success = generator.generate_all_processors_with_components()
            print("\n🖥️ 生成服务器文件...")
            server_success = generator.generate_all_servers()
            
            if processor_success and server_success:
                print("\n🎉 所有文件生成完成！")
                print("\n📝 下一步:")
                print("1. 编辑对应的处理器文件实现具体业务逻辑")
                print("2. 检查 components_config.json 中的组件配置")
                print("3. 运行对应的服务器文件")
            else:
                print("\n⚠️ 部分文件生成失败，请检查错误信息")
            
        elif command == "list-components":
            # 列出组件信息
            server_type = sys.argv[2] if len(sys.argv) > 2 else None
            print(f"\n📋 模式: 列出组件信息" + (f" ({server_type})" if server_type else ""))
            generator.list_components_for_server(server_type)
            
        elif command == "add" and len(sys.argv) >= 5:
            # 添加新服务器处理器
            server_key = sys.argv[2]
            server_name = sys.argv[3]
            port = int(sys.argv[4])
            
            print(f"\n➕ 模式: 添加新服务器处理器")
            print(f"服务器Key: {server_key}")
            print(f"服务器名称: {server_name}")
            print(f"端口: {port}")
            
            generator.add_new_server_processor(server_key, server_name, port)
            
        else:
            print("❌ 无效的命令参数")
            print_usage()
    else:
        # 交互模式
        print("\n🔄 交互模式")
        print("1. 生成所有处理器（基于组件配置）")
        print("2. 生成所有服务器文件")
        print("3. 生成所有文件（处理器+服务器）")
        print("4. 添加新服务器处理器")
        print("5. 查看现有处理器")
        print("6. 列出组件信息")
        
        choice = input("\n请选择操作 (1-6): ").strip()
        
        if choice == "1":
            generator.generate_all_processors_with_components()
        elif choice == "2":
            generator.generate_all_servers()
        elif choice == "3":
            print("\n🧩 生成组件化处理器...")
            processor_success = generator.generate_all_processors_with_components()
            print("\n🖥️ 生成服务器文件...")
            server_success = generator.generate_all_servers()
            
            if processor_success and server_success:
                print("\n🎉 所有文件生成完成！")
            else:
                print("\n⚠️ 部分文件生成失败")
        elif choice == "4":
            server_key = input("输入服务器key (如: market_analysis): ").strip()
            server_name = input("输入服务器名称 (如: 市场分析页面): ").strip()
            port = input("输入端口号 (如: 5009): ").strip()
            
            try:
                port = int(port)
                generator.add_new_server_processor(server_key, server_name, port)
            except ValueError:
                print("❌ 端口号必须是数字")
        elif choice == "5":
            existing = generator.get_existing_processors()
            print(f"\n现有处理器: {existing}")
        elif choice == "6":
            server_type = input("输入服务器类型 (留空查看所有): ").strip()
            if not server_type:
                server_type = None
            generator.list_components_for_server(server_type)
        else:
            print("❌ 无效选择")


def print_usage():
    """打印使用说明"""
    print("""
使用方法:
    python auto_processor_server_generator.py                              # 交互模式
    python auto_processor_server_generator.py generate                     # 生成所有处理器（基础模板）
    python auto_processor_server_generator.py generate-with-components     # 生成所有处理器（基于组件配置）
    python auto_processor_server_generator.py generate-servers             # 生成所有服务器文件
    python auto_processor_server_generator.py generate-all                 # 生成所有文件（基础）
    python auto_processor_server_generator.py generate-all-with-components # 生成所有文件（组件化）
    python auto_processor_server_generator.py list-components [server]     # 列出组件信息
    python auto_processor_server_generator.py add <key> <name> <port>      # 添加新处理器+服务器
    
示例:
    python auto_processor_server_generator.py generate-with-components
    python auto_processor_server_generator.py list-components market_review
    python auto_processor_server_generator.py add market_analysis "市场分析页面" 5009
    python auto_processor_server_generator.py generate-all-with-components
    
功能说明:
    - 基础模板：使用processor_template.txt生成简单的处理器框架
    - 组件化生成：基于components_config.json自动生成完整的处理器方法，包含启动缓存支持
    - 支持多种缓存策略：startup_once（启动缓存）、response_cache（响应缓存）、none（无缓存）
    """)


if __name__ == "__main__":
    main()
