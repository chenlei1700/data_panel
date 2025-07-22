"""
图表数据处理器
负责处理各种图表类型的数据生成逻辑
"""
import pandas as pd
import numpy as np
from flask import jsonify
from .base_processor import BaseDataProcessor


class ChartDataProcessor(BaseDataProcessor):
    """图表数据处理器"""
    
    def process_sector_line_chart_change(self):
        """返回板块涨幅折线图数据"""
        try:
            sector_names = self.server._get_dynamic_titles_list()
            sector_df = self.data_cache.load_data('plate_df')
            
            if sector_df.empty:
                return self.error_response("板块数据文件读取失败")
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            
            # 直接执行数据处理逻辑，缓存由基类自动处理
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
            return self.error_response(f"获取板块涨幅数据失败: {e}")

    def process_sector_line_chart_uplimit(self):
        """返回板块近似涨停折线图数据"""
        try:
            sector_names = self.server._get_dynamic_titles_list()
            sector_df = self.data_cache.load_data('plate_df')
            
            if sector_df.empty:
                return self.error_response("板块数据文件读取失败")
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            
            # 构建用于哈希比较的源数据
            latest_time = sector_df['时间'].max()
            source_data = {
                'data_time': str(latest_time),
                'data_count': len(sector_df),
                'sector_names': sorted(sector_names),  # 排序确保一致性
                'dynamic_titles': self.server.dynamic_titles.copy(),
                'file_timestamp': self.data_cache.timestamps.get('plate_df', 0)  # 添加文件时间戳
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/chart-data/sector-line-chart_uplimit'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, None, source_data)
            
            if should_cache and cached_response:
                self.logger.info("使用缓存数据返回板块近似涨停折线图")
                return cached_response
            
            # 需要重新计算，继续执行原有逻辑
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
            
            # 构建响应数据
            response_data = jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块近似涨停数",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "近似涨停数"},
                    "legend": {"title": "板块名称"}
                }
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, None, source_data, response_data)
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取板块涨停数据失败: {e}")

    def process_sector_line_chart_uprate(self):
        """返回板块红盘率折线图数据"""
        try:
            sector_names = self.server._get_dynamic_titles_list()
            sector_df = self.data_cache.load_data('plate_df')
            
            if sector_df.empty:
                return self.error_response("板块数据文件读取失败")
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            
            # 构建用于哈希比较的源数据
            latest_time = sector_df['时间'].max()
            source_data = {
                'data_time': str(latest_time),
                'data_count': len(sector_df),
                'sector_names': sorted(sector_names),  # 排序确保一致性
                'dynamic_titles': self.server.dynamic_titles.copy(),
                'file_timestamp': self.data_cache.timestamps.get('plate_df', 0)  # 添加文件时间戳
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/chart-data/sector-line-chart_uprate'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, None, source_data)
            
            if should_cache and cached_response:
                self.logger.info("使用缓存数据返回板块红盘率折线图")
                return cached_response
            
            # 需要重新计算，继续执行原有逻辑
            sector_df['uprate'] = sector_df['涨幅分布'].apply(lambda x: self.server._calculate_tail_ratio(x, n=6))
            
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
            
            # 构建响应数据
            response_data = jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块红盘率",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "红盘率"},
                    "legend": {"title": "板块名称"}
                }
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, None, source_data, response_data)
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取板块红盘率数据失败: {e}")

    def process_sector_line_chart_uprate5(self):
        """返回板块uprate5折线图数据"""
        try:
            sector_names = self.server._get_dynamic_titles_list()
            sector_df = self.data_cache.load_data('plate_df')
            
            if sector_df.empty:
                return self.error_response("板块数据文件读取失败")
            
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            sector_df = sector_df[sector_df['时间'].dt.date == sector_df['时间'].dt.date.max()]
            sector_df['uprate5'] = sector_df['涨幅分布'].apply(lambda x: self.server._calculate_tail_ratio(x, n=3))
            
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
            return self.error_response(f"获取板块uprate5数据失败: {e}")

    def process_sector_speed_chart(self):
        """返回板块涨速累加图表数据"""
        try:
            top_sectors = self.server._get_top_sectors(120)
            
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
            
            # 构建用于哈希比较的源数据
            stock_df['time'] = pd.to_datetime(stock_df['time'])
            latest_time = stock_df['time'].max()
            
            source_data = {
                'top_sectors': sorted(top_sectors[:10]),  # 只取前10个用于哈希，避免数据量过大
                'stock_data_time': str(latest_time),
                'stock_minute_count': len(stock_minute_df),
                'file_timestamps': {
                    'stock_df': self.data_cache.timestamps.get('stock_df', 0),
                    'stock_minute_df': self.data_cache.timestamps.get('stock_minute_df', 0),
                    'affinity_df': self.data_cache.timestamps.get('affinity_df', 0)
                }
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/chart-data/sector_speed_chart'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, None, source_data)
            
            if should_cache and cached_response:
                self.logger.info("使用缓存数据返回板块涨速累加图表")
                return cached_response
            
            # 需要重新计算，继续执行原有逻辑
            self.logger.info(f"重新计算板块涨速数据，处理 {len(top_sectors)} 个板块")
            
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
            
            # 优化：限制处理的板块数量以提升性能
            process_sectors = top_sectors[:20]  # 只处理前20个板块，提升性能
            self.logger.info(f"实际处理板块数量: {len(process_sectors)}")
            
            for sector_name in process_sectors:
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
            
            # 构建响应数据
            response_data = jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块涨速变化累计",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "累计涨速"},
                    "legend": {"title": "板块名称"}
                }
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, None, source_data, response_data)
            
            self.logger.info(f"板块涨速数据计算完成，生成 {len(chart_data)} 个板块的图表数据")
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取板块涨速数据失败: {e}")

    def process(self, chart_type: str):
        """根据图表类型处理数据"""
        method_map = {
            'sector-line-chart_change': self.process_sector_line_chart_change,
            'sector-line-chart_uplimit': self.process_sector_line_chart_uplimit,
            'sector-line-chart_uprate': self.process_sector_line_chart_uprate,
            'sector-line-chart_uprate5': self.process_sector_line_chart_uprate5,
            'sector_speed_chart': self.process_sector_speed_chart,
        }
        
        if chart_type in method_map:
            return method_map[chart_type]()
        else:
            return self.error_response(f"未知的图表类型: {chart_type}")
