"""
market_review处理器模板
Author: Auto-generated
Date: 2025-07-26
Description: 复盘页面
"""
import os
from stock_data.factor.index.daily import FactorIndexDailyData
from stock_data.kaipanla.stock.daily import KplStockData

from stock_data.kaipanla.up_limit.daily import KplUpLimitData
from stock_data.night_factor.daily import NightFactorData
from stock_data.sentiment.market.daily import MarketSentimentDailyData
from stock_data.stock.index_daily import IndexDailyData
from stock_data.stock.stock_daily import StockDailyData
from stock_data.stock_minute import StockMinuteData
from stock_data.ths.concept_data import ThsConceptData
from stock_data.ths.concept_index import ThsConceptIndexData
from utils.common import get_latest_stock_name_from_stock_id, get_trade_date_by_offset, get_trade_date_list, get_stock_name_code_list
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
        
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = df['trade_date'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m/%d') for date in all_dates]
        
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
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
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
        
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = df['trade_date'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m/%d') for date in all_dates]
        
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
                "title": "各市场涨幅",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "市场名称"}
            }
        })
    
    def process_plate_stocks_change_daily(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        start_date = request.args.get('startDate', '2025-07-01')  # 默认开始日期
        end_date = request.args.get('endDate', None)  # 默认结束日期为None，使用最新日期
        
        # 直接调用原始方法，不使用启动缓存
        # 因为启动缓存会忽略sector和日期参数，导致选择不同参数时返回相同数据
        return self._original_plate_stocks_change_daily(selected_sector, start_date, end_date)
    
    def _original_plate_stocks_change_daily(self, selected_sector=None, start_date='2025-07-01', end_date=None):
        """各板块股票涨幅 - 支持动态板块选择和具体日期范围选择"""
        
        d = ThsConceptIndexData()
        # 使用传入的开始日期获取数据
        df = d.get_daily_data(start_date=start_date)

        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        
        # 确定实际的开始和结束日期
        if end_date is None or df['trade_date'].max() < pd.to_datetime(end_date, errors='coerce'):
            # 如果没有指定结束日期，使用最新日期
            latest_date = df['trade_date'].max()
        else:
            # 使用指定的结束日期
            latest_date = pd.to_datetime(end_date, errors='coerce')
        
        # 将开始日期转换为datetime类型
        start_date_dt = pd.to_datetime(start_date, errors='coerce')
        
        temp_df = df.copy()  # 保留原始数据
        # 筛选指定日期范围内的数据
        df = df[(df['trade_date'] >= start_date_dt) & (df['trade_date'] <= latest_date)]
        
        latest_date_str = latest_date.strftime('%Y%m%d')
        
        #获取近5日，近10日，近20日的cumsum各排名前10的板块列表
        ranking_results = self.get_sector_rankings_by_period(temp_df, latest_date_str, [5, 10, 20], 10)
        

        # 获取ranking_results的列表，并在df中筛选出这些板块
        sector_names = [item['sector_name'] for sublist in ranking_results.values() for item in sublist]
        
        # 如果没有指定板块，使用默认的第一个板块
        if selected_sector is None:
            sector_name = sector_names[0]
        else:
            sector_names.append(selected_sector)
            sector_name = selected_sector
        
        # 去除重复的板块名称
        sector_names = list(set(sector_names))

        # 获取日线股票数据 - 使用相同的日期范围
        d = StockDailyData()
        stock_df = d.get_daily_data(start_date=start_date)
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        
        # 筛选股票数据到相同的日期范围
        stock_df = stock_df[(stock_df['trade_date'] >= start_date_dt) & (stock_df['trade_date'] <= latest_date)]
        
        # 获取板块内股票列表
        d = ThsConceptData()
        concept_df = d.get_daily_data(start_date=start_date)
        # 获取最新交易日数据
        concept_latest_date = concept_df['trade_date'].max()
        concept_df = concept_df[concept_df['trade_date'] == concept_latest_date]
        # 获取股票列表
        stock_list = concept_df[concept_df['concept_name'] == sector_name]['stocks'].values[0].split(',')
        # 并变成整数型
        stock_list = [int(stock) for stock in stock_list if stock.isdigit()]
        # 获取stock_df中id在stock_list中的数据
        stock_df = stock_df[stock_df['id'].isin(stock_list)]
        # groupby id，计算change列的cumsum
        stock_df['change_cumsum'] = stock_df.groupby('id')['change'].cumsum()
        stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = stock_df['trade_date'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m/%d') for date in all_dates]
        
        chart_data = []
        for stock_id in stock_list:
            stock_data = stock_df[stock_df['id'] == stock_id]
            if not stock_data.empty:
                stock_data = stock_data.sort_values(by='trade_date')
                # 获取股票名称 - 取第一行的值
                stock_name = stock_data['stock_name'].iloc[0]
                # 统计5日，10日，20日涨幅大于9.7的次数，分别用up_limit_count5, up_limit_count_10,up_limit_count20
                x_data = stock_data['date_str'].tolist()
                y_data = stock_data['change_cumsum'].tolist()
                tmp_data = stock_data['change'].tolist()
                up_limit_count_5 = sum(1 for change in tmp_data[-5:] if change > 9.7)
                up_limit_count_10 = sum(1 for change in tmp_data[-10:] if change > 9.7)
                up_limit_count_15 = sum(1 for change in tmp_data[-15:] if change > 9.7)
                up_limit_count_20 = sum(1 for change in tmp_data[-20:] if change > 9.7)
                up_limit_count_20 = up_limit_count_20-up_limit_count_15
                up_limit_count_15 = up_limit_count_15-up_limit_count_10
                up_limit_count_10 = up_limit_count_10-up_limit_count_5


                chart_data.append({
                    "name": f'{stock_name}_{up_limit_count_20}-{up_limit_count_15}-{up_limit_count_10}-{up_limit_count_5}',
                    "x": x_data,
                    "y": y_data,
                    "mode": "lines+markers+text",  # 添加 +text 模式
                    "line": {"width": 2},
                    "text": [f'{stock_name}——{sector_name}' if i == len(x_data)-1 else '' for i in range(len(x_data))],
                    "textposition": "middle right",
                    "textfont": {"size": 10, "color": "black"},
                    "showlegend": True
                })
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": f"板块内股票日线涨幅 - {sector_name} ({start_date_dt.strftime('%Y-%m-%d')} 至 {latest_date.strftime('%Y-%m-%d')})",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "股票名称"}
            },
            "sectorInfo": {
                "currentSector": sector_name,
                "availableSectors": sector_names,
                "sectorCount": len(sector_names)
            },
            "dateRangeInfo": {
                "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                "currentEndDate": latest_date.strftime('%Y-%m-%d')
            }
        })
    
    def process_plate_stocks_change_minute(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        start_date = request.args.get('startDate', '2025-07-01')  # 默认开始日期
        end_date = request.args.get('endDate', None)  # 默认结束日期为None，使用最新日期
        
        # 直接调用原始方法，不使用启动缓存
        # 因为启动缓存会忽略sector和日期参数，导致选择不同参数时返回相同数据
        return self._original_plate_stocks_change_minute(selected_sector, start_date, end_date)
    
    def _original_plate_stocks_change_minute(self, selected_sector=None, start_date='2025-07-01', end_date=None):
        """各板块股票涨幅 - 支持动态板块选择和具体日期范围选择"""
        # 将开始日期转换为datetime类型
        start_date_dt = pd.to_datetime(start_date, errors='coerce')

        d = ThsConceptIndexData()
        # 使用传入的开始日期获取数据
        df = d.get_daily_data(start_date=start_date)

        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        
        #确定实际的开始和结束日期
        if end_date is None or df['trade_date'].max() < pd.to_datetime(end_date, errors='coerce'):
            # 如果没有指定结束日期，使用数据的最新日期
            latest_date = df['trade_date'].max()
        else:
            # 使用指定的结束日期，但不能超过数据的最新日期
            end_date_dt = pd.to_datetime(end_date, errors='coerce')
            data_max_date = df['trade_date'].max()
            latest_date = min(end_date_dt, data_max_date)
        
        
        temp_df = df.copy()  # 保留原始数据
        # 筛选指定日期范围内的数据
        df = df[(df['trade_date'] >= start_date_dt) & (df['trade_date'] <= latest_date)]
        
        latest_date_str = latest_date.strftime('%Y%m%d')
        
        #获取近5日，近10日，近20日的cumsum各排名前10的板块列表
        ranking_results = self.get_sector_rankings_by_period(temp_df, latest_date_str, [5, 10, 20], 10)
        
        # 获取ranking_results的列表，并在df中筛选出这些板块
        sector_names = [item['sector_name'] for sublist in ranking_results.values() for item in sublist]
        
        # 如果没有指定板块，使用默认的第一个板块
        if selected_sector is None :
            sector_name = sector_names[0]
        else:
            sector_name = selected_sector
            sector_names.append(selected_sector)
        
        # 去除重复的板块名称
        sector_names = list(set(sector_names))

        # 获取分钟线股票数据 - 使用相同的日期范围
        d = StockMinuteData()
        d.set_table_name()  # 设置表名
        stock_df = d.get_minute_data_by_date(start_date=latest_date_str, end_date=latest_date_str) # 只取latest_date日的数据
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        # time列应该已经包含日期和时间信息，确保其为datetime类型
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        
        # 筛选股票数据到相同的日期范围
        # stock_df = stock_df[(stock_df['trade_date'] >= start_date_dt) & (stock_df['trade_date'] <= latest_date)]
        
        # 获取板块内股票列表
        d = ThsConceptData()
        concept_df = d.get_daily_data(start_date=start_date)
        # 获取最新交易日数据
        concept_latest_date = concept_df['trade_date'].max()
        concept_df = concept_df[concept_df['trade_date'] == concept_latest_date]
        # 获取股票列表
        stock_list = concept_df[concept_df['concept_name'] == sector_name]['stocks'].values[0].split(',')
        # 并变成整数型
        stock_list = [int(stock) for stock in stock_list if stock.isdigit()]
        # 获取stock_df中id在stock_list中的数据
        stock_df = stock_df[stock_df['id'].isin(stock_list)]
        stock_df['change'] = ((stock_df['close']- stock_df['pre_close'])/ stock_df['pre_close'] *100).round(2) # 计算每分钟的涨幅
        
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        # 去除09:30之前的数据
        stock_df = stock_df[stock_df['time'].dt.strftime('%H:%M') >= '09:30']
        stock_df['time_str'] = stock_df['time'].dt.strftime('%m%d_%H:%M')
        # 如果pre_close列没有值或为0，填充pre_close列的值为1
        stock_df['pre_close'] = stock_df['pre_close'].replace(0, 1)
        
        stock_df = get_latest_stock_name_from_stock_id(stock_df)
        # stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = stock_df['time'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m%d_%H:%M') for date in all_dates]
        
        chart_data = []
        for stock_id in stock_list:
            stock_data = stock_df[stock_df['id'] == stock_id]
            
            if not stock_data.empty:
                stock_data = stock_data.sort_values(by='time')
                # 获取股票名称 - 取第一行的值
                stock_name = stock_data['stock_name'].iloc[0]
                
                x_data = stock_data['time_str'].tolist()
                y_data = stock_data['change'].tolist()
                
                chart_data.append({
                    "name": f'{stock_name}——{sector_name}',
                    "x": x_data,
                    "y": y_data,
                    "mode": "lines+markers+text",  # 添加 +text 模式
                    "line": {"width": 2},
                    "text": [f'{stock_name}' if i == len(x_data)-1 else '' for i in range(len(x_data))],
                    "textposition": "middle right",
                    "textfont": {"size": 10, "color": "black"},
                    "showlegend": True
                })
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": f"板块内股票分钟涨幅 - {sector_name} ({start_date_dt.strftime('%Y-%m-%d')} 至 {latest_date.strftime('%Y-%m-%d')})",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "股票名称"}
            },
            "sectorInfo": {
                "currentSector": sector_name,
                "availableSectors": sector_names,
                "sectorCount": len(sector_names)
            },
            "dateRangeInfo": {
                "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                "currentEndDate": latest_date.strftime('%Y-%m-%d')
            }
        })
    
    def process_plate_stocks_change_minute_diff_kpl_custom(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        start_date = request.args.get('startDate', '2025-07-01')  # 默认开始日期
        end_date = request.args.get('endDate', None)  # 默认结束日期为None，使用最新日期
        
        # 直接调用原始方法，不使用启动缓存
        # 因为启动缓存会忽略sector和日期参数，导致选择不同参数时返回相同数据
        return self._original_plate_stocks_change_minute_diff_kpl_custom(selected_sector, start_date, end_date)
    
    def _original_plate_stocks_change_minute_diff_kpl_custom(self, selected_sector=None, start_date='2025-07-01', end_date=None):
        """各板块股票涨幅 - 支持动态板块选择和具体日期范围选择"""
        # 将开始日期转换为datetime类型
        start_date_dt = pd.to_datetime(start_date, errors='coerce')

        d = KplStockData()
        # 使用传入的开始日期获取数据
        df = d.get_daily_data(start_date=start_date)

        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        
        #确定实际的开始和结束日期
        if end_date is None or df['trade_date'].max() < pd.to_datetime(end_date, errors='coerce'):
            # 如果没有指定结束日期，使用数据的最新日期
            latest_date = df['trade_date'].max()
        else:
            # 使用指定的结束日期，但不能超过数据的最新日期
            end_date_dt = pd.to_datetime(end_date, errors='coerce')
            data_max_date = df['trade_date'].max()
            latest_date = min(end_date_dt, data_max_date)
        
        
        temp_df = df.copy()  # 保留原始数据
        # 筛选指定日期范围内的数据
        temp_df = temp_df[(df['trade_date'] == latest_date)]
        
        # 提取id，concept_1, concept2列到新的tempdf，将板块1列和板块2列的值merge，使之在同一列表示，比如id为600000的股票，板块1为银行，板块2为金融，则merge后的新列分2行表示银行，金融
        temp_df = temp_df[['id', 'concept_1', 'concept_2']].copy()
        # 填充空值为其他
        temp_df['concept_1'] = temp_df['concept_1'].fillna('其他')
        temp_df['concept_2'] = temp_df['concept_2'].fillna('其他')
        temp_df = temp_df.melt(id_vars=['id'], value_vars=['concept_1', 'concept_2'], var_name='concept_type', value_name='sector_name')
        temp_df = temp_df.dropna(subset=['sector_name'])  # 去除空
        
        latest_date_str = latest_date.strftime('%Y%m%d')
        
        
        # 获取ranking_results的列表，并在df中筛选出这些板块
        sector_names = temp_df['sector_name'].unique().tolist()
        # 获取每个sector_name所对应的id列表，用字典形式保存
        sector_id_map = temp_df.groupby('sector_name')['id'].apply(list).to_dict()

        # 如果没有指定板块，使用默认的第一个板块
        if selected_sector is None :
            sector_name = sector_names[0]
        else:
            sector_name = selected_sector
            sector_names.append(selected_sector)
        
        # 去除重复的板块名称
        sector_names = list(set(sector_names))

        # 获取分钟线股票数据 - 使用相同的日期范围
        d = StockMinuteData()
        d.set_table_name()  # 设置表名
        stock_df = d.get_minute_data_by_date(start_date=latest_date_str, end_date=latest_date_str) # 只取latest_date日的数据
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        # time列应该已经包含日期和时间信息，确保其为datetime类型
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        # 去除09:25之前的数据
        stock_df = stock_df[stock_df['time'].dt.strftime('%H:%M') >= '09:30']
        # 筛选股票数据到相同的日期范围
        # stock_df = stock_df[(stock_df['trade_date'] >= start_date_dt) & (stock_df['trade_date'] <= latest_date)]
        
        # 获取板块内股票列表
        # d = ThsConceptData()
        # concept_df = d.get_daily_data(start_date=start_date)
        # # 获取最新交易日数据
        # concept_latest_date = concept_df['trade_date'].max()
        # concept_df = concept_df[concept_df['trade_date'] == concept_latest_date]
        # # 获取股票列表
        # stock_list = concept_df[concept_df['concept_name'] == sector_name]['stocks'].values[0].split(',')
        stock_list = sector_id_map.get(sector_name, [])
        # 并变成整数型
        stock_list = [int(stock) for stock in stock_list]
        # 获取stock_df中id在stock_list中的数据
        stock_df = stock_df[stock_df['id'].isin(stock_list)]
        # groupby id，用（close-09：25分的close）/09：25分的close计算change列
        stock_df['pre_close_0925'] = stock_df.groupby('id')['close'].transform(lambda x: x.iloc[0])  # 获取每只股票09:25分的收盘价
        # 计算每分钟的涨幅
        stock_df['change_diff'] = ((stock_df['close']- stock_df['pre_close_0925'])/ stock_df['pre_close_0925'] *100).round(2) # 计算每分钟的涨幅
        
        # 计算每分钟涨幅change
        stock_df['change'] = ((stock_df['close']- stock_df['pre_close'])/ stock_df['pre_close'] *100).round(2) # 计算每分钟的涨幅

        # 将在区间-2到2的change值设置为2或-2，change为正时则设为2，负时设为-2
        stock_df.loc[(stock_df['change_diff'] >= -2) & (stock_df['change_diff'] <= 2), 'change_diff'] = stock_df['change_diff'].apply(lambda x: 2 if x > 0 else -2)

        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        
        stock_df['time_str'] = stock_df['time'].dt.strftime('%m%d_%H:%M')
        
        stock_df = get_latest_stock_name_from_stock_id(stock_df)
        # stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = stock_df['time'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m%d_%H:%M') for date in all_dates]
        
        chart_data = []
        for stock_id in stock_list:
            stock_data = stock_df[stock_df['id'] == stock_id]
            
            if not stock_data.empty:
                stock_data = stock_data.sort_values(by='time')
                # 获取股票名称 - 取第一行的值
                stock_name = stock_data['stock_name'].iloc[0]
                
                x_data = stock_data['time_str'].tolist()
                y_data = stock_data['change_diff'].tolist()
                
                chart_data.append({
                    "name": f'{stock_name}——{sector_name}',
                    "x": x_data,
                    "y": y_data,
                    "mode": "lines+markers+text",  # 添加 +text 模式
                    "line": {"width": 2},
                    "text": [f'{stock_name}' if i == len(x_data)-1 else '' for i in range(len(x_data))],
                    "textposition": "middle right",
                    "textfont": {"size": 10, "color": "black"},
                    "showlegend": True
                })
        
        # 计算时间维度的因子 - 直接计算，无需合并回原数据
        # 因子1: 每分钟change大于2的个数减去小于-2的个数
        factor_2_df = stock_df.groupby('time_str')['change'].agg(
            factor_2=lambda x: (x > 2).sum() - (x < -2).sum()
        ).reset_index()
        
        # 因子2: 每分钟change大于9.7的个数
        factor_9_7_df = stock_df.groupby('time_str')['change'].agg(
            factor_9_7=lambda x: (x > 9.7).sum()
        ).reset_index()
        
        # 合并两个因子数据并排序
        factor_data = factor_2_df.merge(factor_9_7_df, on='time_str', how='outer').sort_values('time_str')
        
        # 添加因子2的线条
        chart_data.append({
            "x": factor_data['time_str'].tolist(),
            "y": factor_data['factor_2'].tolist(),
            "mode": "lines+markers",
            "line": {"width": 3, "color": "red"},
            "name": "市场情绪因子(>2数量 - <-2数量)",
            "yaxis": "y2",  # 使用右侧Y轴
            "showlegend": True
        })
        
        # 添加因子9.7的线条
        chart_data.append({
            "x": factor_data['time_str'].tolist(),
            "y": factor_data['factor_9_7'].tolist(),
            "mode": "lines+markers",
            "line": {"width": 3, "color": "orange"},
            "name": "强势股因子(>9.7%数量)",
            "yaxis": "y2",  # 使用右侧Y轴
            "showlegend": True
        })
        
            
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": f"板块内股票分钟涨幅_diff + 市场因子 - {sector_name} ({start_date_dt.strftime('%Y-%m-%d')} 至 {latest_date.strftime('%Y-%m-%d')})",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {
                    "title": "涨幅(%)",
                    "side": "left"
                },
                "yaxis2": {
                    "title": "因子数量",
                    "side": "right",
                    "overlaying": "y",
                    "showgrid": False
                },
                "legend": {"title": "指标名称"}
            },
            "sectorInfo": {
                "currentSector": sector_name,
                "availableSectors": sector_names,
                "sectorCount": len(sector_names)
            },
            "dateRangeInfo": {
                "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                "currentEndDate": latest_date.strftime('%Y-%m-%d')
            }
        })
    
    def process_plate_stocks_change_minute_diff(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        start_date = request.args.get('startDate', '2025-07-01')  # 默认开始日期
        end_date = request.args.get('endDate', None)  # 默认结束日期为None，使用最新日期
        
        # 直接调用原始方法，不使用启动缓存
        # 因为启动缓存会忽略sector和日期参数，导致选择不同参数时返回相同数据
        return self._original_plate_stocks_change_minute_diff(selected_sector, start_date, end_date)
    
    def _original_plate_stocks_change_minute_diff(self, selected_sector=None, start_date='2025-07-01', end_date=None):
        """各板块股票涨幅 - 支持动态板块选择和具体日期范围选择"""
        # 将开始日期转换为datetime类型
        start_date_dt = pd.to_datetime(start_date, errors='coerce')

        d = ThsConceptIndexData()
        # 使用传入的开始日期获取数据
        df = d.get_daily_data(start_date=start_date)

        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        
        #确定实际的开始和结束日期
        if end_date is None or df['trade_date'].max() < pd.to_datetime(end_date, errors='coerce'):
            # 如果没有指定结束日期，使用数据的最新日期
            latest_date = df['trade_date'].max()
        else:
            # 使用指定的结束日期，但不能超过数据的最新日期
            end_date_dt = pd.to_datetime(end_date, errors='coerce')
            data_max_date = df['trade_date'].max()
            latest_date = min(end_date_dt, data_max_date)
        
        
        temp_df = df.copy()  # 保留原始数据
        # 筛选指定日期范围内的数据
        df = df[(df['trade_date'] >= start_date_dt) & (df['trade_date'] <= latest_date)]
        
        latest_date_str = latest_date.strftime('%Y%m%d')
        
        #获取近5日，近10日，近20日的cumsum各排名前10的板块列表
        ranking_results = self.get_sector_rankings_by_period(temp_df, latest_date_str, [5, 10, 20], 10)
        
        # 获取ranking_results的列表，并在df中筛选出这些板块
        sector_names = [item['sector_name'] for sublist in ranking_results.values() for item in sublist]
        
        # 如果没有指定板块，使用默认的第一个板块
        if selected_sector is None :
            sector_name = sector_names[0]
        else:
            sector_name = selected_sector
            sector_names.append(selected_sector)
        
        # 去除重复的板块名称
        sector_names = list(set(sector_names))

        # 获取分钟线股票数据 - 使用相同的日期范围
        d = StockMinuteData()
        d.set_table_name()  # 设置表名
        stock_df = d.get_minute_data_by_date(start_date=latest_date_str, end_date=latest_date_str) # 只取latest_date日的数据
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        # time列应该已经包含日期和时间信息，确保其为datetime类型
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        # 去除09:25之前的数据
        stock_df = stock_df[stock_df['time'].dt.strftime('%H:%M') >= '09:30']
        # 筛选股票数据到相同的日期范围
        # stock_df = stock_df[(stock_df['trade_date'] >= start_date_dt) & (stock_df['trade_date'] <= latest_date)]
        
        # 获取板块内股票列表
        d = ThsConceptData()
        concept_df = d.get_daily_data(start_date=start_date)
        # 获取最新交易日数据
        concept_latest_date = concept_df['trade_date'].max()
        concept_df = concept_df[concept_df['trade_date'] == concept_latest_date]
        # 获取股票列表
        stock_list = concept_df[concept_df['concept_name'] == sector_name]['stocks'].values[0].split(',')
        # 并变成整数型
        stock_list = [int(stock) for stock in stock_list if stock.isdigit()]
        # 获取stock_df中id在stock_list中的数据
        stock_df = stock_df[stock_df['id'].isin(stock_list)]
        # groupby id，用（close-09：25分的close）/09：25分的close计算change列
        stock_df['pre_close_0925'] = stock_df.groupby('id')['close'].transform(lambda x: x.iloc[0])  # 获取每只股票09:25分的收盘价
        # 计算每分钟的涨幅
        stock_df['change_diff'] = ((stock_df['close']- stock_df['pre_close_0925'])/ stock_df['pre_close_0925'] *100).round(2) # 计算每分钟的涨幅
        
        # 计算每分钟涨幅change
        stock_df['change'] = ((stock_df['close']- stock_df['pre_close'])/ stock_df['pre_close'] *100).round(2) # 计算每分钟的涨幅

        # 将在区间-2到2的change值设置为2或-2，change为正时则设为2，负时设为-2
        stock_df.loc[(stock_df['change_diff'] >= -2) & (stock_df['change_diff'] <= 2), 'change_diff'] = stock_df['change_diff'].apply(lambda x: 2 if x > 0 else -2)

        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        
        stock_df['time_str'] = stock_df['time'].dt.strftime('%m%d_%H:%M')
        
        stock_df = get_latest_stock_name_from_stock_id(stock_df)
        # stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = stock_df['time'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m%d_%H:%M') for date in all_dates]
        
        chart_data = []
        for stock_id in stock_list:
            stock_data = stock_df[stock_df['id'] == stock_id]
            
            if not stock_data.empty:
                stock_data = stock_data.sort_values(by='time')
                # 获取股票名称 - 取第一行的值
                stock_name = stock_data['stock_name'].iloc[0]
                
                x_data = stock_data['time_str'].tolist()
                y_data = stock_data['change_diff'].tolist()
                
                chart_data.append({
                    "name": f'{stock_name}——{sector_name}',
                    "x": x_data,
                    "y": y_data,
                    "mode": "lines+markers+text",  # 添加 +text 模式
                    "line": {"width": 2},
                    "text": [f'{stock_name}' if i == len(x_data)-1 else '' for i in range(len(x_data))],
                    "textposition": "middle right",
                    "textfont": {"size": 10, "color": "black"},
                    "showlegend": True
                })
        
        # 计算时间维度的因子 - 直接计算，无需合并回原数据
        # 因子1: 每分钟change大于2的个数减去小于-2的个数
        factor_2_df = stock_df.groupby('time_str')['change'].agg(
            factor_2=lambda x: (x > 2).sum() - (x < -2).sum()
        ).reset_index()
        
        # 因子2: 每分钟change大于9.7的个数
        factor_9_7_df = stock_df.groupby('time_str')['change'].agg(
            factor_9_7=lambda x: (x > 9.7).sum()
        ).reset_index()
        
        # 合并两个因子数据并排序
        factor_data = factor_2_df.merge(factor_9_7_df, on='time_str', how='outer').sort_values('time_str')
        
        # 添加因子2的线条
        chart_data.append({
            "x": factor_data['time_str'].tolist(),
            "y": factor_data['factor_2'].tolist(),
            "mode": "lines+markers",
            "line": {"width": 3, "color": "red"},
            "name": "市场情绪因子(>2数量 - <-2数量)",
            "yaxis": "y2",  # 使用右侧Y轴
            "showlegend": True
        })
        
        # 添加因子9.7的线条
        chart_data.append({
            "x": factor_data['time_str'].tolist(),
            "y": factor_data['factor_9_7'].tolist(),
            "mode": "lines+markers",
            "line": {"width": 3, "color": "orange"},
            "name": "强势股因子(>9.7%数量)",
            "yaxis": "y2",  # 使用右侧Y轴
            "showlegend": True
        })
        
            
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": f"板块内股票分钟涨幅_diff + 市场因子 - {sector_name} ({start_date_dt.strftime('%Y-%m-%d')} 至 {latest_date.strftime('%Y-%m-%d')})",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {
                    "title": "涨幅(%)",
                    "side": "left"
                },
                "yaxis2": {
                    "title": "因子数量",
                    "side": "right",
                    "overlaying": "y",
                    "showgrid": False
                },
                "legend": {"title": "指标名称"}
            },
            "sectorInfo": {
                "currentSector": sector_name,
                "availableSectors": sector_names,
                "sectorCount": len(sector_names)
            },
            "dateRangeInfo": {
                "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                "currentEndDate": latest_date.strftime('%Y-%m-%d')
            }
        })
    
    def process_plate_change_daily(self):
        """各板块涨幅 - 带启动缓存"""
        return self._process_with_startup_cache('/api/plate_change_daily', self._original_plate_change_daily)
    
    def process_sector_lianban_distribution(self):
        """板块连板数分布图 - 支持动态板块选择和日期范围选择"""
        from flask import request
        selected_sector = request.args.get('sector', None)
        start_date = request.args.get('startDate', '2025-07-01')
        end_date = request.args.get('endDate', None)
        
        return self._original_sector_lianban_distribution(selected_sector, start_date, end_date)
    
    def _original_sector_lianban_distribution(self, selected_sector=None, start_date='2025-07-01', end_date=None):
        """板块连板数分布图 - 原始实现"""
        import pandas as pd
        from datetime import datetime, timedelta
        
        # 将开始日期转换为datetime类型
        start_date_dt = pd.to_datetime(start_date, errors='coerce')
        d = NightFactorData()
        df = d.get_daily_data(start_date=start_date)
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')

        # 确定结束日期
        # 确定实际的开始和结束日期
        if end_date is None or df['trade_date'].max() < pd.to_datetime(end_date, errors='coerce'):
            # 如果没有指定结束日期，使用最新日期
            latest_date = df['trade_date'].max()
        else:
            # 使用指定的结束日期
            latest_date = pd.to_datetime(end_date, errors='coerce')
        
        # TODO: 这里你需要实现从 factor.night_factor 表获取数据的逻辑
        # 期望的数据结构应该包含以下字段：
        # - trade_date: 交易日期
        # - sector: 板块名称  
        # - stock_name: 股票名称
        # - lian_ban_shu: 连板数
        
        df = df[(df['trade_date'] >= start_date_dt) & (df['trade_date'] <= latest_date)]
        
        
        # 获取可用板块列表 - 你需要替换为实际的板块获取逻辑
        available_sectors = df['sector'].unique().tolist()
        
        # 如果没有指定板块，使用第一个板块
        if selected_sector is None:
            selected_sector = available_sectors[0] if available_sectors else "无板块"
        
        # 筛选指定板块的数据
        sector_data = df[df['sector'] == selected_sector].copy()

        if sector_data.empty:
            return jsonify({
                "chartType": "heatmap", 
                "data": [],
                "layout": {"title": f"板块 {selected_sector} 无连板数据"},
                "sectorInfo": {
                    "currentSector": selected_sector,
                    "availableSectors": available_sectors,
                    "sectorCount": len(available_sectors)
                },
                "dateRangeInfo": {
                    "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                    "currentEndDate": latest_date.strftime('%Y-%m-%d')
                }
            })
        
        # 处理连板数据
        lianban_data = self._process_lianban_data_for_heatmap(sector_data)
        
        # 生成热力图数据
        chart_data = self._generate_lianban_heatmap_chart(lianban_data, start_date_dt, latest_date)
        
        return jsonify({
            "chartType": "heatmap",
            "data": chart_data["data"],
            "layout": {
                "title": f"板块连板数分布 - {selected_sector} ({start_date_dt.strftime('%Y-%m-%d')} 至 {latest_date.strftime('%Y-%m-%d')})",
                "xaxis": {
                    "title": "日期", 
                    "side": "bottom",
                    "tickangle": -45,
                    "automargin": True,
                    "type": "category",  # 明确指定为分类轴
                    "categoryorder": "array",  # 按数组顺序排列
                    "categoryarray": chart_data.get("date_strings", [])  # 使用返回的日期字符串数组
                },
                "yaxis": {
                    "title": "连板数", 
                    "side": "left"
                },
                "colorscale": "Viridis",
                "showscale": True,
                "height": 1000,  # 增大固定高度以容纳动态行高
                "margin": {"l": 120, "r": 50, "t": 80, "b": 120},
                **chart_data["layout"]
            },
            "sectorInfo": {
                "currentSector": selected_sector,
                "availableSectors": available_sectors,
                "sectorCount": len(available_sectors)
            },
            "dateRangeInfo": {
                "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                "currentEndDate": latest_date.strftime('%Y-%m-%d')
            }
        })
    
    def process_sector_lianban_distribution_kpl(self):
        """板块连板数分布图 - 支持动态板块选择和日期范围选择"""
        from flask import request
        selected_sector = request.args.get('sector', None)
        start_date = request.args.get('startDate', '2025-07-01')
        end_date = request.args.get('endDate', None)
        
        return self._original_sector_lianban_distribution_kpl(selected_sector, start_date, end_date)

    def _original_sector_lianban_distribution_kpl(self, selected_sector=None, start_date='2025-07-01', end_date=None):
        """板块连板数分布图 - 原始实现"""
        import pandas as pd
        from datetime import datetime, timedelta
        
        # 将开始日期转换为datetime类型
        start_date_dt = pd.to_datetime(start_date, errors='coerce')
        # d = NightFactorData()
        d = KplUpLimitData()
        df = d.get_daily_data(start_date=start_date)
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')

        # 确定结束日期
        # 确定实际的开始和结束日期
        if end_date is None or df['trade_date'].max() < pd.to_datetime(end_date, errors='coerce'):
            # 如果没有指定结束日期，使用最新日期
            latest_date = df['trade_date'].max()
        else:
            # 使用指定的结束日期
            latest_date = pd.to_datetime(end_date, errors='coerce')
        
        # TODO: 这里你需要实现从 factor.night_factor 表获取数据的逻辑
        # 期望的数据结构应该包含以下字段：
        # - trade_date: 交易日期
        # - sector: 板块名称  
        # - stock_name: 股票名称
        # - lian_ban_shu: 连板数
        
        df = df[(df['trade_date'] >= start_date_dt) & (df['trade_date'] <= latest_date)]
        
        
        # 获取可用板块列表 - 你需要替换为实际的板块获取逻辑
        available_sectors = df['up_limit_reason'].unique().tolist()
        
        # 如果没有指定板块，使用第一个板块
        if selected_sector is None:
            selected_sector = available_sectors[0] if available_sectors else "无板块"
        
        # 筛选指定板块的数据
        sector_data = df[df['up_limit_reason'] == selected_sector].copy()

        if sector_data.empty:
            return jsonify({
                "chartType": "heatmap", 
                "data": [],
                "layout": {"title": f"板块 {selected_sector} 无连板数据"},
                "sectorInfo": {
                    "currentSector": selected_sector,
                    "availableSectors": available_sectors,
                    "sectorCount": len(available_sectors)
                },
                "dateRangeInfo": {
                    "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                    "currentEndDate": latest_date.strftime('%Y-%m-%d')
                }
            })
        
        # 处理连板数据
        lianban_data = self._process_lianban_data_for_heatmap(sector_data, kpl=True)
        
        # 生成热力图数据
        chart_data = self._generate_lianban_heatmap_chart(lianban_data, start_date_dt, latest_date)
        
        return jsonify({
            "chartType": "heatmap",
            "data": chart_data["data"],
            "layout": {
                "title": f"板块连板数分布 - {selected_sector} ({start_date_dt.strftime('%Y-%m-%d')} 至 {latest_date.strftime('%Y-%m-%d')})",
                "xaxis": {
                    "title": "日期", 
                    "side": "bottom",
                    "tickangle": -45,
                    "automargin": True,
                    "type": "category",  # 明确指定为分类轴
                    "categoryorder": "array",  # 按数组顺序排列
                    "categoryarray": chart_data.get("date_strings", [])  # 使用返回的日期字符串数组
                },
                "yaxis": {
                    "title": "连板数", 
                    "side": "left"
                },
                "colorscale": "Viridis",
                "showscale": True,
                "height": 1000,  # 增大固定高度以容纳动态行高
                "margin": {"l": 120, "r": 50, "t": 80, "b": 120},
                **chart_data["layout"]
            },
            "sectorInfo": {
                "currentSector": selected_sector,
                "availableSectors": available_sectors,
                "sectorCount": len(available_sectors)
            },
            "dateRangeInfo": {
                "currentStartDate": start_date_dt.strftime('%Y-%m-%d'),
                "currentEndDate": latest_date.strftime('%Y-%m-%d')
            }
        })
    
    def _process_lianban_data_for_heatmap(self, sector_data,kpl=False):
        """处理连板数据，按日期和连板数分组"""
        lianban_dict = {}
        
        for _, row in sector_data.iterrows():
            date_str = row['trade_date'].strftime('%m%d')  # 改为0701格式
            if kpl:
                lianban_days = int(row.get('up_limit_count', 1))
            else:
                lianban_days = int(row.get('lian_ban_shu', 1))  # 从night_factor表的lian_ban_shu字段获取
            stock_name = row.get('stock_name', '未知股票')
            
            if date_str not in lianban_dict:
                lianban_dict[date_str] = {}
            
            # 将10连板以上的归为"10连板以上"
            if lianban_days >= 10:
                lianban_key = "10连板以上"
            else:
                lianban_key = f"{lianban_days}连板"
            
            if lianban_key not in lianban_dict[date_str]:
                lianban_dict[date_str][lianban_key] = []
            
            lianban_dict[date_str][lianban_key].append(stock_name)
        
        return lianban_dict
    
    def _generate_lianban_heatmap_chart(self, lianban_data, start_date, end_date):
        """生成连板分布热力图数据 - 支持动态行高"""
        # 定义连板数类别 - 顺序从1连板到10连板以上（1连板在最下方）
        lianban_categories = [f"{i}连板" for i in range(1, 10)] + ["10连板以上"]
        
        # 生成日期序列 - 只包含工作日
        date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # 'B'表示工作日
        date_strings = [d.strftime('%m%d') for d in date_range]  # 改为0701格式
        
        # 反转连板类别顺序，让1连板在下方
        reversed_categories = list(reversed(lianban_categories))
        
        # 计算每个连板类型在所有日期中的最大股票数量，用于动态高度分配
        max_stocks_per_category = {}
        for lianban_cat in lianban_categories:
            max_count = 0
            for date_str in date_strings:
                stocks = lianban_data.get(date_str, {}).get(lianban_cat, [])
                max_count = max(max_count, len(stocks))
            # 确保每个类别至少有最小高度（可容纳1只股票）
            max_stocks_per_category[lianban_cat] = max(max_count, 1)
        
        # 计算动态y坐标位置 - 基于最大股票数量分配高度
        y_positions = {}
        current_y = 0
        base_height = 1.2  # 进一步增加基础高度
        stock_height = 1  # 大幅增加每只股票的高度，确保10只股票时有足够空间
        
        # 按照正序排列（1连板在下方），从下往上计算y坐标
        for lianban_cat in lianban_categories:  # 使用原始顺序，1连板先计算（在下方）
            max_stocks = max_stocks_per_category[lianban_cat]
            # 计算该类别所需的总高度（基础高度 + 股票数量*单股高度）
            category_height = base_height + max_stocks * stock_height
            y_positions[lianban_cat] = current_y + category_height / 2  # 中心位置
            current_y += category_height
        
        total_height = current_y
        
        # 创建矩形traces和注释
        traces = []
        annotations = []
        
        for i, date_str in enumerate(date_strings):
            for lianban_cat in lianban_categories:
                stocks = lianban_data.get(date_str, {}).get(lianban_cat, [])
                stock_count = len(stocks)
                
                # 为所有格子创建矩形，包括没有数据的格子
                # 计算颜色强度（基于股票数量）
                if stock_count > 0:
                    max_count_overall = max([len(stocks) for date_data in lianban_data.values() 
                                           for stocks in date_data.values()]) or 1
                    intensity = stock_count / max_count_overall
                    
                    # 白色到红色渐变
                    red_value = int(255 * intensity)
                    color = f"rgb({255}, {255-red_value}, {255-red_value})"
                else:
                    # 没有数据的格子显示为白色
                    color = "rgb(255, 255, 255)"
                    intensity = 0
                
                # 计算矩形的位置和大小
                center_y = y_positions[lianban_cat]
                max_stocks = max_stocks_per_category[lianban_cat]
                
                # 根据实际股票数量计算当前格子的高度
                current_stock_count = len(stocks)
                if current_stock_count == 0:
                    # 空格子使用最小高度
                    actual_rect_height = base_height
                else:
                    # 有股票的格子根据实际股票数量计算高度
                    actual_rect_height = base_height + current_stock_count * stock_height
                
                # 最大高度限制（不超过分配给该类别的总高度）
                max_allowed_height = base_height + max_stocks * stock_height
                actual_rect_height = min(actual_rect_height, max_allowed_height)
                
                y_bottom = center_y - actual_rect_height / 2
                y_top = center_y + actual_rect_height / 2
                
                # 创建悬浮框模板 - 股票列表纵向排列
                if stock_count == 0:
                    hover_template = f'%{{text}}<extra></extra>'
                    hover_text = f'{lianban_cat}<br>日期: 20{date_str}<br>暂无股票'
                else:
                    # 构建股票列表显示 - 纵向排列，每个股票一行
                    stock_list = '<br>'.join([f'• {stock}' for stock in stocks])
                    hover_template = f'%{{text}}<extra></extra>'
                    hover_text = f'{lianban_cat}<br>日期: 20{date_str}<br>股票数量: {stock_count}只<br><br>股票列表:<br>{stock_list}'
                
                # 创建矩形trace - 添加悬浮框样式配置
                traces.append({
                    'type': 'scatter',
                    'x': [i-0.4, i+0.4, i+0.4, i-0.4, i-0.4],
                    'y': [y_bottom, y_bottom, y_top, y_top, y_bottom],
                    'mode': 'lines',
                    'fill': 'toself',
                    'fillcolor': color,
                    'line': {'color': '#ddd', 'width': 1},
                    'showlegend': False,
                    'name': f'{lianban_cat}-{date_str}',
                    'text': hover_text,
                    'hovertemplate': hover_template,
                    'hoverlabel': {
                        'bgcolor': 'rgba(30, 30, 30, 0.9)',  # 深灰色半透明背景
                        'bordercolor': 'white',               # 白色边框
                        'font': {
                            'color': 'white',                 # 白色字体
                            'size': 14,                       # 字体大小
                            'family': 'Arial, sans-serif'    # 字体家族
                        }
                    },
                    'customdata': stocks  # 传递原始股票列表数组
                })
                
                # 添加文本注释（只有当有股票时才添加股票名称）
                if stocks:
                    # 根据矩形高度和股票数量动态调整字体大小
                    # 考虑股票数量：股票越多，字体相对小一些以避免拥挤
                    stock_count_factor = max(0.7, 1.0 - (len(stocks) - 1) * 0.05)  # 股票数量越多，字体稍小
                    base_font_size = min(16, max(13, int(actual_rect_height * 8)))
                    font_size = int(base_font_size * stock_count_factor)
                    stock_text = '<br>'.join(stocks)
                    
                    annotations.append({
                        'x': i,
                        'y': center_y,
                        'text': stock_text,
                        'showarrow': False,
                        'font': {
                            'size': font_size,
                            'color': 'black' if intensity < 0.5 else 'white',
                            'family': 'Arial, sans-serif'  # 添加字体族以提高可读性
                        },
                        'xanchor': 'center',
                        'yanchor': 'middle'
                    })
        
        return {
            "data": traces,
            "layout": {
                "plot_bgcolor": 'white',
                "paper_bgcolor": 'white',
                "margin": {"l": 100, "r": 50, "t": 50, "b": 80},
                "height": max(600, int(total_height * 100)),  # 动态调整总高度
                "xaxis": {
                    "title": "日期",
                    "tickangle": -45,
                    "tickmode": "array",
                    "tickvals": list(range(len(date_strings))),
                    "ticktext": date_strings,
                    "range": [-0.5, len(date_strings)-0.5]
                },
                "yaxis": {
                    "title": "连板类型",
                    "tickmode": "array",
                    "tickvals": [y_positions[cat] for cat in lianban_categories],  # 使用原始顺序
                    "ticktext": lianban_categories,  # 使用原始顺序，1连板在下方
                    "range": [0, total_height],
                    "showgrid": True,
                    "gridcolor": "#f0f0f0"
                },
                "annotations": annotations,
                "showlegend": False
            },
            "date_strings": date_strings  # 返回日期字符串数组
        }

    def _original_plate_change_daily(self):
        """市场情绪日数据的主板，创业板，科创版，ST板成交额"""
        d = ThsConceptIndexData()
        df = d.get_daily_data(start_date='2025-07-01')

        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        #获取最新日期
        latest_date = df['trade_date'].max()
        latest_date_str = latest_date.strftime('%Y%m%d')
        start_date_str = get_trade_date_by_offset(latest_date_str, 20)
        # 将字符串日期转换为datetime类型以便比较
        start_date = pd.to_datetime(start_date_str, format='%Y%m%d')
        # 获取从start_date到latest_date的所有数据
        df = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= latest_date)]

        
        #获取近5日，近10日，近20日的cumsum各排名前10的板块列表
        ranking_results = self.get_sector_rankings_by_period(df, latest_date_str, [5, 10, 20], 10)
        
        print(f"📊 板块排名统计:")
        for period_key in ranking_results:
            if ranking_results[period_key]:  # 确保有数据
                top_3_names = [item['sector_name'] for item in ranking_results[period_key][:3]]
                print(f"   {period_key}前3: {top_3_names}")

        # 获取ranking_results的列表，并在df中筛选出这些板块
        sector_names = [item['sector_name'] for sublist in ranking_results.values() for item in sublist]
        # 去除重复的板块名称
        sector_names = list(set(sector_names))
        
        print(f"🔍 筛选前数据范围: {df['date_str'].min()} 到 {df['date_str'].max()}")
        print(f"🔍 筛选前总板块数: {df['name'].nunique()}")
        print(f"🔍 排名板块数: {len(sector_names)}")
        
        df = df[df['name'].isin(sector_names)]
        
        print(f"🔍 筛选后数据范围: {df['date_str'].min()} 到 {df['date_str'].max()}")
        print(f"🔍 筛选后总记录数: {len(df)}")
        
        # 检查每个板块的数据范围
        for sector in sector_names[:3]:  # 只检查前3个
            sector_data = df[df['name'] == sector]
            if not sector_data.empty:
                print(f"🔍 板块 '{sector}' 数据范围: {sector_data['date_str'].min()} 到 {sector_data['date_str'].max()}")
        
        # groupby name，计算change列的cumsum
        df['change'] = df.groupby('name')['change'].cumsum()

        
        chart_data = []
        
        # 获取完整的日期范围用于调试
        all_dates = sorted(df['date_str'].unique())
        print(f"📅 完整日期范围: {all_dates}")
        
        for sector in sector_names:
            sector_data = df[df['name'] == sector]
            if not sector_data.empty:
                sector_data = sector_data.sort_values(by='trade_date')
                
                # 获取x轴和y轴数据
                x_data = sector_data['date_str'].tolist()
                y_data = sector_data['change'].tolist()
                
                # 添加完整的日期信息以确保排序正确
                date_info = sector_data[['date_str', 'trade_date']].to_dict('records')
                
                # 方案2：只显示有数据的日期（真实数据，不填充）
                chart_data.append({
                    "name": f'{sector}涨幅',
                    "x": x_data,
                    "y": y_data,
                    "dates": [d['trade_date'].strftime('%Y-%m-%d') for d in date_info],  # 添加完整日期用于排序
                    "mode": "lines+markers"  # 明确指定线条模式
                })
                
                print(f"📊 板块 '{sector}': 数据范围 {sector_data['date_str'].min()} 到 {sector_data['date_str'].max()}, 共{len(sector_data)}天")
                
                # 详细检查前几个板块的x轴数据顺序
                if sector in sector_names[:2]:  # 只检查前2个板块
                    print(f"🔍 板块 '{sector}' x轴数据顺序: {x_data}")
                    print(f"🔍 板块 '{sector}' 前5个y值: {y_data[:5]}")
        
        # 检查总的chart_data结构
        print(f"📈 生成图表数据: 共{len(chart_data)}个系列")
        if chart_data:
            first_series = chart_data[0]
            print(f"🔍 第一个系列 '{first_series['name']}' x轴: {first_series['x']}")
        
        
        
        
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "板块涨幅",
                "xaxis": {
                    "title": "时间",
                    "type": "category",  # 强制按分类排序，不自动重排
                    "categoryorder": "array",  # 使用数组顺序
                    "categoryarray": all_dates  # 指定x轴的顺序
                },
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "板块名称"}
            },
            "debug_info": {
                "total_series": len(chart_data),
                "date_range": f"{all_dates[0]} 到 {all_dates[-1]}",
                "total_dates": len(all_dates)
            }
        })
    
    def process_market_stocks_change_daily(self):
        """各板块涨幅 - 带启动缓存"""
        return self._process_with_startup_cache('/api/market_stocks_change_daily', self._original_market_stocks_change_daily)

    def _original_market_stocks_change_daily(self):
        """市场情绪日数据的主板，创业板，科创版，ST板成交额"""
        d = StockMinuteData()
        # 获取最新交易日数据
        trade_date_list = get_trade_date_list()
        latest_date = trade_date_list[-1] 
        latest_date = '20250807' # chen for test
        df = d.get_minute_data_by_date(start_date=latest_date)

        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        # 去除09:30之前的数据
        df = df[df['time'].dt.strftime('%H:%M') >= '09:30']
        df['time_str'] = df['time'].dt.strftime('%H:%M')
        # 如果pre_close列没有值或为0，填充pre_close列的值为1
        df['pre_close'] = df['pre_close'].replace(0, 1)
        # fillna pre_close with 1 if it is NaN
        df['pre_close'] = df['pre_close'].fillna(1)
        # 按id groupby,新增列change，计算close列对pre_close列的百分比变化，并乘以100后保留2位小数
        df['change'] = ((df['close'] - df['pre_close']) / df['pre_close'] * 100).round(2)
        # 选出15:00时刻的change列涨幅大于5的id的list，并去重
        tempdf = df[df['time_str'] == '15:00']
        # 去除change<-31,>31的数据
        tempdf = tempdf[(tempdf['change'] > -31) & (tempdf['change'] < 31)]
        top_stocks = tempdf[tempdf['change'] > 5]['id'].unique().tolist()
        # 选出change列涨幅小于-4的id的list，并去重
        bottom_stocks = tempdf[tempdf['change'] < -5]['id'].unique().tolist()
        # 合并两个列表
        all_stocks = list(set(top_stocks + bottom_stocks))
        chart_data = []
        for stock in all_stocks:
            stock_data = df[df['id'] == stock]
            if not stock_data.empty:
                stock_data = stock_data.sort_values(by='time')
                
                # 获取x轴和y轴数据
                x_data = stock_data['time_str'].tolist()
                y_data = stock_data['change'].tolist()
                
                # 添加完整的日期信息以确保排序正确
                date_info = stock_data[['time_str', 'trade_date']].to_dict('records')
                
                # 方案2：只显示有数据的日期（真实数据，不填充）
                chart_data.append({
                    "name": f'{stock}涨幅',
                    "x": x_data,
                    "y": y_data,
                    "dates": [d['time_str'] for d in date_info],  # 添加完整日期用于排序
                    "mode": "lines+markers"  # 明确指定线条模式
                })
        
        # 获取完整的日期范围用于调试
        all_dates = sorted(df['time_str'].unique())
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "板块涨幅",
                "xaxis": {
                    "title": "时间",
                    "type": "category",  # 强制按分类排序，不自动重排
                    "categoryorder": "array",  # 使用数组顺序
                    "categoryarray": all_dates  # 指定x轴的顺序
                },
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "板块名称"}
            },
            "debug_info": {
                "total_series": len(chart_data),
                "date_range": f"{all_dates[0]} 到 {all_dates[-1]}",
                "total_dates": len(all_dates)
            }
        })

    def process_market_stocks_change_daily_uplimit(self):
        """各板块涨幅 - 带启动缓存"""
        return self._process_with_startup_cache('/api/market_stocks_change_daily_uplimit', self._original_market_stocks_change_daily_uplimit)


    def _original_market_stocks_change_daily_uplimit(self):
        """市场情绪日数据的主板，创业板，科创版，ST板成交额"""
        d = StockMinuteData()
        # 获取最新交易日数据
        trade_date_list = get_trade_date_list()
        latest_date = trade_date_list[-1] 
        latest_date = '20250807' # chen for test
        df = d.get_minute_data_by_date(start_date=latest_date)

        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        # 去除09:30之前的数据
        df = df[df['time'].dt.strftime('%H:%M') >= '09:30']
        df['time_str'] = df['time'].dt.strftime('%H:%M')
        # 如果pre_close列没有值或为0，填充pre_close列的值为1
        df['pre_close'] = df['pre_close'].replace(0, 1)
        # fillna pre_close with 1 if it is NaN
        df['pre_close'] = df['pre_close'].fillna(1)
        # 按id groupby,新增列change，计算close列对pre_close列的百分比变化，并乘以100后保留2位小数
        df['change'] = ((df['close'] - df['pre_close']) / df['pre_close'] * 100).round(2)
        # 选出15:00时刻的change列涨幅大于5的id的list，并去重
        tempdf = df[df['time_str'] == '15:00']
        # 去除change<-31,>31的数据
        tempdf = tempdf[(tempdf['change'] > -31) & (tempdf['change'] < 31)]
        top_stocks = tempdf[tempdf['change'] > 9.7]['id'].unique().tolist()
        # 选出change列涨幅小于-4的id的list，并去重
        bottom_stocks = tempdf[tempdf['change'] < -9.7]['id'].unique().tolist()
        # 合并两个列表
        all_stocks = list(set(top_stocks + bottom_stocks))
        chart_data = []
        for stock in all_stocks:
            stock_data = df[df['id'] == stock]
            if not stock_data.empty:
                stock_data = stock_data.sort_values(by='time')
                
                # 获取x轴和y轴数据
                x_data = stock_data['time_str'].tolist()
                y_data = stock_data['change'].tolist()
                
                # 添加完整的日期信息以确保排序正确
                date_info = stock_data[['time_str', 'trade_date']].to_dict('records')
                
                # 方案2：只显示有数据的日期（真实数据，不填充）
                chart_data.append({
                    "name": f'{stock}涨幅',
                    "x": x_data,
                    "y": y_data,
                    "dates": [d['time_str'] for d in date_info],  # 添加完整日期用于排序
                    "mode": "lines+markers"  # 明确指定线条模式
                })
        
        # 获取完整的日期范围用于调试
        all_dates = sorted(df['time_str'].unique())
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "板块涨幅",
                "xaxis": {
                    "title": "时间",
                    "type": "category",  # 强制按分类排序，不自动重排
                    "categoryorder": "array",  # 使用数组顺序
                    "categoryarray": all_dates  # 指定x轴的顺序
                },
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "板块名称"}
            },
            "debug_info": {
                "total_series": len(chart_data),
                "date_range": f"{all_dates[0]} 到 {all_dates[-1]}",
                "total_dates": len(all_dates)
            }
        })

    def process_market_stocks_change_daily_speed(self):
        """各板块涨幅 - 带启动缓存"""
        return self._process_with_startup_cache('/api/market_stocks_change_daily_speed', self._original_market_stocks_change_daily_speed)


    def _original_market_stocks_change_daily_speed(self):
        """市场情绪日数据的主板，创业板，科创版，ST板成交额"""
        d = StockMinuteData()
        # 获取最新交易日数据
        trade_date_list = get_trade_date_list()
        latest_date = trade_date_list[-1] 
        latest_date = '20250807' # chen for test
        df = d.get_minute_data_by_date(start_date=latest_date)

        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        # 去除09:30之前的数据
        df = df[df['time'].dt.strftime('%H:%M') >= '09:30']
        df['time_str'] = df['time'].dt.strftime('%H:%M')
        # 如果pre_close列没有值或为0，填充pre_close列的值为1
        df['pre_close'] = df['pre_close'].replace(0, 1)
        # fillna pre_close with 1 if it is NaN
        df['pre_close'] = df['pre_close'].fillna(1)
        # 按id groupby,新增列change，计算close列对pre_close列的百分比变化，并乘以100后保留2位小数
        df['change'] = ((df['close'] - df['pre_close']) / df['pre_close'] * 100).round(2)
        # 获取5分涨速
        df['speed5'] = df.groupby('id')['change'].diff(5).fillna(0)
        # 选出15:00时刻的change列涨幅大于5的id的list，并去重
        tempdf = df.copy()
        # 去除change<-31,>31的数据
        tempdf = tempdf[(tempdf['change'] > -31) & (tempdf['change'] < 31)]
        top_stocks = tempdf[tempdf['speed5'] > 5]['id'].unique().tolist()
        # 选出change列涨幅小于-4的id的list，并去重
       
        all_stocks = list(set(top_stocks))
        chart_data = []
        for stock in all_stocks:
            stock_data = df[df['id'] == stock]
            # 过滤掉异常数据点，但保留正常数据
            stock_data = stock_data[(stock_data['change'] >= -31) & (stock_data['change'] <= 31)]
            
            if not stock_data.empty:  # 如果过滤后还有数据
                stock_data = stock_data.sort_values(by='time')
                
                # 获取x轴和y轴数据
                x_data = stock_data['time_str'].tolist()
                y_data = stock_data['change'].tolist()
                
                # 添加完整的日期信息以确保排序正确
                date_info = stock_data[['time_str', 'trade_date']].to_dict('records')
                
                # 方案2：只显示有数据的日期（真实数据，不填充）
                chart_data.append({
                    "name": f'{stock}涨幅',
                    "x": x_data,
                    "y": y_data,
                    "dates": [d['time_str'] for d in date_info],  # 添加完整日期用于排序
                    "mode": "lines+markers"  # 明确指定线条模式
                })
        
        # 获取完整的日期范围用于调试
        all_dates = sorted(df['time_str'].unique())
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "板块涨幅",
                "xaxis": {
                    "title": "时间",
                    "type": "category",  # 强制按分类排序，不自动重排
                    "categoryorder": "array",  # 使用数组顺序
                    "categoryarray": all_dates  # 指定x轴的顺序
                },
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "板块名称"}
            },
            "debug_info": {
                "total_series": len(chart_data),
                "date_range": f"{all_dates[0]} 到 {all_dates[-1]}",
                "total_dates": len(all_dates)
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

    def process_up_limit_stocks_review(self):
        """返回涨停数据表 - 支持日期参数，不使用缓存"""
        return self._original_up_limit_stocks_review()

    def _original_up_limit_stocks_review(self):
        """返回涨停数据表"""
        
        try:
            # 获取时间参数，默认为今天
            from flask import request
            selected_date = request.args.get('date', '2025-07-25')  # 期望格式：YYYY-MM-DD
            
            d = KplUpLimitData()
            up_limit_df = d.get_daily_data(start_date='2025-07-01')
            
            if up_limit_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "涨停数据文件读取失败"
                })
            
            # 时间过滤逻辑
            up_limit_df['trade_date'] = pd.to_datetime(up_limit_df['trade_date'])
            
            if selected_date:
               
                target_date = pd.to_datetime(selected_date).date()
                # 如果日期不存在，使用最新日期的数据
                if target_date not in up_limit_df['trade_date'].dt.date.unique():
                    self.logger.warning(f"指定日期 {target_date} 不存在，使用最新日期的数据")
                    up_limit_df = up_limit_df[up_limit_df['trade_date'].dt.date == up_limit_df['trade_date'].dt.date.max()]
                # 过滤指定日期的数据
                else:
                    up_limit_df = up_limit_df[up_limit_df['trade_date'].dt.date == target_date]
            else:
                # 获取最新的日期的行
                up_limit_df = up_limit_df[up_limit_df['trade_date'].dt.date == up_limit_df['trade_date'].dt.date.max()]
                
            # 将trade_date改为月日的格式
            up_limit_df['trade_date'] = up_limit_df['trade_date'].dt.strftime('%m-%d')
            # 将up_limit_amount，famc列转换为亿元为单位
            up_limit_df['up_limit_amount'] = up_limit_df['up_limit_amount'] / 1e8
            up_limit_df['famc'] = up_limit_df['famc'] / 1e8
            # 需要重新计算，继续执行原有逻辑
            # 定义表格列 - 根据实际CSV文件的列名
            columns = [
                {"field": "trade_date", "header": "时间"},
                {"field": "stock_name", "header": "股票名称"},
                {"field": "up_limit_reason", "header": "涨停原因"},
                {"field": "sector", "header": "板块"},  
                {"field": "up_limit_strength", "header": "涨停强度"},
                {"field": "up_limit_amount", "header": "封单金额", "backgroundColor": "redGreen"},
                {"field": "day_up_limit_count", "header": "涨停日数", "backgroundColor": "redGreen"},
                {"field": "up_limit_count", "header": "涨停次数", "backgroundColor": "redGreen"},
                {"field": "famc", "header": "流通市值", "backgroundColor": "redGreen"},
                {"field": "intro", "header": "公司介绍"},
                {"field": "id", "header": "股票ID", "visible": False},
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
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取涨停数据失败: {e}")

    def process_upLimitStocksDist_v2(self):
        """返回涨停数据表 - 带启动缓存"""
        return self._process_with_startup_cache('/api/upLimitStocksDist_v2', self._original_upLimitStocksDist_v2)

    def _original_upLimitStocksDist_v2(self):
        """返回涨停数据表"""
        
        try:
            d = KplUpLimitData()
            up_limit_df = d.get_daily_data(start_date='2025-07-01')
            
            if up_limit_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "涨停数据文件读取失败"
                })
            
            # 获取最新的日期的行
            up_limit_df['trade_date'] = pd.to_datetime(up_limit_df['trade_date'])
            # 将trade_date改为月日的格式
            up_limit_df['trade_date'] = up_limit_df['trade_date'].dt.strftime('%m-%d')
            # 将up_limit_amount，famc列转换为亿元为单位
            up_limit_df['up_limit_amount'] = up_limit_df['up_limit_amount'] / 1e8
            up_limit_df['famc'] = up_limit_df['famc'] / 1e8

            # 对trade_date进行分组，提取板块列中的所有板块名，板块列中的值是以逗号分隔的字符串，统计每个板块名当日出现的次数
            # 做成一个新的DataFrame，包含trade_date和板块名两列
            sector_count_data = []
            for trade_date, group in up_limit_df.groupby('trade_date'):
                for _, row in group.iterrows():
                    if pd.notna(row['sector']) and row['sector']:  # 确保板块列不为空
                        # 分割逗号分隔的板块字符串
                        sectors = [sector.strip() for sector in str(row['up_limit_reason']).split('、') if sector.strip()]
                        for sector in sectors:
                            if sector != '其他':
                                sector_count_data.append({
                                    'trade_date': trade_date,
                                    'sector_name': sector
                                })
            
            # 创建板块统计DataFrame
            sector_df = pd.DataFrame(sector_count_data)
            if not sector_df.empty:
                # 按日期和板块名分组统计次数
                sector_count_df = sector_df.groupby(['trade_date', 'sector_name']).size().reset_index(name='count')
                
                # 整理成以trade_date为列，板块名为行，count为值的新的DataFrame
                sector_pivot_df = sector_count_df.pivot(index='sector_name', columns='trade_date', values='count')
                # 填充NaN值为0
                sector_pivot_df = sector_pivot_df.fillna(0).astype(int)
                
                # 对sector_count_df排序，获取最新的5个日期，按板块名分组计算count合计，获取排序顺序
                if not sector_count_df.empty:
                    # 获取最新的5个交易日期
                    latest_dates = sorted(sector_count_df['trade_date'].unique(), reverse=True)[:5]
                    
                    # 筛选最新5个日期的数据并按板块分组求和
                    recent_sector_totals = (sector_count_df[sector_count_df['trade_date'].isin(latest_dates)]
                                           .groupby('sector_name')['count'].sum()
                                           .sort_values(ascending=False))  # 按count总和降序排列
                    
                    # 获取排序后的板块名顺序
                    sector_order = recent_sector_totals.index.tolist()
                    
                    # 重新排列sector_pivot_df的行顺序，只包含存在的板块
                    existing_sectors = [sector for sector in sector_order if sector in sector_pivot_df.index]
                    sector_pivot_df = sector_pivot_df.reindex(existing_sectors)
                    
                    # 添加total列，统计每个板块的count总数
                    sector_pivot_df['total'] = sector_pivot_df.sum(axis=1)
            else:
                # 如果没有数据，创建空的DataFrame
                sector_count_df = pd.DataFrame(columns=['trade_date', 'sector_name', 'count'])
                sector_pivot_df = pd.DataFrame()
            
            # 为sector_pivot_df动态定义列 - 高效方法
            if not sector_pivot_df.empty:
                # 动态生成日期列
                date_columns = []
                for date_col in sector_pivot_df.columns:
                    if date_col != 'total':  # 排除total列
                        date_columns.append({
                            "field": date_col,
                            "header": f"25{date_col}",  # 添加年份前缀
                            "backgroundColor": "redGreen"  # 日期列使用redGreen颜色
                        })
                
                # 构建完整的sector列定义
                sector_columns = [
                    {"field": "sector_name", "header": "板块名称"}  # 板块名称列
                ] + date_columns + [
                    {"field": "total", "header": "总计", "backgroundColor": "redGreen"}  # 总计列
                ]
            else:
                sector_columns = []

            # 为sector_pivot_df准备数据 - 将索引转为列
            if not sector_pivot_df.empty:
                # 将索引(sector_name)转为列
                sector_pivot_df_with_names = sector_pivot_df.reset_index()
            else:
                sector_pivot_df_with_names = pd.DataFrame()
            
            valid_columns = [col for col in sector_columns if col["field"] in sector_pivot_df_with_names.columns]
            
            rows = []
            for _, row_data in sector_pivot_df_with_names.iterrows():
                row = {}
                for col in valid_columns:
                    field = col["field"]
                    value = row_data[field]
                    
                    # 处理不同数据类型的JSON序列化
                    if isinstance(value, (float, np.float64, np.float32)):
                        value = round(value, 2)
                    elif isinstance(value, (int, np.int64, np.int32)):
                        value = int(value)  # 转换为Python原生int类型
                    
                    row[field] = value
                
                rows.append(row)
            
            # 构建响应数据
            response_data = jsonify({
                "columns": valid_columns,
                "rows": rows
            })
            
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
        获取指定日期各板块连板数分布（板块内股票日线涨幅分布） - 带启动缓存
        横轴为板块名称，纵轴为股票个数
        分别用堆积图展示各板块的连板数分布，从下往上为1板，2板，3板等
        
        参数:
        - date: 可选，格式为YYYY-MM-DD，如：2024-07-21。不提供则使用今日数据
        
        用法示例:
        - /api/today_plate_up_limit_distribution (使用今日数据)
        - /api/today_plate_up_limit_distribution?date=2024-07-21 (使用指定日期数据)
        """
        return self._original_today_plate_up_limit_distribution()
    
    def _original_today_plate_up_limit_distribution(self):
        """
        获取今日各板块连板数分布
        横轴为板块名称，纵轴为股票个数
        分别用堆积图展示各板块的连板数分布，从下往上为1板，2板，3板等
        支持时间选择功能，可以指定某一天的数据
        """
        try:
            # 获取时间参数，默认为今天
            from flask import request
            selected_date = request.args.get('date','2025-07-25')  # 期望格式：YYYY-MM-DD
            d= NightFactorData()
            stock_all_level_df = d.get_daily_data()
            
            if stock_all_level_df.empty:
                return self.error_response("股票连板数据文件读取失败")
            
            # 时间过滤逻辑
            if selected_date:
                try:
                    # 将字符串日期转换为datetime对象
                    target_date = pd.to_datetime(selected_date).date()
                    
                    # 确保trade_date列是datetime类型
                    if 'trade_date' in stock_all_level_df.columns:
                        stock_all_level_df['trade_date'] = pd.to_datetime(stock_all_level_df['trade_date'])
                        # 如果target_date在数据中不存在，返回最大日期的数据
                        if target_date not in stock_all_level_df['trade_date'].dt.date.unique():
                            target_date = stock_all_level_df['trade_date'].dt.date.max()
                            selected_date = target_date.strftime('%Y-%m-%d')

                        stock_all_level_df = stock_all_level_df[stock_all_level_df['trade_date'].dt.date == target_date]
                        
                        if stock_all_level_df.empty:
                            return self.error_response(f"指定日期 {selected_date} 没有数据")
                    else:
                        # 如果没有trade_date列，使用今天的数据（默认行为）
                        pass
                        
                except Exception as date_error:
                    return self.error_response(f"日期格式错误: {date_error}，请使用YYYY-MM-DD格式")
            
            # 过滤掉不需要的板块
            stock_all_level_df = stock_all_level_df[~stock_all_level_df['sector'].str.contains("沪股通|深股通|季报|融资融券", na=False)]
            stock_all_level_df = stock_all_level_df[stock_all_level_df['lian_ban_shu'] > 0]
           
            stock_all_level_df['Level'] = stock_all_level_df['lian_ban_shu']
            # 将连板数转换为整数，处理异常值
            stock_all_level_df['Level'] = pd.to_numeric(stock_all_level_df['Level'], errors='coerce').fillna(0).astype(int)

            # 按照板块分组，统计每个板块的连板数分布
            sector_level_stats = stock_all_level_df.groupby(['sector', 'Level']).size().unstack(fill_value=0)
            
            # 同时获取每个板块每个连板数对应的股票列表，用于hover显示
            sector_stock_lists = {}
            for sector in stock_all_level_df['sector'].unique():
                sector_stock_lists[sector] = {}
                sector_data = stock_all_level_df[stock_all_level_df['sector'] == sector]
                for level in sector_data['Level'].unique():
                    level_data = sector_data[sector_data['Level'] == level]
                    sector_stock_lists[sector][level] = level_data['stock_name'].tolist() if 'stock_name' in level_data.columns else level_data['code'].tolist()
            
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
            top_sectors = sector_level_stats.sort_values('total', ascending=False).head(20).index.tolist()
            sector_level_stats = sector_level_stats.loc[top_sectors]
            sector_level_stats = sector_level_stats.drop('total', axis=1)
            
            # 构建堆积图数据 - 使用与其他图表一致的格式
            categories = sector_level_stats.index.tolist()  # 板块名称作为横坐标
            chart_data = []
            
            # 为每个连板数等级创建一个系列 - 使用冷色到暖色的渐变
            # 1连板：深蓝色（最冷） -> 高连板：深红色（最暖）
            colors = [
                '#1E3A8A',  # 1连板 - 深蓝色
                '#0D9488',  # 2连板 - 蓝色
                '#CA8A04',  # 3连板 - 青绿色  
                "#F17676",  # 4连板 - 绿色
                '#DC2626',  # 5连板 - 金黄色
                '#7C2D12',  # 6连板 - 橙色
                '#450A0A',  # 7连板 - 红色
                '#450A0A',  # 8连板 - 深红色
                "#450A0A",  # 9连板 - 棕红色
                '#450A0A'   # 10连板+ - 深褐红色
            ]
            
            for i, level in enumerate(level_columns):
                # 为每个板块构建该连板数的数据和hover信息
                y_values = []
                hover_texts = []
                
                for sector in categories:
                    stock_count = sector_level_stats.loc[sector, level]
                    # 转换为Python原生int类型，避免JSON序列化问题
                    stock_count = int(stock_count)
                    y_values.append(stock_count)
                    
                    # 构建hover文本
                    if stock_count > 0 and sector in sector_stock_lists and level in sector_stock_lists[sector]:
                        stock_list = sector_stock_lists[sector][level]
                        # 限制显示的股票数量，避免hover太长
                        if len(stock_list) > 10:
                            stock_display = stock_list[:10] + [f"...等{len(stock_list)}只股票"]
                        else:
                            stock_display = stock_list
                        
                        stock_text = '<br>'.join([f'• {stock}' for stock in stock_display])
                        hover_text = f'{sector}<br>{level}连板: {stock_count}只<br><br>股票列表:<br>{stock_text}'
                    else:
                        hover_text = f'{sector}<br>{level}连板: {stock_count}只'
                    
                    hover_texts.append(hover_text)
                
                chart_data.append({
                    'name': f'{level}连板',
                    'x': categories,  # 板块名称
                    'y': y_values,  # 对应的股票个数
                    'type': 'bar',  # 柱状图类型
                    'marker': {'color': colors[i % len(colors)]},
                    'text': hover_texts,  # hover显示的文本
                    'hovertemplate': '%{text}<extra></extra>',  # 使用自定义hover模板
                    'hoverlabel': {
                        'bgcolor': 'rgba(30, 30, 30, 0.9)',  # 深灰色半透明背景
                        'bordercolor': 'white',               # 白色边框
                        'font': {
                            'color': 'white',                 # 白色字体
                            'size': 24,                       # 字体大小
                            'family': 'Arial, sans-serif'    # 字体家族
                        }
                    }
                })
            
            # 构建动态标题
            if selected_date:
                chart_title = f"各板块连板数分布 ({selected_date})"
            else:
                chart_title = "各板块连板数分布 (今日)"
            
            return jsonify({
                "chartType": "bar",  # 柱状图
                "data": chart_data,  # 图表数据
                "layout": {
                    "title": chart_title,
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
            
            # 同时获取每个板块每个连板数对应的股票列表，用于hover显示
            sector_stock_lists_v2 = {}
            for sector in stock_all_level_df['Sector'].unique():
                sector_stock_lists_v2[sector] = {}
                sector_data = stock_all_level_df[stock_all_level_df['Sector'] == sector]
                for level in sector_data['Level'].unique():
                    level_data = sector_data[sector_data['Level'] == level]
                    # 优先使用stock_name，如果没有则使用code
                    if 'stock_name' in level_data.columns:
                        sector_stock_lists_v2[sector][level] = level_data['stock_name'].tolist()
                    elif 'code' in level_data.columns:
                        sector_stock_lists_v2[sector][level] = level_data['code'].tolist()
                    else:
                        # 如果都没有，尝试使用索引
                        sector_stock_lists_v2[sector][level] = level_data.index.tolist()
            
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
            
            top_sectors_v2 = sector_level_stats.sort_values('total_stocks', ascending=False).head(15).index.tolist()
            sector_level_stats = sector_level_stats.loc[top_sectors_v2]
            
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
                    
                    # 使用预构建的股票列表数据
                    if sector_name in sector_stock_lists_v2 and level in sector_stock_lists_v2[sector_name]:
                        level_stocks = sector_stock_lists_v2[sector_name][level]
                    else:
                        level_stocks = []
                    
                    # 构建hover显示文本
                    if len(level_stocks) > 0:
                        # 限制显示的股票数量，避免hover太长
                        if len(level_stocks) > 8:
                            stock_display = level_stocks[:8] + [f"...等{len(level_stocks)}只股票"]
                        else:
                            stock_display = level_stocks
                        sector_hover[key] = stock_display
                    else:
                        sector_hover[key] = []
                
                data[sector_name] = sector_data
                table_data[sector_name] = f"{total_stocks}只"
                hover_data[sector_name] = sector_hover
            
            # 定义连板数类型的顺序和颜色 - 使用冷色到暖色的渐变
            keyOrder = [f"{level}连板" for level in level_columns]
            # 1连板：深蓝色（最冷） -> 高连板：深红色（最暖）
            colors = [
                '#1E3A8A',  # 1连板 - 深蓝色
                '#1E40AF',  # 2连板 - 蓝色
                '#0D9488',  # 3连板 - 青绿色  
                '#059669',  # 4连板 - 绿色
                '#CA8A04',  # 5连板 - 金黄色
                '#EA580C'   # 6连板 - 橙色
            ][:len(level_columns)]
            
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
    
    def get_sector_rankings_by_period(self, df, latest_date_str, days_list=[5, 10, 20], top_n=10):
        """
        获取指定时间段内cumsum排名前N的板块
        
        Args:
            df: 包含trade_date, name, change列的DataFrame
            latest_date_str: 最新日期字符串，格式'YYYYMMDD'
            days_list: 要统计的天数列表，默认[5, 10, 20]
            top_n: 返回前N名，默认10
            
        Returns:
            dict: 各时间段的排名结果
        """
        ranking_results = {}
        
        for days in days_list:
            try:
                # 计算开始日期
                period_start_str = get_trade_date_by_offset(latest_date_str, days)
                period_start = pd.to_datetime(period_start_str, format='%Y%m%d')
                latest_date = pd.to_datetime(latest_date_str, format='%Y%m%d')
                
                # 筛选指定时间段的数据
                period_df = df[(df['trade_date'] >= period_start) & (df['trade_date'] <= latest_date)]
                
                # 重新计算cumsum（避免使用全局cumsum）
                period_df = period_df.copy()
                period_df = period_df.sort_values(['name', 'trade_date'])
                period_df['period_cumsum'] = period_df.groupby('name')['change'].cumsum()
                
                # 获取每个板块在该时间段的最新cumsum值
                latest_cumsum = period_df.groupby('name')['period_cumsum'].last().reset_index()
                
                # 排序并获取前N名
                top_sectors = latest_cumsum.sort_values('period_cumsum', ascending=False).head(top_n)
                
                ranking_results[f'近{days}日排名'] = [
                    {
                        'rank': idx + 1,
                        'sector_name': row['name'],
                        'cumsum_change': round(row['period_cumsum'], 4)
                    }
                    for idx, (_, row) in enumerate(top_sectors.iterrows())
                ]
                
            except Exception as e:
                print(f"⚠️ 计算近{days}日排名时出错: {e}")
                ranking_results[f'近{days}日排名'] = []
        
        return ranking_results
