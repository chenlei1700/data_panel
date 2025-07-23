"""
处理器工厂 - 根据服务器类型创建对应的处理器
Author: chenlei
Date: 2025-07-23
"""
from .multiplate_processor import MultiPlateProcessor
from .demo_processor import DemoProcessor
from .strong_processor import StrongProcessor


class ProcessorFactory:
    """处理器工厂类"""
    
    # 服务器类型到处理器类的映射
    _processor_classes = {
        'multiplate': MultiPlateProcessor,
        'demo': DemoProcessor, 
        'strong': StrongProcessor,
        'default': DemoProcessor  # 默认使用演示处理器
    }
    
    @classmethod
    def create_processor(cls, server_type: str, server_instance, data_cache, logger):
        """
        创建处理器实例
        
        Args:
            server_type: 服务器类型 ('multiplate', 'demo', 'strong', etc.)
            server_instance: 服务器实例
            data_cache: 数据缓存实例
            logger: 日志记录器
            
        Returns:
            对应的处理器实例
        """
        processor_class = cls._processor_classes.get(server_type.lower(), cls._processor_classes['default'])
        
        return processor_class(
            server=server_instance,
            data_cache=data_cache,
            logger=logger
        )
    
    @classmethod
    def get_supported_types(cls):
        """获取支持的服务器类型列表"""
        return list(cls._processor_classes.keys())
    
    @classmethod
    def register_processor(cls, server_type: str, processor_class):
        """
        注册新的处理器类型
        
        Args:
            server_type: 服务器类型名称
            processor_class: 处理器类
        """
        cls._processor_classes[server_type.lower()] = processor_class
    
    @classmethod
    def get_processor_info(cls):
        """获取所有处理器的信息"""
        info = {}
        for server_type, processor_class in cls._processor_classes.items():
            if server_type == 'default':
                continue
                
            # 尝试获取处理器的描述信息
            description = getattr(processor_class, '__doc__', '').strip().split('\n')[0] if processor_class.__doc__ else f"{server_type}处理器"
            
            info[server_type] = {
                'class_name': processor_class.__name__,
                'description': description,
                'module': processor_class.__module__
            }
        
        return info


class SimplifiedProcessorManager:
    """简化的处理器管理器"""
    
    def __init__(self, server_type: str, server_instance, data_cache, logger):
        """
        初始化处理器管理器
        
        Args:
            server_type: 服务器类型
            server_instance: 服务器实例
            data_cache: 数据缓存实例
            logger: 日志记录器
        """
        self.server_type = server_type
        self.server = server_instance
        self.data_cache = data_cache
        self.logger = logger
        
        # 创建处理器实例
        self.processor = ProcessorFactory.create_processor(
            server_type, server_instance, data_cache, logger
        )
        
        if self.logger:
            self.logger.info(f"初始化 {server_type} 处理器管理器")
    
    def process(self, method_name: str):
        """
        处理请求
        
        Args:
            method_name: 方法名称
            
        Returns:
            处理结果
        """
        return self.processor.process(method_name)
    
    def get_available_methods(self):
        """获取所有可用的处理方法"""
        return self.processor.get_available_methods()
    
    def get_processor_info(self):
        """获取处理器信息"""
        return {
            'server_type': self.server_type,
            'processor_class': self.processor.__class__.__name__,
            'available_methods': self.get_available_methods()
        }


# 便捷函数
def create_processor_manager(server_type: str, server_instance, data_cache, logger):
    """创建处理器管理器的便捷函数"""
    return SimplifiedProcessorManager(server_type, server_instance, data_cache, logger)


def get_supported_server_types():
    """获取支持的服务器类型"""
    return ProcessorFactory.get_supported_types()


def get_all_processor_info():
    """获取所有处理器的信息"""
    return ProcessorFactory.get_processor_info()


if __name__ == "__main__":
    # 测试代码
    print("处理器工厂测试")
    print("支持的服务器类型:", get_supported_server_types())
    print("处理器信息:", get_all_processor_info())
