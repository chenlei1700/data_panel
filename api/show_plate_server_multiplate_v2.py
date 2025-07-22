"""
Author: chenlei
Date: 2024-01-20
Description: 股票多板块仪表盘服务 - 基于新框架重构版本
功能: 提供多板块股票数据展示、实时涨幅分析、涨停监控等功能
"""

import time
import pandas as pd
import numpy as np
import json
import pickle
import datetime
import plotly
import plotly.graph_objects as go
import os
import sys
import queue
import hashlib
from typing import Dict, Any
from flask import request, Response, jsonify
from flask_cors import CORS

# 导入新框架基类
from base_server import BaseStockServer
from config.server_config import get_server_config, create_auto_update_config
from processors import ProcessorManager

# 导入配置驱动架构
from config.component_config_multi import ComponentManager
from config.source_data_mixin import SourceDataLogicMixin

# 将项目根目录添加到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入股票数据和策略函数
from utils.common import get_trade_date_by_offset
from stock_data.stock.stock_daily import StockDailyData
from stock_data.stock_minute import StockMinuteData
from strategy.strategy001.板块信息显示 import plot_stock_line_charts

class MultiPlateStockServer(BaseStockServer, SourceDataLogicMixin):
    """多板块股票服务器 - 继承自BaseStockServer，使用基类的缓存机制，集成配置驱动架构"""
    
    def __init__(self, port=None, auto_update_config=None):
        # 从配置文件获取服务器配置
        server_config = get_server_config("multiplate")
        
        # 使用配置文件中的端口，如果未指定则使用参数或默认值
        if port is None:
            port = server_config.get("port", 5007)
        
        # 使用配置文件中的自动更新配置，允许参数覆盖
        if auto_update_config is None:
            auto_update_config = server_config.get("auto_update_config", {})
        else:
            # 合并配置文件配置和参数配置
            file_config = server_config.get("auto_update_config", {})
            file_config.update(auto_update_config)
            auto_update_config = file_config
        
        server_name = server_config.get("name", "多板块股票仪表盘")
        
        super().__init__(port=port, name=server_name, auto_update_config=auto_update_config)
        
        # 服务特定的配置
        # data_cache已经在基类中通过get_data_cache_file_paths()初始化了
        # response_cache已经在基类中初始化了，无需重复初始化
        
        self.dynamic_titles = {
            "table2": "股票数据表",
            "table21": "股票数据表", 
            "table22": "股票数据表", 
            "table23": "股票数据表", 
            "table24": "股票数据表",
            "table12": "航运概念"
        }
        self.selected_sector = "航运概念"
        self.latest_update = {
            "sector": "航运概念",
            "componentId": "chart2", 
            "timestamp": time.time()
        }
        self.sse_clients = []
        self.message_queue = queue.Queue()
        
        # 初始化股票数据
        self._init_stock_data()
        
        # 读取自定义板块
        self.my_plate_list = self._get_my_plate()
        
        # 初始化处理器管理器
        self.processor_manager = ProcessorManager(self)
        
        # 初始化组件管理器（配置驱动架构）
        # 根据服务器类型选择对应的组件配置
        server_type = "multiplate"  # 可以从配置文件获取或作为参数传入
        self.component_manager = ComponentManager(self, server_type)
        
        # 动态创建处理方法
        self.component_manager.create_handler_methods()

    def get_data_cache_file_paths(self) -> Dict[str, str]:
        """重写基类方法，提供股票数据相关的文件路径配置"""
        return {
            'stock_df': 'strategy\\showhtml\\server\\stock_df.csv',
            'affinity_df': 'strategy\\strategy001\\data\\板块内股票同涨率_长周期.csv',
            'plate_df': 'strategy\\showhtml\\server\\good_plate_df.csv',
            'stock_minute_df': 'strategy\\showhtml\\server\\stock_minute_df.csv',
            'up_limit_df': 'strategy\\showhtml\\server\\up_limit_df.csv',
            'stock_all_level_df': 'strategy\\strategy001\\data\\all_sectors_stock_level.csv',
        }

    def _get_source_data_for_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """重写源数据获取方法，使用配置驱动的源数据逻辑"""
        # 获取请求参数
        request_params = dict(request.args) if hasattr(request, 'args') else {}
        
        # 使用组件管理器获取源数据逻辑
        source_data = self.component_manager.get_source_data_logic(endpoint, request_params)
        
        if source_data:
            return source_data
        
        # 使用基类的默认实现作为后备
        return super()._get_source_data_for_endpoint(endpoint)

    def _init_stock_data(self):
        """初始化股票数据"""
        try:
            self.stock_daily_ins = StockDailyData()
            today = datetime.datetime.now().strftime("%Y%m%d")
            today = '20250530'  # for test
            yesterday = get_trade_date_by_offset(today, 1)
            self.stock_daily_df = self.stock_daily_ins.get_daily_data(
                start_date=yesterday, end_date=yesterday
            )
            self.logger.info(f"股票数据初始化完成，获取 {len(self.stock_daily_df)} 条记录")
        except Exception as e:
            self.logger.error(f"股票数据初始化失败: {e}")
            self.stock_daily_df = pd.DataFrame()

    def _get_my_plate(self, path=r'api\自定义优先板块.txt'):
        """读取自定义优先板块"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                my_plate = f.read().strip()
                my_plate = my_plate.replace('\n', '').replace('\r', '')
                if my_plate:
                    return my_plate.split(',')
                else:
                    return []
        except Exception as e:
            self.logger.warning(f"读取自定义优先板块失败: {e}")
            return []

    def get_dashboard_config(self):
        """获取仪表盘配置 - 使用配置驱动架构"""
        # 初始化动态标题
        if not self.dynamic_titles or all(title == "股票数据表" for title in self.dynamic_titles.values() if 'table' in str(title)):
            self._update_dynamic_titles()
            self.logger.info("初始化动态标题")
        else:
            self.logger.info(f"使用现有动态标题: {self.dynamic_titles}")
        
        # 使用组件管理器生成配置
        return self.component_manager.get_dashboard_config()

    def get_data_sources(self):
        """获取数据源配置 - 使用配置驱动架构"""
        return self.component_manager.get_data_sources_config()

    def register_custom_routes(self):
        """注册自定义路由 - 基类会自动调用handler，无需手工注册"""
        # 由于基类现在支持自动handler调用，大部分路由无需手工注册
        # 只保留特殊的路由需求
        pass
        
        # 注册SSE和更新相关路由
        self.app.add_url_rule('/api/dashboard/update',
                             'update_dashboard',
                             self.update_dashboard, methods=['POST'])
        
        self.app.add_url_rule('/api/dashboard/updates',
                             'dashboard_updates',
                             self.dashboard_updates, methods=['GET'])
        
        self.app.add_url_rule('/api/dashboard/notify-update',
                             'notify_update', 
                             self.notify_update, methods=['POST'])
        
        self.app.add_url_rule('/api/debug/dynamic-titles',
                             'get_dynamic_titles_debug',
                             self.get_dynamic_titles_debug, methods=['GET'])
        
        # 缓存管理路由
        self.app.add_url_rule('/api/cache/status',
                             'get_cache_status',
                             self.get_cache_status, methods=['GET'])
        
        self.app.add_url_rule('/api/cache/clear',
                             'clear_cache',
                             self.clear_cache, methods=['POST'])

    # ===== 数据处理方法 =====
    # 注意：处理方法现在由ComponentManager自动创建，无需手动定义
    # 如需自定义特殊逻辑，可以在这里重写对应方法
    def get_cache_status(self):
        """获取缓存状态"""
        return self.response_cache.get_cache_status()
    def clear_cache(self):
        """清除缓存"""
        self.response_cache.clear_cache()
        return jsonify({"status": "success", "message": "缓存已清除"})
    def get_dynamic_titles(self):
        """获取当前动态标题"""
        return jsonify(self.dynamic_titles)
    def get_selected_sector(self):
        """获取当前选中的板块名称"""
        return jsonify({"selected_sector": self.selected_sector})
    def get_latest_update(self):
        """获取最新更新信息"""
        return jsonify(self.latest_update)
    
    # ===== SSE 和更新相关方法 =====
    
    def update_dashboard(self):
        """接收页面更新请求"""
        data = request.json
        self.logger.info(f"收到更新请求: {data}")
        
        params = data.get('params', {})
        if isinstance(params, dict):
            sector_name = params.get('sectors', '航运概念')
        else:
            sector_name = str(params) if params else '航运概念'
        
        self.selected_sector = sector_name
        self.dynamic_titles['table12'] = sector_name
        
        self.latest_update = {
            "componentId": data.get('componentId', 'chart2'),
            "params": params,
            "timestamp": time.time(),
            "action": "config_update",
            "sector_name": sector_name
        }
        
        update_message = {
            "action": "reload_config",
            "sector_name": sector_name,
            "timestamp": time.time()
        }
        self._send_update_to_clients(update_message)
        
        return jsonify({
            "status": "success",
            "message": "Update request sent",
            "sector_name": sector_name,
            "updated_titles": self.dynamic_titles
        })

    def dashboard_updates(self):
        """SSE事件流"""
        def event_stream():
            client_queue = queue.Queue()
            client_id = f"client_{len(self.sse_clients)}_{time.time()}"
            
            try:
                self.sse_clients.append(client_queue)
                self.logger.info(f"SSE客户端连接: {client_id}，当前总连接数: {len(self.sse_clients)}")
                
                connection_info = {
                    "type": "connection_established",
                    "client_id": client_id,
                    "timestamp": time.time(),
                    "server_status": "online"
                }
                yield f"data: {json.dumps(connection_info)}\n\n"
                
                # 不再自动发送latest_update，避免无差别刷新
                # 只在有实际更新时才发送
                # yield f"data: {json.dumps(self.latest_update)}\n\n"
                
                while True:
                    try:
                        message = client_queue.get(block=True, timeout=10)
                        yield message
                    except queue.Empty:
                        heartbeat = {
                            "type": "heartbeat",
                            "client_id": client_id,
                            "timestamp": time.time(),
                            "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "active_connections": len(self.sse_clients)
                        }
                        yield f"data: {json.dumps(heartbeat)}\n\n"
                        continue
                    except GeneratorExit:
                        self.logger.info(f"SSE客户端主动断开: {client_id}")
                        break
                        
            except Exception as e:
                self.logger.error(f"SSE连接异常 {client_id}: {e}")
            finally:
                if client_queue in self.sse_clients:
                    self.sse_clients.remove(client_queue)
                    self.logger.info(f"SSE客户端清理: {client_id}，剩余连接数: {len(self.sse_clients)}")
        
        response = Response(event_stream(), mimetype="text/event-stream")
        response.headers.update({
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control',
            'Keep-Alive': 'timeout=30, max=1000'
        })
        return response

    def notify_update(self):
        """接收更新通知并通过SSE广播"""
        data = request.json
        
        try:
            top_sectors = self._update_dynamic_titles()
            self.logger.info(f"涨幅前5板块: {top_sectors}")
            self.logger.info(f"动态标题已更新: {self.dynamic_titles}")
        except Exception as e:
            self.logger.error(f"notify_update中更新标题失败: {e}")
        
        update_message = {
            "action": "reload_config",
            "sector_name": self.selected_sector,
            "timestamp": time.time()
        }
        
        self._send_update_to_clients(update_message)
        return jsonify({
            "status": "success",
            "message": "更新通知已发送，前端将重新加载配置"
        })

    def get_dynamic_titles_debug(self):
        """调试端点：返回当前的动态标题状态"""
        try:
            top_sectors = self._get_top_sectors()
        except:
            top_sectors = ["获取失败"]
        
        return jsonify({
            "dynamic_titles": self.dynamic_titles,
            "selected_sector": self.selected_sector,
            "latest_update": self.latest_update,
            "current_top_sectors": top_sectors,
            "timestamp": time.time()
        })

    # ===== 辅助方法 =====
    
    def _send_update_to_clients(self, data):
        """发送更新到所有SSE客户端"""
        for client in list(self.sse_clients):
            try:
                client.put(f"data: {json.dumps(data)}\n\n")
            except:
                self.sse_clients.remove(client)

    def _get_dynamic_titles_list(self):
        """获取动态标题列表"""
        return list(self.dynamic_titles.values())

    def _get_top_sectors(self, n=5):
        """获取涨幅前n的板块名称"""
        try:
            plate_df = self.data_cache.load_data('plate_df')
            if plate_df.empty:
                self.logger.warning("板块数据文件读取失败，使用默认板块")
                return ["航运概念", "可控核聚变", "军工"]
                
            plate_df['时间'] = pd.to_datetime(plate_df['时间'])
            latest_time = plate_df['时间'].max()
            plate_df = plate_df[plate_df['时间'] == latest_time]
            
            top_sectors = plate_df.sort_values(by='板块涨幅', ascending=False).head(n)
            top_sectors_list = top_sectors['板块名'].tolist()
            
            # 加入自定义优先板块
            top_sectors_list = self.my_plate_list + top_sectors_list
            return list(set(top_sectors_list))  # 去重
            
        except Exception as e:
            self.logger.error(f"获取涨幅前{n}板块失败: {e}")
            return ["航运概念", "可控核聚变", "军工"]

    def _update_dynamic_titles(self):
        """更新动态标题"""
        try:
            top_sectors = self._get_top_sectors()
            
            while len(top_sectors) < 5:
                top_sectors.append("默认板块")
            
            current_table12 = self.dynamic_titles.get("table12", self.selected_sector)
            
            self.dynamic_titles.update({
                "table2": f"{top_sectors[0]}",
                "table21": f"{top_sectors[1]}",
                "table22": f"{top_sectors[2]}",
                "table23": f"{top_sectors[3]}",
                "table24": f"{top_sectors[4]}",
            })
            
            self.dynamic_titles["table12"] = current_table12
            
            self.logger.info(f"动态标题已更新: {self.dynamic_titles}")
            return top_sectors
            
        except Exception as e:
            self.logger.error(f"更新动态标题失败: {e}")
            return ["航运概念", "可控核聚变", "军工"]

    def _calculate_tail_ratio(self, number_string, n):
        """计算倒数后n个数的合计与总合计的比值"""
        try:
            numbers = [float(x) for x in number_string.split('-')]
            total_sum = sum(numbers)
            tail_numbers = numbers[-n:] if n <= len(numbers) else numbers
            tail_sum = sum(tail_numbers)
            
            if total_sum == 0:
                return 0.0
            else:
                return round(tail_sum / total_sum, 2)
        except:
            return 0.0

    def _calculate_center_of_mass(self, number_string):
        """计算数字串的重心位置"""
        try:
            numbers = [float(x) for x in number_string.split('-')]
            weighted_sum = 0
            value_sum = 0
            
            for index, value in enumerate(numbers):
                position = index + 1
                weighted_sum += position * value
                value_sum += value
            
            if value_sum == 0:
                return 0
            
            return round(weighted_sum / value_sum, 2)
        except:
            return 0


def main():
    """主函数"""
    print("🚀 启动多板块股票仪表盘服务器...")
    
    # 简单配置：禁用自动更新
    auto_update_config = {'enabled': False}
    
    # 创建服务器实例
    server = MultiPlateStockServer(
        port=5007,  # 固定端口
        auto_update_config=auto_update_config
    )
    
    # 显示服务器基本信息
    print(f"📋 端口: {server.port}")
    print(f"🚫 自动更新: 已禁用")
    
    try:
        # 启动时初始化动态标题
        server._update_dynamic_titles()
        print("✅ 动态标题初始化完成")
    except Exception as e:
        print(f"⚠️ 动态标题初始化失败: {e}")
    
    server.run(debug=True)


if __name__ == '__main__':
    main()

