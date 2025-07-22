# 配置驱动架构使用指南

## 概述

配置驱动架构将所有组件的配置信息统一管理，大大简化了添加新组件的流程。

## 架构优势

1. **集中管理** - 所有组件信息在一个配置文件中定义
2. **自动化** - 仪表盘配置、数据源配置、处理方法都自动生成
3. **减少错误** - 避免在多个地方重复定义，减少不一致性
4. **易于维护** - 修改组件只需更改配置即可
5. **扩展性强** - 轻松添加新的组件类型和属性

## 添加新组件的步骤

### 1. 在 `config/component_config.py` 中添加配置

```python
"new_chart_id": ComponentConfig(
    component_id="new_chart_id",
    component_type="chart",  # 或 "table", "stackedAreaChart"
    title="新图表标题",
    api_path="/api/chart-data/new_chart",
    handler="get_new_chart_data",
    processor_type="chart",  # chart/table/sector
    processor_method="new_chart_method",
    position={"row": 8, "col": 0, "rowSpan": 1, "colSpan": 4},
    description="新图表数据",
    height="600px",  # 可选
    source_data_keys=["plate_df"],  # 依赖的数据源
    source_data_logic="new_chart_source_data"  # 源数据逻辑方法名
)
```

### 2. 在对应的processor中实现数据处理方法

在 `processors/chart_processor.py` 或其他相应的processor文件中：

```python
def process_new_chart_method(self, request_params=None):
    """新图表的数据处理逻辑"""
    # 实现具体的数据处理逻辑
    return {"data": [], "layout": {}}
```

### 3. (可选) 在 `config/source_data_mixin.py` 中添加源数据逻辑

如果需要自定义源数据逻辑：

```python
def _new_chart_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
    """新图表的源数据逻辑"""
    # 实现源数据获取逻辑
    return {
        'endpoint': endpoint,
        # ... 其他源数据字段
    }
```

## 完整示例：添加一个新的资金流向图表

### 1. 配置定义

```python
"fund_flow_chart": ComponentConfig(
    component_id="fund_flow_chart",
    component_type="chart",
    title="板块资金流向图表",
    api_path="/api/chart-data/fund_flow",
    handler="get_fund_flow_data",
    processor_type="chart",
    processor_method="fund_flow",
    position={"row": 8, "col": 0, "rowSpan": 1, "colSpan": 5},
    description="板块资金流向分析图表",
    height="500px",
    source_data_keys=["plate_df", "stock_df"],
    source_data_logic="fund_flow_source_data"
)
```

### 2. Processor实现

```python
def process_fund_flow(self, request_params=None):
    """资金流向图表数据处理"""
    plate_df = self.data_cache.load_data('plate_df')
    stock_df = self.data_cache.load_data('stock_df')
    
    # 数据处理逻辑
    chart_data = {
        "data": [
            # Plotly图表数据
        ],
        "layout": {
            # Plotly布局配置
        }
    }
    
    return jsonify(chart_data)
```

### 3. 源数据逻辑

```python
def _fund_flow_source_data(self, endpoint: str, request_params: Dict[str, Any]) -> Dict[str, Any]:
    """资金流向图表源数据逻辑"""
    plate_df = self.data_cache.load_data('plate_df')
    stock_df = self.data_cache.load_data('stock_df')
    
    return {
        'endpoint': endpoint,
        'plate_data_count': len(plate_df),
        'stock_data_count': len(stock_df),
        'file_timestamps': {
            'plate_df': self.data_cache.timestamps.get('plate_df', 0),
            'stock_df': self.data_cache.timestamps.get('stock_df', 0)
        },
        'request_params': request_params
    }
```

## 禁用组件

如果需要临时禁用某个组件，在配置中添加 `enabled=False`：

```python
"old_component": ComponentConfig(
    # ... 其他配置
    enabled=False  # 禁用该组件
)
```

## 动态标题支持

对于需要动态标题的组件（如table12），系统会自动处理：

```python
# 在ComponentManager.get_dashboard_config()中
if comp_id == "table12":
    dynamic_title = self.server.dynamic_titles.get("table12", comp_config.title)
```

## 文件结构

```
api/
├── config/
│   ├── __init__.py
│   ├── component_config.py      # 组件配置定义
│   └── source_data_mixin.py     # 源数据逻辑混入类
├── processors/
│   ├── chart_processor.py       # 图表处理器
│   ├── table_processor.py       # 表格处理器
│   └── sector_processor.py      # 板块处理器
└── show_plate_server_multiplate_v2.py  # 主服务器文件
```

## 注意事项

1. **配置一致性** - 确保api_path、handler、processor_method等配置保持一致
2. **源数据键** - source_data_keys应包含所有相关的数据文件
3. **位置冲突** - 注意组件的position配置避免重叠
4. **方法命名** - 处理方法和源数据逻辑方法应遵循命名规范

## 迁移指南

从手动配置迁移到配置驱动架构：

1. 将现有组件配置复制到 `component_config.py`
2. 将源数据逻辑移动到 `source_data_mixin.py`
3. 删除主服务器文件中的重复配置
4. 测试所有组件功能正常

这样，添加新组件只需要在配置文件中添加一项配置，在processor中实现处理逻辑即可，大大简化了开发流程。
