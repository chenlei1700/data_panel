"""
组件配置文件 - 统一管理所有仪表盘组件的配置信息（支持多服务器）
Author: chenlei
Date: 2025-07-22
"""

from typing import Dict, Any, Optional, List

class ComponentConfig:
    """组件配置类"""
    
    def __init__(self, 
                 component_id: str,
                 component_type: str,
                 title: str,
                 api_path: str,
                 handler: str,
                 processor_type: str,
                 processor_method: str,
                 position: Dict[str, int],
                 description: str = "",
                 height: Optional[str] = None,
                 cache_ttl: int = 0,
                 source_data_keys: Optional[List[str]] = None,
                 source_data_logic: Optional[str] = None,
                 **kwargs):
        self.id = component_id
        self.type = component_type
        self.title = title
        self.api_path = api_path
        self.handler = handler
        self.processor_type = processor_type
        self.processor_method = processor_method
        self.position = position
        self.description = description
        self.height = height
        self.cache_ttl = cache_ttl
        self.source_data_keys = source_data_keys or []
        self.source_data_logic = source_data_logic
        self.extra_config = kwargs

    def to_dashboard_component(self, dynamic_title: Optional[str] = None) -> Dict[str, Any]:
        """转换为仪表盘组件配置"""
        config = {
            "id": self.id,
            "type": self.type,
            "dataSource": self.api_path,
            "title": dynamic_title or self.title,
            "position": self.position
        }
        
        if self.height:
            config["height"] = self.height
            
        # 添加额外配置
        config.update(self.extra_config)
        
        return config

    def to_data_source_config(self) -> Dict[str, Dict[str, Any]]:
        """转换为数据源配置"""
        return {
            self.api_path: {
                "handler": self.handler,
                "description": self.description,
                "cache_ttl": self.cache_ttl
            }
        }


# 多服务器组件配置定义
COMPONENTS_CONFIGS = {
    "multiplate": {  # 多板块服务器的组件配置
        "chart1": ComponentConfig(
            component_id="chart1",
            component_type="chart",
            title="板块涨幅折线图",
            api_path="/api/chart-data/sector-line-chart_change",
            handler="get_sector_chart_data_change",
            processor_type="chart",
            processor_method="sector-line-chart_change",
            position={"row": 0, "col": 0, "rowSpan": 1, "colSpan": 2},
            description="板块涨幅折线图数据",
            source_data_keys=["plate_df"],
            source_data_logic="sector_line_chart_source_data"
        ),
        
        "chart_speed": ComponentConfig(
            component_id="chart_speed",
            component_type="chart", 
            title="板块涨速累加折线图",
            api_path="/api/chart-data/sector_speed_chart",
            handler="get_sector_speed_chart",
            processor_type="chart",
            processor_method="sector_speed_chart",
            position={"row": 5, "col": 0, "rowSpan": 1, "colSpan": 3},
            description="板块涨速累加图表数据",
            source_data_keys=["plate_df", "stock_minute_df"],
            source_data_logic="sector_speed_chart_source_data"
        ),
        
        "chart2": ComponentConfig(
            component_id="chart2",
            component_type="chart",
            title="板块近似涨停折线图", 
            api_path="/api/chart-data/sector-line-chart_uplimit",
            handler="get_sector_chart_data_uplimit",
            processor_type="chart",
            processor_method="sector-line-chart_uplimit",
            position={"row": 2, "col": 0, "rowSpan": 1, "colSpan": 3},
            description="板块近似涨停折线图数据",
            source_data_keys=["plate_df"],
            source_data_logic="sector_line_chart_source_data"
        ),
        
        "chart3": ComponentConfig(
            component_id="chart3",
            component_type="chart",
            title="板块红盘率折线图",
            api_path="/api/chart-data/sector-line-chart_uprate",
            handler="get_sector_chart_data_uprate",
            processor_type="chart",
            processor_method="sector-line-chart_uprate",
            position={"row": 0, "col": 2, "rowSpan": 1, "colSpan": 1},
            description="板块红盘率折线图数据",
            source_data_keys=["plate_df"],
            source_data_logic="sector_line_chart_source_data"
        ),
        
        "chart4": ComponentConfig(
            component_id="chart4",
            component_type="chart",
            title="板块uprate5折线图",
            api_path="/api/chart-data/sector-line-chart_uprate5",
            handler="get_sector_chart_data_uprate5",
            processor_type="chart",
            processor_method="sector-line-chart_uprate5",
            position={"row": 0, "col": 3, "rowSpan": 1, "colSpan": 1},
            description="板块uprate5折线图数据",
            source_data_keys=["plate_df"],
            source_data_logic="sector_line_chart_source_data"
        ),
        
        "table1": ComponentConfig(
            component_id="table1",
            component_type="table",
            title="板块概要数据表",
            api_path="/api/table-data/plate_info",
            handler="get_plate_info_table_data",
            processor_type="table",
            processor_method="plate_info",
            position={"row": 1, "col": 0, "rowSpan": 1, "colSpan": 3},
            height="800px",
            description="板块概要数据表",
            source_data_keys=["plate_df"],
            source_data_logic="plate_info_source_data"
        ),
        
        "table12": ComponentConfig(
            component_id="table12",
            component_type="table",
            title="股票数据表",  # 动态标题将在运行时覆盖
            api_path="/api/table-data/stocks",
            handler="get_stocks_table_data",
            processor_type="table",
            processor_method="stocks",
            position={"row": 1, "col": 3, "rowSpan": 1, "colSpan": 1},
            height="800px",
            description="股票数据表",
            source_data_keys=["stock_df", "affinity_df"],
            source_data_logic="stocks_source_data"
        ),
        
        "upLimitTable": ComponentConfig(
            component_id="upLimitTable",
            component_type="table",
            title="涨停数据表",
            api_path="/api/table-data/up_limit",
            handler="get_up_limit_table_data",
            processor_type="table",
            processor_method="up_limit",
            position={"row": 0, "col": 4, "rowSpan": 4, "colSpan": 1},
            height="1000px",
            description="涨停数据表",
            source_data_keys=["up_limit_df"],
            source_data_logic="up_limit_source_data"
        ),
        
        "plate_sector": ComponentConfig(
            component_id="plate_sector",
            component_type="chart",
            title="今日各板块连板数分布",
            api_path="/api/chart-data/plate_sector",
            handler="get_today_plate_up_limit_distribution",
            processor_type="sector",
            processor_method="plate_sector",
            position={"row": 6, "col": 0, "rowSpan": 1, "colSpan": 4},
            height="700px",
            description="今日各板块连板数分布",
            source_data_keys=["stock_all_level_df"],
            source_data_logic="plate_sector_source_data"
        ),
        
        "plate_sector_v2": ComponentConfig(
            component_id="plate_sector_v2",
            component_type="stackedAreaChart",
            title="今日各板块连板数分布(面积图)",
            api_path="/api/chart-data/plate_sector_v2",
            handler="get_today_plate_up_limit_distribution_v2",
            processor_type="sector",
            processor_method="plate_sector_v2",
            position={"row": 7, "col": 0, "rowSpan": 1, "colSpan": 4},
            height="700px",
            description="今日各板块连板数分布(堆叠面积图)",
            source_data_keys=["stock_all_level_df"],
            source_data_logic="plate_sector_source_data"
        ),
    },
    
    "demo": {  # 演示服务器的组件配置
        "simple_chart": ComponentConfig(
            component_id="simple_chart",
            component_type="chart",
            title="简单股票图表",
            api_path="/api/chart-data/sector-line-chart_change",
            handler="get_sector_chart_data_change",
            processor_type="chart", 
            processor_method="sector-line-chart_change",
            position={"row": 0, "col": 0, "rowSpan": 2, "colSpan": 3},
            description="简单图表数据",
            source_data_keys=["plate_df"],
            source_data_logic="sector_line_chart_source_data"
        ),
        
        "basic_table": ComponentConfig(
            component_id="basic_table",
            component_type="table",
            title="基础数据表",
            api_path="/api/table-data/plate_info",
            handler="get_plate_info_table_data",
            processor_type="table",
            processor_method="plate_info", 
            position={"row": 2, "col": 0, "rowSpan": 2, "colSpan": 3},
            description="基础表格数据",
            source_data_keys=["plate_df"],
            source_data_logic="plate_info_source_data"
        )
    },
    
    "strong": {  # 强势服务器的组件配置
        "strong_chart": ComponentConfig(
            component_id="strong_chart",
            component_type="chart",
            title="强势股票分析图",
            api_path="/api/chart-data/sector-line-chart_change",
            handler="get_sector_chart_data_change",
            processor_type="chart",
            processor_method="sector-line-chart_change",
            position={"row": 0, "col": 0, "rowSpan": 1, "colSpan": 4},
            description="强势股票分析数据",
            source_data_keys=["plate_df"],
            source_data_logic="sector_line_chart_source_data"
        ),
        
        "upLimitTable": ComponentConfig(
            component_id="upLimitTable",
            component_type="table",
            title="涨停数据表",
            api_path="/api/table-data/up_limit",
            handler="get_up_limit_table_data",
            processor_type="table",
            processor_method="up_limit",
            position={"row": 1, "col": 0, "rowSpan": 3, "colSpan": 4},
            height="800px",
            description="涨停数据表",
            source_data_keys=["up_limit_df"],
            source_data_logic="up_limit_source_data"
        )
    }
}


class ComponentManager:
    """组件管理器 - 支持多服务器"""
    
    def __init__(self, server_instance, server_type: str = "multiplate"):
        self.server = server_instance
        self.server_type = server_type
        self.components = COMPONENTS_CONFIGS.get(server_type, {})
        
    def get_dashboard_config(self) -> Dict[str, Any]:
        """生成仪表盘配置"""
        components = []
        
        for comp_id, comp_config in self.components.items():
            # 检查是否启用该组件
            if comp_config.extra_config.get('enabled', True):
                # 获取动态标题
                dynamic_title = None
                if comp_id == "table12" and hasattr(self.server, 'dynamic_titles'):
                    dynamic_title = self.server.dynamic_titles.get("table12", comp_config.title)
                
                components.append(comp_config.to_dashboard_component(dynamic_title))
        
        return {
            "layout": {
                "rows": 10,
                "cols": 5,
                "components": components
            }
        }
    
    def get_data_sources_config(self) -> Dict[str, Dict[str, Any]]:
        """生成数据源配置"""
        data_sources = {}
        
        for comp_config in self.components.values():
            if comp_config.extra_config.get('enabled', True):
                data_sources.update(comp_config.to_data_source_config())
        
        return data_sources
    
    def get_source_data_logic(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """获取指定端点的源数据逻辑"""
        # 找到对应的组件配置
        for comp_config in self.components.values():
            if comp_config.api_path == endpoint:
                logic_method = comp_config.source_data_logic
                if logic_method and hasattr(self.server, f'_{logic_method}'):
                    # 调用服务器实例的源数据逻辑方法
                    return getattr(self.server, f'_{logic_method}')(endpoint, request_params)
                else:
                    # 使用默认的源数据逻辑
                    return self._default_source_data_logic(comp_config, request_params)
        
        # 未找到配置，使用基类默认实现
        return {}
    
    def _default_source_data_logic(self, comp_config: ComponentConfig, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """默认源数据逻辑"""
        source_data = {
            'endpoint': comp_config.api_path,
            'component_id': comp_config.id,
            'server_type': self.server_type,
            'request_params': request_params,
            'file_timestamps': {}
        }
        
        # 添加依赖的数据文件时间戳
        for data_key in comp_config.source_data_keys:
            if hasattr(self.server, 'data_cache') and hasattr(self.server.data_cache, 'timestamps'):
                source_data['file_timestamps'][data_key] = self.server.data_cache.timestamps.get(data_key, 0)
        
        return source_data
    
    def create_handler_methods(self):
        """为服务器实例动态创建处理方法"""
        for comp_config in self.components.values():
            if comp_config.extra_config.get('enabled', True):
                self._create_handler_method(comp_config)
    
    def _create_handler_method(self, comp_config: ComponentConfig):
        """创建单个处理方法"""
        def handler_method():
            processor_method = getattr(self.server.processor_manager, f'process_{comp_config.processor_type}_data')
            return processor_method(comp_config.processor_method)
        
        # 设置方法名和文档字符串
        handler_method.__name__ = comp_config.handler
        handler_method.__doc__ = f"获取{comp_config.title}数据"
        
        # 将方法绑定到服务器实例
        setattr(self.server, comp_config.handler, handler_method)


# 为了向后兼容，保留原来的COMPONENTS_CONFIG  
COMPONENTS_CONFIG = COMPONENTS_CONFIGS.get("multiplate", {})
