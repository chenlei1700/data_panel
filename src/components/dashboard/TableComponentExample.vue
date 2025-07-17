<template>
  <div class="example-container">
    <h2>TableComponent 背景色功能示例</h2>
    
    <!-- 基本用法示例 -->
    <div class="example-section">
      <h3>1. 基本热力图示例</h3>
      <TableComponent :componentConfig="heatmapConfig" />
    </div>
    
    <!-- 红绿色阶示例 -->
    <div class="example-section">
      <h3>2. 红绿色阶示例（正负值）</h3>
      <TableComponent :componentConfig="redGreenConfig" />
    </div>
    
    <!-- 自定义函数示例 -->
    <div class="example-section">
      <h3>3. 自定义背景色函数示例</h3>
      <TableComponent :componentConfig="customConfig" />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import TableComponent from './TableComponent.vue';

export default defineComponent({
  name: 'TableComponentExample',
  components: {
    TableComponent
  },
  setup() {
    // 示例数据
    const sampleData = {
      columns: [
        { field: 'name', header: '股票名称' },
        { field: 'price', header: '当前价格', backgroundColor: 'heatmap' },
        { field: 'change', header: '涨跌幅', backgroundColor: 'redGreen' },
        { field: 'volume', header: '成交量', backgroundColor: 'rank' },
        { field: 'ratio', header: '换手率', backgroundColor: 'percentage' }
      ],
      rows: [
        { name: '平安银行', price: 12.5, change: 2.3, volume: 15000000, ratio: 3.2 },
        { name: '招商银行', price: 45.2, change: -1.8, volume: 8000000, ratio: 1.5 },
        { name: '中国平安', price: 56.8, change: 0.5, volume: 12000000, ratio: 2.1 },
        { name: '万科A', price: 23.1, change: -0.8, volume: 20000000, ratio: 4.5 },
        { name: '格力电器', price: 38.9, change: 3.2, volume: 5000000, ratio: 1.2 }
      ]
    };

    // 热力图配置
    const heatmapConfig = ref({
      id: 'heatmap-table',
      dataSource: '', // 这里通过直接设置 apiData 来模拟
      apiData: sampleData
    });

    // 红绿色阶配置
    const redGreenConfig = ref({
      id: 'redgreen-table', 
      apiData: {
        ...sampleData,
        columns: sampleData.columns.map(col => ({
          ...col,
          backgroundColor: col.field === 'change' ? 'redGreen' : undefined
        }))
      }
    });

    // 自定义函数配置
    const customBackgroundFunction = (value, column, row, allRows) => {
      // 自定义逻辑：根据价格区间设置不同颜色
      if (column.field === 'price') {
        const numValue = parseFloat(value);
        if (numValue > 50) return 'rgba(255, 215, 0, 0.3)'; // 金色
        if (numValue > 30) return 'rgba(0, 255, 0, 0.3)';   // 绿色
        if (numValue > 20) return 'rgba(255, 255, 0, 0.3)'; // 黄色
        return 'rgba(255, 165, 0, 0.3)';                    // 橙色
      }
      return 'transparent';
    };

    const customConfig = ref({
      id: 'custom-table',
      apiData: {
        ...sampleData,
        columns: sampleData.columns.map(col => ({
          ...col,
          backgroundColor: col.field === 'price' ? customBackgroundFunction : undefined
        }))
      }
    });

    return {
      heatmapConfig,
      redGreenConfig,
      customConfig
    };
  }
});
</script>

<style scoped>
.example-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.example-section {
  margin-bottom: 40px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
}

.example-section h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}
</style>
