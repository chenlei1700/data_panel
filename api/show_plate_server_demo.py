# api/show_plate_server_demo.py
# 股票仪表盘演示服务 - 不依赖外部数据的示例服务
# 支持动态端口配置
# Author: chenlei

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

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
sse_clients = []  # 存储所有SSE连接的客户端队列
latest_update = {"componentId": None, "params": {}}  # 最新的更新状态

# 生成模拟股票数据
def generate_mock_stock_data(count=20):
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
        # 生成随机股票数据
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

# 生成模拟板块数据
def generate_mock_sector_data():
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

# 生成模拟时间序列数据
def generate_mock_time_series():
    """生成模拟时间序列数据"""
    base_time = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
    times = []
    values = []
    
    # 生成一个交易日的数据 (9:30-15:00)
    current_time = base_time
    current_value = 100
    
    while current_time.hour < 15:
        times.append(current_time.strftime("%H:%M"))
        
        # 随机走势
        change = random.uniform(-2, 2)
        current_value += change
        values.append(round(current_value, 2))
        
        # 每5分钟一个数据点
        current_time += timedelta(minutes=5)
        
        # 午间休市
        if current_time.hour == 11 and current_time.minute == 30:
            current_time = current_time.replace(hour=13, minute=0)
    
    return times, values

@app.route('/api/dashboard-config', methods=['GET'])
def get_dashboard_config():
    """返回仪表盘配置"""
    config = {
        "layout": {
            "rows": 4,
            "cols": 2,
            "components": [
                {
                    "id": "chart1",
                    "type": "chart",
                    "dataSource": "/api/chart-data/stock-trend",
                    "title": "股票走势图",
                    "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
                },
                {
                    "id": "chart2", 
                    "type": "chart",
                    "dataSource": "/api/chart-data/sector-performance",
                    "title": "板块表现",
                    "position": {"row": 0, "col": 1, "rowSpan": 1, "colSpan": 1}
                },
                {
                    "id": "table1",
                    "type": "table",
                    "dataSource": "/api/table-data/stock-list",
                    "title": "股票列表",
                    "position": {"row": 1, "col": 0, "rowSpan": 2, "colSpan": 1}
                },
                {
                    "id": "table2",
                    "type": "table", 
                    "dataSource": "/api/table-data/sector-list",
                    "title": "板块列表",
                    "position": {"row": 1, "col": 1, "rowSpan": 2, "colSpan": 1}
                },
                {
                    "id": "chart3",
                    "type": "chart",
                    "dataSource": "/api/chart-data/volume-analysis",
                    "title": "成交量分析",
                    "position": {"row": 3, "col": 0, "rowSpan": 1, "colSpan": 2}
                }
            ]
        },
        "title": "股票仪表盘演示系统",
        "description": "这是一个演示系统，使用模拟数据展示股票分析功能"
    }
    return jsonify(config)

@app.route('/api/table-data/<data_type>', methods=['GET'])
def get_table_data(data_type):
    """返回表格数据"""
    try:
        if data_type == "stock-list":
            # 生成股票列表数据
            stock_data = generate_mock_stock_data(20)
            return jsonify({
                "columns": ["股票代码", "股票名称", "当前价格", "涨跌幅", "成交量", "市值"],
                "data": [[item[col] for col in ["股票代码", "股票名称", "当前价格", "涨跌幅", "成交量", "市值"]] 
                        for item in stock_data]
            })
        
        elif data_type == "sector-list":
            # 生成板块列表数据
            sector_data = generate_mock_sector_data()
            return jsonify({
                "columns": ["板块名称", "涨跌幅", "成交额", "领涨股", "活跃度"],
                "data": [[item[col] for col in ["板块名称", "涨跌幅", "成交额", "领涨股", "活跃度"]] 
                        for item in sector_data]
            })
        
        else:
            return jsonify({"columns": [], "data": []})
            
    except Exception as e:
        logger.error(f"获取表格数据失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart-data/<chart_type>', methods=['GET'])
def get_chart_data(chart_type):
    """返回图表数据"""
    try:
        if chart_type == "stock-trend":
            # 生成股票走势图
            times, values = generate_mock_time_series()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=values,
                mode='lines+markers',
                name='股票走势',
                line=dict(color='#2196F3', width=2)
            ))
            
            fig.update_layout(
                title='股票价格走势',
                xaxis_title='时间',
                yaxis_title='价格 (元)',
                template='plotly_white',
                height=300
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        elif chart_type == "sector-performance":
            # 生成板块表现柱状图
            sector_data = generate_mock_sector_data()
            sector_names = [item["板块名称"] for item in sector_data]
            sector_changes = [float(item["涨跌幅"].replace("%", "").replace("+", "")) for item in sector_data]
            
            colors = ['red' if x < 0 else 'green' for x in sector_changes]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sector_names,
                y=sector_changes,
                marker_color=colors,
                name='板块涨跌幅'
            ))
            
            fig.update_layout(
                title='板块表现',
                xaxis_title='板块',
                yaxis_title='涨跌幅 (%)',
                template='plotly_white',
                height=300
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        elif chart_type == "volume-analysis":
            # 生成成交量分析图
            stock_data = generate_mock_stock_data(10)
            stock_names = [item["股票名称"] for item in stock_data]
            volumes = [item["成交量"] for item in stock_data]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=stock_names,
                y=volumes,
                marker_color='lightblue',
                name='成交量'
            ))
            
            fig.update_layout(
                title='成交量分析',
                xaxis_title='股票',
                yaxis_title='成交量',
                template='plotly_white',
                height=300
            )
            
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        else:
            return jsonify({"error": "未知图表类型"})
            
    except Exception as e:
        logger.error(f"获取图表数据失败: {e}")
        return jsonify({"error": str(e)}), 500

def send_update_to_clients(data):
    """向所有客户端发送更新"""
    message = f"data: {json.dumps(data)}\n\n"
    clients_to_remove = []
    
    for client in list(sse_clients):
        try:
            client.put(message)
        except Exception as e:
            logger.error(f"发送更新失败: {e}")
            clients_to_remove.append(client)
    
    # 清理断开的客户端
    for client in clients_to_remove:
        try:
            sse_clients.remove(client)
        except ValueError:
            pass

@app.route('/api/dashboard/update', methods=['POST'])
def update_dashboard():
    """接收仪表盘更新请求"""
    global latest_update
    
    try:
        data = request.json
        component_id = data.get('componentId')
        params = data.get('params', {})
        
        logger.info(f"接收到更新请求: componentId={component_id}, params={params}")
        
        # 更新全局状态
        latest_update = {
            "componentId": component_id,
            "params": params,
            "timestamp": int(time.time() * 1000)
        }
        
        # 广播更新给所有客户端
        send_update_to_clients(latest_update)
        
        return jsonify({"status": "success", "message": "更新已发送"})
        
    except Exception as e:
        logger.error(f"处理更新请求失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/updates', methods=['GET'])
def dashboard_updates():
    """SSE端点，向前端推送实时更新"""
    def event_stream():
        client_queue = queue.Queue()
        sse_clients.append(client_queue)
        
        try:
            # 发送当前状态
            if latest_update["componentId"]:
                yield f"data: {json.dumps(latest_update)}\n\n"
            
            # 持续监听更新
            while True:
                try:
                    message = client_queue.get(block=True, timeout=30)
                    yield message
                except queue.Empty:
                    # 发送心跳
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': int(time.time() * 1000)})}\n\n"
                    
        except Exception as e:
            logger.error(f"SSE连接错误: {e}")
        finally:
            try:
                sse_clients.remove(client_queue)
            except ValueError:
                pass
    
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "service": "股票仪表盘演示服务",
        "version": "1.0.0",
        "timestamp": int(time.time() * 1000),
        "connected_clients": len(sse_clients)
    })

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    return jsonify({
        "name": "股票仪表盘演示系统",
        "version": "1.0.0",
        "description": "这是一个演示系统，使用模拟数据展示股票分析功能",
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

# 启动后台数据更新线程
def background_data_update():
    """后台定期更新数据"""
    while True:
        try:
            # 每30秒随机更新一次数据
            time.sleep(30)
            
            # 随机选择一个组件进行更新
            components = ["chart1", "chart2", "table1", "table2"]
            random_component = random.choice(components)
            
            update_data = {
                "componentId": random_component,
                "params": {"auto_refresh": True},
                "timestamp": int(time.time() * 1000),
                "type": "auto_update"
            }
            
            # 只有在有客户端连接时才发送更新
            if sse_clients:
                send_update_to_clients(update_data)
                logger.info(f"后台自动更新: {random_component}")
                
        except Exception as e:
            logger.error(f"后台更新失败: {e}")

if __name__ == '__main__':
    # 启动后台更新线程
    update_thread = threading.Thread(target=background_data_update, daemon=True)
    update_thread.start()
    
    # 支持命令行参数指定端口
    port = 5004  # 默认端口
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ 端口参数必须是数字")
            sys.exit(1)
    
    # 从环境变量获取端口（用于批处理脚本）
    if 'SERVER_PORT' in os.environ:
        try:
            port = int(os.environ['SERVER_PORT'])
        except ValueError:
            pass
    
    logger.info(f"启动股票仪表盘演示服务，端口: {port}")
    logger.info("这是一个演示系统，使用模拟数据，不依赖外部数据源")
    app.run(debug=True, host='0.0.0.0', port=port)
