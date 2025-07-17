<template>
  <div class="custom-function-demo">
    <h2>自定义背景色函数示例</h2>
    
    <!-- 示例1：在组件中定义自定义函数 -->
    <div class="demo-section">
      <h3>示例1：简单的价格区间着色</h3>
      <TableComponent :componentConfig="priceColorConfig" />
    </div>
    
    <!-- 示例2：复杂的多条件判断 -->
    <div class="demo-section">
      <h3>示例2：多条件判断着色</h3>
      <TableComponent :componentConfig="complexColorConfig" />
    </div>
    
    <!-- 示例3：动态计算相对排名着色 -->
    <div class="demo-section">
      <h3>示例3：动态相对排名着色</h3>
      <TableComponent :componentConfig="rankColorConfig" />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import TableComponent from './TableComponent.vue';

export default defineComponent({
  name: 'CustomFunctionDemo',
  components: {
    TableComponent
  },
  setup() {
    // 示例数据
    const stockData = {
      rows: [
        { name: '平安银行', price: 12.5, change: 2.3, volume: 15000000, pe: 8.5, status: 'rising' },
        { name: '招商银行', price: 45.2, change: -1.8, volume: 8000000, pe: 12.3, status: 'falling' },
        { name: '中国平安', price: 56.8, change: 0.5, volume: 12000000, pe: 15.6, status: 'stable' },
        { name: '万科A', price: 23.1, change: -0.8, volume: 20000000, pe: 35.2, status: 'falling' },
        { name: '格力电器', price: 38.9, change: 3.2, volume: 5000000, pe: 6.8, status: 'rising' },
        { name: '贵州茅台', price: 1680.5, change: 1.2, volume: 3000000, pe: 25.4, status: 'rising' },
        { name: '比亚迪', price: 185.3, change: -2.1, volume: 25000000, pe: 45.6, status: 'falling' }
      ]
    };

    // 自定义函数1：简单的价格区间着色
    const priceRangeColorFunction = (value, column, row, allRows) => {
      if (column.field === 'price') {
        const price = parseFloat(value);
        if (price > 1000) return 'rgba(138, 43, 226, 0.3)';  // 紫色 - 超高价股
        if (price > 100) return 'rgba(255, 215, 0, 0.3)';    // 金色 - 高价股
        if (price > 50) return 'rgba(0, 255, 0, 0.3)';       // 绿色 - 中价股
        if (price > 20) return 'rgba(255, 255, 0, 0.3)';     // 黄色 - 中低价股
        return 'rgba(255, 165, 0, 0.3)';                     // 橙色 - 低价股
      }
      return 'transparent';
    };

    // 自定义函数2：复杂的多条件判断着色
    const complexColorFunction = (value, column, row, allRows) => {
      // 根据多个字段综合判断
      if (column.field === 'status') {
        const change = parseFloat(row.change);
        const volume = parseFloat(row.volume);
        const pe = parseFloat(row.pe);
        
        // 强势股：涨幅>2% 且 成交量>10M 且 PE<20
        if (change > 2 && volume > 10000000 && pe < 20) {
          return 'rgba(34, 139, 34, 0.6)'; // 深绿色
        }
        
        // 高风险股：跌幅>1% 且 PE>30
        if (change < -1 && pe > 30) {
          return 'rgba(220, 20, 60, 0.6)'; // 深红色
        }
        
        // 稳健股：涨跌幅在±1%以内 且 PE在10-25之间
        if (Math.abs(change) <= 1 && pe >= 10 && pe <= 25) {
          return 'rgba(70, 130, 180, 0.4)'; // 钢蓝色
        }
        
        // 活跃股：成交量>15M
        if (volume > 15000000) {
          return 'rgba(255, 140, 0, 0.4)'; // 橙色
        }
      }
      
      return 'transparent';
    };

    // 自定义函数3：动态相对排名着色
    const dynamicRankColorFunction = (value, column, row, allRows) => {
      if (column.field === 'volume') {
        // 获取所有成交量数据
        const volumes = allRows.map(r => parseFloat(r.volume)).sort((a, b) => b - a);
        const currentVolume = parseFloat(value);
        
        // 计算当前值在所有值中的排名百分位
        const rank = volumes.indexOf(currentVolume);
        const percentile = rank / (volumes.length - 1);
        
        // 根据排名百分位设置颜色强度
        if (percentile <= 0.2) {
          return `rgba(255, 0, 0, ${0.8 - percentile * 2})`; // 前20% - 红色渐变
        } else if (percentile <= 0.4) {
          return `rgba(255, 165, 0, ${0.6 - (percentile - 0.2) * 2})`; // 21-40% - 橙色渐变
        } else if (percentile <= 0.6) {
          return `rgba(255, 255, 0, ${0.4 - (percentile - 0.4) * 2})`; // 41-60% - 黄色渐变
        } else if (percentile <= 0.8) {
          return `rgba(173, 255, 47, ${0.3 - (percentile - 0.6) * 1.5})`; // 61-80% - 绿黄色渐变
        } else {
          return `rgba(211, 211, 211, 0.2)`; // 后20% - 浅灰色
        }
      }
      
      return 'transparent';
    };

    // 自定义函数4：基于PE估值的着色
    const peValuationColorFunction = (value, column, row, allRows) => {
      if (column.field === 'pe') {
        const pe = parseFloat(value);
        
        // 低估值 (PE < 15)
        if (pe < 15) {
          const intensity = Math.max(0.2, 0.6 - pe * 0.03);
          return `rgba(0, 255, 0, ${intensity})`;
        }
        
        // 合理估值 (15 <= PE <= 25)
        if (pe <= 25) {
          return 'rgba(255, 255, 0, 0.2)';
        }
        
        // 高估值 (PE > 25)
        const intensity = Math.min(0.8, 0.3 + (pe - 25) * 0.02);
        return `rgba(255, 0, 0, ${intensity})`;
      }
      
      return 'transparent';
    };

    // 配置1：价格区间着色
    const priceColorConfig = ref({
      id: 'price-color-table',
      apiData: {
        columns: [
          { field: 'name', header: '股票名称' },
          { field: 'price', header: '股价', backgroundColor: priceRangeColorFunction },
          { field: 'change', header: '涨跌幅' },
          { field: 'volume', header: '成交量' },
          { field: 'pe', header: 'PE' }
        ],
        rows: stockData.rows
      }
    });

    // 配置2：复杂条件着色
    const complexColorConfig = ref({
      id: 'complex-color-table',
      apiData: {
        columns: [
          { field: 'name', header: '股票名称' },
          { field: 'price', header: '股价' },
          { field: 'change', header: '涨跌幅' },
          { field: 'volume', header: '成交量' },
          { field: 'pe', header: 'PE', backgroundColor: peValuationColorFunction },
          { field: 'status', header: '综合状态', backgroundColor: complexColorFunction }
        ],
        rows: stockData.rows
      }
    });

    // 配置3：动态排名着色
    const rankColorConfig = ref({
      id: 'rank-color-table',
      apiData: {
        columns: [
          { field: 'name', header: '股票名称' },
          { field: 'price', header: '股价' },
          { field: 'change', header: '涨跌幅', backgroundColor: 'redGreen' },
          { field: 'volume', header: '成交量', backgroundColor: dynamicRankColorFunction },
          { field: 'pe', header: 'PE' }
        ],
        rows: stockData.rows
      }
    });

    return {
      priceColorConfig,
      complexColorConfig,
      rankColorConfig
    };
  }
});
</script>

<style scoped>
.custom-function-demo {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.demo-section {
  margin-bottom: 50px;
  padding: 25px;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  background: linear-gradient(145deg, #fafbfc, #f5f7fa);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.demo-section h3 {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 3px solid #3498db;
  padding-bottom: 12px;
  font-size: 1.3em;
}
</style>
