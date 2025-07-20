#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: chenlei
Date: 2024-01-20
Description: 综合图表演示服务器 - 基于新框架重构版本
功能: 提供多种图表类型的综合演示:
     - 堆叠面积图 (资金流向、板块表现、风险分布)
     - 折线图 (股价趋势)
     - 柱状图 (成交量)
     - 饼图 (板块分布)
     - 仪表盘 (市场情绪)
     - 组合图 (价格-成交量)
     - 散点图 (风险-收益)
     - 智能表格 (支持多种背景色规则)
"""

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import plotly
import plotly.graph_objects as go
import os
import sys
import queue
from flask import request, Response, jsonify
from flask_cors import CORS

# 导入新框架基类
from base_server import BaseStockServer

class StackedAreaDemoServer(BaseStockServer):
    """综合图表演示服务器 - 继承自BaseStockServer
    
    提供多种图表类型的完整演示:
    - 堆叠面积图、折线图、柱状图、饼图
    - 仪表盘、组合图、散点图
    - 智能表格 (支持条件背景色)
    """
    
    def __init__(self, port=5004):
        super().__init__(name="综合图表演示", port=port)
        
        # 服务特定的配置
        self.stacked_data_cache = {}
        self.dynamic_titles = {
            "main_chart": "主要资金流向",
            "detail_table": "详细数据表"
        }
        self.selected_chart_type = "资金流向"
        self.latest_update = {
            "chart_type": "资金流向",
            "componentId": "stackedAreaChart1", 
            "timestamp": time.time()
        }
        self.sse_clients = []
        self.message_queue = queue.Queue()
        
        # 初始化所有类型的演示数据
        self._init_all_demo_data()

    def _init_all_demo_data(self):
        """初始化所有演示数据"""
        try:
            # 堆叠面积图数据
            self.fund_flow_data = self._generate_fund_flow_data()
            self.sector_performance_data = self._generate_sector_performance_data()
            self.risk_distribution_data = self._generate_risk_distribution_data()
            
            # 其他图表基础数据可以在这里预生成
            self.stock_list = ["股票A", "股票B", "股票C", "股票D", "股票E"]
            self.time_segments = ["09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00"]
            
            self.logger.info("所有演示数据初始化完成")
        except Exception as e:
            self.logger.error(f"演示数据初始化失败: {e}")
            # 设置默认空数据
            self.fund_flow_data = {}
            self.sector_performance_data = {}
            self.risk_distribution_data = {}
            self.stock_list = []
            self.time_segments = []

    def get_dashboard_config(self):
        """获取仪表盘配置 - 包含多种图表类型的综合演示"""
        return {
            "layout": {
                "rows": 6,
                "cols": 3,
                "components": [
                    # 第一行 - 堆叠面积图（使用专门组件）
                    {
                        "id": "stackedAreaChart1",
                        "type": "stackedAreaChart",
                        "dataSource": "/api/chart-data/fund-flow-stacked",
                        "title": "资金流向堆叠面积图",
                        "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 3},
                        "height": "650px"
                    },
                    # 第二行 - 使用通用chart类型
                    {
                        "id": "lineChart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/stock-trend-line",
                        "title": "股价趋势折线图",
                        "position": {"row": 1, "col": 0, "rowSpan": 1, "colSpan": 1},
                        "height": "600px"
                    },
                    {
                        "id": "barChart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/volume-bar",
                        "title": "成交量柱状图",
                        "position": {"row": 1, "col": 1, "rowSpan": 1, "colSpan": 1},
                        "height": "600px"
                    },
                    {
                        "id": "pieChart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/sector-distribution-pie",
                        "title": "板块分布饼图",
                        "position": {"row": 1, "col": 2, "rowSpan": 1, "colSpan": 1},
                        "height": "600px"
                    },
                    # 第三行 - 堆叠面积图和其他图表
                    {
                        "id": "stackedAreaChart2",
                        "type": "stackedAreaChart",
                        "dataSource": "/api/chart-data/sector-performance-stacked",
                        "title": "板块表现堆叠图",
                        "position": {"row": 2, "col": 0, "rowSpan": 1, "colSpan": 1},
                        "height": "680px"
                    },
                    {
                        "id": "stackedAreaChart3",
                        "type": "stackedAreaChart",
                        "dataSource": "/api/chart-data/risk-distribution-stacked",
                        "title": "风险分布堆叠图",
                        "position": {"row": 2, "col": 1, "rowSpan": 1, "colSpan": 1},
                        "height": "680px"
                    },
                    {
                        "id": "gaugeChart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/market-sentiment-gauge",
                        "title": "市场情绪指标",
                        "position": {"row": 2, "col": 2, "rowSpan": 1, "colSpan": 1},
                        "height": "680px"
                    },
                    # 第四行 - 表格组件
                    {
                        "id": "table1",
                        "type": "table",
                        "dataSource": "/api/table-data/top-stocks",
                        "title": "热门股票排行榜",
                        "position": {"row": 3, "col": 0, "rowSpan": 1, "colSpan": 2},
                        "height": "600px"
                    },
                    {
                        "id": "table2",
                        "type": "table",
                        "dataSource": "/api/table-data/financial-indicators",
                        "title": "财务指标对比表",
                        "position": {"row": 3, "col": 2, "rowSpan": 1, "colSpan": 1},
                        "height": "600px"
                    },
                    # 第五行 - 混合图表（使用通用chart类型）
                    {
                        "id": "comboChart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/price-volume-combo",
                        "title": "价格成交量组合图",
                        "position": {"row": 4, "col": 0, "rowSpan": 1, "colSpan": 2},
                        "height": "620px"
                    },
                    {
                        "id": "scatterChart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/risk-return-scatter",
                        "title": "风险收益散点图",
                        "position": {"row": 4, "col": 2, "rowSpan": 1, "colSpan": 1},
                        "height": "620px"
                    },
                    # 第六行 - 实时数据表格
                    {
                        "id": "table3",
                        "type": "table",
                        "dataSource": "/api/table-data/realtime-data",
                        "title": "实时数据监控表",
                        "position": {"row": 5, "col": 0, "rowSpan": 1, "colSpan": 3},
                        "height": "650px"
                    }
                ]
            }
        }

    def get_data_sources(self):
        """获取数据源配置 - 支持多种图表类型"""
        return {
            # 堆叠面积图数据源
            "/api/chart-data/fund-flow-stacked": {
                "handler": "get_fund_flow_stacked_data",
                "description": "资金流向堆叠面积图数据",
                "cache_ttl": 30
            },
            "/api/chart-data/sector-performance-stacked": {
                "handler": "get_sector_performance_stacked_data", 
                "description": "板块表现堆叠面积图数据",
                "cache_ttl": 30
            },
            "/api/chart-data/risk-distribution-stacked": {
                "handler": "get_risk_distribution_stacked_data",
                "description": "风险分布堆叠面积图数据", 
                "cache_ttl": 30
            },
            
            # 折线图数据源
            "/api/chart-data/stock-trend-line": {
                "handler": "get_stock_trend_line_data",
                "description": "股价趋势折线图数据",
                "cache_ttl": 10
            },
            
            # 柱状图数据源
            "/api/chart-data/volume-bar": {
                "handler": "get_volume_bar_data",
                "description": "成交量柱状图数据",
                "cache_ttl": 10
            },
            
            # 饼图数据源
            "/api/chart-data/sector-distribution-pie": {
                "handler": "get_sector_distribution_pie_data",
                "description": "板块分布饼图数据",
                "cache_ttl": 60
            },
            
            # 仪表盘数据源
            "/api/chart-data/market-sentiment-gauge": {
                "handler": "get_market_sentiment_gauge_data",
                "description": "市场情绪指标数据",
                "cache_ttl": 30
            },
            
            # 组合图数据源
            "/api/chart-data/price-volume-combo": {
                "handler": "get_price_volume_combo_data",
                "description": "价格成交量组合图数据",
                "cache_ttl": 10
            },
            
            # 散点图数据源
            "/api/chart-data/risk-return-scatter": {
                "handler": "get_risk_return_scatter_data",
                "description": "风险收益散点图数据",
                "cache_ttl": 60
            },
            
            # 表格数据源
            "/api/table-data/top-stocks": {
                "handler": "get_top_stocks_table_data",
                "description": "热门股票排行榜",
                "cache_ttl": 30
            },
            "/api/table-data/financial-indicators": {
                "handler": "get_financial_indicators_table_data",
                "description": "财务指标对比表",
                "cache_ttl": 60
            },
            "/api/table-data/realtime-data": {
                "handler": "get_realtime_data_table_data",
                "description": "实时数据监控表",
                "cache_ttl": 5
            },
            "/api/table-data/stacked_summary": {
                "handler": "get_stacked_summary_table_data", 
                "description": "堆叠数据汇总表",
                "cache_ttl": 30
            }
        }

    def register_custom_routes(self):
        """注册自定义路由 - 基类会自动调用handler，无需手工注册"""
        # 注册SSE和更新相关路由
        self.app.add_url_rule('/api/dashboard/update',
                             'update_dashboard_stacked',
                             self.update_dashboard, methods=['POST'])
        
        self.app.add_url_rule('/api/dashboard/updates',
                             'dashboard_updates_stacked',
                             self.dashboard_updates, methods=['GET'])
        
        self.app.add_url_rule('/api/stacked/regenerate-data',
                             'regenerate_stacked_data',
                             self.regenerate_stacked_data, methods=['POST'])

    # ===== 数据处理方法 =====
    
    def get_fund_flow_stacked_data(self):
        """返回资金流向堆叠面积图数据"""
        try:
            # 更新数据以模拟实时变化
            self._update_fund_flow_data()
            
            time_segments = ["09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00"]
            key_order = ["散户资金", "游资", "机构资金", "外资", "主力资金"]
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
            
            data = {}
            table_data = {}
            
            for time_str in time_segments:
                point_data = {}
                total_value = 0
                
                base_values = self.fund_flow_data.get(time_str, {})
                
                for key in key_order:
                    # 从缓存获取基础值，添加随机波动
                    base_value = base_values.get(key, np.random.uniform(10, 40))
                    value = round(base_value + np.random.uniform(-2, 2), 1)
                    value = max(1.0, value)  # 确保非负
                    
                    point_data[key] = value
                    total_value += value
                
                data[time_str] = point_data
                table_data[time_str] = f"{total_value:.1f}亿"
            
            return jsonify({
                "stackedAreaData": {
                    "data": data,
                    "keyOrder": key_order,
                    "colors": colors
                },
                "xAxisValues": time_segments,
                "tableData": table_data
            })
        
        except Exception as e:
            self.logger.error(f"获取资金流向堆叠数据失败: {e}")
            return jsonify(self._generate_fallback_stacked_data("资金流向"))

    def get_sector_performance_stacked_data(self):
        """返回板块表现堆叠面积图数据"""
        try:
            time_segments = ["09:30", "10:30", "11:30", "14:00", "15:00"]
            key_order = ["科技板块", "金融板块", "医药板块", "消费板块", "能源板块"]
            colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]
            
            data = {}
            table_data = {}
            
            for time_str in time_segments:
                point_data = {}
                total_value = 0
                
                base_values = self.sector_performance_data.get(time_str, {})
                
                for key in key_order:
                    # 生成板块表现数据（涨幅百分比转换为正值）
                    base_value = base_values.get(key, np.random.uniform(-5, 15))
                    # 转换为正值用于面积图显示
                    display_value = max(0.1, base_value + 10)  # 加10确保都是正值
                    value = round(display_value, 1)
                    
                    point_data[key] = value
                    total_value += value
                
                data[time_str] = point_data
                table_data[time_str] = f"{total_value:.1f}"
            
            return jsonify({
                "stackedAreaData": {
                    "data": data,
                    "keyOrder": key_order,
                    "colors": colors
                },
                "xAxisValues": time_segments,
                "tableData": table_data
            })
        
        except Exception as e:
            self.logger.error(f"获取板块表现堆叠数据失败: {e}")
            return jsonify(self._generate_fallback_stacked_data("板块表现"))

    def get_risk_distribution_stacked_data(self):
        """返回风险分布堆叠面积图数据"""
        try:
            time_segments = ["09:30", "10:30", "11:30", "14:00", "15:00"]
            key_order = ["低风险", "中低风险", "中等风险", "中高风险", "高风险"]
            colors = ["#27AE60", "#F1C40F", "#E67E22", "#E74C3C", "#8E44AD"]
            
            data = {}
            table_data = {}
            
            for time_str in time_segments:
                point_data = {}
                total_value = 100  # 风险分布总和为100%
                remaining_value = total_value
                
                base_values = self.risk_distribution_data.get(time_str, {})
                
                for i, key in enumerate(key_order):
                    if i == len(key_order) - 1:  # 最后一个项目
                        value = remaining_value
                    else:
                        base_percentage = base_values.get(key, 20)
                        value = round(base_percentage + np.random.uniform(-3, 3), 1)
                        value = max(1.0, min(value, remaining_value - len(key_order) + i))
                        remaining_value -= value
                    
                    point_data[key] = value
                
                data[time_str] = point_data
                table_data[time_str] = "100%"
            
            return jsonify({
                "stackedAreaData": {
                    "data": data,
                    "keyOrder": key_order,
                    "colors": colors
                },
                "xAxisValues": time_segments,
                "tableData": table_data
            })
        
        except Exception as e:
            self.logger.error(f"获取风险分布堆叠数据失败: {e}")
            return jsonify(self._generate_fallback_stacked_data("风险分布"))

    def get_stacked_summary_table_data(self):
        """返回堆叠数据汇总表"""
        try:
            columns = [
                {"field": "time_segment", "header": "时间段"},
                {"field": "total_fund", "header": "总资金流入(亿)", "backgroundColor": "redGreen"},
                {"field": "main_fund_ratio", "header": "主力占比(%)", "backgroundColor": "redGreen"},
                {"field": "active_sectors", "header": "活跃板块数"},
                {"field": "risk_level", "header": "整体风险等级"},
                {"field": "trend", "header": "趋势", "backgroundColor": "redGreen"}
            ]
            
            rows = []
            time_segments = ["09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00"]
            
            for time_str in time_segments:
                # 模拟汇总数据
                total_fund = round(np.random.uniform(80, 150), 1)
                main_fund_ratio = round(np.random.uniform(20, 45), 1)
                active_sectors = np.random.randint(3, 8)
                risk_levels = ["低", "中低", "中等", "中高", "高"]
                risk_level = np.random.choice(risk_levels)
                trends = ["上涨", "下跌", "震荡"]
                trend = np.random.choice(trends)
                
                row = {
                    "time_segment": time_str,
                    "total_fund": total_fund,
                    "main_fund_ratio": main_fund_ratio,
                    "active_sectors": active_sectors,
                    "risk_level": risk_level,
                    "trend": trend
                }
                rows.append(row)
            
            return jsonify({
                "columns": columns,
                "rows": rows
            })
        
        except Exception as e:
            self.logger.error(f"获取堆叠汇总表格数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    # ===== SSE 和更新相关方法 =====
    
    def update_dashboard(self):
        """接收页面更新请求"""
        data = request.json
        self.logger.info(f"收到堆叠图更新请求: {data}")
        
        params = data.get('params', {})
        chart_type = params.get('chart_type', '资金流向') if isinstance(params, dict) else '资金流向'
        
        self.selected_chart_type = chart_type
        
        self.latest_update = {
            "componentId": data.get('componentId', 'stackedAreaChart1'),
            "params": params,
            "timestamp": time.time(),
            "action": "config_update",
            "chart_type": chart_type
        }
        
        update_message = {
            "action": "reload_config",
            "chart_type": chart_type,
            "timestamp": time.time()
        }
        self._send_update_to_clients(update_message)
        
        return jsonify({
            "status": "success",
            "message": "Stacked chart update request sent",
            "chart_type": chart_type
        })

    def dashboard_updates(self):
        """SSE事件流"""
        def event_stream():
            client_queue = queue.Queue()
            client_id = f"stacked_client_{len(self.sse_clients)}_{time.time()}"
            
            try:
                self.sse_clients.append(client_queue)
                self.logger.info(f"堆叠图SSE客户端连接: {client_id}，当前总连接数: {len(self.sse_clients)}")
                
                connection_info = {
                    "type": "connection_established",
                    "client_id": client_id,
                    "timestamp": time.time(),
                    "server_status": "online"
                }
                yield f"data: {json.dumps(connection_info)}\n\n"
                yield f"data: {json.dumps(self.latest_update)}\n\n"
                
                while True:
                    try:
                        message = client_queue.get(block=True, timeout=10)
                        yield message
                    except queue.Empty:
                        heartbeat = {
                            "type": "heartbeat",
                            "client_id": client_id,
                            "timestamp": time.time(),
                            "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "active_connections": len(self.sse_clients),
                            "stacked_status": "running"
                        }
                        yield f"data: {json.dumps(heartbeat)}\n\n"
                        continue
                    except GeneratorExit:
                        self.logger.info(f"堆叠图SSE客户端主动断开: {client_id}")
                        break
                        
            except Exception as e:
                self.logger.error(f"堆叠图SSE连接异常 {client_id}: {e}")
            finally:
                if client_queue in self.sse_clients:
                    self.sse_clients.remove(client_queue)
                    self.logger.info(f"堆叠图SSE客户端清理: {client_id}，剩余连接数: {len(self.sse_clients)}")
        
        response = Response(event_stream(), mimetype="text/event-stream")
        response.headers.update({
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control',
            'Keep-Alive': 'timeout=30, max=1000'
        })
        return response

    def regenerate_stacked_data(self):
        """重新生成堆叠数据"""
        try:
            self._init_stacked_data()
            self.logger.info("堆叠面积图数据已重新生成")
            
            update_message = {
                "action": "data_regenerate",
                "timestamp": time.time()
            }
            self._send_update_to_clients(update_message)
            
            return jsonify({
                "status": "success",
                "message": "堆叠面积图数据已重新生成"
            })
        except Exception as e:
            self.logger.error(f"重新生成堆叠数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    # ===== 辅助方法 =====
    
    def _send_update_to_clients(self, data):
        """发送更新到所有SSE客户端"""
        for client in list(self.sse_clients):
            try:
                client.put(f"data: {json.dumps(data)}\n\n")
            except:
                self.sse_clients.remove(client)

    def _generate_fund_flow_data(self):
        """生成资金流向基础数据"""
        time_segments = ["09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00"]
        key_order = ["散户资金", "游资", "机构资金", "外资", "主力资金"]
        
        fund_data = {}
        for time_str in time_segments:
            point_data = {}
            for key in key_order:
                # 基础值，后续会添加随机波动
                base_value = np.random.uniform(15, 35)
                # 添加时间相关的趋势
                if time_str in ["10:30", "14:30"]:  # 活跃时段
                    base_value *= 1.2
                elif time_str in ["11:30", "15:00"]:  # 收盘前
                    base_value *= 0.9
                
                point_data[key] = round(base_value, 1)
            
            fund_data[time_str] = point_data
        
        return fund_data

    def _generate_sector_performance_data(self):
        """生成板块表现基础数据"""
        time_segments = ["09:30", "10:30", "11:30", "14:00", "15:00"]
        key_order = ["科技板块", "金融板块", "医药板块", "消费板块", "能源板块"]
        
        sector_data = {}
        for time_str in time_segments:
            point_data = {}
            for key in key_order:
                # 生成板块涨跌幅（-5% 到 15%）
                performance = np.random.uniform(-5, 15)
                point_data[key] = round(performance, 1)
            
            sector_data[time_str] = point_data
        
        return sector_data

    def _generate_risk_distribution_data(self):
        """生成风险分布基础数据"""
        time_segments = ["09:30", "10:30", "11:30", "14:00", "15:00"]
        key_order = ["低风险", "中低风险", "中等风险", "中高风险", "高风险"]
        
        risk_data = {}
        for time_str in time_segments:
            point_data = {}
            # 确保总和为100%
            percentages = np.random.dirichlet([2, 3, 4, 2, 1]) * 100  # 偏向中等风险
            
            for i, key in enumerate(key_order):
                point_data[key] = round(percentages[i], 1)
            
            risk_data[time_str] = point_data
        
        return risk_data

    def _update_fund_flow_data(self):
        """更新资金流向数据（模拟实时变化）"""
        for time_str, point_data in self.fund_flow_data.items():
            for key in point_data:
                # 小幅随机调整
                current_value = point_data[key]
                change = np.random.uniform(-1, 1)
                new_value = max(5.0, current_value + change)
                self.fund_flow_data[time_str][key] = round(new_value, 1)

    def _generate_fallback_stacked_data(self, data_type):
        """生成后备堆叠数据"""
        time_segments = ["09:30", "10:30", "11:30", "14:00", "15:00"]
        
        if data_type == "资金流向":
            key_order = ["散户资金", "游资", "机构资金", "外资", "主力资金"]
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
        elif data_type == "板块表现":
            key_order = ["科技板块", "金融板块", "医药板块", "消费板块", "能源板块"]
            colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6"]
        else:  # 风险分布
            key_order = ["低风险", "中低风险", "中等风险", "中高风险", "高风险"]
            colors = ["#27AE60", "#F1C40F", "#E67E22", "#E74C3C", "#8E44AD"]
        
        data = {}
        table_data = {}
        
        for time_str in time_segments:
            point_data = {}
            total_value = 0
            
            for key in key_order:
                value = round(np.random.uniform(10, 30), 1)
                point_data[key] = value
                total_value += value
            
            data[time_str] = point_data
            table_data[time_str] = f"{total_value:.1f}"
        
        return {
            "stackedAreaData": {
                "data": data,
                "keyOrder": key_order,
                "colors": colors
            },
            "xAxisValues": time_segments,
            "tableData": table_data
        }

    # ===== 新增图表数据处理方法 =====
    
    def get_stock_trend_line_data(self):
        """获取股价趋势折线图数据"""
        try:
            # 生成过去30天的股价数据
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            base_price = 100.0
            
            stocks = ["股票A", "股票B", "股票C"]
            colors = ["#2196F3", "#FF5722", "#4CAF50"]
            
            plotly_traces = []
            for i, stock in enumerate(stocks):
                prices = []
                current_price = base_price + np.random.uniform(-20, 20)
                
                for _ in range(30):
                    change = np.random.uniform(-0.05, 0.05)  # 日变化幅度
                    current_price = current_price * (1 + change)
                    prices.append(round(current_price, 2))
                
                plotly_traces.append({
                    "x": [date.strftime('%m-%d') for date in dates],
                    "y": prices,
                    "name": stock,
                    "mode": "lines+markers",
                    "line": {"color": colors[i], "width": 2},
                    "marker": {"size": 4}
                })
            
            return jsonify({
                "chartType": "scatter",
                "data": plotly_traces,
                "layout": {
                    "title": "股价趋势",
                    "xaxis": {"title": "日期"},
                    "yaxis": {"title": "价格(元)"}
                }
            })
            
        except Exception as e:
            self.logger.error(f"获取折线图数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_volume_bar_data(self):
        """获取成交量柱状图数据"""
        try:
            time_segments = ["09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00"]
            
            volumes = []
            colors = []
            for _ in time_segments:
                volume = round(np.random.uniform(1000, 8000), 1)
                volumes.append(volume)
                # 成交量大于5000用红色，否则用绿色
                colors.append("#FF5722" if volume > 5000 else "#4CAF50")
            
            return jsonify({
                "chartType": "bar",
                "data": [{
                    "x": time_segments,
                    "y": volumes,
                    "name": "成交量",
                    "type": "bar",
                    "marker": {
                        "color": colors
                    }
                }],
                "layout": {
                    "title": "交易时段成交量",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "成交量(万手)"}
                }
            })
            
        except Exception as e:
            self.logger.error(f"获取柱状图数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_sector_distribution_pie_data(self):
        """获取板块分布饼图数据"""
        try:
            sectors = ["科技", "金融", "医药", "消费", "能源", "地产", "制造"]
            colors = ["#2196F3", "#FF5722", "#4CAF50", "#FF9800", "#9C27B0", "#607D8B", "#795548"]
            
            values = []
            for _ in sectors:
                value = round(np.random.uniform(8, 25), 1)
                values.append(value)
            
            return jsonify({
                "chartType": "pie",
                "data": [{
                    "labels": sectors,
                    "values": values,
                    "type": "pie",
                    "marker": {
                        "colors": colors
                    },
                    "textinfo": "label+percent",
                    "hovertemplate": "<b>%{label}</b><br>占比: %{percent}<br>值: %{value}<extra></extra>",
                    "hole": 0.3  # 添加甜甜圈效果
                }],
                "layout": {
                    "title": {"text": "板块资金分布", "x": 0.5},
                    "showlegend": True,
                    "margin": {"t": 40, "l": 20, "r": 20, "b": 20},
                    "font": {"size": 12}
                }
            })
            
        except Exception as e:
            self.logger.error(f"获取饼图数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_market_sentiment_gauge_data(self):
        """获取市场情绪仪表盘数据"""
        try:
            # 生成0-100的市场情绪指数
            sentiment_score = round(np.random.uniform(20, 90), 1)
            
            # 使用 Plotly 的 indicator 类型
            return jsonify({
                "chartType": "indicator",
                "data": [{
                    "type": "indicator",
                    "mode": "gauge+number+delta",
                    "value": sentiment_score,
                    "domain": {"x": [0, 1], "y": [0, 1]},
                    "title": {"text": "市场情绪指数"},
                    "delta": {"reference": 50},
                    "gauge": {
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 30], "color": "lightgray"},
                            {"range": [30, 70], "color": "gray"},
                            {"range": [70, 100], "color": "lightgreen"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 90
                        }
                    }
                }],
                "layout": {
                    "title": "市场情绪仪表盘"
                }
            })
            
        except Exception as e:
            self.logger.error(f"获取仪表盘数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_price_volume_combo_data(self):
        """获取价格成交量组合图数据"""
        try:
            dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
            
            prices = []
            volumes = []
            base_price = 50.0
            
            for _ in range(20):
                # 价格数据
                change = np.random.uniform(-0.03, 0.03)
                base_price = base_price * (1 + change)
                prices.append(round(base_price, 2))
                
                # 成交量数据
                volume = round(np.random.uniform(2000, 10000), 0)
                volumes.append(volume)
            
            return jsonify({
                "chartType": "scatter",
                "data": [
                    {
                        "x": [date.strftime('%m-%d') for date in dates],
                        "y": prices,
                        "name": "股价",
                        "mode": "lines+markers",
                        "line": {"color": "#2196F3"},
                        "yaxis": "y"
                    },
                    {
                        "x": [date.strftime('%m-%d') for date in dates],
                        "y": volumes,
                        "name": "成交量",
                        "type": "bar",
                        "marker": {"color": "#FF5722"},
                        "yaxis": "y2"
                    }
                ],
                "layout": {
                    "title": "价格成交量组合图",
                    "xaxis": {"title": "日期"},
                    "yaxis": {
                        "title": "价格(元)",
                        "side": "left"
                    },
                    "yaxis2": {
                        "title": "成交量(万手)",
                        "side": "right",
                        "overlaying": "y"
                    }
                }
            })
            
        except Exception as e:
            self.logger.error(f"获取组合图数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_risk_return_scatter_data(self):
        """获取风险收益散点图数据"""
        try:
            stocks = ["股票A", "股票B", "股票C", "股票D", "股票E", "股票F", "股票G", "股票H"]
            
            x_data = []  # 风险值
            y_data = []  # 收益率
            sizes = []   # 气泡大小
            names = []   # 股票名称
            
            for stock in stocks:
                risk = round(np.random.uniform(5, 25), 2)  # 风险值 5-25%
                return_rate = round(np.random.uniform(-15, 30), 2)  # 收益率 -15% 到 30%
                size = round(np.random.uniform(20, 100), 0)  # 气泡大小代表市值
                
                x_data.append(risk)
                y_data.append(return_rate)
                sizes.append(size)
                names.append(stock)
            
            return jsonify({
                "chartType": "scatter",
                "data": [{
                    "x": x_data,
                    "y": y_data,
                    "mode": "markers",
                    "type": "scatter",
                    "text": names,
                    "marker": {
                        "size": sizes,
                        "sizemode": "diameter",
                        "sizeref": 2.*max(sizes)/(40.**2),
                        "sizemin": 4,
                        "color": y_data,
                        "colorscale": "Viridis",
                        "showscale": True,
                        "colorbar": {"title": "收益率(%)"}
                    },
                    "name": "股票风险收益"
                }],
                "layout": {
                    "title": "股票风险收益散点图",
                    "xaxis": {"title": "风险(%)"},
                    "yaxis": {"title": "收益率(%)"},
                    "hovermode": "closest"
                }
            })
            
        except Exception as e:
            self.logger.error(f"获取散点图数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ===== 新增表格数据处理方法 =====
    
    def get_top_stocks_table_data(self):
        """获取热门股票排行榜表格数据"""
        try:
            self.logger.info("开始生成热门股票表格数据")
            
            # 新格式：直接在columns中包含backgroundColor配置
            columns = [
                {"field": "排名", "header": "排名"},
                {"field": "股票代码", "header": "股票代码"},
                {"field": "股票名称", "header": "股票名称"},
                {"field": "现价(元)", "header": "现价(元)", "backgroundColor": "highLow"},
                {"field": "涨跌幅(%)", "header": "涨跌幅(%)", "backgroundColor": "redGreen"},
                {"field": "成交量(万手)", "header": "成交量(万手)", "backgroundColor": "highLow"},
                {"field": "市值(亿)", "header": "市值(亿)", "backgroundColor": "highLow"},
                {"field": "市盈率", "header": "市盈率", "backgroundColor": "range"}
            ]
            
            rows = []
            for i in range(1, 21):  # 生成20只股票
                change_rate = round(np.random.uniform(-10, 10), 2)
                current_price = round(np.random.uniform(10, 200), 2)
                volume = int(round(np.random.uniform(1000, 50000), 0))
                market_value = round(np.random.uniform(50, 2000), 1)
                pe_ratio = round(np.random.uniform(5, 50), 1)
                
                row = {
                    "排名": int(i),
                    "股票代码": f"{6000 + i:04d}",
                    "股票名称": f"股票{chr(65 + (i-1) % 26)}",
                    "现价(元)": float(current_price),
                    "涨跌幅(%)": change_rate,
                    "成交量(万手)": float(volume),
                    "市值(亿)": float(market_value),
                    "市盈率": float(pe_ratio)
                }
                rows.append(row)
            
            result = {
                "columns": columns,
                "rows": rows
            }
            
            self.logger.info(f"生成表格数据完成: {len(columns)} 列, {len(rows)} 行")
            self.logger.debug(f"表格数据结构: columns={[c['field'] for c in columns[:3]]}, first_row_keys={list(rows[0].keys())[:3] if rows else 'empty'}")
            
            return jsonify(result)
            
        except Exception as e:
            self.logger.error(f"获取热门股票表格数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_financial_indicators_table_data(self):
        """获取财务指标对比表数据"""
        try:
            # 新格式：直接在columns中包含backgroundColor配置
            columns = [
                {"field": "财务指标", "header": "财务指标"},
                {"field": "股票A", "header": "股票A", "backgroundColor": "performance"},
                {"field": "股票B", "header": "股票B", "backgroundColor": "performance"},
                {"field": "股票C", "header": "股票C", "backgroundColor": "performance"},
                {"field": "行业均值", "header": "行业均值"}
            ]
            
            indicators = [
                "净资产收益率(%)", "毛利率(%)", "净利率(%)", "资产负债率(%)",
                "流动比率", "速动比率", "存货周转率", "应收账款周转率"
            ]
            
            rows = []
            for indicator in indicators:
                row = {
                    "财务指标": indicator,
                    "股票A": round(np.random.uniform(5, 25), 2),
                    "股票B": round(np.random.uniform(5, 25), 2),
                    "股票C": round(np.random.uniform(5, 25), 2),
                    "行业均值": round(np.random.uniform(10, 20), 2)
                }
                rows.append(row)
            
            return jsonify({
                "columns": columns,
                "rows": rows
            })
            
        except Exception as e:
            self.logger.error(f"获取财务指标表格数据失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_realtime_data_table_data(self):
        """获取实时数据监控表数据"""
        try:
            # 新格式：直接在columns中包含backgroundColor配置
            columns = [
                {"field": "时间", "header": "时间"},
                {"field": "API状态", "header": "API状态", "backgroundColor": "status"},
                {"field": "响应时间(ms)", "header": "响应时间(ms)", "backgroundColor": "threshold", "thresholds": [100, 300]},
                {"field": "在线用户", "header": "在线用户", "backgroundColor": "highLow"},
                {"field": "CPU使用率(%)", "header": "CPU使用率(%)", "backgroundColor": "utilization"},
                {"field": "内存使用率(%)", "header": "内存使用率(%)", "backgroundColor": "utilization"},
                {"field": "磁盘使用率(%)", "header": "磁盘使用率(%)", "backgroundColor": "utilization"},
                {"field": "网络IO(MB/s)", "header": "网络IO(MB/s)", "backgroundColor": "highLow"}
            ]
            
            rows = []
            current_time = datetime.now()
            
            for i in range(10):  # 生成10条实时记录
                timestamp = (current_time - timedelta(minutes=i)).strftime("%H:%M:%S")
                api_status = np.random.choice(["正常", "警告", "异常"], p=[0.8, 0.15, 0.05])
                response_time = round(np.random.uniform(50, 500), 0)
                cpu_usage = round(np.random.uniform(20, 90), 1)
                memory_usage = round(np.random.uniform(40, 85), 1)
                disk_usage = round(np.random.uniform(30, 75), 1)
                
                row = {
                    "时间": timestamp,
                    "API状态": api_status,
                    "响应时间(ms)": response_time,
                    "在线用户": round(np.random.uniform(100, 1000), 0),
                    "CPU使用率(%)": cpu_usage,
                    "内存使用率(%)": memory_usage,
                    "磁盘使用率(%)": disk_usage,
                    "网络IO(MB/s)": round(np.random.uniform(1, 50), 2)
                }
                rows.append(row)
            
            return jsonify({
                "columns": columns,
                "rows": rows
            })
            
        except Exception as e:
            self.logger.error(f"获取实时监控表格数据失败: {e}")
            return jsonify({"error": str(e)}), 500


def main():
    """主函数"""
    print("🚀 启动综合图表演示服务器...")
    print("📊 支持的图表类型:")
    print("   - 堆叠面积图 (资金流向、板块表现、风险分布)")
    print("   - 折线图 (股价趋势)")
    print("   - 柱状图 (成交量)")
    print("   - 饼图 (板块分布)")
    print("   - 仪表盘 (市场情绪)")
    print("   - 组合图 (价格-成交量)")
    print("   - 散点图 (风险-收益)")
    print("   - 多种表格 (支持背景色规则)")
    
    # 从命令行参数获取端口
    port = 5004
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("⚠️ 无效的端口参数，使用默认端口 5004")
    
    server = StackedAreaDemoServer(port=port)
    
    try:
        print("✅ 综合图表演示数据初始化完成")
        print(f"🌐 服务器地址: http://localhost:{port}")
        print("📈 包含10+ 种图表类型和智能表格展示")
    except Exception as e:
        print(f"⚠️ 演示数据初始化失败: {e}")
    
    server.run(debug=True)


if __name__ == '__main__':
    main()
