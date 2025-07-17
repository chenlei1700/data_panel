<template>
  <div class="complete-demo">
    <h1>TableComponent 完整背景色功能演示</h1>
    
    <!-- 新增函数演示 -->
    <div class="section">
      <h2>🆕 新增函数演示</h2>
      
      <!-- 技术指标分析 -->
      <div class="demo-card">
        <h3>技术指标综合评分 (technicalAnalysis)</h3>
        <p class="description">
          基于RSI、MACD、KDJ、移动平均线、成交量等多个技术指标进行综合评分，为股票技术面强弱提供直观的颜色标识。
        </p>
        <div class="api-info">
          <strong>API:</strong> <code>/api/table-data/technical-analysis</code>
        </div>
        <TableComponent
          dataSource="/api/table-data/technical-analysis"
          table-class="demo-table"
        />
      </div>

      <!-- 市值规模分析 -->
      <div class="demo-card">
        <h3>市值规模着色 (marketCapSize)</h3>
        <p class="description">
          根据股票市值规模进行分类着色，从微盘股到超大盘股共7个层级，便于快速识别不同规模的股票。
        </p>
        <div class="api-info">
          <strong>API:</strong> <code>/api/table-data/market-cap</code>
        </div>
        <TableComponent
          dataSource="/api/table-data/market-cap"
          table-class="demo-table"
        />
      </div>
    </div>

    <!-- 现有函数演示 -->
    <div class="section">
      <h2>📊 现有函数演示</h2>
      
      <!-- 基础函数 -->
      <div class="demo-card">
        <h3>基础背景色函数</h3>
        <div class="grid-container">
          <div class="grid-item">
            <h4>热力图 (heatmap)</h4>
            <TableComponent
              :apiData="heatmapData"
              table-class="small-table"
            />
          </div>
          <div class="grid-item">
            <h4>红绿色阶 (redGreen)</h4>
            <TableComponent
              :apiData="redGreenData"
              table-class="small-table"
            />
          </div>
          <div class="grid-item">
            <h4>百分比色阶 (percentage)</h4>
            <TableComponent
              :apiData="percentageData"
              table-class="small-table"
            />
          </div>
          <div class="grid-item">
            <h4>等级色阶 (rank)</h4>
            <TableComponent
              :apiData="rankData"
              table-class="small-table"
            />
          </div>
        </div>
      </div>

      <!-- 高级自定义函数 -->
      <div class="demo-card">
        <h3>高级自定义函数</h3>
        <div class="advanced-functions">
          <div class="function-demo">
            <h4>股票强势度 (stockStrength)</h4>
            <TableComponent
              :apiData="stockStrengthData"
              table-class="demo-table"
            />
          </div>
          
          <div class="function-demo">
            <h4>价格区间 (priceRange)</h4>
            <TableComponent
              :apiData="priceRangeData"
              table-class="demo-table"
            />
          </div>
          
          <div class="function-demo">
            <h4>涨停板梯度 (limitUpGradient)</h4>
            <TableComponent
              :apiData="limitUpData"
              table-class="demo-table"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 实时数据演示 -->
    <div class="section">
      <h2>🔄 实时数据演示</h2>
      
      <div class="demo-card">
        <h3>板块数据 (实时API)</h3>
        <TableComponent
          dataSource="/api/table-data/plates"
          table-class="demo-table"
        />
      </div>

      <div class="demo-card">
        <h3>股票数据 (实时API)</h3>
        <TableComponent
          dataSource="/api/table-data/stocks"
          table-class="demo-table"
        />
      </div>
    </div>

    <!-- 颜色图例说明 -->
    <div class="section">
      <h2>🎨 颜色图例说明</h2>
      
      <div class="legend-container">
        <div class="legend-group">
          <h4>技术指标综合评分</h4>
          <div class="legend-items">
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(220, 20, 60, 0.9);"></span>
              <span>技术面极强 (≥8分)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(255, 69, 0, 0.8);"></span>
              <span>技术面强势 (≥6分)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(255, 140, 0, 0.7);"></span>
              <span>技术面偏强 (≥4分)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(255, 215, 0, 0.6);"></span>
              <span>技术面中性偏强 (≥2分)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(240, 248, 255, 0.4);"></span>
              <span>技术面中性 (≥0分)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(255, 182, 193, 0.5);"></span>
              <span>技术面偏弱 (≥-2分)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(176, 196, 222, 0.7);"></span>
              <span>技术面弱势 (<-2分)</span>
            </div>
          </div>
        </div>

        <div class="legend-group">
          <h4>市值规模分类</h4>
          <div class="legend-items">
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(72, 61, 139, 0.5);"></span>
              <span>超大盘股 (>5000亿)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(0, 0, 205, 0.5);"></span>
              <span>大盘股 (1000-5000亿)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(30, 144, 255, 0.4);"></span>
              <span>中大盘股 (500-1000亿)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(0, 191, 255, 0.4);"></span>
              <span>中盘股 (100-500亿)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(135, 206, 250, 0.4);"></span>
              <span>中小盘股 (50-100亿)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(255, 255, 224, 0.6);"></span>
              <span>小盘股 (20-50亿)</span>
            </div>
            <div class="legend-item">
              <span class="color-sample" style="background: rgba(255, 192, 203, 0.6);"></span>
              <span>微盘股 (<20亿)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用指南 -->
    <div class="section">
      <h2>📖 使用指南</h2>
      
      <div class="guide-container">
        <div class="guide-item">
          <h4>1. 服务器端配置</h4>
          <pre><code>columns = [
  {
    "field": "stock_name",
    "header": "股票名称",
    "backgroundColor": "technicalAnalysis"
  },
  {
    "field": "market_cap", 
    "header": "市值",
    "backgroundColor": "marketCapSize"
  }
]</code></pre>
        </div>

        <div class="guide-item">
          <h4>2. 前端直接配置</h4>
          <pre><code>const tableData = {
  columns: [
    {
      field: 'rsi',
      title: 'RSI指标',
      backgroundColor: 'technicalAnalysis'
    }
  ],
  rows: [...]
};</code></pre>
        </div>

        <div class="guide-item">
          <h4>3. 支持的函数列表</h4>
          <ul>
            <li><strong>基础函数:</strong> heatmap, redGreen, percentage, rank</li>
            <li><strong>高级函数:</strong> stockStrength, priceRange, limitUpGradient, relativePerformance</li>
            <li><strong>新增函数:</strong> technicalAnalysis, marketCapSize</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import TableComponent from './TableComponent.vue';

// 基础函数演示数据
const heatmapData = ref({
  columns: [
    { field: 'name', title: '名称' },
    { field: 'value', title: '数值', backgroundColor: 'heatmap' }
  ],
  rows: [
    { name: '项目A', value: 85 },
    { name: '项目B', value: 92 },
    { name: '项目C', value: 76 },
    { name: '项目D', value: 68 }
  ]
});

const redGreenData = ref({
  columns: [
    { field: 'name', title: '名称' },
    { field: 'change', title: '涨跌幅', backgroundColor: 'redGreen' }
  ],
  rows: [
    { name: '股票A', change: 5.2 },
    { name: '股票B', change: -2.8 },
    { name: '股票C', change: 1.5 },
    { name: '股票D', change: -0.9 }
  ]
});

const percentageData = ref({
  columns: [
    { field: 'name', title: '名称' },
    { field: 'percent', title: '百分比', backgroundColor: 'percentage' }
  ],
  rows: [
    { name: '指标A', percent: 75 },
    { name: '指标B', percent: 45 },
    { name: '指标C', percent: 88 },
    { name: '指标D', percent: 32 }
  ]
});

const rankData = ref({
  columns: [
    { field: 'name', title: '名称' },
    { field: 'score', title: '评分', backgroundColor: 'rank' }
  ],
  rows: [
    { name: '选手A', score: 95 },
    { name: '选手B', score: 87 },
    { name: '选手C', score: 92 },
    { name: '选手D', score: 79 }
  ]
});

// 高级函数演示数据
const stockStrengthData = ref({
  columns: [
    { field: 'stock_name', title: '股票名称' },
    { field: 'change', title: '涨幅(%)', backgroundColor: 'stockStrength' },
    { field: 'volume_ratio', title: '量比', backgroundColor: 'stockStrength' },
    { field: '开盘换手率', title: '换手率', backgroundColor: 'stockStrength' }
  ],
  rows: [
    { stock_name: '强势股A', change: 8.5, volume_ratio: 3.2, 开盘换手率: 12.5 },
    { stock_name: '普通股B', change: 2.1, volume_ratio: 1.5, 开盘换手率: 4.2 },
    { stock_name: '弱势股C', change: -3.2, volume_ratio: 0.6, 开盘换手率: 1.8 }
  ]
});

const priceRangeData = ref({
  columns: [
    { field: 'stock_name', title: '股票名称' },
    { field: 'price', title: '股价', backgroundColor: 'priceRange' }
  ],
  rows: [
    { stock_name: '贵州茅台', price: 1680 },
    { stock_name: '五粮液', price: 128 },
    { stock_name: '中小盘股', price: 25 },
    { stock_name: '低价股', price: 6.5 }
  ]
});

const limitUpData = ref({
  columns: [
    { field: 'stock_name', title: '股票名称' },
    { field: '连板数', title: '连板数', backgroundColor: 'limitUpGradient' }
  ],
  rows: [
    { stock_name: '连板龙头', 连板数: 5 },
    { stock_name: '三板股', 连板数: 3 },
    { stock_name: '二板股', 连板数: 2 },
    { stock_name: '首板股', 连板数: 1 }
  ]
});
</script>

<style scoped>
.complete-demo {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #f8f9fa;
}

.complete-demo h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 30px;
  font-size: 2.5em;
  border-bottom: 3px solid #3498db;
  padding-bottom: 15px;
}

.section {
  margin-bottom: 40px;
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.section h2 {
  color: #34495e;
  margin-bottom: 20px;
  font-size: 1.8em;
  display: flex;
  align-items: center;
  gap: 10px;
}

.demo-card {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e0e6ed;
  border-radius: 8px;
  background-color: #fafbfc;
}

.demo-card h3 {
  color: #2980b9;
  margin-bottom: 10px;
  font-size: 1.4em;
}

.description {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.6;
  font-size: 14px;
}

.api-info {
  margin-bottom: 15px;
  padding: 8px 12px;
  background-color: #e8f4f8;
  border-radius: 4px;
  font-size: 13px;
}

.api-info code {
  background-color: #d1ecf1;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.grid-item {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background-color: white;
}

.grid-item h4 {
  color: #27ae60;
  margin-bottom: 10px;
  font-size: 1.1em;
}

.advanced-functions {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.function-demo h4 {
  color: #8e44ad;
  margin-bottom: 15px;
  font-size: 1.2em;
}

.legend-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-top: 20px;
}

.legend-group {
  padding: 20px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background-color: white;
}

.legend-group h4 {
  color: #495057;
  margin-bottom: 15px;
  font-size: 1.2em;
  border-bottom: 2px solid #28a745;
  padding-bottom: 5px;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.color-sample {
  width: 20px;
  height: 15px;
  border: 1px solid #ccc;
  border-radius: 3px;
  display: inline-block;
}

.guide-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-top: 20px;
}

.guide-item {
  padding: 20px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background-color: white;
}

.guide-item h4 {
  color: #fd7e14;
  margin-bottom: 15px;
  font-size: 1.1em;
}

.guide-item pre {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  font-size: 13px;
  border: 1px solid #e9ecef;
}

.guide-item ul {
  padding-left: 20px;
}

.guide-item li {
  margin-bottom: 8px;
  line-height: 1.5;
}

:deep(.demo-table) {
  margin-top: 15px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
}

:deep(.small-table) {
  font-size: 12px;
}

:deep(.demo-table th) {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

:deep(.demo-table td),
:deep(.demo-table th) {
  padding: 10px 12px;
  border: 1px solid #dee2e6;
  text-align: center;
}

:deep(.small-table td),
:deep(.small-table th) {
  padding: 6px 8px;
  font-size: 11px;
}
</style>
