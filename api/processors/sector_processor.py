"""
板块数据处理器
负责处理板块相关的特殊数据处理逻辑，如连板分布等
"""
import pandas as pd
import numpy as np
from flask import jsonify
from .base_processor import BaseDataProcessor


class SectorDataProcessor(BaseDataProcessor):
    """板块数据处理器"""
    
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
        """返回板块资金流向堆叠面积图数据"""
        try:
            # 这里可以实现板块资金流向的具体逻辑
            # 目前返回空数据作为示例
            return jsonify({
                "stackedAreaData": {
                    "data": {},
                    "keyOrder": [],
                    "colors": []
                },
                "xAxisValues": [],
                "tableData": {}
            })
            
        except Exception as e:
            return self.error_response(f"获取板块资金流向数据失败: {e}")

    def process(self, sector_type: str):
        """根据板块数据类型处理数据"""
        method_map = {
            'plate_sector': self.process_today_plate_up_limit_distribution,
            'plate_sector_v2': self.process_today_plate_up_limit_distribution_v2,
            'stacked-area-sector': self.process_sector_stacked_area_data,
        }
        
        if sector_type in method_map:
            return method_map[sector_type]()
        else:
            return self.error_response(f"未知的板块数据类型: {sector_type}")
