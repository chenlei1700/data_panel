"""
多板块服务器处理器
包含多板块服务器的所有数据处理逻辑：图表、表格、板块等

Author: chenlei
Date: 2025-07-23
"""
import time
import pandas as pd
import numpy as np
from flask import jsonify, request

# 处理相对导入问题
try:
    from .base_processor import BaseDataProcessor
except ImportError:
    from base_processor import BaseDataProcessor


class MultiPlateProcessor(BaseDataProcessor):
    """多板块服务器专用处理器 - 统一管理所有处理逻辑"""
    
    # =========================================================================
    # 图表处理方法 (原 chart_processor.py 中的方法)
    # =========================================================================
    
    def process_sector_line_chart_change(self):
        """板块涨幅折线图数据"""
        try:
            sector_names = self.server._get_dynamic_titles_list()
            sector_df = self.data_cache.load_data('plate_df')
            
            if sector_df.empty:
                return self.error_response("板块数据文件读取失败")
            
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
            return self.error_response(f"获取板块涨幅数据失败: {e}")

    def process_sector_speed_chart(self):
        """板块涨速累加图表数据"""
        try:
            self.logger.info("开始处理板块涨速累加图表")
            
            # 读取基础数据
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "chartType": "line",
                    "data": [],
                    "layout": {
                        "title": "板块涨速变化累计",
                        "xaxis": {"title": "时间"},
                        "yaxis": {"title": "累计涨速"},
                        "legend": {"title": "板块名称"}
                    },
                    "message": "股票数据文件读取失败"
                })
            
            # 获取板块涨幅排序
            top_sectors = stock_df['Sector'].value_counts().head(10).index.tolist()
            if not top_sectors:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "未找到有效的板块数据"
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

    def process_sector_line_chart_uplimit(self):
        """板块近似涨停折线图数据"""
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
        """板块红盘率折线图数据"""
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
        """板块uprate5折线图数据"""
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

    # =========================================================================
    # 表格处理方法 (原 table_processor.py 中的方法)
    # =========================================================================
    
    def process_plate_info(self):
        """板块概要数据表"""
        try:
            sector_df = self.data_cache.load_data('plate_df')
            if sector_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "板块数据文件读取失败"
                })
            
            # 简化版数据处理
            sector_df['时间'] = pd.to_datetime(sector_df['时间'])
            latest_data = sector_df[sector_df['时间'] == sector_df['时间'].max()]
            
            # 构建表格数据
            table_data = []
            for _, row in latest_data.iterrows():
                table_data.append({
                    "板块名": row['板块名'],
                    "板块涨幅": f"{row['板块涨幅']:.2f}%",
                    "板块5分涨速": f"{row['板块5分涨速']:.2f}%",
                    "涨幅分布": row['涨幅分布']
                })
            
            return jsonify({
                "columns": ["板块名", "板块涨幅", "板块5分涨速", "涨幅分布"],
                "rows": table_data
            })
        
        except Exception as e:
            return self.error_response(f"获取板块概要数据失败: {e}")

    def process_stocks(self):
        """股票数据表"""
        try:
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "股票数据文件读取失败"
                })
            
            # 简化版处理
            latest_data = stock_df.head(100)  # 限制数据量
            
            table_data = []
            for _, row in latest_data.iterrows():
                table_data.append({
                    "股票代码": row.get('id', ''),
                    "股票名称": row.get('name', ''),
                    "涨跌幅": f"{row.get('change', 0):.2f}%",
                    "板块": row.get('Sector', '')
                })
            
            return jsonify({
                "columns": ["股票代码", "股票名称", "涨跌幅", "板块"],
                "rows": table_data
            })
        
        except Exception as e:
            return self.error_response(f"获取股票数据失败: {e}")

    # =========================================================================
    # 表格处理方法 (原 table_processor.py 中的方法)  
    # =========================================================================
    
    def process_plate_info_table_data(self):
        """返回板块概要数据表"""
        try:
            start_time = time.time()
            sector_name = request.args.get('sectors', '航运概念')
            
            # 构建缓存参数
            cache_params = self.build_cache_params(sector_name=sector_name)
            
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
            
            # 构建用于哈希比较的源数据
            source_data = {
                'sector_name': sector_name,
                'data_time': str(latest_time),
                'data_count': len(plate_df),
                # 添加影响结果的关键字段的哈希
                'plate_summary': plate_df[['板块名', '板块涨幅', '板块5分涨速']].to_dict('records')[:10]  # 只取前10个作为摘要
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/table-data/plate_info'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, cache_params, source_data)
            
            if should_cache and cached_response:
                self.logger.info(f"使用缓存数据返回板块概要表格: {sector_name}")
                return cached_response
            
            # 需要重新计算，继续执行原有逻辑
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
            
            # 构建响应数据
            response_data = jsonify({
                "columns": valid_columns,
                "rows": rows
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, cache_params, source_data, response_data)
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取板块信息失败: {e}")

    def process_stocks_table_data(self):
        """返回股票数据表"""
        try:
            # TODO: 从 table_processor.py 迁移完整实现
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "股票数据文件读取失败"
                })
            
            # 简化版处理逻辑
            columns = [
                {"field": "name", "header": "股票名称"},
                {"field": "change", "header": "涨跌幅", "backgroundColor": "redGreen"},
                {"field": "Sector", "header": "板块"},
                {"field": "speed_change_1min", "header": "1分钟涨速", "backgroundColor": "redGreen"}
            ]
            
            rows = []
            for _, row in stock_df.head(100).iterrows():  # 限制返回数量
                row_data = {}
                for col in columns:
                    field = col["field"]
                    value = row.get(field, '')
                    if isinstance(value, (float, np.float64, np.float32)):
                        value = round(value, 2)
                    row_data[field] = value
                rows.append(row_data)
            
            return jsonify({
                "columns": columns,
                "rows": rows
            })
        
        except Exception as e:
            return self.error_response(f"获取股票数据失败: {e}")
    def process_get_up_limit_table_data(self):
        """返回涨停数据，从固定CSV文件读取"""
        try:
            # 读取CSV文件（使用固定路径）
            
            # 读取涨停数据
            up_limit_df = pd.read_csv(r'strategy\showhtml\server\up_limit_df.csv')
            
            # # 确保时间列被正确处理
            
            # up_limit_df['时间'] = pd.to_datetime(up_limit_df['时间'])
            # # 获取最新的时间的行
            # latest_time = up_limit_df['时间'].max()
            # # for test 获取09：41的时间
            # # latest_time = plate_df['时间'].max().replace(hour=10, minute=5, second=0)
            # up_limit_df = up_limit_df[up_limit_df['时间'] == latest_time]
            # # 获取该时刻的大盘涨速分布，计算方法为：统计该时刻‘板块5分涨速列’-10~-0.6，-0.6~-0.4，-0.4~-0.2，-0.2~0, 0~0.2，0.2~0.4，0.4~0.6,0.6~10的数量，并用-号连接
            # speed_bins = [-10, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 10]
            # speed_counts = []
            # for i in range(len(speed_bins)-1):
            #     count = len(up_limit_df[(up_limit_df['板块5分涨速'] >= speed_bins[i]) & 
            #                         (up_limit_df['板块5分涨速'] < speed_bins[i+1])])
            #     speed_counts.append(str(count))
            # market_speed_distribution = "-".join(speed_counts)
            # up_limit_df['大盘涨速分布'] = market_speed_distribution
            # # 获取列Sector的值为sector_name的行
            # up_limit_df['板块名'] = up_limit_df['板块名'].astype(str)
            # up_limit_df = up_limit_df[up_limit_df['板块名'] == sector_name]
            
            
            # 定义表格列（根据CSV文件的实际列进行调整）
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
            
            # 确保所有列都存在于CSV文件中
            valid_columns = [col for col in columns if col["field"] in up_limit_df.columns]
            
            # 转换DataFrame为所需格式
            rows = []
            for _, row_data in up_limit_df.iterrows():
                row = {}
                for col in valid_columns:
                    field = col["field"]
                    value = row_data[field]
                    
                    # 处理数值格式（保留两位小数）
                    if isinstance(value, (float, np.float64, np.float32)):
                        value = round(value, 2)
                    
                    row[field] = value
                
                rows.append(row)
            
            return jsonify({
                "columns": valid_columns,
                "rows": rows
            })
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
        
    def process_up_limit_table_data(self):
        """返回涨停数据表"""
        # try:
        #     # TODO: 从 table_processor.py 迁移完整实现
        #     up_limit_df = self.data_cache.load_data('up_limit_df')
        #     if up_limit_df.empty:
        #         return jsonify({
        #             "columns": [],
        #             "rows": [],
        #             "message": "涨停数据文件读取失败"
        #         })
            
        #     # 简化版处理逻辑
        #     columns = [
        #         {"field": "name", "header": "股票名称"},
        #         {"field": "连板数", "header": "连板数", "backgroundColor": "redGreen"},
        #         {"field": "Sector", "header": "板块"},
        #         {"field": "涨停时间", "header": "涨停时间"}
        #     ]
            
        #     rows = []
        #     for _, row in up_limit_df.iterrows():
        #         row_data = {}
        #         for col in columns:
        #             field = col["field"]
        #             value = row.get(field, '')
        #             if isinstance(value, (float, np.float64, np.float32)):
        #                 value = round(value, 2)
        #             row_data[field] = value
        #         rows.append(row_data)
            
        #     return jsonify({
        #         "columns": columns,
        #         "rows": rows
        #     })
        
        # except Exception as e:
        #     return self.error_response(f"获取涨停数据失败: {e}")
        try:
            up_limit_df = self.data_cache.load_data('up_limit_df')
            
            if up_limit_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "涨停数据文件读取失败"
                })
            
            # 构建用于哈希比较的源数据
            source_data = {
                'data_count': len(up_limit_df),
                'file_timestamp': self.data_cache.timestamps.get('up_limit_df', 0),
                'data_sample': up_limit_df.head(5).to_dict('records') if not up_limit_df.empty else []
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/table-data/up_limit'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, None, source_data)
            
            if should_cache and cached_response:
                self.logger.info("使用缓存数据返回涨停数据表")
                return cached_response
            
            # 需要重新计算，继续执行原有逻辑
            # 定义表格列 - 根据实际CSV文件的列名
            columns = [
                {"field": "时间", "header": "时间"},
                {"field": "股票名称", "header": "股票名称"},
                {"field": "板块1", "header": "板块1"},
                {"field": "板块2", "header": "板块2"},  
                {"field": "板块3", "header": "板块3", "visible": False},
                {"field": "板块4", "header": "板块4", "visible": False},
                {"field": "板块5", "header": "板块5", "visible": False},
                {"field": "10日涨停数", "header": "10日涨停数", "backgroundColor": "redGreen"},
                {"field": "连板数", "header": "连板数", "backgroundColor": "redGreen"},
                {"field": "股票ID", "header": "股票ID", "visible": False},
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
            
            # 构建响应数据
            response_data = jsonify({
                "columns": valid_columns,
                "rows": rows
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, None, source_data, response_data)
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取涨停数据失败: {e}")

    def process_up_limit(self):
        """涨停数据表"""
        try:
            up_limit_df = self.data_cache.load_data('up_limit_df')
            if up_limit_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "涨停数据文件读取失败"
                })
            
            # 简化版处理
            table_data = []
            for _, row in up_limit_df.iterrows():
                table_data.append({
                    "股票名称": row.get('name', ''),
                    "连板数": row.get('连板数', 0),
                    "板块": row.get('Sector', ''),
                    "涨停时间": row.get('涨停时间', '')
                })
            
            return jsonify({
                "columns": ["股票名称", "连板数", "板块", "涨停时间"],
                "rows": table_data
            })
        
        except Exception as e:
            return self.error_response(f"获取涨停数据失败: {e}")

    # =========================================================================
    # 板块处理方法 (原 sector_processor.py 中的方法)
    # =========================================================================
    
    # =========================================================================
    # 板块处理方法 (原 sector_processor.py 中的方法)
    # =========================================================================
    
    def process_today_plate_up_limit_distribution(self):
        """
        获取今日各板块连板数分布，横轴为板块名称，纵轴为股票个数
        分别用堆积图展示各板块的连板数分布，从下往上为1板，2板，3板等
        """
        try:
            stock_all_level_df = self.data_cache.load_data('stock_all_level_df')
            if stock_all_level_df.empty:
                return self.error_response("股票连板数据文件读取失败")
            
            # 过滤掉不需要的板块
            stock_all_level_df = stock_all_level_df[~stock_all_level_df['Sector'].str.contains("沪股通|深股通|季报|融资融券", na=False)]
            stock_all_level_df = stock_all_level_df[stock_all_level_df['连板数'] > 0]
           
            stock_all_level_df['Level'] = stock_all_level_df['连板数']
            # 将连板数转换为整数，处理异常值
            stock_all_level_df['Level'] = pd.to_numeric(stock_all_level_df['Level'], errors='coerce').fillna(0).astype(int)

            # 按照板块分组，统计每个板块的连板数分布
            sector_level_stats = stock_all_level_df.groupby(['Sector', 'Level']).size().unstack(fill_value=0)
            
            # 获取所有的连板数等级
            max_level = min(stock_all_level_df['Level'].max(), 10)  # 限制最大连板数为10，避免过多分类
            level_columns = list(range(1, max_level + 1))
            
            # 确保所有连板数等级的列都存在
            for level in level_columns:
                if level not in sector_level_stats.columns:
                    sector_level_stats[level] = 0
            
            # 只保留需要的连板数列，并按顺序排列
            sector_level_stats = sector_level_stats[level_columns]
            
            # 计算每个板块的总股票数，按总数排序，只显示前20个板块
            sector_level_stats['total'] = sector_level_stats.sum(axis=1)
            sector_level_stats = sector_level_stats.sort_values('total', ascending=False).head(20)
            sector_level_stats = sector_level_stats.drop('total', axis=1)
            
            # 构建堆积图数据 - 使用与其他图表一致的格式
            categories = sector_level_stats.index.tolist()  # 板块名称作为横坐标
            chart_data = []
            
            # 为每个连板数等级创建一个系列
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#F1948A', '#D5DBDB', '#A569BD', '#F0B27A']
            
            for i, level in enumerate(level_columns):
                chart_data.append({
                    'name': f'{level}连板',
                    'x': categories,  # 板块名称
                    'y': sector_level_stats[level].tolist(),  # 对应的股票个数
                    'type': 'bar',  # 柱状图类型
                    'marker': {'color': colors[i % len(colors)]}
                })
            
            return jsonify({
                "chartType": "bar",  # 柱状图
                "data": chart_data,  # 图表数据
                "layout": {
                    "title": "各板块连板数分布",
                    "xaxis": {"title": "板块名称"},
                    "yaxis": {"title": "股票个数"},
                    "barmode": "stack",  # 堆积模式
                    "legend": {"title": "连板数"}
                }
            })
            
        except Exception as e:
            return self.error_response(f"获取板块连板数分布失败: {e}")
        
    def process_today_plate_up_limit_distribution_v2(self):
        """
        获取今日各板块连板数分布，横轴为板块名称，纵轴为股票个数
        分别用stackedAreaChart展示各板块的连板数分布，从下往上为1板，2板，3板等
        
        始终返回悬浮提示数据，由前端决定是否使用
        """
        try:
            stock_all_level_df = self.data_cache.load_data('stock_all_level_df')
            if stock_all_level_df.empty:
                return self.error_response("股票连板数据文件读取失败")
            
            # 过滤掉不需要的板块
            stock_all_level_df = stock_all_level_df[~stock_all_level_df['Sector'].str.contains("沪股通|深股通|季报|融资融券", na=False)]
            stock_all_level_df = stock_all_level_df[stock_all_level_df['连板数'] > 0]
           
            stock_all_level_df['Level'] = stock_all_level_df['连板数']
            # 将连板数转换为整数，处理异常值
            stock_all_level_df['Level'] = pd.to_numeric(stock_all_level_df['Level'], errors='coerce').fillna(0).astype(int)

            # 按照板块分组，统计每个板块的连板数分布
            sector_level_stats = stock_all_level_df.groupby(['Sector', 'Level']).size().unstack(fill_value=0)
            
            # 获取所有的连板数等级
            max_level = min(stock_all_level_df['Level'].max(), 6)  # 限制最大连板数为6，适合堆叠面积图
            level_columns = list(range(1, max_level + 1))
            
            # 确保所有连板数等级的列都存在
            for level in level_columns:
                if level not in sector_level_stats.columns:
                    sector_level_stats[level] = 0
            
            # 只保留需要的连板数列，并按顺序排列
            sector_level_stats = sector_level_stats[level_columns]
            
            # 计算每个板块的总股票数（所有连板数的合计），按总股票数排序（从大到小），只显示前15个板块（适合面积图显示）
            sector_level_stats['total_stocks'] = sector_level_stats.sum(axis=1)
            
            # 添加调试信息
            self.logger.info("排序前的板块顺序和总股票数:")
            for idx, total in sector_level_stats['total_stocks'].items():
                self.logger.info(f"  {idx}: {total}只")
            
            sector_level_stats = sector_level_stats.sort_values('total_stocks', ascending=False).head(15)
            
            # 添加调试信息
            self.logger.info("排序后的板块顺序和总股票数:")
            for idx, total in sector_level_stats['total_stocks'].items():
                self.logger.info(f"  {idx}: {total}只")
            
            sector_level_stats = sector_level_stats.drop('total_stocks', axis=1)
            
            # 构建 stackedAreaChart 数据格式
            xAxisValues = sector_level_stats.index.tolist()  # 板块名称作为横坐标
            
            # 构建数据字典，每个板块对应其各连板数的股票个数
            data = {}
            table_data = {}
            hover_data = {}  # 始终创建悬浮数据
            
            for sector_name in xAxisValues:
                sector_data = {}
                sector_hover = {}  # 始终存储股票名称列表
                total_stocks = 0
                
                for level in level_columns:
                    key = f"{level}连板"
                    value = int(sector_level_stats.loc[sector_name, level])
                    sector_data[key] = value
                    total_stocks += value
                    
                    # 始终获取该板块该连板等级的股票名称列表
                    level_stocks = stock_all_level_df[
                        (stock_all_level_df['Sector'] == sector_name) & 
                        (stock_all_level_df['Level'] == level)
                    ]['stock_name'].tolist()
                    
                    sector_hover[key] = level_stocks
                
                data[sector_name] = sector_data
                table_data[sector_name] = f"{total_stocks}只"
                hover_data[sector_name] = sector_hover
            
            # 定义连板数类型的顺序和颜色
            keyOrder = [f"{level}连板" for level in level_columns]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'][:len(level_columns)]
            
            # 构建返回数据，始终包含悬浮数据
            return jsonify({
                "stackedAreaData": {
                    "data": data,          # 每个板块的连板数分布数据
                    "keyOrder": keyOrder,  # 连板数类型的显示顺序
                    "colors": colors,      # 每个连板数类型的颜色
                    "hoverData": hover_data  # 鼠标悬浮时显示的股票名称列表
                },
                "xAxisValues": xAxisValues,  # 横轴板块名称
                "tableData": table_data      # 表格数据（总股票数）
            })
            
        except Exception as e:
            return self.error_response(f"获取板块连板数分布失败: {e}")

    def process_sector_stacked_area_data(self):
        """板块堆叠面积图数据 - 调用 v2 方法"""
        return self.process_today_plate_up_limit_distribution_v2()

    # =========================================================================
    # 统一处理入口
    # =========================================================================
    
    def process(self, method_name: str):
        """
        统一处理入口
        
        Args:
            method_name: 方法名称，如 'sector_line_chart_change'、'plate_info' 等
            
        Returns:
            处理结果
        """
        # 添加 process_ 前缀
        full_method_name = f'process_{method_name}'
        
        if hasattr(self, full_method_name):
            method = getattr(self, full_method_name)
            self.logger.info(f"多板块处理器执行方法: {full_method_name}")
            return method()
        else:
            available_methods = [method.replace('process_', '') for method in dir(self) 
                               if method.startswith('process_') and callable(getattr(self, method))]
            
            return self.error_response(
                f"多板块处理器不支持方法: {method_name}。"
                f"可用方法: {', '.join(available_methods)}"
            )
    
    def get_available_methods(self):
        """获取所有可用的处理方法"""
        methods = [method.replace('process_', '') for method in dir(self) 
                   if method.startswith('process_') and callable(getattr(self, method))]
        return sorted(methods)
