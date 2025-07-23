"""
强势服务器处理器
包含强势服务器的所有数据处理逻辑：强势股票、板块分析等

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


class StrongProcessor(BaseDataProcessor):
    """强势服务器专用处理器 - 统一管理所有处理逻辑"""
    
    # =========================================================================
    # 图表处理方法 (强势分析特有)
    # =========================================================================
    
    def process_strong_sector_chart(self):
        """强势板块图表"""
        try:
            self.logger.info("开始处理强势板块图表")
            
            plate_df = self.data_cache.load_data('plate_df')
            if plate_df.empty:
                return jsonify({
                    "chartType": "line",
                    "data": [],
                    "layout": {
                        "title": "强势板块分析",
                        "xaxis": {"title": "时间"},
                        "yaxis": {"title": "强势指标"},
                        "legend": {"title": "板块名称"}
                    },
                    "message": "板块数据文件读取失败"
                })
            
            # 数据预处理
            plate_df['时间'] = pd.to_datetime(plate_df['时间'])
            latest_time = plate_df['时间'].max()
            plate_df = plate_df[plate_df['时间'].dt.date == latest_time.date()]
            
            # 构建用于哈希比较的源数据
            source_data = {
                'data_time': str(latest_time),
                'data_count': len(plate_df),
                'strong_criteria': 'turnover_ratio_threshold',  # 强势判断标准
                'file_timestamp': self.data_cache.timestamps.get('plate_df', 0)
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/chart-data/strong_sector_chart'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, None, source_data)
            
            if should_cache and cached_response:
                self.logger.info("使用缓存数据返回强势板块图表")
                return cached_response
            
            # 强势板块筛选逻辑
            if '强势分时换手占比' in plate_df.columns and '板块涨幅' in plate_df.columns:
                # 强势条件: 强势分时换手占比 > 30% 且 板块涨幅 > 2%
                strong_sectors = plate_df[
                    (plate_df['强势分时换手占比'] > 30) & 
                    (plate_df['板块涨幅'] > 2)
                ].sort_values(by='强势分时换手占比', ascending=False).head(10)
                
                chart_data = []
                
                if not strong_sectors.empty:
                    for _, sector in strong_sectors.iterrows():
                        sector_name = sector['板块名']
                        
                        # 获取该板块的时间序列数据
                        sector_time_data = plate_df[plate_df['板块名'] == sector_name].sort_values(by='时间')
                        
                        chart_data.append({
                            "name": f'{sector_name}强势指标',
                            "x": sector_time_data['时间'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                            "y": sector_time_data['强势分时换手占比'].tolist()
                        })
            else:
                chart_data = []
            
            # 构建响应数据
            response_data = jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "强势板块分析",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "强势分时换手占比(%)"},
                    "legend": {"title": "板块名称"}
                }
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, None, source_data, response_data)
            
            self.logger.info(f"强势板块图表计算完成，生成 {len(chart_data)} 个板块的数据")
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取强势板块图表失败: {e}")

    def process_strong_stock_momentum_chart(self):
        """强势股票动量图表"""
        try:
            self.logger.info("开始处理强势股票动量图表")
            
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "chartType": "scatter",
                    "data": [],
                    "layout": {
                        "title": "强势股票动量分析",
                        "xaxis": {"title": "涨跌幅(%)"},
                        "yaxis": {"title": "成交量"},
                        "legend": {"title": "股票"}
                    },
                    "message": "股票数据文件读取失败"
                })
            
            # 强势股票筛选: 涨幅 > 5% 且有足够的成交量
            if 'change' in stock_df.columns:
                strong_stocks = stock_df[stock_df['change'] > 5].head(20)
                
                if not strong_stocks.empty and 'volume' in strong_stocks.columns:
                    chart_data = [{
                        "name": "强势股票分布",
                        "x": strong_stocks['change'].tolist(),
                        "y": strong_stocks['volume'].tolist(),
                        "mode": "markers",
                        "type": "scatter",
                        "text": strong_stocks['name'].tolist() if 'name' in strong_stocks.columns else [],
                        "marker": {
                            "size": 8,
                            "color": strong_stocks['change'].tolist(),
                            "colorscale": "Reds",
                            "showscale": True
                        }
                    }]
                else:
                    chart_data = []
            else:
                chart_data = []
            
            return jsonify({
                "chartType": "scatter",
                "data": chart_data,
                "layout": {
                    "title": "强势股票动量分析",
                    "xaxis": {"title": "涨跌幅(%)"},
                    "yaxis": {"title": "成交量"},
                    "legend": {"title": "股票"}
                }
            })
        
        except Exception as e:
            return self.error_response(f"获取强势股票动量图表失败: {e}")

    # =========================================================================
    # 表格处理方法 (强势分析特有)
    # =========================================================================
    
    def process_strong_stocks_table(self):
        """强势股票表格数据"""
        try:
            self.logger.info("处理强势股票表格数据")
            
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "股票数据文件读取失败"
                })
            
            # 强势股票筛选条件
            strong_threshold = request.args.get('threshold', 5.0, type=float)
            
            # 构建缓存参数
            cache_params = self.build_cache_params(threshold=strong_threshold)
            
            # 构建用于哈希比较的源数据
            latest_time = stock_df['time'].max() if 'time' in stock_df.columns else None
            source_data = {
                'threshold': strong_threshold,
                'data_time': str(latest_time),
                'data_count': len(stock_df),
                'file_timestamp': self.data_cache.timestamps.get('stock_df', 0)
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/table-data/strong_stocks'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, cache_params, source_data)
            
            if should_cache and cached_response:
                self.logger.info(f"使用缓存数据返回强势股票表格: 阈值{strong_threshold}%")
                return cached_response
            
            # 筛选强势股票
            if 'change' in stock_df.columns:
                strong_stocks = stock_df[stock_df['change'] >= strong_threshold].sort_values(
                    by='change', ascending=False
                ).head(50)
            else:
                strong_stocks = stock_df.head(50)
            
            # 定义表格列
            columns = [
                {"field": "name", "header": "股票名称"},
                {"field": "change", "header": "涨跌幅", "backgroundColor": "redGreen"},
                {"field": "price", "header": "现价"} if "price" in strong_stocks.columns else None,
                {"field": "volume", "header": "成交量"} if "volume" in strong_stocks.columns else None,
                {"field": "turnover", "header": "换手率"} if "turnover" in strong_stocks.columns else None,
                {"field": "Sector", "header": "所属板块"},
                {"field": "强势评分", "header": "强势评分", "backgroundColor": "redGreen"}
            ]
            
            # 过滤掉None列
            columns = [col for col in columns if col is not None]
            
            rows = []
            for _, row in strong_stocks.iterrows():
                row_data = {}
                for col in columns:
                    field = col["field"]
                    
                    if field == "强势评分":
                        # 计算强势评分 (简化公式)
                        change = row.get('change', 0)
                        volume = row.get('volume', 0)
                        score = min(100, change * 2 + (volume / 1000000) * 0.1)
                        value = round(score, 1)
                    else:
                        value = row.get(field, '')
                        if isinstance(value, (float, np.float64, np.float32)):
                            value = round(value, 2)
                    
                    row_data[field] = value
                rows.append(row_data)
            
            # 构建响应数据
            response_data = jsonify({
                "columns": columns,
                "rows": rows
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, cache_params, source_data, response_data)
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取强势股票表格失败: {e}")

    def process_strong_sectors_table(self):
        """强势板块表格数据"""
        try:
            self.logger.info("处理强势板块表格数据")
            
            plate_df = self.data_cache.load_data('plate_df')
            if plate_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "板块数据文件读取失败"
                })
            
            # 获取最新数据
            plate_df['时间'] = pd.to_datetime(plate_df['时间'])
            latest_time = plate_df['时间'].max()
            latest_data = plate_df[plate_df['时间'] == latest_time]
            
            # 强势板块筛选
            if '强势分时换手占比' in latest_data.columns and '板块涨幅' in latest_data.columns:
                strong_sectors = latest_data[
                    (latest_data['强势分时换手占比'] > 20) | 
                    (latest_data['板块涨幅'] > 3)
                ].sort_values(by='强势分时换手占比', ascending=False).head(30)
            else:
                strong_sectors = latest_data.head(30)
            
            # 定义表格列
            columns = [
                {"field": "板块名", "header": "板块名称"},
                {"field": "板块涨幅", "header": "板块涨幅", "backgroundColor": "redGreen"},
                {"field": "强势分时换手占比", "header": "强势换手占比", "backgroundColor": "redGreen"},
                {"field": "板块5分涨速", "header": "5分涨速", "backgroundColor": "redGreen"},
                {"field": "板块量比", "header": "量比", "backgroundColor": "redGreen"},
                {"field": "涨幅分布", "header": "涨幅分布"},
                {"field": "涨停梯度", "header": "涨停梯度"}
            ]
            
            # 过滤有效列
            valid_columns = [col for col in columns if col["field"] in strong_sectors.columns]
            
            rows = []
            for _, row in strong_sectors.iterrows():
                row_data = {}
                for col in valid_columns:
                    field = col["field"]
                    value = row.get(field, '')
                    if isinstance(value, (float, np.float64, np.float32)):
                        value = round(value, 2)
                    row_data[field] = value
                rows.append(row_data)
            
            return jsonify({
                "columns": valid_columns,
                "rows": rows
            })
        
        except Exception as e:
            return self.error_response(f"获取强势板块表格失败: {e}")

    # =========================================================================
    # 强势分析专用方法
    # =========================================================================
    
    def process_momentum_analysis(self):
        """动量分析数据"""
        try:
            self.logger.info("处理动量分析数据")
            
            stock_df = self.data_cache.load_data('stock_df')
            stock_minute_df = self.data_cache.load_data('stock_minute_df')
            
            if stock_df.empty:
                return self.error_response("股票数据文件读取失败")
            
            # 动量分析逻辑
            momentum_data = {
                "strong_count": len(stock_df[stock_df['change'] > 5]) if 'change' in stock_df.columns else 0,
                "moderate_count": len(stock_df[(stock_df['change'] > 2) & (stock_df['change'] <= 5)]) if 'change' in stock_df.columns else 0,
                "weak_count": len(stock_df[(stock_df['change'] > 0) & (stock_df['change'] <= 2)]) if 'change' in stock_df.columns else 0,
                "decline_count": len(stock_df[stock_df['change'] < 0]) if 'change' in stock_df.columns else 0,
                "total_stocks": len(stock_df),
                "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "market_sentiment": "强势" if len(stock_df[stock_df['change'] > 5]) / len(stock_df) > 0.1 else "一般"
            }
            
            return jsonify({
                "momentum": momentum_data,
                "status": "success"
            })
        
        except Exception as e:
            return self.error_response(f"动量分析失败: {e}")

    def process_strength_ranking(self):
        """强势排行榜"""
        try:
            self.logger.info("处理强势排行榜")
            
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return self.error_response("股票数据文件读取失败")
            
            # 计算强势排行 (按涨幅排序)
            if 'change' in stock_df.columns:
                ranking = stock_df.sort_values(by='change', ascending=False).head(20)
                
                ranking_data = []
                for rank, (_, stock) in enumerate(ranking.iterrows(), 1):
                    ranking_data.append({
                        "rank": rank,
                        "name": stock.get('name', ''),
                        "change": round(stock.get('change', 0), 2),
                        "price": round(stock.get('price', 0), 2) if 'price' in stock else None,
                        "sector": stock.get('Sector', ''),
                        "volume": stock.get('volume', 0) if 'volume' in stock else None
                    })
            else:
                ranking_data = []
            
            return jsonify({
                "ranking": ranking_data,
                "status": "success"
            })
        
        except Exception as e:
            return self.error_response(f"强势排行榜获取失败: {e}")

    # =========================================================================
    # 统一处理入口
    # =========================================================================
    
    def process(self, method_name: str):
        """
        统一处理入口
        
        Args:
            method_name: 方法名称，如 'strong_sector_chart'、'strong_stocks_table' 等
            
        Returns:
            处理结果
        """
        # 添加 process_ 前缀
        full_method_name = f'process_{method_name}'
        
        if hasattr(self, full_method_name):
            method = getattr(self, full_method_name)
            self.logger.info(f"强势处理器执行方法: {full_method_name}")
            return method()
        else:
            available_methods = [method.replace('process_', '') for method in dir(self) 
                               if method.startswith('process_') and callable(getattr(self, method))]
            
            return self.error_response(
                f"强势处理器不支持方法: {method_name}。"
                f"可用方法: {', '.join(available_methods)}"
            )
    
    def get_available_methods(self):
        """获取所有可用的处理方法"""
        methods = [method.replace('process_', '') for method in dir(self) 
                   if method.startswith('process_') and callable(getattr(self, method))]
        return sorted(methods)
