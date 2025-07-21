# 基类防重复缓存机制使用指南

## 概述

BaseStockServer基类现在提供了通用的防重复缓存机制，可以自动处理API响应的缓存，避免重复计算。这个机制可以：

1. 自动检测数据是否发生变化
2. 智能决定是否使用缓存响应
3. 提供统一的缓存管理接口
4. 减少子类中的重复代码

## 核心组件

### 1. BaseDataCache
负责数据文件的缓存管理：
```python
class BaseDataCache:
    def load_data(self, key: str):  # 加载数据
    def update_data(self, key: str, data: Any):  # 更新缓存
    def clear_cache(self):  # 清空缓存
```

### 2. BaseResponseCache  
负责API响应的缓存管理：
```python
class BaseResponseCache:
    def should_use_cache(self, endpoint, params, source_data):  # 检查是否使用缓存
    def store_response(self, endpoint, params, source_data, response_data):  # 存储响应
    def clear_cache(self):  # 清空缓存
```

## 使用方法

### 1. 在数据源配置中启用缓存

在`get_data_sources()`方法中，为需要缓存的端点设置`cache_ttl`：

```python
def get_data_sources(self):
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
```

### 2. 重写_get_source_data_for_endpoint方法

提供精确的源数据用于缓存判断：

```python
def _get_source_data_for_endpoint(self, endpoint: str) -> Dict[str, Any]:
    if "plate_info" in endpoint:
        plate_df = self.data_cache.load_data('plate_df')
        return {
            "endpoint": endpoint,
            "plate_df_timestamp": self.data_cache.timestamps.get('plate_df', 0),
            "data_count": len(plate_df),
            "latest_time": str(plate_df['时间'].max()) if not plate_df.empty else "",
            "request_params": dict(request.args) if hasattr(request, 'args') else {}
        }
    return super()._get_source_data_for_endpoint(endpoint)
```

### 3. 简化handler方法

移除手动缓存逻辑，专注于业务逻辑：

**旧方式（手动缓存）：**
```python
def get_plate_info_table_data(self):
    try:
        # 构建用于哈希比较的源数据
        source_data = {
            'data_time': str(latest_time),
            'data_count': len(plate_df),
            # ... 更多源数据
        }
        
        # 检查是否可以使用缓存
        cache_endpoint = '/api/table-data/plate_info'
        should_cache, cached_response = self.response_cache.should_use_cache(
            cache_endpoint, cache_params, source_data
        )
        
        if should_cache and cached_response:
            return cached_response
        
        # 数据处理逻辑
        # ...
        
        # 存储到缓存
        self.response_cache.store_response(
            cache_endpoint, cache_params, source_data, response_data
        )
        
        return response_data
    except Exception as e:
        # 错误处理
```

**新方式（自动缓存）：**
```python
def get_plate_info_table_data(self):
    try:
        # 直接执行数据处理逻辑，缓存由基类自动处理
        plate_df = self.data_cache.load_data('plate_df')
        
        if plate_df.empty:
            return jsonify({"error": "数据读取失败"})
        
        # 数据处理逻辑
        columns = [...]
        rows = [...]
        
        return jsonify({
            "columns": columns,
            "rows": rows
        })
    except Exception as e:
        self.logger.error(f"处理失败: {e}")
        return jsonify({"error": str(e)}), 500
```

## 迁移步骤

### 1. 更新服务器类

```python
class MultiPlateStockServer(BaseStockServer):
    def __init__(self, port=5008):
        super().__init__(port=port, name="多板块股票仪表盘")
        
        # 使用现有的DataCache，不需要再单独初始化ResponseCache
        self.data_cache = DataCache()
        # self.response_cache 已经在基类中初始化
```

### 2. 配置缓存策略

在`get_data_sources()`中为需要缓存的端点添加`cache_ttl`：

```python
"/api/chart-data/sector-line-chart_change": {
    "handler": "get_sector_chart_data_change",
    "description": "板块涨幅折线图数据",
    "cache_ttl": 0  # 0 = 禁用缓存，>0 = 启用缓存
},
```

### 3. 实现源数据提取

重写`_get_source_data_for_endpoint`方法，为每个端点提供精确的源数据。

### 4. 简化handler方法

从现有的handler方法中移除所有手动缓存相关的代码。

## 优势

### 1. 代码简化
- 移除重复的缓存检查代码
- 统一的缓存管理接口
- 更清晰的业务逻辑分离

### 2. 更好的可维护性  
- 缓存逻辑集中在基类中
- 更容易调试和优化
- 统一的缓存状态监控

### 3. 更灵活的缓存策略
- 可以针对不同端点设置不同的缓存TTL
- 精确的源数据比较机制
- 支持参数化的缓存键

### 4. 更好的性能
- 智能的缓存清理机制
- LRU缓存策略
- 统一的哈希计算

## API端点

基类自动提供以下缓存管理端点：

- `GET /api/cache/status` - 查看缓存状态
- `POST /api/cache/clear` - 清理所有缓存

## 调试建议

1. 查看日志中的缓存使用情况
2. 使用`/api/cache/status`监控缓存状态  
3. 在开发环境中设置较短的缓存TTL进行测试
4. 确保`_get_source_data_for_endpoint`返回的数据能够准确反映数据变化

## 注意事项

1. 设置合适的`cache_ttl`值：
   - 实时数据：0-30秒
   - 半实时数据：30-300秒  
   - 静态数据：300-3600秒

2. 源数据要包含所有影响结果的因素：
   - 数据文件时间戳
   - 请求参数
   - 配置状态
   - 数据摘要

3. 避免在源数据中包含过大的对象，会影响哈希计算性能。

通过这种方式，新增服务器时只需要关注业务逻辑，缓存机制完全由基类自动处理！
