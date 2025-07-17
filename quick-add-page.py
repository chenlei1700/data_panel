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
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "project-config.json"
        
    def load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            print("❌ 配置文件 project-config.json 不存在")
            print("请先运行: python auto-config-generator.py")
            sys.exit(1)
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_next_port(self, config):
        """获取下一个可用端口"""
        used_ports = [s['port'] for s in config['services']]
        return max(used_ports) + 1 if used_ports else config['projectInfo']['basePort']
    
    def create_server_template(self, service_info):
        """创建服务器文件模板"""
        template = f'''# api/{service_info['serverFile']}
# {service_info['name']} API 服务器
# 端口: {service_info['port']}

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/dashboard-config', methods=['GET'])
def get_dashboard_config():
    """返回仪表盘配置"""
    config = {{
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
        }}
    }}
    return jsonify(config)

@app.route('/api/table-data/<data_type>', methods=['GET'])
def get_table_data(data_type):
    """返回表格数据"""
    try:
        # 示例数据 - 请根据实际需求修改
        if data_type == "sample-table":
            data = {{
                "columns": ["股票代码", "股票名称", "当前价格", "涨跌幅"],
                "data": [
                    ["000001", "平安银行", "12.34", "+2.5%"],
                    ["000002", "万科A", "23.45", "-1.2%"],
                    ["600000", "浦发银行", "8.76", "+0.8%"]
                ]
            }}
        else:
            data = {{"columns": [], "data": []}}
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"获取表格数据失败: {{e}}")
        return jsonify({{"error": str(e)}}), 500

@app.route('/api/chart-data/<chart_type>', methods=['GET'])
def get_chart_data(chart_type):
    """返回图表数据"""
    try:
        # 示例图表数据 - 请根据实际需求修改
        if chart_type == "sample-chart":
            # 创建示例折线图
            x_data = ["09:30", "10:00", "10:30", "11:00", "11:30"]
            y_data = [100, 102, 98, 105, 103]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines+markers',
                name='{service_info['name']}趋势',
                line=dict(color='#2196F3', width=2)
            ))
            
            fig.update_layout(
                title='{service_info['name']}数据趋势',
                xaxis_title='时间',
                yaxis_title='数值',
                template='plotly_white'
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        else:
            return jsonify({{"error": "未知图表类型"}})
            
    except Exception as e:
        logger.error(f"获取图表数据失败: {{e}}")
        return jsonify({{"error": str(e)}}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({{"status": "healthy", "service": "{service_info['name']}"}})

@app.route('/api/dashboard/updates', methods=['GET'])
def dashboard_updates():
    """SSE 数据更新端点"""
    def generate():
        import time
        while True:
            # 发送示例更新数据
            data = {{
                "timestamp": int(time.time() * 1000),
                "type": "data_update",
                "data": {{
                    "message": f"{service_info['name']}数据已更新",
                    "value": np.random.randint(90, 110)
                }}
            }}
            yield f"data: {{json.dumps(data)}}\\n\\n"
            time.sleep(5)  # 每5秒发送一次更新
    
    return app.response_class(generate(), mimetype='text/plain')

if __name__ == '__main__':
    port = {service_info['port']}
    logger.info(f"启动{service_info['name']}API服务，端口: {{port}}")
    app.run(debug=True, host='0.0.0.0', port=port)
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
        spec = importlib.util.spec_from_file_location("auto_config_generator", "auto-config-generator.py")
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
        spec = importlib.util.spec_from_file_location("auto_config_generator", "auto-config-generator.py")
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
