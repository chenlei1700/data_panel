"""
演示服务器处理器
包含演示服务器的所有数据处理逻辑

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


class DemoProcessor(BaseDataProcessor):
    """演示服务器专用处理器 - 统一管理所有处理逻辑"""
    
    # =========================================================================
    # 图表处理方法
    # =========================================================================
    
    def process_demo_line_chart(self):
        """演示折线图数据"""
        try:
            self.logger.info("处理演示折线图数据")
            
            # 演示服务器通常使用简化的数据处理
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "chartType": "line",
                    "data": [],
                    "layout": {
                        "title": "演示折线图",
                        "xaxis": {"title": "时间"},
                        "yaxis": {"title": "数值"},
                        "legend": {"title": "系列"}
                    },
                    "message": "股票数据文件读取失败"
                })
            
            # 构建用于哈希比较的源数据
            latest_time = stock_df['time'].max() if 'time' in stock_df.columns else None
            source_data = {
                'data_time': str(latest_time),
                'data_count': len(stock_df),
                'file_timestamp': self.data_cache.timestamps.get('stock_df', 0)
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/chart-data/demo_line_chart'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, None, source_data)
            
            if should_cache and cached_response:
                self.logger.info("使用缓存数据返回演示折线图")
                return cached_response
            
            # 简化的演示数据处理
            sample_data = stock_df.head(10) if not stock_df.empty else pd.DataFrame()
            
            chart_data = []
            if not sample_data.empty and 'name' in sample_data.columns and 'change' in sample_data.columns:
                chart_data.append({
                    "name": "股票涨跌幅示例",
                    "x": sample_data['name'].tolist(),
                    "y": sample_data['change'].tolist()
                })
            
            # 构建响应数据
            response_data = jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "演示折线图",
                    "xaxis": {"title": "股票名称"},
                    "yaxis": {"title": "涨跌幅(%)"},
                    "legend": {"title": "数据系列"}
                }
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, None, source_data, response_data)
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取演示折线图数据失败: {e}")

    def process_demo_bar_chart(self):
        """演示柱状图数据"""
        try:
            self.logger.info("处理演示柱状图数据")
            
            plate_df = self.data_cache.load_data('plate_df')
            if plate_df.empty:
                return jsonify({
                    "chartType": "bar",
                    "data": [],
                    "layout": {
                        "title": "演示柱状图",
                        "xaxis": {"title": "类别"},
                        "yaxis": {"title": "数值"},
                        "legend": {"title": "系列"}
                    },
                    "message": "板块数据文件读取失败"
                })
            
            # 简化的演示数据处理
            if '板块名' in plate_df.columns and '板块涨幅' in plate_df.columns:
                sample_data = plate_df.head(10)
                
                chart_data = [{
                    "name": "板块涨幅示例",
                    "x": sample_data['板块名'].tolist(),
                    "y": sample_data['板块涨幅'].tolist(),
                    "type": "bar"
                }]
            else:
                chart_data = []
            
            return jsonify({
                "chartType": "bar",
                "data": chart_data,
                "layout": {
                    "title": "演示柱状图",
                    "xaxis": {"title": "板块名称"},
                    "yaxis": {"title": "涨幅(%)"},
                    "legend": {"title": "数据系列"}
                }
            })
        
        except Exception as e:
            return self.error_response(f"获取演示柱状图数据失败: {e}")

    # =========================================================================
    # 表格处理方法
    # =========================================================================
    
    def process_demo_table_data(self):
        """演示表格数据"""
        try:
            self.logger.info("处理演示表格数据")
            
            stock_df = self.data_cache.load_data('stock_df')
            if stock_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "股票数据文件读取失败"
                })
            
            # 简化的表格数据处理
            sample_data = stock_df.head(20)
            
            # 定义演示表格列
            columns = [
                {"field": "name", "header": "股票名称"},
                {"field": "change", "header": "涨跌幅", "backgroundColor": "redGreen"},
                {"field": "price", "header": "价格"} if "price" in sample_data.columns else None,
                {"field": "volume", "header": "成交量"} if "volume" in sample_data.columns else None
            ]
            
            # 过滤掉None列
            columns = [col for col in columns if col is not None]
            
            rows = []
            for _, row in sample_data.iterrows():
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
            return self.error_response(f"获取演示表格数据失败: {e}")

    # =========================================================================
    # 基础数据处理方法
    # =========================================================================
    
    def process_demo_summary(self):
        """演示汇总数据"""
        try:
            self.logger.info("处理演示汇总数据")
            
            stock_df = self.data_cache.load_data('stock_df')
            plate_df = self.data_cache.load_data('plate_df')
            
            summary = {
                "stock_count": len(stock_df) if not stock_df.empty else 0,
                "plate_count": len(plate_df) if not plate_df.empty else 0,
                "data_status": "正常" if not stock_df.empty and not plate_df.empty else "数据不完整",
                "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return jsonify({
                "summary": summary,
                "status": "success"
            })
        
        except Exception as e:
            return self.error_response(f"获取演示汇总数据失败: {e}")

    def process_demo_config(self):
        """演示配置数据"""
        try:
            # 返回演示服务器的配置信息
            config = {
                "server_type": "demo",
                "features": [
                    "基础图表展示",
                    "简化数据表格",
                    "配置管理示例"
                ],
                "data_sources": [
                    "stock_df",
                    "plate_df"
                ],
                "refresh_interval": 30,  # 秒
                "max_records": 100
            }
            
            return jsonify({
                "config": config,
                "status": "success"
            })
        
        except Exception as e:
            return self.error_response(f"获取演示配置失败: {e}")

    # =========================================================================
    # 统一处理入口
    # =========================================================================
    
    def process(self, method_name: str):
        """
        统一处理入口
        
        Args:
            method_name: 方法名称，如 'demo_line_chart'、'demo_table_data' 等
            
        Returns:
            处理结果
        """
        # 添加 process_ 前缀
        full_method_name = f'process_{method_name}'
        
        if hasattr(self, full_method_name):
            method = getattr(self, full_method_name)
            self.logger.info(f"演示处理器执行方法: {full_method_name}")
            return method()
        else:
            available_methods = [method.replace('process_', '') for method in dir(self) 
                               if method.startswith('process_') and callable(getattr(self, method))]
            
            return self.error_response(
                f"演示处理器不支持方法: {method_name}。"
                f"可用方法: {', '.join(available_methods)}"
            )
    
    def get_available_methods(self):
        """获取所有可用的处理方法"""
        methods = [method.replace('process_', '') for method in dir(self) 
                   if method.startswith('process_') and callable(getattr(self, method))]
        return sorted(methods)
