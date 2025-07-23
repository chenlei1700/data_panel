"""
简化的处理器管理器 - 一服务器一处理器架构
Simplified Processor Manager - One Server One Processor Architecture

Author: chenlei
Date: 2025-07-23
"""

import importlib
from typing import Dict, Any, Type
try:
    from .base_processor import BaseDataProcessor
except ImportError:
    # 用于测试时的导入
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from base_processor import BaseDataProcessor


class SimplifiedProcessorManager:
    """简化的处理器管理器 - 每个服务器只有一个处理器"""
    
    # 服务器处理器映射
    PROCESSOR_MAP = {
        "multiplate": "processors.multiplate_processor.MultiPlateProcessor",
        "demo": "processors.demo_processor.DemoProcessor",
        "strong": "processors.strong_processor.StrongProcessor"
    }
    
    def __init__(self, server_type: str, server_instance):
        """
        初始化处理器管理器
        
        Args:
            server_type: 服务器类型
            server_instance: 服务器实例
        """
        self.server_type = server_type
        self.server = server_instance
        self.logger = getattr(server_instance, 'logger', None)
        
        # 创建处理器实例
        self.processor = self._create_processor()
        
        if self.logger:
            self.logger.info(f"初始化 {server_type} 处理器管理器")
    
    def _create_processor(self) -> BaseDataProcessor:
        """创建处理器实例"""
        if self.server_type not in self.PROCESSOR_MAP:
            raise ValueError(f"不支持的服务器类型: {self.server_type}")
        
        processor_class_path = self.PROCESSOR_MAP[self.server_type]
        processor_class = self._import_class(processor_class_path)
        
        return processor_class(self.server)
    
    @staticmethod
    def _import_class(class_path: str) -> Type:
        """动态导入类"""
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    
    # =========================================================================
    # 统一的处理方法
    # =========================================================================
    
    def process_chart_data(self, chart_type: str):
        """处理图表数据"""
        return self.processor.process(chart_type)
    
    def process_table_data(self, table_type: str):
        """处理表格数据"""
        return self.processor.process(table_type)
    
    def process_sector_data(self, sector_type: str):
        """处理板块数据"""
        return self.processor.process(sector_type)
    
    def process_data(self, method_name: str):
        """通用数据处理方法"""
        return self.processor.process(method_name)
    
    # =========================================================================
    # 端点解析方法 (保持兼容性)
    # =========================================================================
    
    def get_processor_for_endpoint(self, endpoint: str):
        """
        根据端点获取对应的处理器和方法
        
        Args:
            endpoint: API端点路径
            
        Returns:
            tuple: (processor, method_name)
        """
        # 解析端点获取方法名
        method_name = self._parse_endpoint_to_method(endpoint)
        return self.processor, method_name
    
    def _parse_endpoint_to_method(self, endpoint: str) -> str:
        """将端点路径解析为方法名"""
        # 图表数据端点
        if '/api/chart-data/' in endpoint:
            chart_type = endpoint.split('/api/chart-data/')[-1]
            return chart_type
        
        # 表格数据端点  
        elif '/api/table-data/' in endpoint:
            table_type = endpoint.split('/api/table-data/')[-1]
            return table_type
        
        # 板块数据端点（特殊图表类型）
        elif endpoint.endswith('plate_sector') or endpoint.endswith('plate_sector_v2') or 'stacked-area-sector' in endpoint:
            if 'plate_sector_v2' in endpoint:
                return 'plate_sector_v2'
            elif 'plate_sector' in endpoint:
                return 'plate_sector'
            elif 'stacked-area-sector' in endpoint:
                return 'stacked-area-sector'
            else:
                return endpoint.split('/')[-1]
        
        # 其他端点
        else:
            return endpoint.split('/')[-1]
    
    # =========================================================================
    # 管理方法
    # =========================================================================
    
    def get_available_methods(self) -> list:
        """获取处理器的所有可用方法"""
        if hasattr(self.processor, 'get_available_methods'):
            return self.processor.get_available_methods()
        else:
            # 回退方案：扫描所有process_*方法
            methods = [method.replace('process_', '') for method in dir(self.processor) 
                      if method.startswith('process_') and callable(getattr(self.processor, method))]
            return sorted(methods)
    
    def get_processor_info(self) -> Dict[str, Any]:
        """获取处理器信息"""
        return {
            "server_type": self.server_type,
            "processor_class": self.processor.__class__.__name__,
            "available_methods": self.get_available_methods(),
            "method_count": len(self.get_available_methods())
        }
    
    def reload_processor(self):
        """重新加载处理器"""
        self.processor = self._create_processor()
        if self.logger:
            self.logger.info(f"已重新加载 {self.server_type} 处理器")
    
    @classmethod
    def register_processor(cls, server_type: str, processor_class_path: str):
        """注册新的处理器"""
        cls.PROCESSOR_MAP[server_type] = processor_class_path
        print(f"已注册处理器: {server_type} -> {processor_class_path}")
    
    @classmethod
    def get_supported_servers(cls) -> list:
        """获取支持的服务器类型"""
        return list(cls.PROCESSOR_MAP.keys())


# =========================================================================
# 便捷函数
# =========================================================================

def create_processor_manager(server_type: str, server_instance):
    """创建处理器管理器的便捷函数"""
    return SimplifiedProcessorManager(server_type, server_instance)


def register_processor(server_type: str, processor_class_path: str):
    """注册处理器的便捷函数"""
    return SimplifiedProcessorManager.register_processor(server_type, processor_class_path)


def get_supported_servers() -> list:
    """获取支持的服务器类型"""
    return SimplifiedProcessorManager.get_supported_servers()


# =========================================================================
# 测试代码
# =========================================================================

if __name__ == "__main__":
    print("🚀 简化处理器管理器测试")
    
    # 显示支持的服务器类型
    print(f"\n📋 支持的服务器类型: {get_supported_servers()}")
    
    # 显示处理器映射
    print(f"\n🗂 处理器映射:")
    for server_type, processor_path in SimplifiedProcessorManager.PROCESSOR_MAP.items():
        print(f"  {server_type}: {processor_path}")
    
    print("\n✨ 架构优势:")
    print("  ✅ 一个服务器一个处理器文件")
    print("  ✅ 职责边界清晰明确")
    print("  ✅ 开发和维护简单")
    print("  ✅ 测试和调试容易")
    print("  ✅ 扩展和修改方便")
