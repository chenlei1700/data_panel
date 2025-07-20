<!-- 堆叠面积图组件使用示例页面 -->
<template>
  <div class="stacked-area-demo-page">
    <div class="page-header">
      <h1>📊 堆叠面积图组件演示</h1>
      <p class="description">
        展示新增的堆叠面积图组件，支持三维数据可视化：X轴、Y轴累积值、以及每个X点的字典数据分解
      </p>
    </div>

    <div class="demo-sections">
      <!-- 基本示例 -->
      <div class="demo-section">
        <h2>🎯 基本堆叠面积图</h2>
        <div class="chart-container">
          <StackedAreaChartComponent :component-config="basicConfig" />
        </div>
      </div>

      <!-- 带表格的示例 -->
      <div class="demo-section">
        <h2>📋 带上方表格的堆叠面积图</h2>
        <div class="chart-container">
          <StackedAreaChartComponent :component-config="tableConfig" />
        </div>
      </div>

      <!-- 自定义颜色示例 -->
      <div class="demo-section">
        <h2>🎨 自定义颜色配置</h2>
        <div class="chart-container">
          <StackedAreaChartComponent :component-config="customColorConfig" />
        </div>
      </div>
    </div>

    <div class="feature-explanation">
      <h2>✨ 功能特点</h2>
      <div class="features">
        <div class="feature">
          <h3>📈 堆叠面积显示</h3>
          <p>将字典中各个key的值按顺序累加，形成堆叠效果，每个区域代表一个key的贡献</p>
        </div>
        <div class="feature">
          <h3>🎯 鼠标悬停详情</h3>
          <p>悬停时显示当前key的原始值和累积值，提供详细的数据分析</p>
        </div>
        <div class="feature">
          <h3>📋 可选表格显示</h3>
          <p>可在图表上方显示表格，展示每个X轴点对应的汇总数据</p>
        </div>
        <div class="feature">
          <h3>🎨 自定义颜色</h3>
          <p>支持自定义颜色配置和表格单元格颜色映射函数</p>
        </div>
      </div>
    </div>

    <div class="usage-guide">
      <h2>📖 使用指南</h2>
      
      <h3>数据格式要求</h3>
      <pre><code>{
  "stackedAreaData": {
    "data": {
      "时间点1": {"key1": 10, "key2": 15, "key3": 8},
      "时间点2": {"key1": 12, "key2": 18, "key3": 10},
      ...
    },
    "keyOrder": ["key1", "key2", "key3"],
    "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
  },
  "xAxisValues": ["时间点1", "时间点2", ...],
  "tableData": {
    "时间点1": "25.3亿",
    "时间点2": "30.1亿"
  }
}</code></pre>

      <h3>组件配置</h3>
      <pre><code>{
  "id": "stackedChart1",
  "type": "stackedAreaChart", 
  "dataSource": "/api/chart-data/stacked-area-demo",
  "title": "资金流向堆叠分析",
  "tableCellColors": colorFunction  // 可选的表格颜色函数
}</code></pre>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import StackedAreaChartComponent from '@/components/dashboard/StackedAreaChartComponent.vue';

export default defineComponent({
  name: 'StackedAreaDemoPage',
  components: {
    StackedAreaChartComponent
  },
  setup() {
    // 基本配置（不带表格）
    const basicConfig = ref({
      id: 'demo-basic',
      type: 'stackedAreaChart',
      dataSource: '/api/chart-data/stacked-area-no-table',
      title: '基础堆叠面积图演示（不带表格）'
    });

    // 带表格配置
    const tableConfig = ref({
      id: 'demo-table',
      type: 'stackedAreaChart', 
      dataSource: '/api/chart-data/stacked-area-demo',
      title: '带表格的堆叠面积图演示（显示成交额汇总）'
    });

    // 自定义颜色配置
    const customColorConfig = ref({
      id: 'demo-custom',
      type: 'stackedAreaChart',
      dataSource: '/api/chart-data/stacked-area-demo',
      title: '自定义颜色堆叠面积图',
      tableCellColors: (value) => {
        if (!value) return 'transparent';
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return 'transparent';
        
        // 根据数值大小返回不同颜色
        if (numValue > 150) return 'rgba(255, 107, 107, 0.8)';
        if (numValue > 100) return 'rgba(255, 193, 7, 0.6)';
        if (numValue > 50) return 'rgba(76, 175, 80, 0.4)';
        return 'rgba(33, 150, 243, 0.3)';
      }
    });

    return {
      basicConfig,
      tableConfig,
      customColorConfig
    };
  }
});
</script>

<style scoped>
.stacked-area-demo-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5em;
}

.description {
  font-size: 1.1em;
  opacity: 0.9;
  margin: 0;
}

.demo-sections {
  margin-bottom: 40px;
}

.demo-section {
  margin-bottom: 40px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.demo-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  padding-bottom: 10px;
  border-bottom: 2px solid #eee;
}

.chart-container {
  height: 500px;
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
}

.feature-explanation {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.feature-explanation h2 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature {
  padding: 15px;
  border-left: 4px solid #667eea;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.feature h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.feature p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.usage-guide {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.usage-guide h2 {
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.usage-guide h3 {
  color: #555;
  margin: 20px 0 10px 0;
}

.usage-guide pre {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 15px;
  overflow-x: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9em;
  line-height: 1.4;
}

.usage-guide code {
  color: #e83e8c;
}
</style>
