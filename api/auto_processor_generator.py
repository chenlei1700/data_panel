#!/usr/bin/env python3
"""
自动处理器生成器
根据server_config.json自动生成对应的处理器文件并更新processor_factory.py
Author: chenlei  
Date: 2025-07-26
"""

import json
import os
import sys
import datetime
from pathlib import Path


class ProcessorGenerator:
    """处理器自动生成器"""
    
    def __init__(self, config_dir="config", processors_dir="processors", servers_dir="server"):
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
        self.servers_dir = base_dir / servers_dir
        self.api_dir = base_dir / servers_dir  # 为了兼容性，保持api_dir指向servers_dir
        self.server_config_file = self.config_dir / "server_config.json"
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
    
    def load_processor_template(self):
        """加载处理器模板"""
        try:
            with open(self.processor_template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"错误: 处理器模板文件 {self.processor_template_file} 不存在")
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
    
    def generate_processor_file(self, server_key, server_config):
        """
        生成单个处理器文件
        
        Args:
            server_key: 服务器配置key
            server_config: 服务器配置
        """
        template = self.load_processor_template()
        if not template:
            return False
        
        # 生成类名和文件名
        class_name = self.generate_processor_class_name(server_key)
        processor_filename = f"{server_key}_processor.py"
        processor_file_path = self.processors_dir / processor_filename
        
        # 如果文件已存在，询问是否覆盖
        if processor_file_path.exists():
            # response = input(f"处理器文件 {processor_filename} 已存在，是否覆盖? (y/N): ")
            # if response.lower() != 'y':
            #     print(f"跳过生成 {processor_filename}")
            #     return True
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
            print(f"✅ 成功生成处理器: {processor_filename}")
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
            # response = input(f"服务器文件 {server_filename} 已存在，是否覆盖? (y/N): ")
            # if response.lower() != 'y':
            #     print(f"跳过生成 {server_filename}")
            #     return True
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
    
    def generate_all_processors(self):
        """生成所有处理器"""
        config = self.load_server_config()
        if not config:
            return False
        
        servers = config.get('servers', {})
        if not servers:
            print("警告: 配置中没有找到服务器定义")
            return False
        
        print(f"发现 {len(servers)} 个服务器配置:")
        for key, server_config in servers.items():
            name = server_config.get('name', key)
            port = server_config.get('port', 'N/A')
            print(f"  - {key}: {name} (端口: {port})")
        
        print("\\n开始生成处理器...")
        
        success_count = 0
        server_keys = list(servers.keys())
        
        # 生成每个处理器文件
        for server_key, server_config in servers.items():
            if self.generate_processor_file(server_key, server_config):
                success_count += 1
        
        print(f"\\n生成完成: {success_count}/{len(servers)} 个处理器文件")
        
        # 更新processor_factory.py
        if success_count > 0:
            print("\\n更新processor_factory.py...")
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
        
        print(f"\\n开始生成服务器文件...")
        
        success_count = 0
        
        # 生成每个服务器文件
        for server_key, server_config in servers.items():
            if self.generate_server_file(server_key, server_config):
                success_count += 1
        
        print(f"\\n服务器文件生成完成: {success_count}/{len(servers)} 个")
        
        return success_count == len(servers)
    
    def generate_all_files(self):
        """生成所有文件（处理器+服务器）"""
        print("🚀 开始生成所有文件...")
        
        # 生成处理器
        processor_success = self.generate_all_processors()
        
        # 生成服务器文件
        server_success = self.generate_all_servers()
        
        if processor_success and server_success:
            print("\\n🎉 所有文件生成完成！")
            print("\\n📝 下一步:")
            print("1. 编辑对应的处理器文件实现具体业务逻辑")
            print("2. 在 components_config.json 中添加组件配置")
            print("3. 运行对应的服务器文件")
            return True
        else:
            print("\\n⚠️ 部分文件生成失败，请检查错误信息")
            return False
    
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
    print("🤖 处理器和服务器自动生成器")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"当前目录: {current_dir}")
    
    # 初始化生成器
    generator = ProcessorGenerator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "generate":
            # 生成所有处理器
            print("\\n📋 模式: 生成所有处理器")
            generator.generate_all_processors()
            
        elif command == "generate-servers":
            # 生成所有服务器文件
            print("\\n🖥️ 模式: 生成所有服务器文件")
            generator.generate_all_servers()
            
        elif command == "generate-all":
            # 生成所有文件
            print("\\n🚀 模式: 生成所有文件")
            generator.generate_all_files()
            
        elif command == "add" and len(sys.argv) >= 5:
            # 添加新服务器处理器
            server_key = sys.argv[2]
            server_name = sys.argv[3]
            port = int(sys.argv[4])
            
            print(f"\\n➕ 模式: 添加新服务器处理器")
            print(f"服务器Key: {server_key}")
            print(f"服务器名称: {server_name}")
            print(f"端口: {port}")
            
            generator.add_new_server_processor(server_key, server_name, port)
            
        else:
            print("❌ 无效的命令参数")
            print_usage()
    else:
        # 交互模式
        print("\\n🔄 交互模式")
        print("1. 生成所有处理器")
        print("2. 生成所有服务器文件")
        print("3. 生成所有文件（处理器+服务器）")
        print("4. 添加新服务器处理器")
        print("5. 查看现有处理器")
        
        choice = input("\\n请选择操作 (1-5): ").strip()
        
        if choice == "1":
            generator.generate_all_processors()
        elif choice == "2":
            generator.generate_all_servers()
        elif choice == "3":
            generator.generate_all_files()
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
            print(f"\\n现有处理器: {existing}")
        else:
            print("❌ 无效选择")


def print_usage():
    """打印使用说明"""
    print("""
使用方法:
    python auto_processor_generator.py                              # 交互模式
    python auto_processor_generator.py generate                     # 生成所有处理器
    python auto_processor_generator.py generate-servers             # 生成所有服务器文件
    python auto_processor_generator.py generate-all                 # 生成所有文件
    python auto_processor_generator.py add <key> <name> <port>      # 添加新处理器+服务器
    
示例:
    python auto_processor_generator.py add market_analysis "市场分析页面" 5009
    python auto_processor_generator.py generate-all
    """)


if __name__ == "__main__":
    main()
