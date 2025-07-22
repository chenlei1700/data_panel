"""
表格数据处理器
负责处理各种表格类型的数据生成逻辑
"""
import time
import pandas as pd
import numpy as np
from flask import jsonify, request
from .base_processor import BaseDataProcessor


class TableDataProcessor(BaseDataProcessor):
    """表格数据处理器"""
    
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
            sector_name = request.args.get('sector_name') or request.args.get('sectors', '航运概念')
            component_id = request.args.get('componentId', 'table2')
            
            # 构建缓存参数
            cache_params = self.build_cache_params(
                sector_name=sector_name,
                component_id=component_id
            )
            
            self.logger.info(f"API调用: componentId={component_id}, 传入的sector_name={sector_name}")
            
            # 对于table12，优先使用动态标题
            if component_id == 'table12':
                sector_name = self.server.dynamic_titles.get('table12', sector_name)
                cache_params['sector_name'] = sector_name  # 更新缓存参数
                self.logger.info(f"table12 使用动态标题中的板块: {sector_name}")
            
            # 根据组件ID获取对应板块
            if component_id in ['table2', 'table21', 'table22', 'table23', 'table24']:
                try:
                    top_sectors = self.server._get_top_sectors()
                    sector_map = {
                        'table2': 0, 'table21': 1, 'table22': 2, 'table23': 3, 'table24': 4
                    }
                    if component_id in sector_map and len(top_sectors) > sector_map[component_id]:
                        sector_name = top_sectors[sector_map[component_id]]
                        cache_params['sector_name'] = sector_name  # 更新缓存参数
                        self.logger.info(f"组件 {component_id} 使用动态板块: {sector_name}")
                except Exception as e:
                    self.logger.warning(f"获取动态板块失败，使用默认板块: {e}")
            
            self.logger.info(f"最终使用的板块名称: {sector_name}")
            
            # 读取股票数据作为数据源进行哈希比较
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
            
            # 读取板块关联数据
            affinity_df = self.data_cache.load_data('affinity_df')
            
            if affinity_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "板块关联数据文件读取失败"
                })
            
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
            
            # 构建用于哈希比较的源数据（包含影响结果的关键数据）
            source_data = {
                'sector_name': sector_name,
                'stock_data_time': str(latest_time),
                'stock_count': len(stock_df),
                'sector_stock_ids': sorted(sector_affinity_df['股票id'].tolist()),
                'dynamic_titles': self.server.dynamic_titles.copy()
            }
            
            # 检查是否可以使用缓存
            cache_endpoint = '/api/table-data/stocks'
            should_cache, cached_response = self.should_use_cache(cache_endpoint, cache_params, source_data)
            
            if should_cache and cached_response:
                self.logger.info(f"使用缓存数据返回股票表格: {sector_name}")
                return cached_response
            
            # 需要重新计算，继续执行原有逻辑
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
                        value = round(value, 2)
                    
                    row[field] = value
                
                rows.append(row)
            
            # 构建响应数据
            response_data = jsonify({
                "columns": valid_columns,
                "rows": rows,
                "sector_name": sector_name,
                "total_stocks": len(rows)
            })
            
            # 存储到缓存
            self.store_cache(cache_endpoint, cache_params, source_data, response_data)
            
            return response_data
        
        except Exception as e:
            return self.error_response(f"获取股票表格数据失败: {e}")

    def process_up_limit_table_data(self):
        """返回涨停数据表"""
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
                {"field": "板块3", "header": "板块3"},
                {"field": "板块4", "header": "板块4"},
                {"field": "板块5", "header": "板块5"},
                {"field": "10日涨停数", "header": "10日涨停数", "backgroundColor": "redGreen"},
                {"field": "连板数", "header": "连板数", "backgroundColor": "redGreen"},
                {"field": "股票ID", "header": "股票ID"},
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

    def process(self, table_type: str):
        """根据表格类型处理数据"""
        method_map = {
            'plate_info': self.process_plate_info_table_data,
            'stocks': self.process_stocks_table_data,
            'up_limit': self.process_up_limit_table_data,
        }
        
        if table_type in method_map:
            return method_map[table_type]()
        else:
            return self.error_response(f"未知的表格类型: {table_type}")
