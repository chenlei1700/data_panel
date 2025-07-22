"""
处理器管理器
负责协调和管理各种数据处理器
"""
from .chart_processor import ChartDataProcessor
from .table_processor import TableDataProcessor  
from .sector_processor import SectorDataProcessor


class ProcessorManager:
    """处理器管理器"""
    
    def __init__(self, server_instance):
        """
        初始化处理器管理器
        
        Args:
            server_instance: 服务器实例
        """
        self.server = server_instance
        
        # 初始化各种处理器
        self.chart_processor = ChartDataProcessor(server_instance)
        self.table_processor = TableDataProcessor(server_instance)
        self.sector_processor = SectorDataProcessor(server_instance)
    
    def process_chart_data(self, chart_type: str):
        """处理图表数据"""
        return self.chart_processor.process(chart_type)
    
    def process_table_data(self, table_type: str):
        """处理表格数据"""
        return self.table_processor.process(table_type)
    
    def process_sector_data(self, sector_type: str):
        """处理板块数据"""
        return self.sector_processor.process(sector_type)
    
    def get_processor_for_endpoint(self, endpoint: str):
        """
        根据端点获取对应的处理器和方法
        
        Args:
            endpoint: API端点路径
            
        Returns:
            tuple: (processor, method_name) 或 (None, None) 如果未找到匹配的处理器
        """
        # 图表数据端点
        if '/api/chart-data/' in endpoint:
            chart_type = endpoint.split('/api/chart-data/')[-1]
            return self.chart_processor, chart_type
        
        # 表格数据端点
        elif '/api/table-data/' in endpoint:
            table_type = endpoint.split('/api/table-data/')[-1]
            return self.table_processor, table_type
        
        # 板块数据端点（特殊图表类型）
        elif endpoint.endswith('plate_sector') or endpoint.endswith('plate_sector_v2') or 'stacked-area-sector' in endpoint:
            if 'plate_sector_v2' in endpoint:
                sector_type = 'plate_sector_v2'
            elif 'plate_sector' in endpoint:
                sector_type = 'plate_sector'
            elif 'stacked-area-sector' in endpoint:
                sector_type = 'stacked-area-sector'
            else:
                sector_type = endpoint.split('/')[-1]
            return self.sector_processor, sector_type
        
        return None, None
