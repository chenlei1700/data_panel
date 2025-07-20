# 📊 堆叠面积图组件使用指南

## 概述

堆叠面积图组件（`StackedAreaChartComponent`）是一个专门用于展示三维数据的可视化组件。它可以处理具有以下结构的数据：

- **维度1 (X轴)**：横坐标值，通常是时间序列或类别
- **维度2 (Y轴)**：纵坐标值，由第三维度的各个值累加而成
- **维度3 (字典)**：每个X轴点对应的字典数据，字典中的各个key的值会被累加

## 🎯 主要特点

- ✅ **堆叠面积显示**：将字典中各key的值按指定顺序累加，形成堆叠面积图
- ✅ **折线连接**：每个key在各X轴点的累积值形成一条折线
- ✅ **区域填充**：相邻折线之间的区域使用不同颜色填充
- ✅ **可选表格**：支持在图表上方显示汇总数据的表格
- ✅ **自定义颜色**：支持自定义颜色方案和表格单元格颜色映射
- ✅ **交互式悬停**：鼠标悬停显示详细的数值信息

## 📝 数据格式要求

### 后端API响应格式

```json
{
  "stackedAreaData": {
    "data": {
      "09:30": {"基础资金": 10.5, "成长资金": 15.2, "价值资金": 8.3},
      "10:00": {"基础资金": 12.1, "成长资金": 18.7, "价值资金": 9.8},
      "10:30": {"基础资金": 14.3, "成长资金": 16.5, "价值资金": 11.2}
    },
    "keyOrder": ["基础资金", "成长资金", "价值资金"],
    "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
  },
  "xAxisValues": ["09:30", "10:00", "10:30"],
  "tableData": {
    "09:30": "34.0亿",
    "10:00": "40.6亿", 
    "10:30": "42.0亿"
  }
}
```

### 数据字段说明

- **stackedAreaData.data**: 主要数据对象，key为X轴值，value为该点的字典数据
- **stackedAreaData.keyOrder**: 指定字典中key的堆叠顺序（从下到上）
- **stackedAreaData.colors**: 可选，自定义颜色数组
- **xAxisValues**: X轴值的顺序数组
- **tableData**: 可选，表格显示的数据，key为X轴值，value为显示内容

## 🛠️ 使用方法

### 1. 在仪表盘配置中使用

```javascript
// 在dashboard配置中
{
  "id": "stackedAreaChart1",
  "type": "stackedAreaChart",
  "dataSource": "/api/chart-data/stacked-area-demo",
  "title": "资金流向堆叠面积图",
  "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
}
```

### 2. 在Vue组件中直接使用

```vue
<template>
  <div class="chart-container">
    <StackedAreaChartComponent :component-config="chartConfig" />
  </div>
</template>

<script>
import StackedAreaChartComponent from '@/components/dashboard/StackedAreaChartComponent.vue';

export default {
  components: {
    StackedAreaChartComponent
  },
  data() {
    return {
      chartConfig: {
        id: 'my-stacked-chart',
        type: 'stackedAreaChart',
        dataSource: '/api/my-stacked-data',
        title: '我的堆叠面积图',
        // 可选：自定义表格颜色函数
        tableCellColors: (value) => {
          const numValue = parseFloat(value);
          if (numValue > 50) return 'rgba(76, 175, 80, 0.6)';
          if (numValue > 30) return 'rgba(255, 193, 7, 0.6)';
          return 'rgba(244, 67, 54, 0.6)';
        }
      }
    }
  }
}
</script>
```

## 🎨 自定义表格颜色

支持通过配置`tableCellColors`属性来自定义表格单元格的背景颜色：

```javascript
// 方式1：使用函数
tableCellColors: (value) => {
  const numValue = parseFloat(value);
  if (numValue > 100) return 'rgba(255, 107, 107, 0.8)';
  if (numValue > 50) return 'rgba(255, 193, 7, 0.6)';
  return 'rgba(76, 175, 80, 0.4)';
}

// 方式2：使用预定义颜色映射
tableCellColors: {
  '高': '#ff4757',
  '中': '#ffa502', 
  '低': '#2ed573'
}
```

## 📊 后端API实现示例

### Flask后端示例

```python
@app.route('/api/chart-data/stacked-area-demo')
def get_stacked_area_data():
    # 定义时间点
    x_values = ["09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00"]
    
    # 定义key的顺序（从下到上堆叠）
    key_order = ["基础资金", "成长资金", "价值资金", "投机资金", "机构资金"]
    
    # 定义颜色
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
    
    # 生成每个时间点的数据
    data = {}
    table_data = {}
    
    for x_val in x_values:
        point_data = {}
        total_value = 0
        
        for key in key_order:
            # 生成随机值（实际应用中从数据库获取）
            value = round(random.uniform(10, 50), 1)
            point_data[key] = value
            total_value += value
        
        data[x_val] = point_data
        table_data[x_val] = f"{total_value:.1f}亿"
    
    return jsonify({
        "stackedAreaData": {
            "data": data,
            "keyOrder": key_order,
            "colors": colors
        },
        "xAxisValues": x_values,
        "tableData": table_data
    })
```

## 🔧 技术实现细节

### 累积值计算

组件会自动处理数据的累积计算：

```javascript
// 例如原始数据：
// 时间点1: {"A": 10, "B": 15, "C": 8}
// 
// 计算后的累积值：
// A的线: y = 10
// B的线: y = 10 + 15 = 25  
// C的线: y = 10 + 15 + 8 = 33
//
// 填充区域：
// A区域: 0 到 10
// B区域: 10 到 25
// C区域: 25 到 33
```

### 图表渲染

使用Plotly.js进行渲染，每个key对应一个trace：

```javascript
traces.push({
  x: xValues,
  y: cumulativeYValues,
  name: key,
  type: 'scatter',
  mode: 'lines',
  fill: index === 0 ? 'tozeroy' : 'tonexty', // 关键：填充方式
  fillcolor: color + '80', // 添加透明度
  line: { color: color, width: 2 }
});
```

## 🐛 常见问题

### Q1: 图表不显示数据
- 检查API返回的数据格式是否正确
- 确认`keyOrder`数组中的key在`data`中都存在
- 检查浏览器控制台是否有错误信息

### Q2: 颜色显示不正确
- 确认`colors`数组长度不少于`keyOrder`长度
- 颜色格式应为有效的CSS颜色值（如"#FF6B6B"）

### Q3: 表格不显示
- 检查`tableData`字段是否存在于API响应中
- 确认`tableData`的key与`xAxisValues`匹配

### Q4: 累积值计算错误
- 确认`data`中每个时间点的字典包含所有key
- 检查数据中是否有NaN或undefined值

## 🚀 性能优化

- 数据量大时，考虑在后端进行数据预处理
- 使用适当的缓存策略减少API调用
- 大量数据点时考虑数据采样

## 📈 扩展功能

可以基于当前组件扩展以下功能：

- 支持多个Y轴
- 添加数据导出功能  
- 支持实时数据更新动画
- 添加缩放和平移功能
- 支持数据点标注

## 📞 技术支持

如有问题或建议，请：

1. 查看浏览器控制台错误信息
2. 检查API响应数据格式
3. 参考项目中的演示页面 (`/stacked-area-demo`)
4. 查看源码中的注释和实现细节
