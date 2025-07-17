#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用股票仪表盘服务器基类
Base Stock Dashboard Server - 可重用的服务器框架

Author: chenlei
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import logging
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly
import time
import threading
import queue
from datetime import datetime, timedelta
import random
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple

class BaseStockServer(ABC):
    """股票仪表盘服务器基类"""
    
    def __init__(self, name: str = "股票仪表盘服务", port: int = 5004):
        self.name = name
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # SSE相关
        self.sse_clients = []
        self.latest_update = {"componentId": None, "params": {}}
        
        # 注册通用路由
        self._register_routes()
        
        # 启动后台更新线程
        self.update_thread = threading.Thread(target=self._background_data_update, daemon=True)
        self.update_thread.start()
    
    def _register_routes(self):
        """注册所有路由"""
        # 通用路由
        self.app.add_url_rule('/health', 'health_check', self.health_check, methods=['GET'])
        self.app.add_url_rule('/api/system/info', 'get_system_info', self.get_system_info, methods=['GET'])
        self.app.add_url_rule('/api/dashboard-config', 'get_dashboard_config', self.get_dashboard_config, methods=['GET'])
        
        # 数据路由
        self.app.add_url_rule('/api/table-data/<data_type>', 'get_table_data', self.get_table_data, methods=['GET'])
        self.app.add_url_rule('/api/chart-data/<chart_type>', 'get_chart_data', self.get_chart_data, methods=['GET'])
        
        # SSE路由
        self.app.add_url_rule('/api/dashboard/update', 'update_dashboard', self.update_dashboard, methods=['POST'])
        self.app.add_url_rule('/api/dashboard/updates', 'dashboard_updates', self.dashboard_updates, methods=['GET'])
        
        # 允许子类注册自定义路由
        self.register_custom_routes()
        
        # 兼容旧方法名
        if hasattr(self, 'register_routes') and self.register_routes != self.register_custom_routes:
            self.register_routes()
    
    def register_custom_routes(self):
        """子类可以重写此方法注册自定义路由"""
        pass
    
    @abstractmethod
    def get_dashboard_config(self) -> Dict[str, Any]:
        """获取仪表盘配置 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_data_sources(self) -> Dict[str, Any]:
        """获取数据源配置 - 子类必须实现"""
        pass
    
    # === 通用数据生成方法 ===
    
    def generate_mock_stock_data(self, count: int = 20) -> List[Dict[str, Any]]:
        """生成模拟股票数据"""
        stock_codes = [f"{1000 + i:04d}" for i in range(count)]
        stock_names = [
            "平安银行", "万科A", "招商银行", "中国平安", "美的集团",
            "五粮液", "贵州茅台", "恒瑞医药", "迈瑞医疗", "宁德时代",
            "比亚迪", "海康威视", "立讯精密", "药明康德", "爱尔眼科",
            "东方财富", "海尔智家", "格力电器", "洋河股份", "三安光电"
        ]
        
        data = []
        for i in range(count):
            price = round(random.uniform(5, 150), 2)
            change_pct = round(random.uniform(-10, 10), 2)
            volume = random.randint(1000, 50000)
            
            data.append({
                "股票代码": stock_codes[i],
                "股票名称": stock_names[i % len(stock_names)],
                "当前价格": price,
                "涨跌幅": f"{change_pct:+.2f}%",
                "成交量": volume,
                "市值": round(price * volume / 100, 2)
            })
        
        return data
    
    def generate_mock_sector_data(self) -> List[Dict[str, Any]]:
        """生成模拟板块数据"""
        sectors = [
            "科技板块", "医药板块", "新能源", "金融板块", "消费板块",
            "军工板块", "地产板块", "汽车板块", "钢铁板块", "化工板块"
        ]
        
        data = []
        for sector in sectors:
            change_pct = round(random.uniform(-5, 5), 2)
            data.append({
                "板块名称": sector,
                "涨跌幅": f"{change_pct:+.2f}%",
                "成交额": round(random.uniform(100, 1000), 2),
                "领涨股": random.choice(["股票A", "股票B", "股票C"]),
                "活跃度": random.choice(["高", "中", "低"])
            })
        
        return data
    
    def generate_mock_time_series(self) -> Tuple[List[str], List[float]]:
        """生成模拟时间序列数据"""
        base_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
        times = []
        values = []
        
        current_time = base_time
        current_value = 100
        
        while current_time.hour < 15:
            times.append(current_time.strftime("%H:%M"))
            
            change = random.uniform(-2, 2)
            current_value += change
            values.append(round(current_value, 2))
            
            current_time += timedelta(minutes=5)
            
            if current_time.hour == 11 and current_time.minute == 30:
                current_time = current_time.replace(hour=13, minute=0)
        
        return times, values
    
    # === 通用图表生成方法 ===
    
    def create_line_chart(self, x_data: List, y_data: List, title: str = "线性图", 
                         x_title: str = "X轴", y_title: str = "Y轴") -> str:
        """创建线性图"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name=title,
            line=dict(color='#2196F3', width=2)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white',
            height=300
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_bar_chart(self, x_data: List, y_data: List, title: str = "柱状图",
                        x_title: str = "X轴", y_title: str = "Y轴", colors: Optional[List] = None) -> str:
        """创建柱状图"""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_data,
            y=y_data,
            marker_color=colors or 'lightblue',
            name=title
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title=y_title,
            template='plotly_white',
            height=300
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # === 通用路由处理方法 ===
    
    def get_table_data(self, data_type: str):
        """获取表格数据 - 可被子类重写"""
        try:
            data_sources = self.get_data_sources()
            
            # 检查数据源配置（支持完整路径匹配）
            table_path = f"/api/table-data/{data_type}"
            if table_path in data_sources:
                config = data_sources[table_path]
                
                # 如果配置中有 handler，尝试调用对应的方法
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        return handler_method()
                    else:
                        self.logger.warning(f"Handler方法 {handler_name} 不存在，使用默认处理")
                else:
                    # 如果没有handler，直接返回配置数据
                    return jsonify(config)
            
            # 兼容旧的配置格式 (tables 字典)
            if data_type in data_sources.get('tables', {}):
                config = data_sources['tables'][data_type]
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        return handler_method()
                return jsonify(config)
            
            # 默认处理
            if data_type == "stock-list":
                stock_data = self.generate_mock_stock_data(20)
                return jsonify({
                    "columns": ["股票代码", "股票名称", "当前价格", "涨跌幅", "成交量", "市值"],
                    "data": [[item[col] for col in ["股票代码", "股票名称", "当前价格", "涨跌幅", "成交量", "市值"]] 
                            for item in stock_data]
                })
            elif data_type == "sector-list":
                sector_data = self.generate_mock_sector_data()
                return jsonify({
                    "columns": ["板块名称", "涨跌幅", "成交额", "领涨股", "活跃度"],
                    "data": [[item[col] for col in ["板块名称", "涨跌幅", "成交额", "领涨股", "活跃度"]] 
                            for item in sector_data]
                })
            
            return jsonify({"columns": [], "data": []})
            
        except Exception as e:
            self.logger.error(f"获取表格数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_chart_data(self, chart_type: str):
        """获取图表数据 - 可被子类重写"""
        try:
            data_sources = self.get_data_sources()
            
            # 检查数据源配置（支持完整路径匹配）
            chart_path = f"/api/chart-data/{chart_type}"
            if chart_path in data_sources:
                config = data_sources[chart_path]
                
                # 如果配置中有 handler，尝试调用对应的方法
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        return handler_method()
                    else:
                        self.logger.warning(f"Handler方法 {handler_name} 不存在，使用默认处理")
                else:
                    # 如果没有handler，直接返回配置数据
                    return config
            
            # 兼容旧的配置格式 (charts 字典)
            if chart_type in data_sources.get('charts', {}):
                config = data_sources['charts'][chart_type]
                if isinstance(config, dict) and 'handler' in config:
                    handler_name = config['handler']
                    if hasattr(self, handler_name):
                        handler_method = getattr(self, handler_name)
                        return handler_method()
                return config
            
            # 默认处理
            if chart_type == "stock-trend":
                times, values = self.generate_mock_time_series()
                return self.create_line_chart(times, values, '股票价格走势', '时间', '价格 (元)')
            
            elif chart_type == "sector-performance":
                sector_data = self.generate_mock_sector_data()
                sector_names = [item["板块名称"] for item in sector_data]
                sector_changes = [float(item["涨跌幅"].replace("%", "").replace("+", "")) for item in sector_data]
                colors = ['red' if x < 0 else 'green' for x in sector_changes]
                return self.create_bar_chart(sector_names, sector_changes, '板块表现', '板块', '涨跌幅 (%)', colors)
            
            elif chart_type == "volume-analysis":
                stock_data = self.generate_mock_stock_data(10)
                stock_names = [item["股票名称"] for item in stock_data]
                volumes = [item["成交量"] for item in stock_data]
                return self.create_bar_chart(stock_names, volumes, '成交量分析', '股票', '成交量')
            
            return jsonify({"error": "未知图表类型"})
            
        except Exception as e:
            self.logger.error(f"获取图表数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    # === SSE相关方法 ===
    
    def send_update_to_clients(self, data: Dict[str, Any]):
        """向所有客户端发送更新"""
        message = f"data: {json.dumps(data)}\n\n"
        clients_to_remove = []
        
        for client in list(self.sse_clients):
            try:
                client.put(message)
            except Exception as e:
                self.logger.error(f"发送更新失败: {e}")
                clients_to_remove.append(client)
        
        for client in clients_to_remove:
            try:
                self.sse_clients.remove(client)
            except ValueError:
                pass
    
    def update_dashboard(self):
        """接收仪表盘更新请求"""
        try:
            data = request.json
            component_id = data.get('componentId')
            params = data.get('params', {})
            
            self.logger.info(f"接收到更新请求: componentId={component_id}, params={params}")
            
            self.latest_update = {
                "componentId": component_id,
                "params": params,
                "timestamp": int(time.time() * 1000)
            }
            
            self.send_update_to_clients(self.latest_update)
            
            return jsonify({"status": "success", "message": "更新已发送"})
            
        except Exception as e:
            self.logger.error(f"处理更新请求失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def dashboard_updates(self):
        """SSE端点，向前端推送实时更新"""
        def event_stream():
            client_queue = queue.Queue()
            self.sse_clients.append(client_queue)
            
            try:
                if self.latest_update["componentId"]:
                    yield f"data: {json.dumps(self.latest_update)}\n\n"
                
                while True:
                    try:
                        message = client_queue.get(block=True, timeout=30)
                        yield message
                    except queue.Empty:
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': int(time.time() * 1000)})}\n\n"
                        
            except Exception as e:
                self.logger.error(f"SSE连接错误: {e}")
            finally:
                try:
                    self.sse_clients.remove(client_queue)
                except ValueError:
                    pass
        
        return Response(event_stream(), mimetype='text/event-stream')
    
    def health_check(self):
        """健康检查端点"""
        return jsonify({
            "status": "healthy",
            "service": self.name,
            "version": "1.0.0",
            "timestamp": int(time.time() * 1000),
            "connected_clients": len(self.sse_clients)
        })
    
    def get_system_info(self):
        """获取系统信息"""
        return jsonify({
            "name": self.name,
            "version": "1.0.0",
            "description": "基于通用框架的股票仪表盘服务",
            "features": [
                "实时数据模拟",
                "多种图表类型", 
                "交互式仪表盘",
                "SSE实时更新"
            ],
            "endpoints": {
                "dashboard-config": "/api/dashboard-config",
                "table-data": "/api/table-data/<data_type>",
                "chart-data": "/api/chart-data/<chart_type>",
                "dashboard-updates": "/api/dashboard/updates",
                "health": "/health"
            }
        })
    
    def _background_data_update(self):
        """后台定期更新数据"""
        while True:
            try:
                time.sleep(30)
                
                components = ["chart1", "chart2", "table1", "table2"]
                random_component = random.choice(components)
                
                update_data = {
                    "componentId": random_component,
                    "params": {"auto_refresh": True},
                    "timestamp": int(time.time() * 1000),
                    "type": "auto_update"
                }
                
                if self.sse_clients:
                    self.send_update_to_clients(update_data)
                    self.logger.info(f"后台自动更新: {random_component}")
                    
            except Exception as e:
                self.logger.error(f"后台更新失败: {e}")
    
    def run(self, debug: bool = True, host: str = '0.0.0.0'):
        """启动服务器"""
        self.logger.info(f"启动{self.name}，端口: {self.port}")
        self.app.run(debug=debug, host=host, port=self.port)


def parse_command_line_args() -> int:
    """解析命令行参数获取端口"""
    port = 5004  # 默认端口
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ 端口参数必须是数字")
            sys.exit(1)
    
    # 从环境变量获取端口
    if 'SERVER_PORT' in os.environ:
        try:
            port = int(os.environ['SERVER_PORT'])
        except ValueError:
            pass
    
    return port
