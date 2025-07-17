<template>
  <div class="custom-functions-showcase">
    <h2>📊 新增自定义背景色函数展示</h2>
    
    <!-- 股票强势度评分示例 -->
    <div class="demo-section">
      <h3>🔥 股票强势度综合评分着色</h3>
      <p class="description">基于涨幅、成交量、换手率、连板数、PE等多个指标综合评分</p>
      <TableComponent :componentConfig="strengthTableConfig" />
      <div class="color-legend">
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 0, 0, 0.8);"></span>超强势 (≥7分)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 69, 0, 0.7);"></span>强势 (5-6分)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 140, 0, 0.6);"></span>较强势 (3-4分)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 215, 0, 0.5);"></span>偏强势 (1-2分)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(144, 238, 144, 0.4);"></span>中性 (0分)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 182, 193, 0.5);"></span>偏弱势 (-1至-2分)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(220, 20, 60, 0.6);"></span>弱势 (<-2分)</span>
      </div>
    </div>

    <!-- 价格区间着色示例 -->
    <div class="demo-section">
      <h3>💰 价格区间着色</h3>
      <p class="description">根据股价区间显示不同颜色，便于识别高价股和低价股</p>
      <TableComponent :componentConfig="priceRangeTableConfig" />
      <div class="color-legend">
        <span class="legend-item"><span class="color-box" style="background: rgba(138, 43, 226, 0.4);"></span>>1000元 (超高价股)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 215, 0, 0.4);"></span>100-1000元 (高价股)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(0, 191, 255, 0.4);"></span>50-100元 (中高价股)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(0, 255, 0, 0.4);"></span>20-50元 (中价股)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 255, 0, 0.4);"></span>10-20元 (中低价股)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 165, 0, 0.4);"></span>5-10元 (低价股)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 99, 71, 0.4);"></span><5元 (超低价股)</span>
      </div>
    </div>

    <!-- 涨停板梯度着色示例 -->
    <div class="demo-section">
      <h3>📈 涨停板梯度着色</h3>
      <p class="description">根据连板数显示不同强度的颜色，突出显示高连板股票</p>
      <TableComponent :componentConfig="limitUpTableConfig" />
      <div class="color-legend">
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 192, 203, 0.5);"></span>首板</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 255, 0, 0.6);"></span>二板</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 165, 0, 0.7);"></span>三板</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 69, 0, 0.8);"></span>四板</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 0, 0, 0.9);"></span>五板以上</span>
      </div>
    </div>

    <!-- 相对表现着色示例 -->
    <div class="demo-section">
      <h3>📊 相对表现着色</h3>
      <p class="description">基于统计学Z-score，显示相对于同组平均值的表现</p>
      <TableComponent :componentConfig="relativeTableConfig" />
      <div class="color-legend">
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 0, 0, 0.8);"></span>显著高于平均 (Z>2)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 69, 0, 0.6);"></span>高于平均 (Z>1)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 140, 0, 0.4);"></span>略高于平均 (Z>0.5)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(144, 238, 144, 0.3);"></span>接近平均 (-0.5<Z<0.5)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(255, 182, 193, 0.4);"></span>略低于平均 (Z<-0.5)</span>
        <span class="legend-item"><span class="color-box" style="background: rgba(105, 105, 105, 0.8);"></span>显著低于平均 (Z<-2)</span>
      </div>
    </div>

    <div class="usage-tips">
      <h3>💡 使用方法</h3>
      <div class="code-example">
        <h4>在服务器端配置：</h4>
        <pre><code># 在 show_plate_server.py 中
columns = [
  {"field": "综合评分", "header": "综合评分", "backgroundColor": "stockStrength"},
  {"field": "price", "header": "股价", "backgroundColor": "priceRange"},
  {"field": "连板数", "header": "连板数", "backgroundColor": "limitUpGradient"},
  {"field": "change", "header": "涨跌幅", "backgroundColor": "relativePerformance"}
]</code></pre>
        
        <h4>在前端组件中使用：</h4>
        <pre><code>// 在 Vue 组件中
{
  field: 'price',
  header: '股价',
  backgroundColor: 'priceRange'  // 使用自定义函数名
}</code></pre>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import TableComponent from './TableComponent.vue';

export default defineComponent({
  name: 'CustomFunctionsShowcase',
  components: {
    TableComponent
  },
  setup() {
    // 股票强势度评分数据
    const strengthData = {
      columns: [
        { field: 'name', header: '股票名称' },
        { field: 'price', header: '股价' },
        { field: 'change', header: '涨跌幅' },
        { field: 'volume_ratio', header: '量比' },
        { field: '开盘换手率', header: '开盘换手率' },
        { field: '连板数', header: '连板数' },
        { field: 'pe_ratio', header: 'PE' },
        { field: 'strength', header: '综合评分', backgroundColor: 'stockStrength' }
      ],
      rows: [
        { name: '东方财富', price: 18.5, change: 9.8, volume_ratio: 4.2, '开盘换手率': 12.5, '连板数': 2, pe_ratio: 18.5, strength: '强势' },
        { name: '比亚迪', price: 185.3, change: 6.2, volume_ratio: 2.8, '开盘换手率': 8.3, '连板数': 1, pe_ratio: 25.6, strength: '较强势' },
        { name: '宁德时代', price: 320.5, change: 4.1, volume_ratio: 1.9, '开盘换手率': 5.2, '连板数': 0, pe_ratio: 45.2, strength: '偏强势' },
        { name: '平安银行', price: 12.5, change: 2.3, volume_ratio: 1.2, '开盘换手率': 3.1, '连板数': 0, pe_ratio: 8.5, strength: '中性' },
        { name: '招商银行', price: 45.2, change: -1.8, volume_ratio: 0.8, '开盘换手率': 2.1, '连板数': 0, pe_ratio: 12.3, strength: '偏弱势' },
        { name: '中国石油', price: 8.2, change: -3.5, volume_ratio: 0.6, '开盘换手率': 1.5, '连板数': 0, pe_ratio: 55.8, strength: '弱势' }
      ]
    };

    // 价格区间数据
    const priceRangeData = {
      columns: [
        { field: 'name', header: '股票名称' },
        { field: 'price', header: '股价', backgroundColor: 'priceRange' },
        { field: 'market_cap', header: '市值(亿)' },
        { field: 'category', header: '价格分类' }
      ],
      rows: [
        { name: '贵州茅台', price: 1680.5, market_cap: 21000, category: '超高价股' },
        { name: '长春高新', price: 185.3, market_cap: 580, category: '高价股' },
        { name: '隆基绿能', price: 28.9, market_cap: 1850, category: '中价股' },
        { name: '格力电器', price: 38.9, market_cap: 2200, category: '中价股' },
        { name: '万科A', price: 23.1, market_cap: 2600, category: '中价股' },
        { name: '平安银行', price: 12.5, market_cap: 2400, category: '中低价股' },
        { name: '中国石油', price: 8.2, market_cap: 7500, category: '低价股' },
        { name: 'ST海医', price: 3.8, market_cap: 35, category: '超低价股' }
      ]
    };

    // 涨停板梯度数据
    const limitUpData = {
      columns: [
        { field: 'name', header: '股票名称' },
        { field: 'price', header: '股价' },
        { field: 'change', header: '涨跌幅' },
        { field: '连板数', header: '连板数', backgroundColor: 'limitUpGradient' },
        { field: 'reason', header: '涨停原因' }
      ],
      rows: [
        { name: '妖股王', price: 25.8, change: 10.0, '连板数': 6, reason: 'AI概念+业绩暴增' },
        { name: '四板龙头', price: 18.2, change: 10.0, '连板数': 4, reason: '新能源汽车' },
        { name: '三板跟风', price: 12.5, change: 10.0, '连板数': 3, reason: '跟风炒作' },
        { name: '二板加速', price: 15.8, change: 10.0, '连板数': 2, reason: '政策利好' },
        { name: '首板启动', price: 22.3, change: 10.0, '连板数': 1, reason: '重组预期' },
        { name: '普通股票', price: 28.9, change: 3.2, '连板数': 0, reason: '正常波动' }
      ]
    };

    // 相对表现数据
    const relativeData = {
      columns: [
        { field: 'name', header: '板块名称' },
        { field: 'change', header: '板块涨幅', backgroundColor: 'relativePerformance' },
        { field: 'volume_ratio', header: '量比', backgroundColor: 'relativePerformance' },
        { field: 'up_stocks', header: '上涨股票数' }
      ],
      rows: [
        { name: '人工智能', change: 8.5, volume_ratio: 3.2, up_stocks: 45 },
        { name: '新能源汽车', change: 6.8, volume_ratio: 2.8, up_stocks: 38 },
        { name: '光伏概念', change: 4.2, volume_ratio: 1.9, up_stocks: 32 },
        { name: '半导体', change: 2.1, volume_ratio: 1.5, up_stocks: 25 },
        { name: '消费电子', change: 0.8, volume_ratio: 1.1, up_stocks: 18 },
        { name: '房地产', change: -1.2, volume_ratio: 0.8, up_stocks: 8 },
        { name: '银行板块', change: -2.1, volume_ratio: 0.6, up_stocks: 5 },
        { name: '煤炭钢铁', change: -4.5, volume_ratio: 0.4, up_stocks: 2 }
      ]
    };

    const strengthTableConfig = ref({
      id: 'strength-table',
      apiData: strengthData
    });

    const priceRangeTableConfig = ref({
      id: 'price-range-table',
      apiData: priceRangeData
    });

    const limitUpTableConfig = ref({
      id: 'limit-up-table',
      apiData: limitUpData
    });

    const relativeTableConfig = ref({
      id: 'relative-table',
      apiData: relativeData
    });

    return {
      strengthTableConfig,
      priceRangeTableConfig,
      limitUpTableConfig,
      relativeTableConfig
    };
  }
});
</script>

<style scoped>
.custom-functions-showcase {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
  font-size: 1.4em;
}

.description {
  color: #7f8c8d;
  font-style: italic;
  margin-bottom: 20px;
  font-size: 1.1em;
}

.color-legend {
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding: 15px;
  background: rgba(255,255,255,0.8);
  border-radius: 8px;
  border: 1px solid #ddd;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 0.9em;
  color: #555;
}

.color-box {
  width: 20px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
  border: 1px solid #ccc;
  display: inline-block;
}

.usage-tips {
  margin-top: 40px;
  padding: 25px;
  background: #f8f9fa;
  border-radius: 10px;
  border-left: 5px solid #28a745;
}

.usage-tips h3 {
  color: #28a745;
  margin-top: 0;
}

.code-example {
  margin-top: 20px;
}

.code-example h4 {
  color: #495057;
  margin-bottom: 10px;
}

.code-example pre {
  background: #2d3748;
  color: #e2e8f0;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  line-height: 1.4;
}

.code-example code {
  color: #e2e8f0;
}
</style>
