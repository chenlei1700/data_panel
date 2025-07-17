#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速添加页面工具 - 一键添加新的功能页面
Quick Page Addition Tool - Add new functional pages with one command

Author: chenlei
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

class QuickPageAdder:
    def __init__(self):
        # 基于脚本自身位置确定项目根目录
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / "project-config.json"
        
    def load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            print("❌ 配置文件 project-config.json 不存在")
            print("请先运行: python scripts/auto-config-generator.py")
            sys.exit(1)
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_next_port(self, config):
        """获取下一个可用端口"""
        used_ports = [s['port'] for s in config['services']]
        return max(used_ports) + 1 if used_ports else config['projectInfo']['basePort']
    
    def create_server_template(self, service_info):
        """创建基于框架的服务器文件模板"""
        template = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{service_info['name']} API 服务器
{service_info['description']}
端口: {service_info['port']}

Author: chenlei
"""

from base_server import BaseStockServer, parse_command_line_args
from typing import Dict, Any
import random

class {service_info['id'].title().replace('_', '')}Server(BaseStockServer):
    """{service_info['name']}服务器"""
    
    def __init__(self, port: int = {service_info['port']}):
        super().__init__(name="{service_info['name']}", port=port)
    
    def register_custom_routes(self):
        """注册自定义路由"""
        # 可以在这里添加特定于此服务的路由
        self.app.add_url_rule('/api/custom/info', 'custom_info', self.get_custom_info, methods=['GET'])
    
    def get_dashboard_config(self) -> Dict[str, Any]:
        """返回仪表盘配置"""
        return {{
            "layout": {{
                "rows": 2,
                "cols": 2,
                "components": [
                    {{
                        "id": "chart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/sample-chart",
                        "title": "{service_info['name']}数据图表",
                        "position": {{"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}}
                    }},
                    {{
                        "id": "table1", 
                        "type": "table",
                        "dataSource": "/api/table-data/sample-table",
                        "title": "{service_info['name']}数据表格",
                        "position": {{"row": 1, "col": 0, "rowSpan": 1, "colSpan": 2}}
                    }}
                ]
            }},
            "title": "{service_info['name']}",
            "description": "{service_info['description']}"
        }}
    
    def get_data_sources(self) -> Dict[str, Any]:
        """返回数据源配置"""
        return {{
            "tables": {{
                "sample-table": self._get_sample_table_data()
            }},
            "charts": {{
                "sample-chart": self._create_sample_chart()
            }}
        }}
    
    def _get_sample_table_data(self) -> Dict[str, Any]:
        """生成示例表格数据"""
        data = []
        for i in range(10):
            data.append([
                f"项目{{i+1}}",
                round(random.uniform(1, 100), 2),
                random.choice(["正常", "警告", "异常"]),
                f"2025-07-{{i+1:02d}}"
            ])
        
        return {{
            "columns": ["项目名称", "数值", "状态", "日期"],
            "data": data
        }}
    
    def _create_sample_chart(self) -> str:
        """创建示例图表"""
        categories = [f"类别{{i+1}}" for i in range(5)]
        values = [random.randint(10, 100) for _ in categories]
        
        return self.create_bar_chart(
            categories, 
            values, 
            "{service_info['name']}数据分布",
            "类别",
            "数值"
        )
    
    def get_custom_info(self):
        """自定义信息端点"""
        return {{
            "service": "{service_info['name']}",
            "description": "{service_info['description']}",
            "version": "1.0.0",
            "custom_features": [
                "基于通用框架",
                "快速开发",
                "易于扩展"
            ]
        }}

if __name__ == '__main__':
    port = parse_command_line_args()
    server = {service_info['id'].title().replace('_', '')}Server(port=port)
    server.run()
'''
        
        # 写入服务器文件，使用相对路径
        api_dir = self.project_root / "api"
        api_dir.mkdir(exist_ok=True)
        
        server_path = api_dir / service_info['serverFile']
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"✅ 创建服务器文件: api/{service_info['serverFile']}")
    
    def interactive_add(self):
        """交互式添加新页面"""
        print("🚀 快速添加新页面")
        print("=" * 50)
        
        # 加载配置
        config = self.load_config()
        
        # 显示现有服务
        print("📋 现有服务:")
        for i, service in enumerate(config['services'], 1):
            status = "✅" if service['enabled'] else "❌"
            print(f"   {i}. {status} {service['name']} ({service['id']}) - 端口 {service['port']}")
        print()
        
        # 获取基本信息
        print("📝 请输入新页面信息:")
        service_id = input("🔸 服务ID (英文,如 StockDashboard_ai): ").strip()
        if not service_id:
            print("❌ 服务ID不能为空")
            return
        
        # 检查ID是否已存在
        if any(s['id'] == service_id for s in config['services']):
            print(f"❌ 服务ID '{service_id}' 已存在")
            return
        
        name = input("🔸 服务名称 (中文,如 AI分析): ").strip()
        if not name:
            print("❌ 服务名称不能为空")
            return
        
        description = input("🔸 功能描述: ").strip() or f"{name}功能模块"
        
        # 选择图标
        icons = ["📊", "📈", "🚀", "🎯", "⚡", "🔬", "🤖", "💡", "🌟", "🔥"]
        print(f"🔸 选择图标 (1-{len(icons)}):")
        for i, icon in enumerate(icons, 1):
            print(f"   {i}. {icon}")
        
        icon_choice = input("选择 (默认1): ").strip() or "1"
        try:
            icon = icons[int(icon_choice) - 1]
        except (ValueError, IndexError):
            icon = icons[0]
        
        # 自动生成其他信息
        next_port = self.get_next_port(config)
        path = f"/{service_id.lower().replace('_', '-')}"
        title = f"{name}仪表盘"
        server_file = f"show_plate_server_{service_id.lower()}.py"
        task_label = f"{name}服务器"
        
        # 确认信息
        print("\n📋 配置信息确认:")
        print(f"   服务ID: {service_id}")
        print(f"   名称: {name}")
        print(f"   描述: {description}")
        print(f"   图标: {icon}")
        print(f"   端口: {next_port}")
        print(f"   路径: {path}")
        print(f"   服务器文件: {server_file}")
        
        confirm = input("\n确认添加? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 已取消")
            return
        
        # 创建新服务配置
        new_service = {
            "id": service_id,
            "name": name,
            "description": description,
            "icon": icon,
            "port": next_port,
            "path": path,
            "title": title,
            "serverFile": server_file,
            "component": "StockDashboard",
            "taskLabel": task_label,
            "enabled": True
        }
        
        print("\n🚀 开始创建页面...")
        
        # 1. 添加到配置文件
        config['services'].append(new_service)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ 更新配置文件")
        
        # 2. 创建服务器文件
        self.create_server_template(new_service)
        
        # 3. 重新生成所有配置
        print("🔄 重新生成项目配置...")
        import importlib.util
        auto_config_path = self.project_root / "scripts" / "auto-config-generator.py"
        spec = importlib.util.spec_from_file_location("auto_config_generator", str(auto_config_path))
        auto_config_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_config_generator)
        
        generator = auto_config_generator.ConfigGenerator()
        generator.generate_api_config()
        generator.generate_router_config()
        generator.generate_home_vue()
        generator.generate_vscode_tasks()
        generator.generate_startup_scripts()
        
        print("\n🎉 新页面创建完成!")
        print(f"📋 页面信息:")
        print(f"   - 访问地址: http://localhost:8080{path}")
        print(f"   - API端口: {next_port}")
        print(f"   - 服务器文件: api/{server_file}")
        
        print(f"\n🚀 下一步:")
        print(f"   1. 编辑 api/{server_file} 实现具体业务逻辑")
        print(f"   2. 运行启动脚本: start-all-services.bat")
        print(f"   3. 访问 http://localhost:8080{path} 查看页面")
        
        # 询问是否立即启动
        start_now = input("\n是否立即启动所有服务? (y/N): ").strip().lower()
        if start_now == 'y':
            if os.name == 'nt':  # Windows
                os.system("start-all-services.bat")
            else:  # Linux/Mac
                os.system("./start-all-services.sh")
    
    def batch_add(self, services_config):
        """批量添加服务"""
        config = self.load_config()
        
        print(f"📦 批量添加 {len(services_config)} 个服务...")
        
        for service_info in services_config:
            # 检查ID是否已存在
            if any(s['id'] == service_info['id'] for s in config['services']):
                print(f"⚠️  跳过已存在的服务: {service_info['id']}")
                continue
            
            # 自动分配端口
            service_info['port'] = self.get_next_port(config)
            
            # 添加默认值
            service_info.setdefault('component', 'StockDashboard')
            service_info.setdefault('enabled', True)
            service_info.setdefault('path', f"/{service_info['id'].lower().replace('_', '-')}")
            service_info.setdefault('title', f"{service_info['name']}仪表盘")
            service_info.setdefault('serverFile', f"show_plate_server_{service_info['id'].lower()}.py")
            service_info.setdefault('taskLabel', f"{service_info['name']}服务器")
            
            # 添加到配置
            config['services'].append(service_info)
            
            # 创建服务器文件
            self.create_server_template(service_info)
            
            print(f"✅ 添加服务: {service_info['name']} (端口 {service_info['port']})")
        
        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 重新生成配置
        print("🔄 重新生成项目配置...")
        import importlib.util
        auto_config_path = self.project_root / "scripts" / "auto-config-generator.py"
        spec = importlib.util.spec_from_file_location("auto_config_generator", str(auto_config_path))
        auto_config_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auto_config_generator)
        
        generator = auto_config_generator.ConfigGenerator()
        generator.generate_all()
        
        print("\n🎉 批量添加完成!")

def main():
    adder = QuickPageAdder()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            # 批量添加示例
            example_services = [
                {
                    "id": "StockDashboard_ai",
                    "name": "AI智能分析",
                    "description": "基于机器学习的股票趋势预测",
                    "icon": "🤖"
                },
                {
                    "id": "StockDashboard_risk",
                    "name": "风险监控",
                    "description": "实时风险评估和预警系统",
                    "icon": "⚠️"
                }
            ]
            adder.batch_add(example_services)
        elif sys.argv[1] == "--help":
            print("""
快速添加页面工具使用说明

用法:
  python quick-add-page.py         # 交互式添加新页面
  python quick-add-page.py batch   # 批量添加示例页面
  python quick-add-page.py --help  # 显示帮助信息

功能:
  - 交互式添加新功能页面
  - 自动创建服务器文件模板
  - 自动更新所有配置文件
  - 支持批量添加多个页面
            """)
    else:
        adder.interactive_add()

if __name__ == "__main__":
    main()
