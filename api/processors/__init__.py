"""
处理器包 - 新架构
包含所有处理器相关的类和工厂

Author: chenlei
Date: 2025-07-23
"""
from .processor_factory import ProcessorFactory, SimplifiedProcessorManager, create_processor_manager
from .base_processor import BaseDataProcessor
from .multiplate_processor import MultiPlateProcessor
from .demo_processor import DemoProcessor

__all__ = [
    'ProcessorFactory',
    'SimplifiedProcessorManager', 
    'create_processor_manager',
    'BaseDataProcessor',
    'MultiPlateProcessor',
    'DemoProcessor',
    'StrongProcessor'
]
