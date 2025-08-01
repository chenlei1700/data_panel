# Processor 启动缓存使用指南

## 概述

我们已经在 `BaseDataProcessor` 基类中实现了启动缓存功能，所有继承自该基类的processor都可以使用这个功能。

## 缓存类型

### 1. 启动缓存 (startup_once)
- **适用场景**: 计算量大且结果不经常变化的数据
- **特点**: 服务启动时计算一次，之后直接返回缓存结果
- **典型用例**: 历史数据分析、基准数据、配置信息、统计报表等

### 2. 响应缓存 (response)
- **适用场景**: 需要定期更新但计算成本较高的数据
- **特点**: 基于数据源文件时间戳自动判断是否更新缓存
- **典型用例**: 日更新数据、周期性报表等

### 3. 无缓存 (none)
- **适用场景**: 实时数据、用户个性化数据
- **特点**: 每次请求都重新计算
- **典型用例**: 实时行情、用户偏好数据等

## 使用方法

### 启动缓存使用步骤

1. **创建包装方法**:
```python
def process_your_method(self):
    """你的方法描述 - 使用启动缓存"""
    return self._process_with_startup_cache('/api/your_endpoint', self._original_your_method)
```

2. **实现原始处理方法**:
```python
def _original_your_method(self):
    """原始数据处理方法"""
    try:
        # 你的数据处理逻辑
        result_data = {
            "status": "success",
            "data": your_processed_data,
            "metadata": {
                "description": "数据描述"
            }
        }
        return jsonify(result_data)
    except Exception as e:
        return self.error_response(f"处理失败: {e}")
```

3. **在组件配置中启用启动缓存**:
```json
{
    "your_component_id": {
        "type": "chart",
        "title": "你的组件标题",
        "api_path": "/api/your_endpoint",
        "extra_config": {
            "cache": {
                "strategy": "startup_once"
            }
        }
    }
}
```

### 响应缓存使用步骤

1. **创建包装方法**:
```python
def process_your_method(self):
    """你的方法描述 - 使用响应缓存"""
    cache_params = self.build_cache_params()
    source_data = {
        'file_path': 'path/to/your/data/file.csv'
    }
    return self._process_with_response_cache('/api/your_endpoint', self._original_your_method, cache_params, source_data)
```

## 代码示例

### 完整的Processor示例

```python
from .base_processor import BaseDataProcessor
from flask import jsonify, request
import pandas as pd
import time

class YourProcessor(BaseDataProcessor):
    """你的处理器"""
    
    # 启动缓存示例
    def process_heavy_calculation(self):
        """重计算数据 - 使用启动缓存"""
        return self._process_with_startup_cache('/api/heavy_calculation', self._original_heavy_calculation)
    
    def _original_heavy_calculation(self):
        """原始重计算数据处理方法"""
        try:
            # 模拟重计算
            time.sleep(2)  # 模拟计算时间
            
            # 复杂数据处理逻辑
            result = {
                "chart_data": [...],
                "summary": {...},
                "metadata": {
                    "calculation_time": "2秒",
                    "cache_type": "startup_once"
                }
            }
            
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"重计算失败: {e}")
    
    # 响应缓存示例
    def process_daily_update(self):
        """日更新数据 - 使用响应缓存"""
        cache_params = self.build_cache_params()
        source_data = {'file_path': 'daily_data.csv'}
        return self._process_with_response_cache('/api/daily_update', self._original_daily_update, cache_params, source_data)
    
    def _original_daily_update(self):
        """原始日更新数据处理方法"""
        try:
            # 从文件读取数据
            df = pd.read_csv('daily_data.csv')
            
            # 数据处理
            processed_data = df.to_dict('records')
            
            result = {
                "data": processed_data,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "metadata": {
                    "cache_type": "response"
                }
            }
            
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"日更新数据处理失败: {e}")
    
    # 无缓存示例
    def process_realtime_data(self):
        """实时数据 - 不使用缓存"""
        try:
            # 获取实时数据
            realtime_value = self.get_realtime_value()
            
            result = {
                "value": realtime_value,
                "timestamp": time.time(),
                "metadata": {
                    "cache_type": "none",
                    "realtime": True
                }
            }
            
            return jsonify(result)
            
        except Exception as e:
            return self.error_response(f"获取实时数据失败: {e}")
```

## 最佳实践

### 1. 方法命名约定
- 包装方法: `process_xxx()`
- 原始方法: `_original_xxx()`

### 2. 缓存策略选择
- **启动缓存**: 计算时间 > 1秒 且 数据更新频率 < 1天
- **响应缓存**: 计算时间 > 0.5秒 且 数据更新频率 = 1天-1小时
- **无缓存**: 计算时间 < 0.5秒 或 实时性要求高

### 3. 错误处理
- 始终在原始方法中包含try-catch
- 使用 `self.error_response()` 返回统一的错误格式
- 记录详细的错误日志

### 4. 元数据添加
- 在返回的数据中包含 `metadata` 字段
- 添加缓存类型、计算时间等信息
- 便于前端显示和调试

## 配置示例

### components_config.json 配置

```json
{
    "heavy_calculation_chart": {
        "type": "chart",
        "title": "重计算图表",
        "api_path": "/api/heavy_calculation",
        "extra_config": {
            "cache": {
                "strategy": "startup_once"
            }
        }
    },
    "daily_update_table": {
        "type": "table",
        "title": "日更新表格",
        "api_path": "/api/daily_update",
        "extra_config": {
            "cache": {
                "strategy": "response"
            }
        }
    },
    "realtime_chart": {
        "type": "chart",
        "title": "实时图表",
        "api_path": "/api/realtime_data",
        "extra_config": {
            "cache": {
                "strategy": "none"
            }
        }
    }
}
```

## 注意事项

1. **初始化顺序**: 确保processor_manager在服务器初始化完成后再创建
2. **缓存预热**: 启动缓存会在服务器启动时自动预热
3. **内存使用**: 启动缓存会占用内存，注意数据大小
4. **调试信息**: 查看服务器日志了解缓存命中情况

## 故障排除

### 常见问题

1. **AttributeError: 'processor_manager' not found**
   - 检查processor_manager的初始化顺序
   - 确保在super().__init__()之后创建processor_manager

2. **缓存未生效**
   - 检查组件配置中的cache.strategy设置
   - 查看服务器日志确认缓存预热状态

3. **预热失败**
   - 检查原始处理方法的错误处理
   - 确保所有依赖的数据源可用
