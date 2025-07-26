#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: chenlei
Date: 2024-01-20
Description: 堆叠面积图演示服务器 - 基于新框架重构版本
功能: 提供专门的堆叠面积图组件演示、三维数据可视化测试
"""

import time
import pandas as pd
import numpy as np
import json
import datetime
import plotly
import plotly.graph_objects as go
import os
import sys
import queue
from flask import request, Response, jsonify
from flask_cors import CORS

# 导入新框架基类
from .base_server import BaseStockServer

class StackedAreaDemoServer(BaseStockServer):
    """堆叠面积图演示服务器 - 继承自BaseStockServer"""
    
    def __init__(self, port=5007):
        super().__init__(name="堆叠面积图演示", port=port)
        
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
        
        # 初始化堆叠面积图数据
        self._init_stacked_data()

    def _init_stacked_data(self):
        """初始化堆叠面积图数据"""
        try:
            # 生成多种类型的堆叠数据
            self.fund_flow_data = self._generate_fund_flow_data()
            self.sector_performance_data = self._generate_sector_performance_data()
            self.risk_distribution_data = self._generate_risk_distribution_data()
            self.logger.info("堆叠面积图演示数据初始化完成")
        except Exception as e:
            self.logger.error(f"堆叠面积图数据初始化失败: {e}")
            self.fund_flow_data = {}
            self.sector_performance_data = {}
            self.risk_distribution_data = {}

    def get_dashboard_config(self):
        """获取仪表盘配置"""
        return {
            "layout": {
                "rows": 3,
                "cols": 2,
                "components": [
                    {
                        "id": "stackedAreaChart1",
                        "type": "stackedAreaChart",
                        "dataSource": "/api/chart-data/fund-flow-stacked",
                        "title": "资金流向堆叠面积图",
                        "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 2},
                        "height": "400px"
                    },
                    {
                        "id": "stackedAreaChart2",
                        "type": "stackedAreaChart",
                        "dataSource": "/api/chart-data/sector-performance-stacked",
                        "title": "板块表现堆叠面积图",
                        "position": {"row": 1, "col": 0, "rowSpan": 1, "colSpan": 1},
                        "height": "350px"
                    },
                    {
                        "id": "stackedAreaChart3",
                        "type": "stackedAreaChart",
                        "dataSource": "/api/chart-data/risk-distribution-stacked",
                        "title": "风险分布堆叠面积图",
                        "position": {"row": 1, "col": 1, "rowSpan": 1, "colSpan": 1},
                        "height": "350px"
                    },
                    {
                        "id": "table1",
                        "type": "table",
                        "dataSource": "/api/table-data/stacked_summary",
                        "title": "堆叠数据汇总表",
                        "position": {"row": 2, "col": 0, "rowSpan": 1, "colSpan": 2},
                        "height": "300px"
                    }
                ]
            }
        }

    def get_data_sources(self):
        """获取数据源配置"""
        return {
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


def main():
    """主函数"""
    print("🚀 启动堆叠面积图演示服务器...")
    
    # 从命令行参数获取端口
    port = 5007
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("⚠️ 无效的端口参数，使用默认端口 5007")
    
    server = StackedAreaDemoServer(port=port)
    
    try:
        print("✅ 堆叠面积图演示数据初始化完成")
    except Exception as e:
        print(f"⚠️ 堆叠面积图数据初始化失败: {e}")
    
    server.run(debug=True)


if __name__ == '__main__':
    main()
