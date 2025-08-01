"""
market_review处理器模板
Author: Auto-generated
Date: 2025-07-26
Description: 复盘页面
"""
import os
from stock_data.factor.index.daily import FactorIndexDailyData
from stock_data.sentiment.market.daily import MarketSentimentDailyData
from stock_data.stock.index_daily import IndexDailyData
from stock_data.stock.stock_daily import StockDailyData
from .base_processor import BaseDataProcessor
from flask import jsonify, request
import pandas as pd
import numpy as np
import time


class MarketReviewProcessor(BaseDataProcessor):
    """复盘页面数据处理器"""
    
    def process_market_sentiment_daily(self):
        """市场情绪日数据的主板，创业板，科创版，ST板成交额 - 带启动缓存"""
        return self._process_with_startup_cache('/api/market_sentiment_daily', self._original_market_sentiment_daily)
    
    def _original_market_sentiment_daily(self):
        """市场情绪日数据的主板，创业板，科创版，ST板成交额"""
        d = FactorIndexDailyData()
        df = d.get_daily_data(start_date='2025-03-01')
        # 成交额amount变为以亿为单位，并保留2位小数
        df['amount'] = df['amount'] / 1e8
        df['amount'] = df['amount'].round(2)
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        market_list = ['主板', '创业板', '科创板', 'ST','全市场']
        chart_data = []
        for market in market_list:
            market_data = df[df['name'] == market]
            if not market_data.empty:
                market_data = market_data.sort_values(by='trade_date')
                chart_data.append({
                    "name": f'{market}成交额',
                    "x": market_data['date_str'].tolist(),
                    "y": market_data['amount'].tolist()
                })
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "各市场成交额",
                "xaxis": {"title": "时间"},
                "yaxis": {"title": "成交额(亿元)"},
                "legend": {"title": "市场名称"}
            }
        })
    
    def process_market_change_daily(self):
        """各市场涨幅 - 带启动缓存"""
        return self._process_with_startup_cache('/api/market_change_daily', self._original_market_change_daily)
    
    def _original_market_change_daily(self):
        """市场情绪日数据的主板，创业板，科创版，ST板成交额"""
        d = FactorIndexDailyData()
        df = d.get_daily_data(start_date='2025-03-01')
        # 成交额amount变为以亿为单位，并保留2位小数
       
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        market_list = ['主板', '创业板', 'ST','全市场']
        # 对name列groupby，计算change列的cumsum
        df['change'] = df.groupby('name')['change'].cumsum()
        chart_data = []
        for market in market_list:
            market_data = df[df['name'] == market]
            if not market_data.empty:
                market_data = market_data.sort_values(by='trade_date')
                chart_data.append({
                    "name": f'{market}涨幅',
                    "x": market_data['date_str'].tolist(),
                    "y": market_data['change'].tolist()
                })
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "各市场成交额",
                "xaxis": {"title": "时间"},
                "yaxis": {"title": "成交额(亿元)"},
                "legend": {"title": "市场名称"}
            }
        })
    
    def process_market_change_daily(self):
        """市场情绪日数据的主板，创业板，科创版，ST板涨幅"""
        d = FactorIndexDailyData()
        df = d.get_daily_data(start_date='2025-03-01')
        # 成交额amount变为以亿为单位，并保留2位小数
       
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        market_list = ['主板', '创业板', 'ST','全市场']
        # 对name列groupby，计算change列的cumsum
        df['change'] = df.groupby('name')['change'].cumsum()
        chart_data = []
        for market in market_list:
            market_data = df[df['name'] == market]
            if not market_data.empty:
                market_data = market_data.sort_values(by='trade_date')
                chart_data.append({
                    "name": f'{market}涨幅',
                    "x": market_data['date_str'].tolist(),
                    "y": market_data['change'].tolist()
                })
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "各市场成交额",
                "xaxis": {"title": "时间"},
                "yaxis": {"title": "成交额(亿元)"},
                "legend": {"title": "市场名称"}
            }
        })

    def process_shizhiyu_change_daily(self):
        """各市值域情绪日数据的平均涨幅 - 带启动缓存"""
        return self._process_with_startup_cache('/api/shizhiyu_change_daily', self._original_shizhiyu_change_daily)
    
    def _original_shizhiyu_change_daily(self):
        """各市值域情绪日数据的平均涨幅"""
        d = StockDailyData()

        df = d.get_daily_data(start_date='2025-07-01')
       
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        # 新建一列‘市值域’，按照total_mv列的值进行分类，分类规则为
        # 0-20亿：微盘 20-50亿：小盘 50-100亿：中盘 100亿-300亿：中大盘，300亿以上：大盘
        df['市值域'] = pd.cut(df['total_mv'], bins=[0, 20e8, 50e8, 100e8, 300e8, float('inf')],
                           labels=['微盘', '小盘', '中盘', '中大盘', '大盘'])
        # 按trade_date和市值域分组，计算change列的平均值
        df['day_change'] = df.groupby(['trade_date', '市值域'])['change'].transform('mean')
        # 每天的市值域各取1个，去掉重复的市值域
        df_temp = df.drop_duplicates(subset=['trade_date', '市值域'])
        # 按市值域分组，计算每个市值域的cumsum
        df_temp['cumsum_change'] = df_temp.groupby('市值域')['day_change'].cumsum()
        market_list = ['微盘', '小盘', '中盘', '中大盘', '大盘']
        chart_data = []
        for market in market_list:
            market_data = df_temp[df_temp['市值域'] == market]
            if not market_data.empty:
                market_data = market_data.sort_values(by='trade_date')
                chart_data.append({
                    "name": f'{market}涨幅',
                    "x": market_data['date_str'].tolist(),
                    "y": market_data['cumsum_change'].tolist()
                })
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "市值域日线涨幅",
                "xaxis": {"title": "时间"},
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "市场名称"}
            }
        })

    def process_lianban_jiji_rate(self):
        """连板晋级率 - 带启动缓存"""
        return self._process_with_startup_cache('/api/lianban_jiji_rate', self._original_lianban_jiji_rate)
    
    def _original_lianban_jiji_rate(self):
        """连板晋级率"""
        d = StockDailyData()

        df = d.get_daily_data(start_date='2025-03-01')
       
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        # 新建一列‘市值域’，按照total_mv列的值进行分类，分类规则为
        # 0-20亿：微盘 20-50亿：小盘 50-100亿：中盘 100亿-300亿：中大盘，300亿以上：大盘
        df['next_day_change'] = df.groupby('id')['change'].shift(-1)  # 获取下一天的涨跌幅
        # 因为shift了-1，所以需要groupby后去掉最后一行
        df = df[df['next_day_change'].notna()]
        df = df[df['change']>=9.7]
        
        # 先计算每个交易日的涨停晋级率
        daily_stats = df.groupby('trade_date')['next_day_change'].agg([
            ('total_count', 'count'),
            ('upgrade_count', lambda x: (x >= 9.7).sum())
        ]).reset_index()
        daily_stats['涨停晋级率'] = daily_stats['upgrade_count'] / daily_stats['total_count']
        
        # 添加date_str列
        daily_stats['date_str'] = pd.to_datetime(daily_stats['trade_date']).dt.strftime('%m/%d')
        
        df = daily_stats[['trade_date', 'date_str', '涨停晋级率']]
        chart_data = []
        chart_data.append({
            "name": f'涨停晋级率',
            "x": df['date_str'].tolist(),
            "y": df['涨停晋级率'].tolist()
        })
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "市值域日线涨幅",
                "xaxis": {"title": "时间"},
                "yaxis": {"title": "涨停晋级率(%)"},
                "legend": {"title": "涨停晋级率"}
            }
        })

    def process_every_lianban_jiji_rate(self):
        """各连板晋级率 - 带启动缓存"""
        return self._process_with_startup_cache('/api/every_lianban_jiji_rate', self._original_every_lianban_jiji_rate)
    
    def _original_every_lianban_jiji_rate(self):
        """各连板晋级率"""
        # 读取data\kpl_market_sentiment_data.csv的数据
        kpl_data = pd.read_csv('data/kpl_market_sentiment_data.csv', encoding='gbk')
        kpl_data['trade_date'] = pd.to_datetime(kpl_data['trade_date'], errors='coerce')
        # 升序排列
        kpl_data = kpl_data.sort_values(by='trade_date').reset_index(drop=True)
        # 取最新的100天数据
        kpl_data = kpl_data.tail(100)
        kpl_data['date_str'] = kpl_data['trade_date'].dt.strftime('%m/%d')
        # rename up_limit_2_rate：2连板晋级率，up_limit_3_rate：3连板晋级率，up_limit_4_rate：4连板晋级率
        kpl_data = kpl_data.rename(columns={
            'up_limit_2_rate': '1进2晋级率',
            'up_limit_3_rate': '2进3晋级率',
            'up_limit_high_rate': '3板以上晋级率'
        })
        
        chart_data = []
        for column in ['1进2晋级率', '2进3晋级率', '3板以上晋级率']:
            if column in kpl_data.columns:
                chart_data.append({
                    "name": column,
                    "x": kpl_data['trade_date'].dt.strftime('%Y-%m-%d').tolist(),  # 使用完整日期格式
                    "y": kpl_data[column].tolist()
                })
       
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "各连板晋级率",
                "xaxis": {
                    "title": "时间",
                    "type": "date",  # 指定x轴为日期类型
                    "tickformat": "%m/%d"  # 显示格式仍为月/日
                },
                "yaxis": {"title": "涨停晋级率(%)"},
                "legend": {"title": "涨停晋级率"}
            }
        })


    def process_sector_line_chart_change(self):
        """板块涨幅折线图数据 - 带启动缓存"""
        return self._process_with_startup_cache('/api/sector_line_chart_change', self._original_sector_line_chart_change)
    
    def _original_sector_line_chart_change(self):
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
        """板块涨速累加图表数据 - 带启动缓存"""
        return self._process_with_startup_cache('/api/sector_speed_chart', self._original_sector_speed_chart)
    
    def _original_sector_speed_chart(self):
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
        """板块近似涨停折线图数据 - 带启动缓存"""
        return self._process_with_startup_cache('/api/sector_line_chart_uplimit', self._original_sector_line_chart_uplimit)
    
    def _original_sector_line_chart_uplimit(self):
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
        """板块红盘率折线图数据 - 带启动缓存"""
        return self._process_with_startup_cache('/api/sector_line_chart_uprate', self._original_sector_line_chart_uprate)
    
    def _original_sector_line_chart_uprate(self):
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
        """板块uprate5折线图数据 - 带启动缓存"""
        return self._process_with_startup_cache('/api/sector_line_chart_uprate5', self._original_sector_line_chart_uprate5)
    
    def _original_sector_line_chart_uprate5(self):
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
        """板块概要数据表 - 带启动缓存"""
        return self._process_with_startup_cache('/api/plate_info', self._original_plate_info)
    
    def _original_plate_info(self):
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
        """股票数据表 - 带启动缓存"""
        return self._process_with_startup_cache('/api/stocks', self._original_stocks)
    
    def _original_stocks(self):
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
        """返回板块概要数据表 - 带启动缓存"""
        return self._process_with_startup_cache('/api/plate_info_table_data', self._original_plate_info_table_data)
    
    def _original_plate_info_table_data(self):
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
        """返回股票数据表 - 带启动缓存"""
        return self._process_with_startup_cache('/api/stocks_table_data', self._original_stocks_table_data)
    
    def _original_stocks_table_data(self):
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
        """返回涨停数据，从固定CSV文件读取 - 带启动缓存"""
        return self._process_with_startup_cache('/api/get_up_limit_table_data', self._original_get_up_limit_table_data)
    
    def _original_get_up_limit_table_data(self):
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
        """返回涨停数据表 - 带启动缓存"""
        return self._process_with_startup_cache('/api/up_limit_table_data', self._original_up_limit_table_data)
    
    def _original_up_limit_table_data(self):
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
        """涨停数据表 - 带启动缓存"""
        return self._process_with_startup_cache('/api/up_limit', self._original_up_limit)
    
    def _original_up_limit(self):
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
    def build_stacked_area_data(self, df, x_axis_col, data_columns_config, colors=None):
        """
        构建堆叠面积图数据的通用函数
        
        Args:
            df: 数据DataFrame
            x_axis_col: x轴列名
            data_columns_config: 数据列配置，格式为 [{"key": "显示名称", "column": "列名"}, ...]
            colors: 颜色列表，如果不提供则使用默认颜色
        
        Returns:
            dict: 包含stackedAreaData、xAxisValues、tableData的字典
        """
        try:
            # 构建 stackedAreaChart 数据格式
            xAxisValues = df[x_axis_col].tolist()  # x轴数据
            
            # 构建数据字典
            data = {}
            table_data = {}
            hover_data = {}
            
            for _, row in df.iterrows():
                x_value = row[x_axis_col]
                
                # 按照配置顺序构建数据
                row_data = {}
                row_hover = {}
                
                for config in data_columns_config:
                    key = config["key"]
                    column = config["column"]
                    value = int(row[column]) if pd.notna(row[column]) else 0
                    
                    row_data[key] = value
                    row_hover[key] = [f"{value}"]
                
                data[x_value] = row_data
                
                # 计算总数
                total = sum(row_data.values())
                table_data[x_value] = f"{total}"
                hover_data[x_value] = row_hover
            
            # 定义显示顺序和颜色
            keyOrder = [config["key"] for config in data_columns_config]
            
            if colors is None:
                # 默认颜色配置
                default_colors = ['#00008B', '#4169E1', '#87CEEB', '#FFA07A', '#FF6B6B', '#FF0000', 
                                '#9932CC', '#FF69B4', '#FFD700', '#32CD32', '#FF4500', '#1E90FF']
                colors = default_colors[:len(keyOrder)]
            
            # 构建返回数据
            return {
                "stackedAreaData": {
                    "data": data,
                    "keyOrder": keyOrder,
                    "colors": colors,
                    "hoverData": hover_data
                },
                "xAxisValues": xAxisValues,
                "tableData": table_data
            }
            
        except Exception as e:
            self.logger.error(f"构建堆叠面积图数据失败: {e}")
            return None

    def process_all_market_change_distribution(self):
        """
        获取全市场日线级别各涨幅分布的股票数 - 带启动缓存
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：limit_up_count, up5, up0, down0, down5, limit_down_count
        """
        return self._process_with_startup_cache('/api/all_market_change_distribution', self._original_all_market_change_distribution)
    
    def _original_all_market_change_distribution(self):
        """
        获取全市场日线级别各涨幅分布的股票数
        """
        try:
            d = MarketSentimentDailyData()
            df = d.get_daily_data(start_date='2025-03-01')
            
            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
            
            # 过滤掉不需要的板块，只保留全市场数据
            df = df[df['name'] == '全市场']
            
            # 计算各个区间的股票数
            df['up5'] = df['up5_count'] - df['limit_up_count']
            df['down5'] = df['down5_count'] - df['limit_down_count']
            df['up0'] = df['up_count'] - df['up5_count']      
            df['down0'] = df['down_count'] - df['down5_count']
            
            # 按日期排序
            df = df.sort_values('trade_date')

            # 定义数据列配置（按照从下到上的堆叠顺序）
            data_columns_config = [
                {"key": "跌停", "column": "limit_down_count"},
                {"key": "跌5-10%", "column": "down5"},
                {"key": "跌0-5%", "column": "down0"},
                {"key": "涨0-5%", "column": "up0"},
                {"key": "涨5-10%", "column": "up5"},
                {"key": "涨停", "column": "limit_up_count"},
            ]
            
            # 定义颜色（从下到上：跌停到涨停）
            colors = ['#00008B', '#4169E1', '#87CEEB', '#FFA07A', '#FF6B6B', '#FF0000']
            
            # 使用通用函数构建数据
            result = self.build_stacked_area_data(df, 'date_str', data_columns_config, colors)
            
            if result is None:
                return self.error_response("构建堆叠面积图数据失败")
            
            # 构建返回数据
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取全市场涨跌幅分布失败: {e}")

    def process_up5_shizhiyu_distribution(self):
        """
        获取涨幅大于5的各市值域日线级别的股票数 - 带启动缓存
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：微盘, 小盘, 中盘, 中大盘, 大盘
        """
        return self._process_with_startup_cache('/api/up5_shizhiyu_distribution', self._original_up5_shizhiyu_distribution)
    
    def _original_up5_shizhiyu_distribution(self):
        """
        获取涨幅大于5的各市值域日线级别的股票数
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：微盘, 小盘, 中盘, 中大盘, 大盘
        """
        try:
            d = StockDailyData()
            df = d.get_daily_data(start_date='2025-03-01')
            
            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
            
            df['市值域'] = pd.cut(df['total_mv'], bins=[0, 20e8, 50e8, 100e8, 300e8, float('inf')],
                           labels=['微盘', '小盘', '中盘', '中大盘', '大盘'])
            df = df[df['change']>=5]  # 去掉没有市值域的行
            # 按trade_date和市值域分组，计算个数
            df['day_count'] = df.groupby(['trade_date', '市值域'])['change'].transform('count')
            # 每天的市值域各取1个，去掉重复的市值域
            df_temp = df.drop_duplicates(subset=['trade_date', '市值域'])
            # 将市值域列内的值作为列名，pivot表格
            df_pivot = df_temp.pivot(index='date_str', columns='市值域', values='day_count').fillna(0).reset_index()
            # 将'微盘', '小盘', '中盘', '中大盘', '大盘'各列的值变为百分比，分母为每行的总和
            df_pivot['总数'] = df_pivot[['微盘', '小盘', '中盘', '中大盘', '大盘']].sum(axis=1)
            df_pivot[['微盘', '小盘', '中盘', '中大盘', '大盘']] = df_pivot[['微盘', '小盘', '中盘', '中大盘', '大盘']].div(df_pivot['总数'], axis=0) * 100 
            df_pivot = df_pivot.drop(columns=['总数'])
            # 计算'微盘', '小盘', '中盘', '中大盘', '大盘'各列的percentchange
            market_cap_columns = ['微盘', '小盘', '中盘', '中大盘', '大盘']
            
        
            # 定义数据列配置（按照从下到上的堆叠顺序）
            data_columns_config = [
                {"key": "微盘", "column": "微盘"},
                {"key": "小盘", "column": "小盘"},
                {"key": "中盘", "column": "中盘"},
                {"key": "中大盘", "column": "中大盘"},
                {"key": "大盘", "column": "大盘"},
            ]
            
            # 定义颜色（从下到上：跌停到涨停）
            colors = ['#00008B', '#4169E1', '#87CEEB', '#FFA07A', '#FF6B6B', '#FF0000']
            
            # 使用通用函数构建数据
            result = self.build_stacked_area_data(df_pivot, 'date_str', data_columns_config, colors)
            
            if result is None:
                return self.error_response("构建堆叠面积图数据失败")
            
            # 构建返回数据
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取全市场涨跌幅分布失败: {e}")

    def process_up5_zhubanyu_distribution(self):
        """
        获取涨幅大于5的主板与创业板分布 - 带启动缓存
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：主板, 创业板, 科创版, 北交所+新三板
        """
        return self._process_with_startup_cache('/api/up5_zhubanyu_distribution', self._original_up5_zhubanyu_distribution)
    
    def _original_up5_zhubanyu_distribution(self):
        """
        获取涨幅大于5的主板与创业板分布
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：主板, 创业板, 科创版, 北交所+新三板
        """
        try:
            d = StockDailyData()
            df = d.get_daily_data(start_date='2025-03-01')
            
            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            df['date_str'] = df['trade_date'].dt.strftime('%m/%d')

            df['市值域'] = pd.cut(df['id'], bins=[0, 300000, 400000, 499999, 680000, 800000, float('inf')],
                           labels=['主板1', '创业板', '新三板', '主板2', '科创版', '北交所'])
            df = df[df['change']>=5]  # 去掉没有市值域的行
            # 按trade_date和市值域分组，计算个数
            df['day_count'] = df.groupby(['trade_date', '市值域'])['change'].transform('count')
            

            # 每天的市值域各取1个，去掉重复的市值域
            df_temp = df.drop_duplicates(subset=['trade_date', '市值域'])
            # 将市值域列内的值作为列名，pivot表格
            df_pivot = df_temp.pivot(index='date_str', columns='市值域', values='day_count').fillna(0).reset_index()
            # 将'主板', '创业板', '科创版', '新三板+北交所'各列的值变为百分比，分母为每行的总和
            df_pivot['总数'] = df_pivot[['主板1', '创业板', '新三板', '主板2', '科创版', '北交所']].sum(axis=1)
            df_pivot['主板'] = df_pivot['主板1'] + df_pivot['主板2']  # 合并主板1和主板2
            df_pivot = df_pivot.drop(columns=['主板1', '主板2'])  # 删除合并后的列
            df_pivot['新三板+北交所'] = df_pivot['新三板'] + df_pivot['北交所']  # 合并新三板和北交所
            df_pivot = df_pivot.drop(columns=['新三板', '北交所'])  # 删除合并后的列
            df_pivot[['主板', '创业板', '科创版', '新三板+北交所']] = df_pivot[['主板', '创业板', '科创版', '新三板+北交所']].div(df_pivot['总数'], axis=0) * 100
            df_pivot = df_pivot.drop(columns=['总数'])
            
        
            # 定义数据列配置（按照从下到上的堆叠顺序）
            data_columns_config = [
                {"key": "主板", "column": "主板"},
                {"key": "创业板", "column": "创业板"},
                {"key": "科创版", "column": "科创版"},
                {"key": "新三板+北交所", "column": "新三板+北交所"},
            ]
            
            # 定义颜色（从下到上：跌停到涨停）
            colors = ['#00008B', '#4169E1', '#87CEEB', '#FFA07A', '#FF6B6B', '#FF0000']
            
            # 使用通用函数构建数据
            result = self.build_stacked_area_data(df_pivot, 'date_str', data_columns_config, colors)
            
            if result is None:
                return self.error_response("构建堆叠面积图数据失败")
            
            # 构建返回数据
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取全市场涨跌幅分布失败: {e}")

    def process_plate_stock_day_change_distribution(self):
        """
        从txt读取文件中的板块名,在csv文件中找到该板块对应的股票id，并获取其日线涨幅数据 - 带启动缓存
        横坐标为日期（月/日格式），纵轴为各涨幅分布的股票个数
        """
        return self._process_with_startup_cache('/api/plate_stock_day_change_distribution', self._original_plate_stock_day_change_distribution)
    
    def _original_plate_stock_day_change_distribution(self):
        """
        从txt读取文件中的板块名,在csv文件中找到该板块对应的股票id，并获取其日线涨幅数据
        横坐标为日期（月/日格式），纵轴为各涨幅分布的股票个数
        """
        try:
            # 获取data\plate_name.txt中的板块名
            plate_name_file = r'data\plate_name.txt'
            if not os.path.exists(plate_name_file):
                return self.error_response("板块名文件不存在，请先创建 data/plate_name.txt 文件")
            with open(plate_name_file, 'r', encoding='utf-8') as f:
                sector_name = f.read().strip()
            
            # 读取strategy\strategy001\data\all_sectors_stock_level.csv中的数据
            all_sectors_stock_df = pd.read_csv(r'strategy\strategy001\data\all_sectors_stock_level.csv')
            # 获取Sector列中包含sector_name的行的id列的list
            sector_ids = all_sectors_stock_df[all_sectors_stock_df['Sector'].str.contains(sector_name, na=False)]['id'].tolist()
            
            # 读取股票日线数据
            d = StockDailyData()
            df = d.get_daily_data(start_date='2025-03-01')
            
            df = df[df['id'].isin(sector_ids)]

            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            df['date_str'] = df['trade_date'].dt.strftime('%m/%d')

            # 获取最近20日的行
            df = df[df['trade_date'] >= (df['trade_date'].max() - pd.Timedelta(days=20))]
            # 创建涨幅域列
            df['涨幅域'] = pd.cut(df['change'], bins=[float('-inf'), -9.7, -5, -2, 0, 2, 5, 9.7, float('inf')],
                           labels=['c_inf_c-10', 'c-10_c-5', 'c-5_c-2', 'c-2_c0', 'c0_c2', 'c2_c5', 'c5_c10', 'c10_c_inf'])

            # 按trade_date和涨幅域分组，计算个数
            df['day_count'] = df.groupby(['trade_date', '涨幅域'])['change'].transform('count')

            # 每天的涨幅域各取1个，去掉重复的涨幅域
            df_temp = df.drop_duplicates(subset=['trade_date', '涨幅域'])
            # 将涨幅域列内的值作为列名，pivot表格
            df_pivot = df_temp.pivot(index='date_str', columns='涨幅域', values='day_count').fillna(0).reset_index()
        
            # 定义数据列配置（按照从下到上的堆叠顺序）
            data_columns_config = [
                {"key": "c_inf_c-10", "column": "c_inf_c-10"},
                {"key": "c-10_c-5", "column": "c-10_c-5"},
                {"key": "c-5_c-2", "column": "c-5_c-2"},
                {"key": "c-2_c0", "column": "c-2_c0"},
                {"key": "c0_c2", "column": "c0_c2"},
                {"key": "c2_c5", "column": "c2_c5"},
                {"key": "c5_c10", "column": "c5_c10"},
                {"key": "c10_c_inf", "column": "c10_c_inf"},
            ]
            
            # 定义颜色（从下到上：跌停到涨停）
            colors = ['#00008B', '#4169E1', '#87CEEB', "#697472", '#FF6B6B', '#FF0000', '#9932CC', '#FF69B4']
            
            # 使用通用函数构建数据
            result = self.build_stacked_area_data(df_pivot, 'date_str', data_columns_config, colors)
            
            if result is None:
                return self.error_response("构建堆叠面积图数据失败")
            
            # 构建返回数据
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取全市场涨跌幅分布失败: {e}")
        
    def process_up5_fan_sencer_distribution(self):
        """
        获取涨幅大于9.7的昨日买入平均涨幅分布 - 带启动缓存
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：主板, 创业板, 科创版, 北交所+新三板
        """
        return self._process_with_startup_cache('/api/up5_fan_sencer_distribution', self._original_up5_fan_sencer_distribution)
    
    def _original_up5_fan_sencer_distribution(self):
        """
        获取涨幅大于9.7的昨日买入平均涨幅分布
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：主板, 创业板, 科创版, 北交所+新三板
        """
        try:
            d = StockDailyData()
            df = d.get_daily_data(start_date='2025-03-01')
            
            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
            df['next_day_change'] = df.groupby('id')['change'].shift(-1)  # 获取下一天的涨跌幅
            # 因为shift了-1，所以需要groupby后去掉最后一行
            df = df[df['next_day_change'].notna()]
            df = df[df['change']>=9.7] 
            # 去除open， close, high, low为相同值的行
            df = df[(df['open'] != df['close']) | (df['open'] != df['high']) | (df['open'] != df['low'])]
            
            df['涨幅域'] = pd.cut(df['next_day_change'], bins=[float('-inf'), -9.7, -5, -2, 0, 2, 5, 9.7, float('inf')],
                           labels=['c_inf_c-10', 'c-10_c-5', 'c-5_c-2', 'c-2_c0', 'c0_c2', 'c2_c5', 'c5_c10', 'c10_c_inf'])
           
            # 按trade_date和市值域分组，计算个数
            df['day_count'] = df.groupby(['trade_date', '涨幅域'])['change'].transform('count')

            # 每天的涨幅域各取1个，去掉重复的涨幅域
            df_temp = df.drop_duplicates(subset=['trade_date', '涨幅域'])

            # 将涨幅域列内的值作为列名，pivot表格
            df_pivot = df_temp.pivot(index='date_str', columns='涨幅域', values='day_count').fillna(0).reset_index()
            # 将'主板', '创业板', '科创版', '新三板+北交所'各列的值变为百分比，分母为每行的总和
            df_pivot['总数'] = df_pivot[['c_inf_c-10', 'c-10_c-5', 'c-5_c-2', 'c-2_c0', 'c0_c2', 'c2_c5', 'c5_c10', 'c10_c_inf']].sum(axis=1)
            df_pivot[['c_inf_c-10', 'c-10_c-5', 'c-5_c-2', 'c-2_c0', 'c0_c2', 'c2_c5', 'c5_c10', 'c10_c_inf']] = df_pivot[['c_inf_c-10', 'c-10_c-5', 'c-5_c-2', 'c-2_c0', 'c0_c2', 'c2_c5', 'c5_c10', 'c10_c_inf']].div(df_pivot['总数'], axis=0) * 100
            df_pivot = df_pivot.drop(columns=['总数'])
            
        
            # 定义数据列配置（按照从下到上的堆叠顺序）
            data_columns_config = [
                {"key": "c_inf_c-10", "column": "c_inf_c-10"},
                {"key": "c-10_c-5", "column": "c-10_c-5"},
                {"key": "c-5_c-2", "column": "c-5_c-2"},
                {"key": "c-2_c0", "column": "c-2_c0"},
                {"key": "c0_c2", "column": "c0_c2"},
                {"key": "c2_c5", "column": "c2_c5"},
                {"key": "c5_c10", "column": "c5_c10"},
                {"key": "c10_c_inf", "column": "c10_c_inf"},
            ]
            
            # 定义颜色（从下到上：跌停到涨停）
            colors = ['#00008B', '#4169E1', '#87CEEB', "#697472", '#FF6B6B', '#FF0000', '#9932CC', '#FF69B4']
            
            # 使用通用函数构建数据
            result = self.build_stacked_area_data(df_pivot, 'date_str', data_columns_config, colors)
            
            if result is None:
                return self.error_response("构建堆叠面积图数据失败")
            
            # 构建返回数据
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取全市场涨跌幅分布失败: {e}")
                
    def process_chuangye_change_distribution(self):
        """
        获取创业板日线级别各涨幅分布的股票数 - 带启动缓存
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：limit_up_count, up5, up0, down0, down5, limit_down_count
        """
        return self._process_with_startup_cache('/api/chuangye_change_distribution', self._original_chuangye_change_distribution)
    
    def _original_chuangye_change_distribution(self):
        """
        获取创业板日线级别各涨幅分布的股票数
        """
        try:
            d = MarketSentimentDailyData()
            df = d.get_daily_data(start_date='2025-03-01')
            
            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
            # 过滤掉不需要的板块，只保留创业板数据
            df = df[df['name'] == '创业板']
            
            # 计算各个区间的股票数
            df['up5'] = df['up5_count'] - df['limit_up_count']
            df['down5'] = df['down5_count'] - df['limit_down_count']
            df['up0'] = df['up_count'] - df['up5_count']      
            df['down0'] = df['down_count'] - df['down5_count']
            
            # 按日期排序
            df = df.sort_values('trade_date')

            # 定义数据列配置（按照从下到上的堆叠顺序）
            data_columns_config = [
                {"key": "跌停", "column": "limit_down_count"},
                {"key": "跌5-10%", "column": "down5"},
                {"key": "跌0-5%", "column": "down0"},
                {"key": "涨0-5%", "column": "up0"},
                {"key": "涨5-10%", "column": "up5"},
                {"key": "涨停", "column": "limit_up_count"},
            ]
            
            # 定义颜色（从下到上：跌停到涨停）
            colors = ['#00008B', '#4169E1', '#87CEEB', '#FFA07A', '#FF6B6B', '#FF0000']
            
            # 使用通用函数构建数据
            result = self.build_stacked_area_data(df, 'date_str', data_columns_config, colors)
            
            if result is None:
                return self.error_response("构建堆叠面积图数据失败")
            
            # 构建返回数据
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取全市场涨跌幅分布失败: {e}")
        
    def process_st_change_distribution(self):
        """
        获取ST股票日线级别各涨幅分布的股票数 - 带启动缓存
        横坐标为日期（月/日格式），纵轴为股票个数
        按照y轴从高到低的累计顺序显示：limit_up_count, up5, up0, down0, down5, limit_down_count
        """
        return self._process_with_startup_cache('/api/st_change_distribution', self._original_st_change_distribution)
    
    def _original_st_change_distribution(self):
        """
        获取ST股票日线级别各涨幅分布的股票数
        """
        try:
            d = MarketSentimentDailyData()
            df = d.get_daily_data(start_date='2025-03-01')
            
            df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
            df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
            # 过滤掉不需要的板块，只保留ST数据
            df = df[df['name'] == 'ST']
            
            # 计算各个区间的股票数
            df['up5'] = df['up5_count'] - df['limit_up_count']
            df['down5'] = df['down5_count'] - df['limit_down_count']
            df['up0'] = df['up_count'] - df['up5_count']      
            df['down0'] = df['down_count'] - df['down5_count']
            
            # 按日期排序
            df = df.sort_values('trade_date')

            # 定义数据列配置（按照从下到上的堆叠顺序）
            data_columns_config = [
                {"key": "跌停", "column": "limit_down_count"},
                {"key": "跌5-10%", "column": "down5"},
                {"key": "跌0-5%", "column": "down0"},
                {"key": "涨0-5%", "column": "up0"},
                {"key": "涨5-10%", "column": "up5"},
                {"key": "涨停", "column": "limit_up_count"},
            ]
            
            # 定义颜色（从下到上：跌停到涨停）
            colors = ['#00008B', '#4169E1', '#87CEEB', '#FFA07A', '#FF6B6B', '#FF0000']
            
            # 使用通用函数构建数据
            result = self.build_stacked_area_data(df, 'date_str', data_columns_config, colors)
            
            if result is None:
                return self.error_response("构建堆叠面积图数据失败")
            
            # 构建返回数据
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取全市场涨跌幅分布失败: {e}")    
            
    def process_today_plate_up_limit_distribution(self):
        """
        获取今日各板块连板数分布（板块内股票日线涨幅分布） - 带启动缓存
        横轴为板块名称，纵轴为股票个数
        分别用堆积图展示各板块的连板数分布，从下往上为1板，2板，3板等
        """
        return self._process_with_startup_cache('/api/today_plate_up_limit_distribution', self._original_today_plate_up_limit_distribution)
    
    def _original_today_plate_up_limit_distribution(self):
        """
        获取今日各板块连板数分布
        横轴为板块名称，纵轴为股票个数
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
    
    def process(self, method_name: str):
        """
        处理请求的主入口
        
        Args:
            method_name: 方法名称
            
        Returns:
            Flask响应对象
        """
        try:
            # 构建缓存参数
            cache_params = self.build_cache_params(method=method_name)
            
            # 检查是否有对应的处理方法
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                
                # 获取源数据（用于缓存判断）
                source_data = self.server._get_source_data_for_endpoint(f"/api/{method_name}")
                
                # 检查是否应该使用缓存
                if self.should_use_cache(method_name, cache_params, source_data):
                    cached_response = self.response_cache.get_cached_response(method_name, cache_params)
                    if cached_response:
                        self.logger.info(f"返回market_review缓存数据: {method_name}")
                        return cached_response
                
                # 执行方法获取新数据
                self.logger.info(f"执行market_review方法: {method_name}")
                result = method()
                
                # 存储到缓存
                self.store_cache(method_name, cache_params, source_data, result)
                
                return result
            else:
                return self.error_response(f"方法 {method_name} 不存在", 404)
                
        except Exception as e:
            return self.error_response(f"处理请求失败: {str(e)}")
    
    def get_available_methods(self):
        """获取所有可用的处理方法"""
        methods = []
        for attr_name in dir(self):
            if not attr_name.startswith('_') and callable(getattr(self, attr_name)):
                if attr_name not in ['process', 'get_available_methods', 'get_request_params', 
                                   'build_cache_params', 'should_use_cache', 'store_cache', 'error_response']:
                    methods.append(attr_name)
        return methods
    
    # ===== 示例数据处理方法 =====
    # 以下是一些示例方法，您可以根据需要修改或添加新方法
    
    def chart1(self):
        """示例图表1数据"""
        try:
            # TODO: 根据您的业务需求实现具体的数据处理逻辑
            # 这里是一个示例实现
            
            # 获取请求参数
            params = self.get_request_params()
            
            # 从数据缓存加载数据
            # data = self.data_cache.load_data('your_data_file')
            
            # 处理数据逻辑
            sample_data = {
                "title": "market_review - 图表1",
                "data": [
                    {"x": "2024-01", "y": 100},
                    {"x": "2024-02", "y": 120},
                    {"x": "2024-03", "y": 110}
                ],
                "timestamp": time.time(),
                "params": params
            }
            
            return jsonify(sample_data)
            
        except Exception as e:
            return self.error_response(f"获取chart1数据失败: {str(e)}")
    
    def table1(self):
        """示例表格1数据"""
        try:
            # TODO: 实现表格数据处理逻辑
            
            params = self.get_request_params()
            
            sample_data = {
                "title": "market_review - 表格1",
                "columns": ["名称", "数值", "变化"],
                "data": [
                    ["项目1", 100, "+5%"],
                    ["项目2", 200, "+3%"],
                    ["项目3", 150, "-2%"]
                ],
                "timestamp": time.time(),
                "params": params
            }
            
            return jsonify(sample_data)
            
        except Exception as e:
            return self.error_response(f"获取table1数据失败: {str(e)}")
    
    def config(self):
        """获取market_review配置信息"""
        try:
            config_data = {
                "processor_name": self.processor_name,
                "available_methods": self.get_available_methods(),
                "description": "复盘页面",
                "timestamp": time.time()
            }
            
            return jsonify(config_data)
            
        except Exception as e:
            return self.error_response(f"获取配置信息失败: {str(e)}")
