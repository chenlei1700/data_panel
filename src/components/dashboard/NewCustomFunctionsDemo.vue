<template>
  <div class="new-functions-demo">
    <h2>新增自定义背景色函数演示</h2>
    
    <!-- 技术指标综合评分演示 -->
    <div class="demo-section">
      <h3>1. 技术指标综合评分着色 (technicalAnalysis)</h3>
      <p class="description">
        基于RSI、MACD、KDJ、移动平均线等技术指标进行综合评分着色，评估股票技术面强弱。
      </p>
      
      <div class="legend">
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(220, 20, 60, 0.9);"></span>
          <span>技术面极强 (评分≥8)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(255, 69, 0, 0.8);"></span>
          <span>技术面强势 (评分≥6)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(255, 140, 0, 0.7);"></span>
          <span>技术面偏强 (评分≥4)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(255, 215, 0, 0.6);"></span>
          <span>技术面中性偏强 (评分≥2)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(240, 248, 255, 0.4);"></span>
          <span>技术面中性 (评分≥0)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(255, 182, 193, 0.5);"></span>
          <span>技术面偏弱 (评分≥-2)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(176, 196, 222, 0.7);"></span>
          <span>技术面弱势 (评分<-2)</span>
        </div>
      </div>

      <TableComponent
        :apiData="technicalData"
        table-class="demo-table"
        style="margin-top: 20px;"
      />
    </div>

    <!-- 市值规模着色演示 -->
    <div class="demo-section">
      <h3>2. 市值规模着色 (marketCapSize)</h3>
      <p class="description">
        根据股票市值规模进行分类着色，便于识别不同规模的股票。
      </p>
      
      <div class="legend">
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(72, 61, 139, 0.5);"></span>
          <span>超大盘股 (市值>5000亿)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(0, 0, 205, 0.5);"></span>
          <span>大盘股 (1000-5000亿)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(30, 144, 255, 0.4);"></span>
          <span>中大盘股 (500-1000亿)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(0, 191, 255, 0.4);"></span>
          <span>中盘股 (100-500亿)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(135, 206, 250, 0.4);"></span>
          <span>中小盘股 (50-100亿)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(255, 255, 224, 0.6);"></span>
          <span>小盘股 (20-50亿)</span>
        </div>
        <div class="legend-item">
          <span class="color-box" style="background-color: rgba(255, 192, 203, 0.6);"></span>
          <span>微盘股 (<20亿)</span>
        </div>
      </div>

      <TableComponent
        :apiData="marketCapData"
        table-class="demo-table"
        style="margin-top: 20px;"
      />
    </div>

    <!-- 使用说明 -->
    <div class="demo-section">
      <h3>使用说明</h3>
      <div class="usage-guide">
        <h4>1. 技术指标综合评分函数 (technicalAnalysis)</h4>
        <ul>
          <li><strong>RSI指标 (25%权重):</strong> 相对强弱指标，判断超买超卖状态</li>
          <li><strong>MACD指标 (20%权重):</strong> 指数平滑异同移动平均线，判断趋势强弱</li>
          <li><strong>KDJ指标 (20%权重):</strong> 随机指标，判断短期买卖时机</li>
          <li><strong>移动平均线 (20%权重):</strong> MA5和MA20，判断趋势方向</li>
          <li><strong>成交量确认 (15%权重):</strong> 量比指标，确认价格走势的有效性</li>
        </ul>

        <h4>2. 市值规模函数 (marketCapSize)</h4>
        <ul>
          <li>根据市值大小自动分类着色</li>
          <li>支持从微盘股到超大盘股的7个层级</li>
          <li>颜色从暖色调（小盘）到冷色调（大盘）渐变</li>
        </ul>

        <h4>3. 服务器端配置示例</h4>
        <pre><code>columns: [
  {
    field: 'stock_code',
    title: '股票代码',
    backgroundColor: 'technicalAnalysis'
  },
  {
    field: 'market_cap',
    title: '市值',
    backgroundColor: 'marketCapSize'
  }
]</code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import TableComponent from './TableComponent.vue';

// 技术指标演示数据
const technicalData = ref({
  columns: [
    { field: 'stock_name', title: '股票名称' },
    { field: 'current_price', title: '现价' },
    { field: 'RSI', title: 'RSI', backgroundColor: 'technicalAnalysis' },
    { field: 'MACD', title: 'MACD', backgroundColor: 'technicalAnalysis' },
    { field: 'KDJ_K', title: 'KDJ_K', backgroundColor: 'technicalAnalysis' },
    { field: 'KDJ_D', title: 'KDJ_D', backgroundColor: 'technicalAnalysis' },
    { field: 'MA5', title: 'MA5', backgroundColor: 'technicalAnalysis' },
    { field: 'MA20', title: 'MA20', backgroundColor: 'technicalAnalysis' },
    { field: '量比', title: '量比', backgroundColor: 'technicalAnalysis' }
  ],
  rows: [
    {
      stock_name: '贵州茅台',
      current_price: 1680.50,
      RSI: 75.2,
      MACD: 0.8,
      KDJ_K: 85.3,
      KDJ_D: 78.1,
      MA5: 1675.20,
      MA20: 1650.80,
      量比: 2.1
    },
    {
      stock_name: '五粮液',
      current_price: 128.30,
      RSI: 45.8,
      MACD: -0.2,
      KDJ_K: 35.6,
      KDJ_D: 42.1,
      MA5: 130.50,
      MA20: 125.30,
      量比: 0.8
    },
    {
      stock_name: '宁德时代',
      current_price: 185.20,
      RSI: 65.4,
      MACD: 0.5,
      KDJ_K: 72.8,
      KDJ_D: 68.3,
      MA5: 182.10,
      MA20: 175.60,
      量比: 1.5
    },
    {
      stock_name: '比亚迪',
      current_price: 245.80,
      RSI: 58.2,
      MACD: 0.1,
      KDJ_K: 55.7,
      KDJ_D: 52.4,
      MA5: 248.30,
      MA20: 240.90,
      量比: 1.2
    },
    {
      stock_name: '东方财富',
      current_price: 15.60,
      RSI: 28.5,
      MACD: -0.8,
      KDJ_K: 18.2,
      KDJ_D: 25.6,
      MA5: 16.80,
      MA20: 17.20,
      量比: 0.4
    }
  ]
});

// 市值规模演示数据
const marketCapData = ref({
  columns: [
    { field: 'stock_name', title: '股票名称' },
    { field: 'market_cap', title: '市值(亿)', backgroundColor: 'marketCapSize' },
    { field: 'price', title: '股价(元)' },
    { field: 'scale_type', title: '规模类型' }
  ],
  rows: [
    {
      stock_name: '贵州茅台',
      market_cap: 210000000000,  // 2100亿
      price: 1680.50,
      scale_type: '大盘股'
    },
    {
      stock_name: '中国平安',
      market_cap: 120000000000,  // 1200亿
      price: 65.30,
      scale_type: '大盘股'
    },
    {
      stock_name: '宁德时代',
      market_cap: 80000000000,   // 800亿
      price: 185.20,
      scale_type: '中大盘股'
    },
    {
      stock_name: '比亚迪',
      market_cap: 70000000000,   // 700亿
      price: 245.80,
      scale_type: '中大盘股'
    },
    {
      stock_name: '立讯精密',
      market_cap: 30000000000,   // 300亿
      price: 42.60,
      scale_type: '中盘股'
    },
    {
      stock_name: '恒瑞医药',
      market_cap: 8000000000,    // 80亿
      price: 58.20,
      scale_type: '中小盘股'
    },
    {
      stock_name: '三六零',
      market_cap: 3500000000,    // 35亿
      price: 12.80,
      scale_type: '小盘股'
    },
    {
      stock_name: '某科技股',
      market_cap: 1500000000,    // 15亿
      price: 8.50,
      scale_type: '微盘股'
    }
  ]
});
</script>

<style scoped>
.new-functions-demo {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.demo-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fafafa;
}

.demo-section h3 {
  color: #333;
  margin-bottom: 10px;
  border-bottom: 2px solid #4CAF50;
  padding-bottom: 5px;
}

.description {
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 5px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.color-box {
  width: 20px;
  height: 15px;
  border: 1px solid #ccc;
  border-radius: 3px;
}

.usage-guide {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  border-left: 4px solid #2196F3;
}

.usage-guide h4 {
  color: #2196F3;
  margin-bottom: 10px;
}

.usage-guide ul {
  margin-bottom: 20px;
  padding-left: 20px;
}

.usage-guide li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.usage-guide pre {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  border: 1px solid #ddd;
}

.usage-guide code {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.demo-table {
  margin-top: 20px;
}

:deep(.demo-table) {
  border: 1px solid #e0e0e0;
  border-radius: 5px;
}

:deep(.demo-table th) {
  background-color: #f0f0f0;
  font-weight: bold;
}

:deep(.demo-table td),
:deep(.demo-table th) {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  text-align: center;
}
</style>
