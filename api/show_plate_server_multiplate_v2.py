"""
Author: chenlei
Date: 2024-01-20
Description: 股票多板块仪表盘服务 - 基于新框架重构版本
功能: 提供多板块股票数据展示、实时涨幅分析、涨停监控等功能
"""

import time
import pandas as pd
import numpy as np
import json
import pickle
import datetime
import plotly
import plotly.graph_objects as go
import os
import sys
import queue
from flask import request, Response, jsonify
from flask_cors import CORS

# 导入新框架基类
from base_server import BaseStockServer

# 将项目根目录添加到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入股票数据和策略函数
from utils.common import get_trade_date_by_offset
from stock_data.stock.stock_daily import StockDailyData
from stock_data.stock_minute import StockMinuteData
from strategy.strategy001.板块信息显示 import plot_stock_line_charts

class MultiPlateStockServer(BaseStockServer):
    """多板块股票服务器 - 继承自BaseStockServer"""
    
    def __init__(self, port=5008):
        super().__init__(port=port, service_name="多板块股票仪表盘")
        
        # 服务特定的配置
        self.data_cache = DataCache()
        self.dynamic_titles = {
            "table2": "股票数据表",
            "table21": "股票数据表", 
            "table22": "股票数据表", 
            "table23": "股票数据表", 
            "table24": "股票数据表",
            "table12": "航运概念"
        }
        self.selected_sector = "航运概念"
        self.latest_update = {
            "sector": "航运概念",
            "componentId": "chart2", 
            "timestamp": time.time()
        }
        self.sse_clients = []
        self.message_queue = queue.Queue()
        
        # 初始化股票数据
        self._init_stock_data()
        
        # 读取自定义板块
        self.my_plate_list = self._get_my_plate()

    def _init_stock_data(self):
        """初始化股票数据"""
        try:
            self.stock_daily_ins = StockDailyData()
            today = datetime.datetime.now().strftime("%Y%m%d")
            today = '20250530'  # for test
            yesterday = get_trade_date_by_offset(today, 1)
            self.stock_daily_df = self.stock_daily_ins.get_daily_data(
                start_date=yesterday, end_date=yesterday
            )
            self.logger.info(f"股票数据初始化完成，获取 {len(self.stock_daily_df)} 条记录")
        except Exception as e:
            self.logger.error(f"股票数据初始化失败: {e}")
            self.stock_daily_df = pd.DataFrame()

    def _get_my_plate(self, path=r'api\自定义优先板块.txt'):
        """读取自定义优先板块"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                my_plate = f.read().strip()
                my_plate = my_plate.replace('\n', '').replace('\r', '')
                if my_plate:
                    return my_plate.split(',')
                else:
                    return []
        except Exception as e:
            self.logger.warning(f"读取自定义优先板块失败: {e}")
            return []

    def get_dashboard_config(self):
        """获取仪表盘配置"""
        # 初始化动态标题
        if not self.dynamic_titles or all(title == "股票数据表" for title in self.dynamic_titles.values() if 'table' in str(title)):
            self._update_dynamic_titles()
            self.logger.info("初始化动态标题")
        else:
            self.logger.info(f"使用现有动态标题: {self.dynamic_titles}")
        
        return {
            "layout": {
                "rows": 6,
                "cols": 5,
                "components": [
                    {
                        "id": "chart1",
                        "type": "chart",
                        "dataSource": "/api/chart-data/sector-line-chart_change",
                        "title": "板块涨幅折线图",
                        "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
                    },
                    {
                        "id": "chart_speed",
                        "type": "chart",
                        "dataSource": "/api/table-data/sector_speed_chart",
                        "title": "板块涨速累加折线图",
                        "position": {"row": 5, "col": 0, "rowSpan": 1, "colSpan": 3}
                    },
                    {
                        "id": "chart2",
                        "type": "chart", 
                        "dataSource": "/api/chart-data/sector-line-chart_uplimit",
                        "title": "板块近似涨停折线图",
                        "position": {"row": 2, "col": 0, "rowSpan": 1, "colSpan": 3}
                    },
                    {
                        "id": "chart3",
                        "type": "chart", 
                        "dataSource": "/api/chart-data/sector-line-chart_uprate",
                        "title": "板块红盘率折线图",
                        "position": {"row": 0, "col": 2, "rowSpan": 1, "colSpan": 1}
                    },
                    {
                        "id": "chart4",
                        "type": "chart", 
                        "dataSource": "/api/chart-data/sector-line-chart_uprate5",
                        "title": "板块uprate5折线图",
                        "position": {"row": 0, "col": 3, "rowSpan": 1, "colSpan": 1}
                    },
                    {
                        "id": "table1",
                        "type": "table",
                        "dataSource": "/api/table-data/plate_info",
                        "title": "板块概要数据表",
                        "position": {"row": 1, "col": 0, "rowSpan": 1, "colSpan": 3},
                        "height": "800px"
                    },
                    {
                        "id": "table12",
                        "type": "table",
                        "dataSource": "/api/table-data/stocks",
                        "title": self.dynamic_titles.get("table12", "股票数据表"),
                        "position": {"row": 1, "col": 3, "rowSpan": 1, "colSpan": 1},
                        "height": "800px"
                    },
                    {
                        "id": "upLimitTable",
                        "type": "table",
                        "dataSource": "/api/table-data/up_limit",
                        "title": "涨停数据表",
                        "position": {"row": 0, "col": 4, "rowSpan": 5, "colSpan": 1},
                        "height": "1300px"
                    }
                ]
            }
        }

    def get_data_sources(self):
        """获取数据源配置"""
        return {
            "/api/chart-data/sector-line-chart_change": {
                "handler": "get_sector_chart_data_change",
                "description": "板块涨幅折线图数据",
                "cache_ttl": 30
            },
            "/api/chart-data/sector-line-chart_uplimit": {
                "handler": "get_sector_chart_data_uplimit", 
                "description": "板块近似涨停折线图数据",
                "cache_ttl": 30
            },
            "/api/chart-data/sector-line-chart_uprate": {
                "handler": "get_sector_chart_data_uprate",
                "description": "板块红盘率折线图数据", 
                "cache_ttl": 30
            },
            "/api/chart-data/sector-line-chart_uprate5": {
                "handler": "get_sector_chart_data_uprate5",
                "description": "板块uprate5折线图数据",
                "cache_ttl": 30
            },
            "/api/table-data/sector_speed_chart": {
                "handler": "get_sector_speed_chart",
                "description": "板块涨速累加图表数据",
                "cache_ttl": 30
            },
            "/api/table-data/plate_info": {
                "handler": "get_plate_info_table_data",
                "description": "板块概要数据表",
                "cache_ttl": 60
            },
            "/api/table-data/stocks": {
                "handler": "get_stocks_table_data", 
                "description": "股票数据表",
                "cache_ttl": 30
            },
            "/api/table-data/up_limit": {
                "handler": "get_up_limit_table_data",
                "description": "涨停数据表",
                "cache_ttl": 60
            }
        }

    def register_custom_routes(self):
        """注册自定义路由 - 基类会自动调用handler，无需手工注册"""
        # 由于基类现在支持自动handler调用，大部分路由无需手工注册
        # 只保留特殊的路由需求
        pass
        
        # 注册SSE和更新相关路由
        self.app.add_url_rule('/api/dashboard/update',
                             'update_dashboard',
                             self.update_dashboard, methods=['POST'])
        
        self.app.add_url_rule('/api/dashboard/updates',
                             'dashboard_updates',
                             self.dashboard_updates, methods=['GET'])
        
        self.app.add_url_rule('/api/dashboard/notify-update',
                             'notify_update', 
                             self.notify_update, methods=['POST'])
        
        self.app.add_url_rule('/api/debug/dynamic-titles',
                             'get_dynamic_titles_debug',
                             self.get_dynamic_titles_debug, methods=['GET'])

    # ===== 数据处理方法 =====
    
    def get_sector_chart_data_change(self):
        """返回板块涨幅折线图数据"""
        try:
            sector_names = self._get_dynamic_titles_list()
            sector_df = pd.read_csv('strategy\\showhtml\\server\\good_plate_df.csv')
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            
            chart_data = []
            latest_time = sector_df['时间'].max()
            temp_df = sector_df[sector_df['时间'] == latest_time]
            
            sector_names_speed = temp_df.sort_values(by='板块5分涨速', ascending=False).head(10)['板块名'].tolist()
            sector_names_change = temp_df.sort_values(by='板块涨幅', ascending=False).head(20)['板块名'].tolist()
            sector_names = list(set(sector_names + sector_names_speed + sector_names_change))
            
            for sector_name in sector_names:
                sector_data = sector_df[sector_df['板块名'] == sector_name]
                if not sector_data.empty:
                    sector_data = sector_data.sort_values(by='时间')
                    chart_data.append({
                        "name": f'{sector_name}涨幅',
                        "x": sector_data['时间'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                        "y": sector_data['板块涨幅'].tolist()
                    })
            
            return jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块涨幅",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "涨幅(%)"},
                    "legend": {"title": "板块名称"}
                }
            })
        
        except Exception as e:
            self.logger.error(f"获取板块涨幅数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    def get_sector_chart_data_uplimit(self):
        """返回板块近似涨停折线图数据"""
        try:
            sector_names = self._get_dynamic_titles_list()
            sector_df = pd.read_csv('strategy\\showhtml\\server\\good_plate_df.csv')
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            
            # 添加近似涨停数列
            sector_df['近似涨停数'] = sector_df['涨幅分布'].apply(
                lambda x: int(x.split('-')[-1]) if '-' in x else 0
            )
            
            chart_data = []
            latest_time = sector_df['时间'].max()
            temp_df = sector_df[sector_df['时间'] == latest_time]
            
            sector_names_speed = temp_df.sort_values(by='板块5分涨速', ascending=False).head(3)['板块名'].tolist()
            sector_names_change = temp_df.sort_values(by='板块涨幅', ascending=False).head(220)['板块名'].tolist()
            sector_names = list(set(sector_names + sector_names_speed + sector_names_change))
            
            for sector_name in sector_names:
                sector_data = sector_df[sector_df['板块名'] == sector_name]
                if not sector_data.empty:
                    sector_data = sector_data.sort_values(by='时间')
                    chart_data.append({
                        "name": f'{sector_name}近似涨停数',
                        "x": sector_data['时间'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                        "y": sector_data['近似涨停数'].tolist()
                    })
            
            return jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块近似涨停数",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "近似涨停数"},
                    "legend": {"title": "板块名称"}
                }
            })
        
        except Exception as e:
            self.logger.error(f"获取板块涨停数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    def get_sector_chart_data_uprate(self):
        """返回板块红盘率折线图数据"""
        try:
            sector_names = self._get_dynamic_titles_list()
            sector_df = pd.read_csv('strategy\\showhtml\\server\\good_plate_df.csv')
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            sector_df['uprate'] = sector_df['涨幅分布'].apply(lambda x: self._calculate_tail_ratio(x, n=6))
            
            chart_data = []
            latest_time = sector_df['时间'].max()
            temp_df = sector_df[sector_df['时间'] == latest_time]
            
            sector_names_speed = temp_df.sort_values(by='板块5分涨速', ascending=False).head(3)['板块名'].tolist()
            sector_names_change = temp_df.sort_values(by='板块涨幅', ascending=False).head(3)['板块名'].tolist()
            sector_names = list(set(sector_names + sector_names_speed + sector_names_change))
            
            for sector_name in sector_names:
                sector_data = sector_df[sector_df['板块名'] == sector_name]
                if not sector_data.empty:
                    sector_data = sector_data.sort_values(by='时间')
                    chart_data.append({
                        "name": f'{sector_name}红盘率',
                        "x": sector_data['时间'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                        "y": sector_data['uprate'].tolist()
                    })
            
            return jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块红盘率",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "红盘率"},
                    "legend": {"title": "板块名称"}
                }
            })
        
        except Exception as e:
            self.logger.error(f"获取板块红盘率数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    def get_sector_chart_data_uprate5(self):
        """返回板块uprate5折线图数据"""
        try:
            sector_names = self._get_dynamic_titles_list()
            sector_df = pd.read_csv('strategy\\showhtml\\server\\good_plate_df.csv')
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            sector_df['uprate5'] = sector_df['涨幅分布'].apply(lambda x: self._calculate_tail_ratio(x, n=3))
            
            chart_data = []
            latest_time = sector_df['时间'].max()
            temp_df = sector_df[sector_df['时间'] == latest_time]
            
            sector_names_speed = temp_df.sort_values(by='板块5分涨速', ascending=False).head(3)['板块名'].tolist()
            sector_names_change = temp_df.sort_values(by='板块涨幅', ascending=False).head(3)['板块名'].tolist()
            sector_names = list(set(sector_names + sector_names_speed + sector_names_change))
            
            for sector_name in sector_names:
                sector_data = sector_df[sector_df['板块名'] == sector_name]
                if not sector_data.empty:
                    sector_data = sector_data.sort_values(by='时间')
                    chart_data.append({
                        "name": f'{sector_name}红盘率',
                        "x": sector_data['时间'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                        "y": sector_data['uprate5'].tolist()
                    })
            
            return jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块uprate5",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "uprate5"},
                    "legend": {"title": "板块名称"}
                }
            })
        
        except Exception as e:
            self.logger.error(f"获取板块uprate5数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    def get_sector_speed_chart(self):
        """返回板块涨速累加图表数据"""
        try:
            top_sectors = self._get_top_sectors(120)
            
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "股票数据文件读取失败"
                })
            
            stock_minute_df = self.data_cache.load_data('stock_minute_df')
            if stock_minute_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "分钟数据文件读取失败"
                })
            
            # 数据清理和预处理
            stock_df = stock_df.replace([np.inf, -np.inf], 0).fillna(0)
            stock_minute_df = stock_minute_df.replace([np.inf, -np.inf], 0).fillna(0)
            
            stock_df['Sector'] = stock_df['Sector'].astype(str)
            stock_df['id'] = stock_df['id'].astype(int)
            stock_df['change'] = stock_df['change'].astype(float)
            stock_df['time'] = pd.to_datetime(stock_df['time'])
            
            latest_time = stock_df['time'].max()
            stock_df = stock_df[stock_df['time'] == latest_time]
            
            affinity_df = self.data_cache.load_data('affinity_df')
            if affinity_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "板块关联数据文件读取失败"
                })
            
            chart_data = []
            
            for sector_name in top_sectors:
                # 模糊匹配板块
                sector_affinity_df = affinity_df[
                    affinity_df['板块'].str.contains(sector_name, na=False, case=False) |
                    affinity_df['板块'].apply(lambda x: sector_name in str(x) if pd.notna(x) else False)
                ]
                
                if sector_affinity_df.empty:
                    continue
                
                stock_ids = list(set(sector_affinity_df['股票id'].tolist()))
                stock_count = len(stock_ids)
                
                # 过滤股票ID
                stock_ids = [id for id in stock_ids if id < 680000 and (id < 400000 or id > 600000)]
                filtered_count = len(stock_ids)
                
                stock_minute_df_temp = stock_minute_df[stock_minute_df['id'].isin(stock_ids)]
                stock_minute_df_temp = stock_minute_df_temp[stock_minute_df_temp['change'] > 2]
                
                if stock_minute_df_temp.empty:
                    continue
                
                # 按时间组聚合
                stock_minute_df_temp = stock_minute_df_temp.groupby('time').agg({
                    'speed_change_1min': 'mean',
                    'id': 'count'
                }).reset_index()
                
                stock_minute_df_temp = stock_minute_df_temp.rename(columns={'id': 'stock_count'})
                stock_minute_df_temp = stock_minute_df_temp.sort_values('time')
                
                stock_minute_df_temp['speed_change_1min_rate'] = (
                    stock_minute_df_temp['speed_change_1min'] * 
                    stock_minute_df_temp['stock_count'] / filtered_count
                )
                stock_minute_df_temp['speed_change_1min_cumsum'] = (
                    stock_minute_df_temp['speed_change_1min_rate'].cumsum()
                )
                
                stock_minute_df_temp['time'] = pd.to_datetime(stock_minute_df_temp['time'])
                
                chart_data.append({
                    "name": f'{sector_name}涨速变化累计',
                    "x": stock_minute_df_temp['time'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                    "y": stock_minute_df_temp['speed_change_1min_cumsum'].tolist()
                })
            
            return jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块涨速变化累计",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "累计涨速"},
                    "legend": {"title": "板块名称"}
                }
            })
        
        except Exception as e:
            self.logger.error(f"获取板块涨速数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    def get_plate_info_table_data(self):
        """返回板块概要数据表"""
        try:
            start_time = time.time()
            sector_name = request.args.get('sectors', '航运概念')
            
            plate_df = self.data_cache.load_data('plate_df')
            if plate_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "板块数据文件读取失败"
                })
            
            # 数据处理
            plate_df['时间'] = pd.to_datetime(plate_df['时间'])
            latest_time = plate_df['时间'].max()
            plate_df = plate_df[plate_df['时间'] == latest_time]
            
            # 计算大盘涨速分布
            speed_bins = [-10, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 10]
            speed_counts = []
            for i in range(len(speed_bins)-1):
                count = len(plate_df[
                    (plate_df['板块5分涨速'] >= speed_bins[i]) & 
                    (plate_df['板块5分涨速'] < speed_bins[i+1])
                ])
                speed_counts.append(str(count))
            market_speed_distribution = "-".join(speed_counts)
            plate_df['大盘涨速分布'] = market_speed_distribution
            
            plate_df['板块名'] = plate_df['板块名'].astype(str)
            
            # 获取排名前15的板块
            top_by_change = plate_df.sort_values(by='板块涨幅', ascending=False).head(15)['板块名'].tolist()
            top_by_turnover = plate_df.sort_values(by='强势分时换手占比', ascending=False).head(15)['板块名'].tolist()
            top_plates_list = list(set(top_by_change + top_by_turnover))
            
            if sector_name not in top_plates_list:
                top_plates_list.append(sector_name)
            
            plate_df = plate_df[plate_df['板块名'].isin(top_plates_list)]
            plate_df = plate_df.sort_values(by='板块涨幅', ascending=False)
            plate_df = plate_df.drop_duplicates(subset=['板块名']).reset_index(drop=True)
            
            # 定义表格列
            columns = [
                {"field": "时间", "header": "时间"},
                {"field": "板块名", "header": "板块名"},
                {"field": "板块涨幅", "header": "板块涨幅", "backgroundColor": "redGreen"},
                {"field": "板块昨日涨幅", "header": "板块昨日涨幅", "backgroundColor": "redGreen"},
                {"field": "强势分时换手占比", "header": "强势分时换手占比", "backgroundColor": "redGreen"},
                {"field": "板块5分涨速", "header": "板块5分涨速", "backgroundColor": "redGreen"},
                {"field": "板块量比", "header": "板块量比", "backgroundColor": "redGreen"},
                {"field": "涨速分布", "header": "涨速分布"},
                {"field": "涨幅分布", "header": "涨幅分布"},
                {"field": "涨停梯度", "header": "涨停梯度"},
                {"field": "涨速排名", "header": "涨速排名"},
                {"field": "涨幅排名", "header": "涨幅排名"},
                {"field": "大盘量比", "header": "大盘量比"},
                {"field": "大盘涨速分布", "header": "大盘涨速分布"},
            ]
            
            valid_columns = [col for col in columns if col["field"] in plate_df.columns]
            
            rows = []
            for _, row_data in plate_df.iterrows():
                row = {}
                for col in valid_columns:
                    field = col["field"]
                    value = row_data[field]
                    
                    if isinstance(value, (float, np.float64, np.float32)):
                        value = round(value, 2)
                    
                    row[field] = value
                
                rows.append(row)
            
            return jsonify({
                "columns": valid_columns,
                "rows": rows
            })
        
        except Exception as e:
            self.logger.error(f"获取板块信息失败: {e}")
            return jsonify({"error": str(e)}), 500

    def get_stocks_table_data(self):
        """返回股票数据表"""
        try:
            sector_name = request.args.get('sector_name') or request.args.get('sectors', '航运概念')
            component_id = request.args.get('componentId', 'table2')
            
            self.logger.info(f"API调用: componentId={component_id}, 传入的sector_name={sector_name}")
            
            # 对于table12，优先使用动态标题
            if component_id == 'table12':
                sector_name = self.dynamic_titles.get('table12', sector_name)
                self.logger.info(f"table12 使用动态标题中的板块: {sector_name}")
            
            # 根据组件ID获取对应板块
            if component_id in ['table2', 'table21', 'table22', 'table23', 'table24']:
                try:
                    top_sectors = self._get_top_sectors()
                    sector_map = {
                        'table2': 0, 'table21': 1, 'table22': 2, 'table23': 3, 'table24': 4
                    }
                    if component_id in sector_map and len(top_sectors) > sector_map[component_id]:
                        sector_name = top_sectors[sector_map[component_id]]
                        self.logger.info(f"组件 {component_id} 使用动态板块: {sector_name}")
                except Exception as e:
                    self.logger.warning(f"获取动态板块失败，使用默认板块: {e}")
            
            self.logger.info(f"最终使用的板块名称: {sector_name}")
            
            # 读取股票数据
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "股票数据文件读取失败"
                })
            
            # 数据预处理
            stock_df['time'] = pd.to_datetime(stock_df['time'])
            latest_time = stock_df['time'].max()
            stock_df = stock_df[stock_df['time'] == latest_time]
            
            stock_df['Sector'] = stock_df['Sector'].astype(str)
            stock_df['id'] = stock_df['id'].astype(int)
            stock_df['change'] = stock_df['change'].astype(float)
            
            # 读取板块关联数据
            affinity_df = pd.read_csv('strategy\\strategy001\\data\\板块内股票同涨率_长周期.csv')
            
            # 模糊匹配板块
            sector_affinity_df = affinity_df[
                affinity_df['板块'].str.contains(sector_name, na=False, case=False) |
                affinity_df['板块'].apply(lambda x: sector_name in str(x) if pd.notna(x) else False)
            ]
            
            if sector_affinity_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": f"未找到包含 '{sector_name}' 的板块股票数据"
                })
            
            matched_sectors = sector_affinity_df['板块'].unique()
            self.logger.info(f"匹配到的板块: {matched_sectors}")
            
            stock_ids = sector_affinity_df['股票id'].tolist()
            original_count = len(stock_ids)
            
            # 过滤股票ID
            stock_ids = [id for id in stock_ids if id < 680000 and (id < 400000 or id > 600000)]
            self.logger.info(f"过滤后剩余 {len(stock_ids)} 只股票（原始: {original_count}）")
            
            # 获取股票数据
            sector_stock_df = stock_df[stock_df['id'].isin(stock_ids)]
            
            if sector_stock_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": f"在当前数据中未找到板块 '{sector_name}' 的股票"
                })
            
            # 筛选优质股票
            stock1_list = sector_stock_df.sort_values(by='change', ascending=False).head(30)['id'].tolist()
            stock2_list = sector_stock_df[sector_stock_df['开盘换手率'] > 0.08].sort_values(by='开盘换手率', ascending=False)['id'].tolist()
            stock3_list = sector_stock_df[sector_stock_df['近10日内涨停数'] > 0]['id'].tolist()
            
            final_stock_ids = list(set(stock1_list) | set(stock2_list) | set(stock3_list))
            final_stock_df = sector_stock_df[sector_stock_df['id'].isin(final_stock_ids)]
            
            self.logger.info(f"最终筛选出 {len(final_stock_df)} 只优质股票")
            
            # 合并同涨率数据
            final_stock_df = pd.merge(
                final_stock_df, 
                sector_affinity_df[['股票id', '同涨率']], 
                left_on='id', right_on='股票id', how='left'
            )
            
            # 排序和填充
            final_stock_df = final_stock_df.sort_values(by='开盘换手率', ascending=False)
            final_stock_df = final_stock_df.fillna(-1)
            final_stock_df = final_stock_df.sort_values(by='change', ascending=False)
            
            # 定义表格列
            columns = [
                {"field": "id", "header": "股票ID", "visible": False},
                {"field": "stock_name", "header": "股票名称"},
                {"field": "昨日涨幅", "header": "昨涨幅", "backgroundColor": "redGreen"},
                {"field": "change", "header": "今涨幅(%)", "backgroundColor": "redGreen"},
                {"field": "竞价涨幅", "header": "竞涨幅", "backgroundColor": "redGreen"},
                {"field": "开盘换手率", "header": "竞换手", "backgroundColor": "redGreen"},
                {"field": "volume_ratio", "header": "量比", "backgroundColor": "redGreen"},
                {"field": "近10日内涨停数", "header": "10日涨停", "backgroundColor": "redGreen"},
                {"field": "连板数", "header": "连板数", "backgroundColor": "redGreen", "visible": False},
                {"field": "当日换手率", "header": "当日换手率", "backgroundColor": "redGreen", "visible": False},
                {"field": "同涨率", "header": "同涨率", "backgroundColor": "redGreen", "visible": False},
            ]
            
            valid_columns = [col for col in columns if col["field"] in final_stock_df.columns]
            
            rows = []
            for _, row_data in final_stock_df.iterrows():
                row = {}
                for col in valid_columns:
                    field = col["field"]
                    value = row_data[field]
                    
                    if isinstance(value, (float, np.float64, np.float32)):
                        if np.isinf(value):
                            value = 999.99
                        else:
                            value = round(value, 2)
                    
                    row[field] = value
                
                rows.append(row)
            
            return jsonify({
                "columns": valid_columns,
                "rows": rows,
                "sector_name": sector_name,
                "total_stocks": len(rows)
            })
        
        except Exception as e:
            self.logger.error(f"获取股票表格数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    def get_up_limit_table_data(self):
        """返回涨停数据表"""
        try:
            up_limit_df = pd.read_csv(r'strategy\showhtml\server\up_limit_df.csv')
            
            columns = [
                {"field": "时间", "header": "时间"},
                {"field": "股票ID", "header": "股票ID", "visible": False},
                {"field": "股票名称", "header": "股票名称"},
                {"field": "板块1", "header": "板块1"},
                {"field": "板块2", "header": "板块2"},
                {"field": "板块3", "header": "板块3", "visible": False},
                {"field": "板块4", "header": "板块4", "visible": False},
                {"field": "板块5", "header": "板块5", "visible": False},
                {"field": "10日涨停数", "header": "10日涨停数"},
                {"field": "连板数", "header": "连板数", "visible": False},
            ]
            
            valid_columns = [col for col in columns if col["field"] in up_limit_df.columns]
            
            rows = []
            for _, row_data in up_limit_df.iterrows():
                row = {}
                for col in valid_columns:
                    field = col["field"]
                    value = row_data[field]
                    
                    if isinstance(value, (float, np.float64, np.float32)):
                        value = round(value, 2)
                    
                    row[field] = value
                
                rows.append(row)
            
            return jsonify({
                "columns": valid_columns,
                "rows": rows
            })
        
        except Exception as e:
            self.logger.error(f"获取涨停数据失败: {e}")
            return jsonify({"error": str(e)}), 500

    # ===== SSE 和更新相关方法 =====
    
    def update_dashboard(self):
        """接收页面更新请求"""
        data = request.json
        self.logger.info(f"收到更新请求: {data}")
        
        params = data.get('params', {})
        if isinstance(params, dict):
            sector_name = params.get('sectors', '航运概念')
        else:
            sector_name = str(params) if params else '航运概念'
        
        self.selected_sector = sector_name
        self.dynamic_titles['table12'] = sector_name
        
        self.latest_update = {
            "componentId": data.get('componentId', 'chart2'),
            "params": params,
            "timestamp": time.time(),
            "action": "config_update",
            "sector_name": sector_name
        }
        
        update_message = {
            "action": "reload_config",
            "sector_name": sector_name,
            "timestamp": time.time()
        }
        self._send_update_to_clients(update_message)
        
        return jsonify({
            "status": "success",
            "message": "Update request sent",
            "sector_name": sector_name,
            "updated_titles": self.dynamic_titles
        })

    def dashboard_updates(self):
        """SSE事件流"""
        def event_stream():
            client_queue = queue.Queue()
            client_id = f"client_{len(self.sse_clients)}_{time.time()}"
            
            try:
                self.sse_clients.append(client_queue)
                self.logger.info(f"SSE客户端连接: {client_id}，当前总连接数: {len(self.sse_clients)}")
                
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
                            "active_connections": len(self.sse_clients)
                        }
                        yield f"data: {json.dumps(heartbeat)}\n\n"
                        continue
                    except GeneratorExit:
                        self.logger.info(f"SSE客户端主动断开: {client_id}")
                        break
                        
            except Exception as e:
                self.logger.error(f"SSE连接异常 {client_id}: {e}")
            finally:
                if client_queue in self.sse_clients:
                    self.sse_clients.remove(client_queue)
                    self.logger.info(f"SSE客户端清理: {client_id}，剩余连接数: {len(self.sse_clients)}")
        
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

    def notify_update(self):
        """接收更新通知并通过SSE广播"""
        data = request.json
        
        try:
            top_sectors = self._update_dynamic_titles()
            self.logger.info(f"涨幅前5板块: {top_sectors}")
            self.logger.info(f"动态标题已更新: {self.dynamic_titles}")
        except Exception as e:
            self.logger.error(f"notify_update中更新标题失败: {e}")
        
        update_message = {
            "action": "reload_config",
            "sector_name": self.selected_sector,
            "timestamp": time.time()
        }
        
        self._send_update_to_clients(update_message)
        return jsonify({
            "status": "success",
            "message": "更新通知已发送，前端将重新加载配置"
        })

    def get_dynamic_titles_debug(self):
        """调试端点：返回当前的动态标题状态"""
        try:
            top_sectors = self._get_top_sectors()
        except:
            top_sectors = ["获取失败"]
        
        return jsonify({
            "dynamic_titles": self.dynamic_titles,
            "selected_sector": self.selected_sector,
            "latest_update": self.latest_update,
            "current_top_sectors": top_sectors,
            "timestamp": time.time()
        })

    # ===== 辅助方法 =====
    
    def _send_update_to_clients(self, data):
        """发送更新到所有SSE客户端"""
        for client in list(self.sse_clients):
            try:
                client.put(f"data: {json.dumps(data)}\n\n")
            except:
                self.sse_clients.remove(client)

    def _get_dynamic_titles_list(self):
        """获取动态标题列表"""
        return list(self.dynamic_titles.values())

    def _get_top_sectors(self, n=5):
        """获取涨幅前n的板块名称"""
        try:
            plate_df = pd.read_csv('strategy\\showhtml\\server\\good_plate_df.csv')
            plate_df['时间'] = pd.to_datetime(plate_df['时间'])
            latest_time = plate_df['时间'].max()
            plate_df = plate_df[plate_df['时间'] == latest_time]
            
            top_sectors = plate_df.sort_values(by='板块涨幅', ascending=False).head(n)
            top_sectors_list = top_sectors['板块名'].tolist()
            
            # 加入自定义优先板块
            top_sectors_list = self.my_plate_list + top_sectors_list
            return list(set(top_sectors_list))  # 去重
            
        except Exception as e:
            self.logger.error(f"获取涨幅前{n}板块失败: {e}")
            return ["航运概念", "可控核聚变", "军工"]

    def _update_dynamic_titles(self):
        """更新动态标题"""
        try:
            top_sectors = self._get_top_sectors()
            
            while len(top_sectors) < 5:
                top_sectors.append("默认板块")
            
            current_table12 = self.dynamic_titles.get("table12", self.selected_sector)
            
            self.dynamic_titles.update({
                "table2": f"{top_sectors[0]}",
                "table21": f"{top_sectors[1]}",
                "table22": f"{top_sectors[2]}",
                "table23": f"{top_sectors[3]}",
                "table24": f"{top_sectors[4]}",
            })
            
            self.dynamic_titles["table12"] = current_table12
            
            self.logger.info(f"动态标题已更新: {self.dynamic_titles}")
            return top_sectors
            
        except Exception as e:
            self.logger.error(f"更新动态标题失败: {e}")
            return ["航运概念", "可控核聚变", "军工"]

    def _calculate_tail_ratio(self, number_string, n):
        """计算倒数后n个数的合计与总合计的比值"""
        try:
            numbers = [float(x) for x in number_string.split('-')]
            total_sum = sum(numbers)
            tail_numbers = numbers[-n:] if n <= len(numbers) else numbers
            tail_sum = sum(tail_numbers)
            
            if total_sum == 0:
                return 0.0
            else:
                return round(tail_sum / total_sum, 2)
        except:
            return 0.0

    def _calculate_center_of_mass(self, number_string):
        """计算数字串的重心位置"""
        try:
            numbers = [float(x) for x in number_string.split('-')]
            weighted_sum = 0
            value_sum = 0
            
            for index, value in enumerate(numbers):
                position = index + 1
                weighted_sum += position * value
                value_sum += value
            
            if value_sum == 0:
                return 0
            
            return round(weighted_sum / value_sum, 2)
        except:
            return 0


# 数据缓存类 - 保持原有逻辑
class DataCache:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        
    def get_file_path(self, file_key):
        """获取文件路径"""
        paths = {
            'stock_df': 'strategy\\showhtml\\server\\stock_df.csv',
            'affinity_df': 'strategy\\strategy001\\data\\板块内股票同涨率_长周期.csv',
            'plate_df': 'strategy\\showhtml\\server\\good_plate_df.csv',
            'stock_minute_df': 'strategy\\showhtml\\server\\stock_minute_df.csv',
        }
        return paths.get(file_key)
        
    def get_file_timestamp(self, file_path):
        """获取文件的修改时间戳"""
        try:
            return os.path.getmtime(file_path)
        except OSError:
            return 0
            
    def should_reload(self, file_key):
        """检查是否需要重新加载文件"""
        file_path = self.get_file_path(file_key)
        if not file_path or not os.path.exists(file_path):
            return False
            
        current_timestamp = self.get_file_timestamp(file_path)
        cached_timestamp = self.timestamps.get(file_key, 0)
        
        return current_timestamp > cached_timestamp
        
    def load_data(self, file_key):
        """加载或返回缓存的数据"""
        if file_key not in self.cache or self.should_reload(file_key):
            file_path = self.get_file_path(file_key)
            if not file_path or not os.path.exists(file_path):
                print(f"警告: 文件不存在 {file_path}")
                return pd.DataFrame()
                
            try:
                print(f"重新加载文件: {file_path}")
                df = pd.read_csv(file_path)
                self.cache[file_key] = df
                self.timestamps[file_key] = self.get_file_timestamp(file_path)
                return df
            except Exception as e:
                print(f"加载文件失败 {file_path}: {e}")
                return pd.DataFrame()
        else:
            print(f"使用缓存数据: {file_key}")
            return self.cache[file_key].copy()
            
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()


def main():
    """主函数"""
    print("🚀 启动多板块股票仪表盘服务器...")
    
    server = MultiPlateStockServer(port=5008)
    
    try:
        # 启动时初始化动态标题
        server._update_dynamic_titles()
        print("✅ 动态标题初始化完成")
    except Exception as e:
        print(f"⚠️ 动态标题初始化失败: {e}")
    
    server.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
