"""
market_realtime处理器
根据components_config.json和server_config.json自动生成
Author: Auto-generated
Date: 2025-08-14 10:57:34
"""

from datetime import datetime
from flask import jsonify
import pandas as pd

from stock_data.kaipanla.stock.daily import KplStockData
from stock_data.stock.stock_daily import StockDailyData
from stock_data.stock_minute import StockMinuteData
from stock_data.ths.concept_data import ThsConceptData
from stock_data.ths.concept_index import ThsConceptIndexData
from stock_data.ths.concept_minute import ThsConceptMinuteData
from utils.common import get_latest_stock_name_from_stock_id, get_trade_date_by_offset
from .base_processor import BaseDataProcessor

class MarketRealtimeProcessor(BaseDataProcessor):
    """
    market_realtime数据处理器
    
    基于components_config.json中的market_realtime配置自动生成
    包含以下组件的处理方法:
    - 板块内股票日线涨幅: 板块内股票日线涨幅
    - 板块内股票分钟涨幅: 板块内股票分钟涨幅
    - 板块内股票分钟涨幅_diff: 板块内股票分钟涨幅_diff
    - 板块内股票分钟涨幅_diff_KPL_custom: 板块内股票分钟涨幅_diff_KPL_custom
    - 涨停数据表: 涨停数据表
    """
    # # 在初始化函数中增加以下处理
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化时可以添加一些通用的处理逻辑
        # 例如，加载配置文件、初始化数据源等
        f = StockDailyData()
        df = f.get_daily_data(start_date='20250701', end_date=None)   
        #获取最新日期的数据
        latest_date = df['trade_date'].max()
        df = df[df['trade_date'] == latest_date]
        self.stock_name_df = df.copy()  # 保留最新日期的数据副本

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
                    "marker": {"size": 3},  # 设置圆点大小为3
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
        stock_df = d.get_realtime_data() # 只取latest_date日的数据
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
        
        # stock_df = get_latest_stock_name_from_stock_id(stock_df)
        # stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        stock_df = stock_df.merge(self.stock_name_df[['id', 'stock_name']], on='id', how='left')
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
                    "marker": {"size": 3},  # 设置圆点大小为3
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
        stock_df = d.get_realtime_data() # 只取latest_date日的数据
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
        
        # 如果pre_close列没有值或为0，填充pre_close列的值为0930开盘价的值
        stock_df['pre_close'] = stock_df['pre_close'].replace(0, 9999)
        
        # 计算每分钟涨幅change
        stock_df['change'] = ((stock_df['close']- stock_df['pre_close'])/ stock_df['pre_close'] *100).round(2) # 计算每分钟的涨幅
        

        # 将在区间-2到2的change值设置为2或-2，change为正时则设为2，负时设为-2
        stock_df.loc[(stock_df['change_diff'] >= -2) & (stock_df['change_diff'] <= 2), 'change_diff'] = stock_df['change_diff'].apply(lambda x: 2 if x > 0 else -2)

        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        
        stock_df['time_str'] = stock_df['time'].dt.strftime('%m%d_%H:%M')
        
        # stock_df = get_latest_stock_name_from_stock_id(stock_df)
        # stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        stock_df = stock_df.merge(self.stock_name_df[['id', 'stock_name']], on='id', how='left')
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
                    "marker": {"size": 3},  # 设置圆点大小为3
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
            "mode": "lines+markers+text",
            "line": {"width": 2, "color": "red"},
            "marker": {"size": 2},
            "text": factor_data['factor_9_7'].tolist(),  # 在factor_2点上显示factor_9_7的值
            "textposition": "top center",
            "textfont": {"size": 10, "color": "blue"},
            "name": "市场情绪因子(>2数量 - <-2数量)",
            "yaxis": "y2",  # 使用右侧Y轴
            "showlegend": True
        })
        
        # 添加因子9.7的线条
        chart_data.append({
            "x": factor_data['time_str'].tolist(),
            "y": factor_data['factor_9_7'].tolist(),
            "mode": "lines+markers",
            "line": {"width": 2, "color": "orange"},
            "marker": {"size": 2},
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
    
    def process_strong_plates_change2_factor(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        start_date = request.args.get('startDate', '2025-07-01')  # 默认开始日期
        end_date = request.args.get('endDate', None)  # 默认结束日期为None，使用最新日期
        
        # 直接调用原始方法，不使用启动缓存
        # 因为启动缓存会忽略sector和日期参数，导致选择不同参数时返回相同数据
        return self._original_strong_plates_change2_factor(selected_sector, start_date, end_date)

    def get_ths_change_big_than_0_sector(self, selected_sector=None):
        d = ThsConceptMinuteData()
        """获取涨幅大于0的板块"""
        df = d.get_realtime_minute_data()
        df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        # 获取最新时间的行的df
        df = df[df['time'] == df['time'].max()]
        # 筛选涨幅大于0的板块
        df = df[df['change'] > 0]
        # 获取name列的list
        sector_names = df['name'].tolist()
        if selected_sector is not None:
            # 如果指定了板块，则添加到列表中
            sector_names.append(selected_sector)
        sector_names = list(set(sector_names))  # 去重
        return sector_names

    def get_ths_recent_days_strong_sectors(self, start_date='2025-07-01', end_date=None, selected_sector=None):
        """获取近5日，近10日，近20日涨幅排名前10的板块"""
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
        if selected_sector is not None:
            sector_names.append(selected_sector)
        # 去除重复的板块名称
        sector_names = list(set(sector_names))

    def _original_strong_plates_change2_factor(self, selected_sector=None, start_date='2025-07-01', end_date=None):
        """各板块股票涨幅 - 支持动态板块选择和具体日期范围选择"""
        # # 将开始日期转换为datetime类型
        # start_date_dt = pd.to_datetime(start_date, errors='coerce')

        # d = ThsConceptIndexData()
        # # 使用传入的开始日期获取数据
        # df = d.get_daily_data(start_date=start_date)

        # df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
        # df['date_str'] = df['trade_date'].dt.strftime('%m/%d')
        
        # #确定实际的开始和结束日期
        # if end_date is None or df['trade_date'].max() < pd.to_datetime(end_date, errors='coerce'):
        #     # 如果没有指定结束日期，使用数据的最新日期
        #     latest_date = df['trade_date'].max()
        # else:
        #     # 使用指定的结束日期，但不能超过数据的最新日期
        #     end_date_dt = pd.to_datetime(end_date, errors='coerce')
        #     data_max_date = df['trade_date'].max()
        #     latest_date = min(end_date_dt, data_max_date)
        
        
        # temp_df = df.copy()  # 保留原始数据
        # # 筛选指定日期范围内的数据
        # df = df[(df['trade_date'] >= start_date_dt) & (df['trade_date'] <= latest_date)]
        
        # latest_date_str = latest_date.strftime('%Y%m%d')
        
        # #获取近5日，近10日，近20日的cumsum各排名前10的板块列表
        # ranking_results = self.get_sector_rankings_by_period(temp_df, latest_date_str, [5, 10, 20], 10)
        
        # # 获取ranking_results的列表，并在df中筛选出这些板块
        # sector_names = [item['sector_name'] for sublist in ranking_results.values() for item in sublist]
        # if selected_sector is not None:
        #     sector_names.append(selected_sector)
        # # 去除重复的板块名称
        # sector_names = list(set(sector_names))
        sector_names = self.get_ths_change_big_than_0_sector(selected_sector)

        chart_data = []
        
        d = ThsConceptData()
        concept_df = d.get_daily_data(start_date=start_date)
        # 获取最新交易日数据
        concept_latest_date = concept_df['trade_date'].max()
        concept_df = concept_df[concept_df['trade_date'] == concept_latest_date]

        d = StockMinuteData()
        stock_df = d.get_realtime_data() # 只取latest_date日的数据
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        # time列应该已经包含日期和时间信息，确保其为datetime类型
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        # 去除09:25之前的数据
        stock_df = stock_df[stock_df['time'].dt.strftime('%H:%M') >= '09:30']
        # 筛选股票数据到相同的日期范围
        # stock_df = stock_df[(stock_df['trade_date'] >= start_date_dt) & (stock_df['trade_date'] <= latest_date)]

        # groupby id，用（close-09：25分的close）/09：25分的close计算change列
        stock_df['pre_close_0925'] = stock_df.groupby('id')['close'].transform(lambda x: x.iloc[0])  # 获取每只股票09:25分的收盘价
        # 计算每分钟的涨幅
        stock_df['change_diff'] = ((stock_df['close']- stock_df['pre_close_0925'])/ stock_df['pre_close_0925'] *100).round(2) # 计算每分钟的涨幅
        
        # 如果pre_close列没有值或为0，填充pre_close列的值为0930开盘价的值
        stock_df['pre_close'] = stock_df['pre_close'].replace(0, 9999)
        
        # 计算每分钟涨幅change
        stock_df['change'] = ((stock_df['close']- stock_df['pre_close'])/ stock_df['pre_close'] *100).round(2) # 计算每分钟的涨幅
        

        # 将在区间-2到2的change值设置为2或-2，change为正时则设为2，负时设为-2
        stock_df.loc[(stock_df['change_diff'] >= -2) & (stock_df['change_diff'] <= 2), 'change_diff'] = stock_df['change_diff'].apply(lambda x: 2 if x > 0 else -2)

        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        
        stock_df['time_str'] = stock_df['time'].dt.strftime('%m%d_%H:%M')
        
        # stock_df = get_latest_stock_name_from_stock_id(stock_df)
        # stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        stock_df = stock_df.merge(self.stock_name_df[['id', 'stock_name']], on='id', how='left')
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = stock_df['time'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m%d_%H:%M') for date in all_dates]
        
        for sector_name in sector_names:
            
            # 获取股票列表
            stock_list = concept_df[concept_df['concept_name'] == sector_name]['stocks'].values[0].split(',')
            # 并变成整数型
            stock_list = [int(stock) for stock in stock_list if stock.isdigit()]
            # 获取stock_df中id在stock_list中的数据
            temp_stock_df = stock_df[stock_df['id'].isin(stock_list)]
            
            
            
            # for stock_id in stock_list:
            #     stock_data = stock_df[stock_df['id'] == stock_id]
                
            #     if not stock_data.empty:
            #         stock_data = stock_data.sort_values(by='time')
            #         # 获取股票名称 - 取第一行的值
            #         stock_name = stock_data['stock_name'].iloc[0]
                    
            #         x_data = stock_data['time_str'].tolist()
            #         y_data = stock_data['change_diff'].tolist()
                    
            #         chart_data.append({
            #             "name": f'{stock_name}——{sector_name}',
            #             "x": x_data,
            #             "y": y_data,
            #             "mode": "lines+markers+text",  # 添加 +text 模式
            #             "line": {"width": 2},
            #             "marker": {"size": 3},  # 设置圆点大小为3
            #             "text": [f'{stock_name}' if i == len(x_data)-1 else '' for i in range(len(x_data))],
            #             "textposition": "middle right",
            #             "textfont": {"size": 10, "color": "black"},
            #             "showlegend": True
            #         })
            
            # 计算时间维度的因子 - 直接计算，无需合并回原数据
            # 因子1: 每分钟change大于2的个数减去小于-2的个数
            factor_2_df = temp_stock_df.groupby('time_str')['change'].agg(
                factor_2=lambda x: (x > 2).sum() - (x < -2).sum()
            ).reset_index()
            
            # 因子2: 每分钟change大于9.7的个数
            factor_9_7_df = temp_stock_df.groupby('time_str')['change'].agg(
                factor_9_7=lambda x: (x > 9.7).sum()
            ).reset_index()
            
            # 合并两个因子数据并排序
            factor_data = factor_2_df.merge(factor_9_7_df, on='time_str', how='outer').sort_values('time_str')
            
            # 添加因子2的线条
            chart_data.append({
                "x": factor_data['time_str'].tolist(),
                "y": factor_data['factor_2'].tolist(),
                "mode": "lines+markers+text",
                "line": {"width": 2},
                "marker": {"size": 2},
                "text": factor_data['factor_9_7'].tolist(),  # 在factor_2点上显示factor_9_7的值
                "textposition": "top center",
                "textfont": {"size": 10, "color": "blue"},
                "name": f"{sector_name}",
                # "yaxis": "y2",  # 使用右侧Y轴
                "showlegend": True
            })
            
            
            # # 添加因子9.7的线条
            # chart_data.append({
            #     "x": factor_data['time_str'].tolist(),
            #     "y": factor_data['factor_9_7'].tolist(),
            #     "mode": "lines+markers",
            #     "line": {"width": 2, "color": "orange"},
            #     "marker": {"size": 2},
            #     "name": "强势股因子(>9.7%数量)",
            #     # "yaxis": "y2",  # 使用右侧Y轴
            #     "showlegend": True
            # })
        
            
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": f"板块内股票分钟涨幅_diff + 市场因子 - {sector_name} ",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {
                    "title": "涨幅因子(%)",
                    "side": "left"
                },
                # "yaxis2": {
                #     "title": "因子数量",
                #     "side": "right",
                #     "overlaying": "y",
                #     "showgrid": False
                # },
                "legend": {"title": "指标名称"}
            },
            "sectorInfo": {
                "currentSector": sector_name,
                "availableSectors": sector_names,
                "sectorCount": len(sector_names)
            },
            
        })
    
    def get_sector_name_by_component_id(self, component_id):
        """获取组件ID"""
        sector_list = ['机器人概念','芯片','新疆','军工','算力','PEEK','锂电池','医药','西藏水电站','PEEK']
        sector_map = {
            'plate_stocks_change_minute_diff_kpl_custom_1': '机器人概念',
            'plate_stocks_change_minute_diff_kpl_custom_2': '芯片',
            'plate_stocks_change_minute_diff_kpl_custom_3': '新疆',
            'plate_stocks_change_minute_diff_kpl_custom_4': '军工',
            'plate_stocks_change_minute_diff_kpl_custom_5': '算力',
            'plate_stocks_change_minute_diff_kpl_custom_6': 'PEEK',
            'plate_stocks_change_minute_diff_kpl_custom_7': '锂电池',
            'plate_stocks_change_minute_diff_kpl_custom_8': '医药',
            'plate_stocks_change_minute_diff_kpl_custom_9': '西藏水电站',
            'plate_stocks_change_minute_diff_kpl_custom_10': 'PEEK'
        }
        sector= sector_map.get(component_id, None)
        return sector
    
    def process_plate_stocks_change_minute_diff_kpl_custom(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        if selected_sector is None:
            # 如果没有指定板块，使用组件ID来获取默认板块名称
            component_id = request.args.get('componentId', 'default')
            selected_sector = self.get_sector_name_by_component_id(component_id)
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
        stock_df = d.get_realtime_data(start_time = datetime.now().strftime("%Y-%m-%d") + " 09:30:00") # 只取latest_date日的数据
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        # time列应该已经包含日期和时间信息，确保其为datetime类型
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        # 去除09:25之前的数据
        # stock_df = stock_df[stock_df['time'].dt.strftime('%H:%M') >= '09:30']
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
        
        # stock_df = get_latest_stock_name_from_stock_id(stock_df)
        stock_df = stock_df.merge(self.stock_name_df[['id', 'stock_name']], on='id', how='left')
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
                    "line": {"width": 1},
                    "marker": {"size": 1},  # 设置圆点大小为3
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
            "mode": "lines+markers+text",
            "line": {"width": 2, "color": "red"},
            "marker": {"size": 2},
            "text": factor_data['factor_9_7'].tolist(),  # 在factor_2点上显示factor_9_7的值
            "textposition": "top center",
            "textfont": {"size": 10, "color": "blue"},
            "name": "市场情绪因子(>2数量 - <-2数量)",
            "yaxis": "y2",  # 使用右侧Y轴
            "showlegend": True
        })
        
        # 添加因子9.7的线条
        chart_data.append({
            "x": factor_data['time_str'].tolist(),
            "y": factor_data['factor_9_7'].tolist(),
            "mode": "lines+markers",
            "line": {"width": 2, "color": "orange"},
            "marker": {"size": 2},
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
    
    def process_kpl_2sector_custom_change_view(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        change_value = 2  # 默认值
        if selected_sector is None:
            # 如果没有指定板块，使用组件ID来获取默认板块名称
            component_id = request.args.get('componentId', 'default')
            if component_id == 'kpl_2sector_custom_change2_view':
                change_value = 2
            elif component_id == 'kpl_2sector_custom_change5_view':
                change_value = 5

            
        start_date = request.args.get('startDate', '2025-07-01')  # 默认开始日期
        end_date = request.args.get('endDate', None)  # 默认结束日期为None，使用最新日期
        
        # 直接调用原始方法，不使用启动缓存
        # 因为启动缓存会忽略sector和日期参数，导致选择不同参数时返回相同数据
        return self._original_kpl_2sector_custom_change_view(selected_sector, start_date, end_date, change_value)

    def _original_kpl_2sector_custom_change_view(self, selected_sector=None, start_date='2025-07-01', end_date=None, change_value=0):
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
        temp_df = temp_df[(temp_df['trade_date'] == latest_date)]
        
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
        stock_df = d.get_realtime_data(start_time = datetime.now().strftime("%Y-%m-%d") + " 09:30:00") # 只取latest_date日的数据
        # stock_df = d.get_realtime_data(start_time = "2025-08-14" + " 09:30:00") # chen for test
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        # time列应该已经包含日期和时间信息，确保其为datetime类型
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
       
        # 计算每分钟涨幅change
        stock_df['change'] = ((stock_df['close']- stock_df['pre_close'])/ stock_df['pre_close'] *100).round(2) # 计算每分钟的涨幅
        # 获取change大于change_value的行
        stock_df = stock_df[stock_df['change'] > change_value]

        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        stock_df['time_str'] = stock_df['time'].dt.strftime('%m%d_%H:%M')
        
        # 对每分钟groupby, 获取每分钟对应的id list,做成一个时间，id list的map
        time_id_map = stock_df.groupby('time_str')['id'].apply(list).to_dict()
        # 运用sector_id_map，获取每分钟对应的板块名称出现的次数
        sector_count_map = {}
        for time_str, id_list in time_id_map.items():
            sector_count_map[time_str] = {}
            for sector_name, sector_ids in sector_id_map.items():
                count = len(set(id_list) & set(sector_ids))
                sector_count_map[time_str][sector_name] = count
        # 将sector_count_map转换为DataFrame
        sector_count_df = pd.DataFrame.from_dict(sector_count_map, orient='index').reset_index()
        sector_count_df.columns = ['time_str'] + list(sector_count_df.columns[1:])

        # 只对数值列进行过滤，排除time_str列
        numeric_columns = [col for col in sector_count_df.columns if col != 'time_str']
        # 找出至少有一个值大于10的板块列
        columns_to_keep = ['time_str']  # 始终保留时间列
        for col in numeric_columns:
            if (sector_count_df[col] > 10).any():
                columns_to_keep.append(col)
        
        sector_count_df = sector_count_df[columns_to_keep]

        # 将sector_count_df绘制为折线图数据，横轴为时间，纵轴为个数，以sector_count_df的sector_name为legend,绘制sector_count_df的折线图
        chart_data = []
        
        # 获取所有板块名称（除了time_str列）
        sector_columns = [col for col in sector_count_df.columns if col != 'time_str']
        
        # 为每个板块创建折线图数据，只显示数量大于0的板块
        for sector_col in sector_columns:
            sector_data = sector_count_df[sector_count_df[sector_col] > 0]  # 只显示有数据的时间点
            if not sector_data.empty:
                chart_data.append({
                    "name": f'{sector_col}板块突破数量',
                    "x": sector_data['time_str'].tolist(),
                    "y": sector_data[sector_col].tolist(),
                    "mode": "lines+markers",
                    "line": {"width": 2},
                    "marker": {"size": 4},
                    "showlegend": True
                })

        # 获取所有唯一的时间并按时间顺序排序，用于强制x轴顺序
        all_dates = sector_count_df['time_str'].unique()
        all_dates = sorted(all_dates)  # 直接排序时间字符串
        date_order = all_dates
            
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": f"各板块突破2%股票数量变化 - {sector_name}板块视角 ({start_date_dt.strftime('%Y-%m-%d')})",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {
                    "title": "突破股票数量",
                    "side": "left"
                },
                "legend": {"title": "板块名称"}
            }
        })

    
    def process_strong_plates_change2_factor_pkl(self):
        """各板块股票涨幅 - 支持动态板块选择和日期范围选择"""
        # 从请求参数中获取选中的板块名称和日期范围
        from flask import request
        selected_sector = request.args.get('sector', None)
        change_value = 2  # 默认值
        
        if selected_sector is None:
            # 如果没有指定板块，使用组件ID来获取默认板块名称
            component_id = request.args.get('componentId', 'default')
            if component_id == 'kpl_2sector_custom_change2_view':
                change_value = 2
            elif component_id == 'kpl_2sector_custom_change5_view':
                change_value = 5

            
        start_date = request.args.get('startDate', '2025-07-01')  # 默认开始日期
        end_date = request.args.get('endDate', None)  # 默认结束日期为None，使用最新日期
        
        # 直接调用原始方法，不使用启动缓存
        # 因为启动缓存会忽略sector和日期参数，导致选择不同参数时返回相同数据
        return self._original_strong_plates_change2_factor_pkl(selected_sector, start_date, end_date, change_value)

    def _original_strong_plates_change2_factor_pkl(self, selected_sector=None, start_date='2025-07-01', end_date=None, change_value=0):
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
        temp_df = temp_df[(temp_df['trade_date'] == latest_date)]
        
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

        d = StockMinuteData()
        stock_df = d.get_realtime_data(start_time = datetime.now().strftime("%Y-%m-%d") + " 09:30:00") # 只取latest_date日的数据
        stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'], errors='coerce')
        # time列应该已经包含日期和时间信息，确保其为datetime类型
        stock_df['time'] = pd.to_datetime(stock_df['time'], errors='coerce')
        # 去除09:25之前的数据
        # stock_df = stock_df[stock_df['time'].dt.strftime('%H:%M') >= '09:30']
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
        
        # stock_df = get_latest_stock_name_from_stock_id(stock_df)
        stock_df = stock_df.merge(self.stock_name_df[['id', 'stock_name']], on='id', how='left')
        # stock_df['date_str'] = stock_df['trade_date'].dt.strftime('%m/%d')
        
        # 获取所有唯一的日期并按时间顺序排序，用于强制x轴顺序
        all_dates = stock_df['time'].unique()
        all_dates = sorted(pd.to_datetime(all_dates))
        date_order = [date.strftime('%m%d_%H:%M') for date in all_dates]

        # 一次性计算所有股票的因子标记，避免重复计算
        # 为每只股票标记是否满足因子条件
        stock_df['is_factor_2_positive'] = stock_df['change'] > 2
        stock_df['is_factor_2_negative'] = stock_df['change'] < -2
        stock_df['is_factor_9_7'] = stock_df['change'] > 9.7
        
        # 创建股票到板块的映射展开表
        stock_sector_list = []
        for sector_name, stock_ids in sector_id_map.items():
            for stock_id in stock_ids:
                stock_sector_list.append({'id': stock_id, 'sector_name': sector_name})
        
        stock_sector_df = pd.DataFrame(stock_sector_list)
        
        # 将股票数据与板块信息合并
        stock_with_sector = stock_df.merge(stock_sector_df, on='id', how='inner')
        
        # 一次性按时间和板块聚合所有因子
        sector_time_factors = stock_with_sector.groupby(['sector_name', 'time_str']).agg({
            'is_factor_2_positive': 'sum',
            'is_factor_2_negative': 'sum', 
            'is_factor_9_7': 'sum',
            'id': 'count'  # 统计该板块在该时间点的股票数量
        }).reset_index()
        
        # 计算factor_2 = positive - negative
        sector_time_factors['factor_2'] = sector_time_factors['is_factor_2_positive'] - sector_time_factors['is_factor_2_negative']
        # 取factor_2的5均值
        # sector_time_factors['factor_2'] = sector_time_factors.groupby('sector_name')['factor_2'].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
        sector_time_factors['factor_9_7'] = sector_time_factors['is_factor_9_7']
        
        # 为每个板块计算最大factor_2值
        sector_max_factors = sector_time_factors.groupby('sector_name')['factor_2'].max().to_dict()
        
        chart_data = []
        
        # 现在循环中只进行判断和数据组装
        for sector_name in sector_names:
            
            # 检查该板块是否有因子数据
            if sector_name not in sector_max_factors:
                continue
                
            # 如果所有的change都小于等于10，则不绘制该板块的因子线条
            if sector_max_factors[sector_name] <= 10:
                continue
                
            # 获取该板块的时间序列因子数据
            sector_data = sector_time_factors[sector_time_factors['sector_name'] == sector_name].sort_values('time_str')
            
            if sector_data.empty:
                continue
            
            # 添加因子2的线条
            chart_data.append({
                "x": sector_data['time_str'].tolist(),
                "y": sector_data['factor_2'].tolist(),
                "mode": "lines+markers+text",
                "line": {"width": 2},
                "marker": {"size": 2},
                "text": sector_data['factor_9_7'].tolist(),  # 在factor_2点上显示factor_9_7的值
                "textposition": "top center",
                "textfont": {"size": 10, "color": "blue"},
                "name": f"{sector_name}",
                # "yaxis": "y2",  # 使用右侧Y轴
                "showlegend": True
            })
            
            
            # # 添加因子9.7的线条
            # chart_data.append({
            #     "x": factor_data['time_str'].tolist(),
            #     "y": factor_data['factor_9_7'].tolist(),
            #     "mode": "lines+markers",
            #     "line": {"width": 2, "color": "orange"},
            #     "marker": {"size": 2},
            #     "name": "强势股因子(>9.7%数量)",
            #     # "yaxis": "y2",  # 使用右侧Y轴
            #     "showlegend": True
            # })
        
            
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": f"板块内股票分钟涨幅_diff + 市场因子 - {sector_name} ",
                "xaxis": {
                    "title": "时间",
                    "type": "category",
                    "categoryorder": "array",
                    "categoryarray": date_order
                },
                "yaxis": {
                    "title": "涨幅因子(%)",
                    "side": "left"
                },
                # "yaxis2": {
                #     "title": "因子数量",
                #     "side": "right",
                #     "overlaying": "y",
                #     "showgrid": False
                # },
                "legend": {"title": "指标名称"}
            },
            "sectorInfo": {
                "currentSector": sector_name,
                "availableSectors": sector_names,
                "sectorCount": len(sector_names)
            },
            
        })

    def process(self, method_name: str, *args, **kwargs):
        """处理数据请求的统一入口方法"""
        try:
            # 获取原始方法名（移除process_前缀）
            original_method = method_name.replace('process_', '') if method_name.startswith('process_') else method_name
            
            # 查找对应的方法
            method_to_call = None
            for attr_name in dir(self):
                if not attr_name.startswith('_') and attr_name != 'process':
                    if attr_name == f"process_{original_method}" or attr_name == original_method:
                        method_to_call = getattr(self, attr_name)
                        break
            
            if method_to_call and callable(method_to_call):
                return method_to_call(*args, **kwargs)
            else:
                return self.error_response(f"未找到方法: {method_name}")
                
        except Exception as e:
            return self.error_response(f"处理请求时发生错误: {str(e)}")

    def config(self):
        """获取处理器配置信息"""
        try:
            available_methods = self.get_available_methods()
            return jsonify({
                "processor_name": self.__class__.__name__,
                "available_methods": available_methods,
                "description": "自动生成的数据处理器",
                "version": "1.0.0"
            })
        except Exception as e:
            return self.error_response(f"获取配置信息失败: {str(e)}")

    def get_available_methods(self):
        """获取所有可用的处理方法"""
        try:
            methods = []
            for attr_name in dir(self):
                if not attr_name.startswith('_') and attr_name not in ['process', 'config', 'get_available_methods', 'error_response']:
                    attr = getattr(self, attr_name)
                    if callable(attr):
                        methods.append(attr_name)
            return methods
        except Exception as e:
            return []
