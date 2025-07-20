# 📊 堆叠面积图组件 - 项目更新摘要

## 🎯 更新概述

本次更新为项目新增了**堆叠面积图组件**（StackedAreaChartComponent），这是一个专门处理三维数据可视化的图表组件，特别适用于展示分类数据在时间序列上的累积效果。

## ✨ 新增功能

### 1. 堆叠面积图组件
- **文件位置**: `src/components/dashboard/StackedAreaChartComponent.vue`
- **功能特点**:
  - 支持三维数据可视化（X轴、Y轴累积值、字典数据分解）
  - 自动计算累积值并生成堆叠面积效果
  - 每个key形成独立折线，相邻折线间填充颜色
  - 支持交互式鼠标悬停显示详细信息
  - 可选的上方表格显示汇总数据
  - 自定义颜色配置和表格单元格颜色映射

### 2. 组件集成
- **更新文件**: `src/components/dashboard/ComponentRenderer.vue`
- **新增类型**: `stackedAreaChart`
- 完美集成到现有的组件渲染体系中

### 3. API后端支持

#### 演示服务器 (show_plate_server_demo.py)
- 新增端点: `/api/chart-data/stacked-area-demo`
- 新增数据生成函数: `generate_mock_stacked_area_data()`
- 更新仪表盘配置，包含堆叠面积图示例

#### 生产服务器 (show_plate_server_multiplate_v2.py)
- 新增端点: `/api/chart-data/stacked-area-sector`
- 新增方法: `get_sector_stacked_area_data()`
- 智能的实际数据处理和演示数据回退机制
- 板块资金流向分析功能

### 4. 演示页面
- **新增页面**: `src/views/StackedAreaDemo.vue`
- **路由配置**: `/stacked-area-demo`
- 包含多个演示示例：
  - 基本堆叠面积图
  - 带表格的堆叠面积图  
  - 自定义颜色配置示例
- 详细的功能说明和使用指南

### 5. 文档和工具
- **使用指南**: `docs/STACKED_AREA_CHART_GUIDE.md`
- **演示脚本**: `scripts/demo-stacked-area-chart.py`
- **VS Code任务**: 新增"📊 堆叠面积图演示"任务

## 📁 文件更新清单

### 新增文件
```
src/components/dashboard/StackedAreaChartComponent.vue    # 堆叠面积图组件
src/views/StackedAreaDemo.vue                           # 演示页面
docs/STACKED_AREA_CHART_GUIDE.md                       # 使用指南
scripts/demo-stacked-area-chart.py                     # 演示脚本
```

### 修改文件
```
src/components/dashboard/ComponentRenderer.vue          # 集成新组件
src/router/index.js                                   # 添加演示页面路由
src/views/Home.vue                                    # 添加演示入口
api/show_plate_server_demo.py                        # 演示API支持
api/show_plate_server_multiplate_v2.py               # 生产API支持
.vscode/tasks.json                                    # 添加演示任务
```

## 🎨 数据格式设计

### 输入数据结构
```json
{
  "stackedAreaData": {
    "data": {
      "时间点1": {"类型A": 10.5, "类型B": 15.2, "类型C": 8.3},
      "时间点2": {"类型A": 12.1, "类型B": 18.7, "类型C": 9.8}
    },
    "keyOrder": ["类型A", "类型B", "类型C"],
    "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
  },
  "xAxisValues": ["时间点1", "时间点2"],
  "tableData": {"时间点1": "34.0亿", "时间点2": "40.6亿"}
}
```

### 累积计算逻辑
- 类型A: y = 10.5 (原始值)
- 类型B: y = 10.5 + 15.2 = 25.7 (累积值)
- 类型C: y = 25.7 + 8.3 = 34.0 (累积值)

## 🔧 技术实现

### 前端技术栈
- **Vue 3 Composition API**: 响应式数据管理
- **Plotly.js**: 图表渲染引擎
- **CSS Grid/Flexbox**: 布局管理
- **自定义样式**: 深度控制Plotly元素外观

### 后端技术栈
- **Flask**: API端点实现
- **Pandas**: 数据处理和分析
- **NumPy**: 数值计算
- **数据缓存机制**: 优化性能

### 关键算法
```javascript
// 累积值计算
const calculateCumulativeData = (data, xValues, keyOrder) => {
  keyOrder.forEach((xValue, xIndex) => {
    let cumulativeSum = 0;
    keyOrder.forEach(key => {
      const currentValue = data[xValue][key] || 0;
      cumulativeSum += currentValue;
      // 存储累积值和原始值
      cumulativeData[key].push({
        x: xValue, y: cumulativeSum, originalValue: currentValue
      });
    });
  });
};
```

## 🎯 应用场景

### 1. 资金流向分析
- 展示不同类型资金的流入流出
- 分析机构资金、散户资金等构成
- 时间段内的资金变化趋势

### 2. 板块表现分析
- 多个板块的综合表现对比
- 各板块贡献度可视化
- 板块间的相对强弱对比

### 3. 成交量结构分析
- 大单、中单、小单的成交量分布
- 不同规模订单的时间变化
- 市场参与者结构分析

## 🚀 使用方法

### 1. 在现有仪表盘中使用
```javascript
{
  "id": "myStackedChart",
  "type": "stackedAreaChart",
  "dataSource": "/api/chart-data/my-stacked-data",
  "title": "我的堆叠面积图"
}
```

### 2. 直接使用组件
```vue
<StackedAreaChartComponent :component-config="config" />
```

### 3. 查看演示
- 启动项目后访问: `http://localhost:8081/stacked-area-demo`
- 或者运行演示脚本: `python scripts/demo-stacked-area-chart.py`

## 🧪 测试和验证

### 数据格式验证
- 自动检查必需字段
- 验证数据结构一致性
- 检查颜色配置有效性

### 演示数据生成
- 多种场景的演示数据
- 实时数据更新演示
- API格式兼容性测试

## 📈 性能优化

### 前端优化
- 响应式大小调整
- Plotly图表复用和缓存
- 数据变化时的智能重渲染

### 后端优化
- 数据缓存机制
- 智能降级到演示数据
- 高效的数据处理流水线

## 🔮 扩展方向

### 短期扩展
- 添加数据导出功能
- 支持更多图表样式定制
- 增强交互性（缩放、平移）

### 长期规划
- 实时数据流支持
- 多Y轴支持
- 3D堆叠面积图
- 动画过渡效果

## 🎉 总结

这次更新成功为项目引入了强大的堆叠面积图功能，不仅提供了完整的组件实现，还包含了全面的演示、文档和工具支持。新组件完美融入现有架构，为用户提供了新的数据可视化选择，特别适合展示多维度、分类型的累积数据。

通过精心设计的数据格式和灵活的配置选项，这个组件能够适应多种业务场景，为股票分析、资金监控、板块研究等提供了新的分析工具。
