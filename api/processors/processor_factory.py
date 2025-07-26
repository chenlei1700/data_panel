"""
处理器工厂 - 根据服务器类型创建对应的处理器
Author: chenlei
Date: 2025-07-23
Enhanced: 2025-07-26 支持动态加载处理器
"""
import os
import importlib
import json
from pathlib import Path

# try:
#     # 自动生成的导入语句
#     from .multiplate_processor import MultiPlateProcessor
#     from .market_review_processor import MarketReviewProcessor
#     from .demo_processor import DemoProcessor
#     from .strong_processor import StrongProcessor
# except ImportError:
#     # 回退到绝对导入
#     from multiplate_processor import MultiPlateProcessor
#     from market_review_processor import MarketReviewProcessor
#     from demo_processor import DemoProcessor
#     from strong_processor import StrongProcessor


class ProcessorFactory:
    """处理器工厂类 - 支持动态加载处理器"""
    
    # 静态定义的处理器类（兼容性保持）
    _static_processor_classes = {
        # 'multiplate': MultiPlateProcessor,
        # 'market_review': MarketReviewProcessor,
        # 'demo': DemoProcessor,
        # 'strong': StrongProcessor,
        # 'default': DemoProcessor  # 默认使用演示处理器
    }
    
    # 动态加载的处理器类缓存
    _dynamic_processor_cache = {}
    
    @classmethod
    def _load_server_config(cls):
        """加载服务器配置文件"""
        try:
            config_file = Path(__file__).parent.parent / "config" / "server_config.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load server config: {e}")
            return None
    
    @classmethod
    def _try_dynamic_import(cls, server_type):
        """尝试动态导入处理器类"""
        if server_type in cls._dynamic_processor_cache:
            return cls._dynamic_processor_cache[server_type]
        
        try:
            # 尝试导入处理器模块
            module_name = f"{server_type}_processor"
            
            # 先尝试相对导入
            try:
                module = importlib.import_module(f".{module_name}", package=__package__)
            except ImportError:
                # 回退到绝对导入
                module = importlib.import_module(module_name)
            
            # 生成类名
            class_name_parts = server_type.split('_')
            class_name = ''.join(word.capitalize() for word in class_name_parts) + 'Processor'
            
            # 获取处理器类
            processor_class = getattr(module, class_name)
            
            # 缓存成功导入的类
            cls._dynamic_processor_cache[server_type] = processor_class
            print(f"✅ 动态加载处理器: {server_type} -> {class_name}")
            
            return processor_class
            
        except Exception as e:
            print(f"❌ 动态加载处理器失败 {server_type}: {e}")
            return None
    
    @classmethod
    def _get_all_processor_classes(cls):
        """获取所有可用的处理器类（包括动态发现的）"""
        all_classes = cls._static_processor_classes.copy()
        
        # 尝试从配置文件中发现新的处理器
        config = cls._load_server_config()
        if config and 'servers' in config:
            for server_type in config['servers']:
                if server_type not in all_classes:
                    processor_class = cls._try_dynamic_import(server_type)
                    if processor_class:
                        all_classes[server_type] = processor_class
        
        return all_classes
    
    @classmethod
    def create_processor(cls, server_type, server_instance, data_cache, logger):
        """
        创建处理器实例
        
        Args:
            server_type: 服务器类型
            server_instance: 服务器实例
            data_cache: 数据缓存实例
            logger: 日志记录器
            
        Returns:
            处理器实例
        """
        # 首先尝试静态定义的处理器
        processor_class = cls._static_processor_classes.get(server_type)
        
        # 如果静态处理器不存在，尝试动态加载
        if not processor_class:
            processor_class = cls._try_dynamic_import(server_type)
        
        # 如果仍然没有找到，使用默认处理器
        if not processor_class:
            print(f"⚠️ 未找到处理器 {server_type}，使用默认处理器")
            # 动态加载一个默认处理器
            processor_class = cls._try_dynamic_import('demo')
            if not processor_class:
                return None
        
        # 创建并返回处理器实例
        # return processor_class(server_instance, data_cache, logger)
        return processor_class(server_instance)
    
    @classmethod
    def get_processor_info(cls):
        """
        获取所有处理器信息
        
        Returns:
            dict: 处理器信息字典
        """
        all_classes = cls._get_all_processor_classes()
        info = {}
        
        for server_type, processor_class in all_classes.items():
            # 检查是否为动态加载的处理器
            is_dynamic = server_type in cls._dynamic_processor_cache
            
            info[server_type] = {
                'class_name': processor_class.__name__,
                'module': processor_class.__module__,
                'description': getattr(processor_class, '__doc__', f'{server_type}处理器').strip().split('\\n')[0],
                'is_dynamic': is_dynamic
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
        
        if self.processor:
            self.logger.info(f"✅ 处理器管理器初始化成功: {server_type}")
        else:
            self.logger.error(f"❌ 处理器管理器初始化失败: {server_type}")
    
    def process(self, data_type: str, **kwargs):
        """
        处理数据请求
        
        Args:
            data_type: 数据类型
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        if not self.processor:
            return {"error": "处理器未初始化"}
        
        try:
            # 调用处理器的数据处理方法
            method_name = f"process_{data_type}"
            if hasattr(self.processor, method_name):
                method = getattr(self.processor, method_name)
                return method(**kwargs)
            else:
                self.logger.warning(f"处理器 {self.server_type} 不支持数据类型: {data_type}")
                return {"error": f"不支持的数据类型: {data_type}"}
                
        except Exception as e:
            self.logger.error(f"处理数据时出错 {data_type}: {e}")
            return {"error": f"处理失败: {str(e)}"}


def create_processor_manager(server_type: str, server_instance, data_cache, logger):
    """
    工厂函数：创建处理器管理器
    
    Args:
        server_type: 服务器类型
        server_instance: 服务器实例
        data_cache: 数据缓存实例
        logger: 日志记录器
        
    Returns:
        SimplifiedProcessorManager: 处理器管理器实例
    """
    return SimplifiedProcessorManager(server_type, server_instance, data_cache, logger)


# 兼容性导出
ProcessorManager = SimplifiedProcessorManager
