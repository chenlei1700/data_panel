<template>
  <div class="advanced-demo">
    <h2>使用工具库的高级背景色示例</h2>
    
    <div class="demo-section">
      <h3>股票综合评分表</h3>
      <TableComponent :componentConfig="stockTableConfig" />
    </div>
    
    <div class="demo-section">
      <h3>板块热度排行</h3>
      <TableComponent :componentConfig="sectorTableConfig" />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import TableComponent from './TableComponent.vue';
// 导入自定义颜色函数库
import { stockColorFunctions, sectorColorFunctions } from '@/utils/tableColorFunctions.js';

export default defineComponent({
  name: 'AdvancedColorDemo',
  components: {
    TableComponent
  },
  setup() {
    // 股票数据
    const stockData = {
      columns: [
        { field: 'name', header: '股票名称' },
        { field: 'price', header: '股价', backgroundColor: stockColorFunctions.priceRange },
        { field: 'change', header: '涨跌幅', backgroundColor: 'redGreen' },
        { field: 'pe', header: 'PE', backgroundColor: stockColorFunctions.peValuation },
        { field: 'boards', header: '连板', backgroundColor: stockColorFunctions.limitUpBoards },
        { field: 'volume', header: '成交量', backgroundColor: stockColorFunctions.volumeRank },
        { field: 'strength', header: '综合评分', backgroundColor: stockColorFunctions.strengthScore }
      ],
      rows: [
        { name: '平安银行', price: 12.5, change: 2.3, pe: 8.5, boards: 0, volume: 15000000, strength: '计算中' },
        { name: '招商银行', price: 45.2, change: -1.8, pe: 12.3, boards: 0, volume: 8000000, strength: '计算中' },
        { name: '比亚迪', price: 185.3, change: 6.2, pe: 25.6, boards: 2, volume: 35000000, strength: '计算中' },
        { name: '宁德时代', price: 320.5, change: 4.1, pe: 45.2, boards: 1, volume: 28000000, strength: '计算中' },
        { name: '贵州茅台', price: 1680.5, change: 1.2, pe: 25.4, boards: 0, volume: 3000000, strength: '计算中' }
      ]
    };

    // 板块数据
    const sectorData = {
      columns: [
        { field: 'name', header: '板块名称' },
        { field: 'change', header: '板块涨幅', backgroundColor: sectorColorFunctions.sectorHeat },
        { field: 'volumeRatio', header: '量比', backgroundColor: sectorColorFunctions.volumeRatio },
        { field: 'leadStock', header: '领涨股' },
        { field: 'stockCount', header: '上涨股票数' }
      ],
      rows: [
        { name: '新能源汽车', change: 8.5, volumeRatio: 3.2, leadStock: '比亚迪', stockCount: 45 },
        { name: '人工智能', change: 6.8, volumeRatio: 2.8, leadStock: '科大讯飞', stockCount: 38 },
        { name: '光伏概念', change: 4.2, volumeRatio: 1.9, leadStock: '隆基绿能', stockCount: 32 },
        { name: '医药生物', change: -1.2, volumeRatio: 0.8, leadStock: '恒瑞医药', stockCount: 15 },
        { name: '银行板块', change: -2.1, volumeRatio: 0.6, leadStock: '招商银行', stockCount: 8 }
      ]
    };

    const stockTableConfig = ref({
      id: 'advanced-stock-table',
      apiData: stockData
    });

    const sectorTableConfig = ref({
      id: 'advanced-sector-table', 
      apiData: sectorData
    });

    return {
      stockTableConfig,
      sectorTableConfig
    };
  }
});
</script>

<style scoped>
.advanced-demo {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.demo-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fafbfc;
}

.demo-section h3 {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}
</style>
