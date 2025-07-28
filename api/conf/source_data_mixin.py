"""
源数据逻辑混入类 - 为MultiPlateStockServer提供各组件的源数据获取逻辑
Author: chenlei
Date: 2025-07-22
"""

import pandas as pd
from typing import Dict, Any


class SourceDataLogicMixin:
    """源数据逻辑混入类"""
    
    def _sector_line_chart_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """板块折线图的源数据逻辑（涨幅、涨停、红盘率等）"""
        sector_df = self.data_cache.load_data('plate_df')
        latest_time = sector_df['时间'].max() if not sector_df.empty else None
        
        return {
            'endpoint': endpoint,
            'data_time': str(latest_time),
            'data_count': len(sector_df),
            'sector_names': sorted(self._get_dynamic_titles_list()),
            'dynamic_titles': self.dynamic_titles.copy(),
            'file_timestamp': self.data_cache.timestamps.get('plate_df', 0),
            'request_params': request_params
        }
    
    def _sector_speed_chart_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """板块涨速累加图表的源数据逻辑"""
        plate_df = self.data_cache.load_data('plate_df')
        stock_minute_df = self.data_cache.load_data('stock_minute_df')
        
        latest_plate_time = plate_df['时间'].max() if not plate_df.empty else None
        latest_minute_time = stock_minute_df['time'].max() if not stock_minute_df.empty else None
        
        return {
            'endpoint': endpoint,
            'plate_data_time': str(latest_plate_time),
            'minute_data_time': str(latest_minute_time),
            'plate_data_count': len(plate_df),
            'minute_data_count': len(stock_minute_df),
            'file_timestamps': {
                'plate_df': self.data_cache.timestamps.get('plate_df', 0),
                'stock_minute_df': self.data_cache.timestamps.get('stock_minute_df', 0)
            },
            'request_params': request_params
        }
    
    def _plate_info_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """板块概要数据表的源数据逻辑"""
        sector_name = request_params.get('sectors', '航运概念')
        plate_df = self.data_cache.load_data('plate_df')
        latest_time = plate_df['时间'].max() if not plate_df.empty else None
        
        return {
            'endpoint': endpoint,
            'sector_name': sector_name,
            'data_time': str(latest_time),
            'data_count': len(plate_df),
            'plate_summary': plate_df[['板块名', '板块涨幅', '板块5分涨速']].to_dict('records')[:10] if not plate_df.empty else [],
            'request_params': request_params
        }
    
    def _stocks_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """股票数据表的源数据逻辑"""
        sector_name = request_params.get('sector_name', request_params.get('sectors', '航运概念'))
        component_id = request_params.get('componentId', 'table2')
        
        stock_df = self.data_cache.load_data('stock_df')
        affinity_df = self.data_cache.load_data('affinity_df')
        
        latest_time = stock_df['time'].max() if not stock_df.empty else None
        
        # 获取相关股票ID作为源数据的一部分
        sector_stock_ids = []
        if not affinity_df.empty:
            sector_affinity_df = affinity_df[
                affinity_df['板块'].str.contains(sector_name, na=False, case=False) |
                affinity_df['板块'].apply(lambda x: sector_name in str(x) if pd.notna(x) else False)
            ]
            sector_stock_ids = sorted(sector_affinity_df['股票id'].tolist()) if not sector_affinity_df.empty else []
        
        return {
            'endpoint': endpoint,
            'sector_name': sector_name,
            'component_id': component_id,
            'stock_data_time': str(latest_time),
            'stock_count': len(stock_df),
            'sector_stock_ids': sector_stock_ids[:50],  # 限制数量以避免哈希过大
            'dynamic_titles': self.dynamic_titles.copy(),
            'request_params': request_params
        }
    
    def _up_limit_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """涨停数据表的源数据逻辑"""
        up_limit_df = self.data_cache.load_data('up_limit_df')
        
        return {
            'endpoint': endpoint,
            'data_count': len(up_limit_df),
            'file_timestamp': self.data_cache.timestamps.get('up_limit_df', 0),
            'data_sample': up_limit_df.head(5).to_dict('records') if not up_limit_df.empty else [],
            'request_params': request_params
        }
    
    def _plate_sector_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """板块连板数分布的源数据逻辑"""
        stock_all_level_df = self.data_cache.load_data('stock_all_level_df')
        
        return {
            'endpoint': endpoint,
            'data_count': len(stock_all_level_df),
            'file_timestamp': self.data_cache.timestamps.get('stock_all_level_df', 0),
            'data_sample': stock_all_level_df.head(5).to_dict('records') if not stock_all_level_df.empty else [],
            'request_params': request_params
        }
    
    def _stacked_area_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """堆叠面积图的源数据逻辑"""
        plate_df = self.data_cache.load_data('plate_df')
        latest_time = plate_df['时间'].max() if not plate_df.empty else None
        
        return {
            'endpoint': endpoint,
            'data_time': str(latest_time),
            'data_count': len(plate_df),
            'file_timestamp': self.data_cache.timestamps.get('plate_df', 0),
            'request_params': request_params
        }
