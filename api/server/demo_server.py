"""
演示股票仪表盘服务器 - 使用配置驱动架构
Author: chenlei
Date: 2025-07-22
"""

from .base_server import BaseStockServer
from ..conf.server_config import get_server_config
from ..processors import ProcessorManager
from ..conf.component_config_multi import ComponentManager
from ..conf.source_data_mixin import SourceDataLogicMixin

class DemoStockServer(BaseStockServer, SourceDataLogicMixin):
    """演示股票服务器 - 简化版本，只显示基础图表和表格"""
    
    def __init__(self, port=None, auto_update_config=None):
        # 从配置文件获取服务器配置
        server_config = get_server_config("demo")
        
        if port is None:
            port = server_config.get("port", 5004)
        
        if auto_update_config is None:
            auto_update_config = server_config.get("auto_update_config", {})
        
        server_name = server_config.get("name", "演示股票仪表盘")
        
        super().__init__(port=port, name=server_name, auto_update_config=auto_update_config)
        
        # 初始化处理器管理器
        self.processor_manager = ProcessorManager(self)
        
        # 初始化组件管理器（使用demo配置）
        self.component_manager = ComponentManager(self, server_type="demo")
        
        # 动态创建处理方法
        self.component_manager.create_handler_methods()

    def get_data_cache_file_paths(self) -> dict:
        """演示服务器只需要基础数据"""
        return {
            'plate_df': 'strategy\\showhtml\\server\\good_plate_df.csv',
        }

    def get_dashboard_config(self):
        """获取仪表盘配置 - 使用配置驱动架构"""
        return self.component_manager.get_dashboard_config()

    def get_data_sources(self):
        """获取数据源配置 - 使用配置驱动架构"""
        return self.component_manager.get_data_sources_config()

    def register_custom_routes(self):
        """注册自定义路由"""
        pass


def main():
    """主函数"""
    print("🚀 启动演示股票仪表盘服务器...")
    
    auto_update_config = {'enabled': True, 'interval': 45}
    
    server = DemoStockServer(
        port=5004,
        auto_update_config=auto_update_config
    )
    
    print(f"📋 端口: {server.port}")
    print(f"📊 组件配置: demo (简化版)")
    
    server.run(debug=True)


if __name__ == '__main__':
    main()
