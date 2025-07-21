#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用BaseStockServer防重复缓存机制的示例

这个示例展示了如何在继承BaseStockServer的子类中使用防重复缓存机制
"""

from base_server import BaseStockServer, BaseDataCache, BaseResponseCache
from flask import request, jsonify
import pandas as pd
import time
import os
from typing import Dict, Any


class ExampleDataCache(BaseDataCache):
    """示例数据缓存类 - 继承自BaseDataCache"""
    
    def load_data(self, key: str):
        """加载数据，可以从文件、数据库等加载"""
        if key == 'plate_df':
            # 模拟从文件加载板块数据
            if key not in self.cache:
                # 模拟数据加载
                self.cache[key] = pd.DataFrame({
                    '板块名': ['科技板块', '医药板块', '新能源'],
                    '板块涨幅': [2.5, -1.2, 3.8],
                    '时间': pd.to_datetime(['2025-01-21 09:30', '2025-01-21 09:30', '2025-01-21 09:30'])
                })
                self.timestamps[key] = time.time()
                print(f"从文件加载数据: {key}")
        
        return self.cache.get(key, pd.DataFrame())


class ExampleStockServer(BaseStockServer):
    """示例股票服务器 - 展示如何使用防重复缓存机制"""
    
    def __init__(self, port=5009):
        super().__init__(port=port, name="示例股票仪表盘")
        
        # 使用自定义数据缓存
        self.data_cache = ExampleDataCache()
        
    def get_dashboard_config(self):
        """获取仪表盘配置"""
        return {
            "layout": {
                "rows": 2,
                "cols": 2,
                "components": [
                    {
                        "id": "table1",
                        "type": "table",
                        "dataSource": "/api/table-data/plate_info",
                        "title": "板块信息表",
                        "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 2}
                    },
                    {
                        "id": "chart1", 
                        "type": "chart",
                        "dataSource": "/api/chart-data/sector_trend",
                        "title": "板块趋势图",
                        "position": {"row": 1, "col": 0, "rowSpan": 1, "colSpan": 2}
                    }
                ]
            }
        }
    
    def get_data_sources(self):
        """获取数据源配置"""
        return {
            "/api/table-data/plate_info": {
                "handler": "get_plate_info_table_data",
                "description": "板块信息数据表",
                "cache_ttl": 60  # 60秒缓存，启用防重复机制
            },
            "/api/chart-data/sector_trend": {
                "handler": "get_sector_trend_chart",
                "description": "板块趋势图表数据", 
                "cache_ttl": 30  # 30秒缓存
            }
        }
    
    def get_cache_observables(self):
        """定义需要观察的数据源"""
        return {
            # 针对板块数据表的观察配置
            "/api/table-data/plate_info": {
                "data_keys": ["plate_df_timestamp", "data_count", "latest_time"],
                "params_keys": ["sector_name", "limit"]
            },
            # 针对图表数据的观察配置
            "/api/chart-data/sector_trend": {
                "data_keys": ["plate_df_timestamp", "chart_type"],
                "params_keys": ["sector_name", "time_range"]
            }
        }
    
    def _get_source_data_for_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """重写源数据获取方法，提供更精确的源数据"""
        if "plate_info" in endpoint:
            # 针对板块信息表的源数据
            plate_df = self.data_cache.load_data('plate_df')
            return {
                "endpoint": endpoint,
                "plate_df_timestamp": self.data_cache.timestamps.get('plate_df', 0),
                "data_count": len(plate_df),
                "latest_time": str(plate_df['时间'].max()) if not plate_df.empty else "",
                "sector_names": plate_df['板块名'].tolist() if not plate_df.empty else [],
                "request_params": dict(request.args) if hasattr(request, 'args') else {}
            }
        elif "sector_trend" in endpoint:
            # 针对趋势图的源数据
            plate_df = self.data_cache.load_data('plate_df')
            return {
                "endpoint": endpoint,
                "plate_df_timestamp": self.data_cache.timestamps.get('plate_df', 0),
                "chart_type": "line",
                "data_summary": plate_df.describe().to_dict() if not plate_df.empty else {},
                "request_params": dict(request.args) if hasattr(request, 'args') else {}
            }
        
        # 默认源数据
        return super()._get_source_data_for_endpoint(endpoint)
    
    # === 数据处理方法（这些方法会自动使用缓存保护机制）===
    
    def get_plate_info_table_data(self):
        """获取板块信息表数据 - 会自动使用缓存保护"""
        try:
            print("🔄 执行板块信息数据处理...")
            
            # 模拟耗时操作
            time.sleep(0.1)  # 模拟数据处理延迟
            
            plate_df = self.data_cache.load_data('plate_df')
            
            if plate_df.empty:
                return jsonify({
                    "columns": [],
                    "rows": [],
                    "message": "板块数据文件读取失败"
                })
            
            # 处理数据
            columns = [
                {"field": "板块名", "header": "板块名称"},
                {"field": "板块涨幅", "header": "涨跌幅(%)", "backgroundColor": "redGreen"},
                {"field": "时间", "header": "更新时间"}
            ]
            
            rows = []
            for _, row_data in plate_df.iterrows():
                row = {
                    "板块名": row_data["板块名"],
                    "板块涨幅": round(row_data["板块涨幅"], 2),
                    "时间": row_data["时间"].strftime("%H:%M:%S")
                }
                rows.append(row)
            
            print("✅ 板块信息数据处理完成")
            return jsonify({
                "columns": columns,
                "rows": rows
            })
            
        except Exception as e:
            self.logger.error(f"获取板块信息失败: {e}")
            return jsonify({"error": str(e)}), 500
    
    def get_sector_trend_chart(self):
        """获取板块趋势图数据 - 会自动使用缓存保护"""
        try:
            print("🔄 执行板块趋势图数据处理...")
            
            # 模拟耗时操作
            time.sleep(0.2)  # 模拟图表数据处理延迟
            
            plate_df = self.data_cache.load_data('plate_df')
            
            if plate_df.empty:
                return jsonify({"error": "板块数据文件读取失败"}), 500
            
            # 构建图表数据
            chart_data = []
            for _, row in plate_df.iterrows():
                chart_data.append({
                    "name": f"{row['板块名']}涨幅",
                    "x": [row['时间'].strftime("%H:%M")],
                    "y": [row['板块涨幅']]
                })
            
            print("✅ 板块趋势图数据处理完成")
            return jsonify({
                "chartType": "line",
                "data": chart_data,
                "layout": {
                    "title": "板块涨幅趋势",
                    "xaxis": {"title": "时间"},
                    "yaxis": {"title": "涨幅(%)"}
                }
            })
            
        except Exception as e:
            self.logger.error(f"获取板块趋势图失败: {e}")
            return jsonify({"error": str(e)}), 500


def main():
    """主函数"""
    print("🚀 启动示例股票仪表盘服务器（带缓存防重复机制）...")
    
    server = ExampleStockServer(port=5009)
    
    print("""
    ===== 使用说明 =====
    
    1. 访问 http://localhost:5009/api/dashboard-config 查看配置
    2. 访问 http://localhost:5009/api/table-data/plate_info 获取板块数据（会被缓存）
    3. 访问 http://localhost:5009/api/chart-data/sector_trend 获取图表数据（会被缓存）
    4. 访问 http://localhost:5009/api/cache/status 查看缓存状态
    5. 访问 http://localhost:5009/api/cache/clear 清理缓存
    
    多次访问相同API，第二次及以后的请求会使用缓存数据，避免重复计算！
    
    ====================
    """)
    
    server.run(debug=True)


if __name__ == '__main__':
    main()
