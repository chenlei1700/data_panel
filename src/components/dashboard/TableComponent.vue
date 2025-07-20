<template>
  <div class="table-component">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>            <th 
              v-for="column in visibleColumns" 
              :key="column.field"
              @click="sortBy(column.field)"
              :class="{ sortable: true, active: sortKey === column.field, asc: sortKey === column.field && sortOrder === 'asc', desc: sortKey === column.field && sortOrder === 'desc' }"
            >
              {{ column.header }}
              <span class="sort-icon" v-if="sortKey === column.field">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>           
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in sortedRows" :key="index">            
            <td v-for="column in visibleColumns" :key="column.field" 
                :style="{ backgroundColor: getCellBackgroundColor(row[column.field], column, row) }">
              <!-- 股票名称列使用特殊渲染 -->
              <span v-if="column.field === 'stock_name'" v-html="renderStockLink(row[column.field], row['id'])"></span>
              <span v-else-if="column.field === '股票名称'" v-html="renderStockLink(row[column.field], row['股票ID'])"></span>
              <!-- 板块1-5列使用特殊渲染 -->
              <span v-else-if="['板块1', '板块2', '板块3', '板块4', '板块5', '板块名'].includes(column.field)" 
                    v-html="renderSectorNameCell({value: row[column.field], style: ''})"></span>
              <span v-else>{{ formatCellValue(row[column.field]) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'TableComponent',
  props: {
    componentConfig: {
      type: Object,
      required: true
    }
  },
  setup(props, { expose }) {
    const apiData = ref({
      rows: [],
      columns: []
    });
    const loading = ref(true);
    const error = ref(null);
    
    // 排序相关状态
    const sortKey = ref('');
    const sortOrder = ref('asc'); // 'asc' 或 'desc'
    
    // 格式化单元格值
    const formatCellValue = (value) => {
      if (value === null || value === undefined) return '';
      
      // 如果是数字且需要格式化
      if (typeof value === 'number') {
        // 对于百分比类型，保留两位小数
        return Number.isInteger(value) ? value : value.toFixed(2);
      }
      
      return value;
    };
      // 渲染股票链接
    const renderStockLink = (stockName, stockId) => {
      if (!stockName || !stockId) return stockName || '';
      
      // 股票代码格式化为6位数字
      const paddedStockId = String(stockId).padStart(6, '0');
      
      // 获取前2个字符
      const prefix = paddedStockId.substring(0, 2);
      
      // 返回带链接的HTML，包含前2个字符
      return `<a href="http://www.treeid/code_${paddedStockId}" onclick="changeCss(this, 'stockTableBody')" 
          style="color: blue; text-decoration: underline; cursor: pointer;">${stockName}_${prefix}</a>`;
    };
    
    const renderSectorNameCell = (cell) => {
      if (!cell || !cell.value) return '';
      
      // 提取括号前的部分
      const fullName = cell.value;
      // 当有多个括号时，取最后一个括号前的部分
      const parenIndex = fullName.lastIndexOf('(');
      
      // 如果有括号，只取括号前的部分，否则使用完整名称
      const sectorName = parenIndex !== -1 ? fullName.substring(0, parenIndex).trim() : fullName;
      
      // 创建带有点击事件的板块名链接
      return `<a href="#" 
        onclick="event.preventDefault(); window.updateSectorDashboard('${sectorName}'); return false;" 
        style="${cell.style || ''}; cursor: pointer; text-decoration: underline; color: blue;">
        ${fullName}      </a>`;
    };
    
    // 内置的背景色计算函数
    const backgroundColorFunctions = {
      // 数值热力图 - 根据数值大小显示不同颜色（绿色=小值，红色=大值）
      heatmap: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const numValue = parseFloat(value);
        const columnValues = allRows
          .map(r => parseFloat(r[column.field]))
          .filter(v => !isNaN(v));
        
        if (columnValues.length === 0) return 'transparent';
        
        const min = Math.min(...columnValues);
        const max = Math.max(...columnValues);
        
        if (min === max) return 'transparent';
        
        const ratio = (numValue - min) / (max - min); // 0到1之间，0为最小值，1为最大值
        
        if (ratio <= 0.5) {
          // 小值区域：绿色到黄色过渡
          const intensity = Math.round(255 * (ratio * 2));
          return `rgba(${intensity}, 255, 0, 0.6)`;
        } else {
          // 大值区域：黄色到红色过渡
          const intensity = Math.round(255 * (1 - (ratio - 0.5) * 2));
          return `rgba(255, ${intensity}, 0, 0.6)`;
        }
      },
      
      // 绿红色阶 - 负值绿色（小值），正值红色（大值）
      redGreen: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const numValue = parseFloat(value);
        if (numValue === 0) return 'transparent';
        
        const columnValues = allRows
          .map(r => parseFloat(r[column.field]))
          .filter(v => !isNaN(v));
        
        const maxAbs = Math.max(...columnValues.map(v => Math.abs(v)));
        if (maxAbs === 0) return 'transparent';
        
        const ratio = Math.abs(numValue) / maxAbs * 0.6; // 0.6 控制颜色深度
        
        if (numValue > 0) {
          // 正值（大值） - 红色
          const intensity = Math.round(255 * (1 - ratio));
          return `rgb(255, ${intensity}, ${intensity})`;
        } else {
          // 负值（小值） - 绿色
          const intensity = Math.round(255 * (1 - ratio));
          return `rgb(${intensity}, 255, ${intensity})`;
        }
      },
      
      // 百分比色阶（绿色=负百分比即小值，红色=正百分比即大值）
      percentage: (value, column, row, allRows) => {
        if (value === null || value === undefined) return 'transparent';
        
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return 'transparent';
        
        // 假设百分比值在 -100 到 100 之间
        const normalizedValue = Math.max(-100, Math.min(100, numValue));
        const ratio = (normalizedValue + 100) / 200; // 转换到 0-1 范围，0为-100%，1为+100%
        
        // 创建从绿到黄到红的渐变（绿=负值/小值，红=正值/大值）
        if (ratio < 0.5) {
          // 绿到黄 (ratio 0-0.5，对应-100%到0%)
          const intensity = Math.round(255 * ratio * 2);
          return `rgba(${intensity}, 255, 0, 0.4)`;
        } else {
          // 黄到红 (ratio 0.5-1，对应0%到+100%)
          const intensity = Math.round(255 * (1 - (ratio - 0.5) * 2));
          return `rgba(255, ${intensity}, 0, 0.4)`;
        }
      },
        // 等级色阶 - 根据值的排名显示颜色（绿色=高排名即小值，红色=低排名即大值）
      rank: (value, column, row, allRows) => {
        if (value === null || value === undefined) return 'transparent';
        
        const columnValues = allRows
          .map(r => r[column.field])
          .filter(v => v !== null && v !== undefined);
        
        columnValues.sort((a, b) => parseFloat(b) - parseFloat(a)); // 降序排列
        const rank = columnValues.indexOf(value);
        
        if (rank === -1) return 'transparent';
        
        const ratio = rank / (columnValues.length - 1); // 0为第一名（最大值），1为最后一名（最小值）
        
        if (ratio <= 0.5) {
          // 前半部分排名（大值）：黄色到红色
          const intensity = Math.round(255 * (1 - ratio * 2));
          return `rgba(255, ${intensity}, 0, 0.6)`;
        } else {
          // 后半部分排名（小值）：黄色到绿色
          const intensity = Math.round(255 * ((ratio - 0.5) * 2));
          return `rgba(${255 - intensity}, 255, 0, 0.6)`;
        }
      },

      // 自定义函数：股票强势度综合评分着色
      stockStrength: (value, column, row, allRows) => {
        if (!row) return 'transparent';
        
        // 获取相关数据字段
        const change = parseFloat(row.change || row['涨幅(%)'] || row['板块涨幅'] || 0);
        const volume = parseFloat(row.volume || row.volume_ratio || row['板块量比'] || 0);
        const turnover = parseFloat(row['开盘换手率'] || row['当日换手率'] || row['强势分时换手占比'] || 0);
        const boards = parseInt(row['连板数'] || row['涨停梯度'] || 0);
        const pe = parseFloat(row.pe || row.pe_ratio || 0);
        
        let score = 0;
        
        // 涨幅评分 (权重: 40%)
        if (change > 8) score += 4;
        else if (change > 5) score += 3;
        else if (change > 2) score += 2;
        else if (change > 0) score += 1;
        else if (change < -5) score -= 3;
        else if (change < -2) score -= 2;
        else if (change < 0) score -= 1;
        
        // 成交量/量比评分 (权重: 25%)
        if (volume > 5) score += 2.5;
        else if (volume > 3) score += 2;
        else if (volume > 1.5) score += 1.5;
        else if (volume > 1) score += 1;
        else if (volume < 0.5) score -= 1;
        
        // 换手率评分 (权重: 20%)
        if (turnover > 15) score += 2;
        else if (turnover > 8) score += 1.5;
        else if (turnover > 3) score += 1;
        else if (turnover > 1) score += 0.5;
        
        // 连板数评分 (权重: 10%)
        if (boards >= 3) score += 1.5;
        else if (boards === 2) score += 1;
        else if (boards === 1) score += 0.5;
        
        // PE估值调整 (权重: 5%)
        if (pe > 0 && pe < 20) score += 0.5;
        else if (pe > 50) score -= 0.5;
        
        // 根据综合评分返回颜色
        if (score >= 7) return 'rgba(255, 0, 0, 0.8)';       // 深红 - 超强势
        if (score >= 5) return 'rgba(255, 69, 0, 0.7)';      // 红橙 - 强势
        if (score >= 3) return 'rgba(255, 140, 0, 0.6)';     // 橙色 - 较强势
        if (score >= 1) return 'rgba(255, 215, 0, 0.5)';     // 金色 - 偏强势
        if (score >= 0) return 'rgba(144, 238, 144, 0.4)';   // 浅绿 - 中性
        if (score >= -2) return 'rgba(255, 182, 193, 0.5)';  // 浅红 - 偏弱势
        return 'rgba(220, 20, 60, 0.6)';                     // 深红 - 弱势
      },

      // 自定义函数：价格区间着色
      priceRange: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const price = parseFloat(value);
        
        // 超高价股 (>1000元)
        if (price > 1000) return 'rgba(138, 43, 226, 0.4)';  // 紫色
        // 高价股 (100-1000元)  
        if (price > 100) return 'rgba(255, 215, 0, 0.4)';    // 金色
        // 中高价股 (50-100元)
        if (price > 50) return 'rgba(0, 191, 255, 0.4)';     // 深天蓝色
        // 中价股 (20-50元)
        if (price > 20) return 'rgba(0, 255, 0, 0.4)';       // 绿色
        // 中低价股 (10-20元)
        if (price > 10) return 'rgba(255, 255, 0, 0.4)';     // 黄色
        // 低价股 (5-10元)
        if (price > 5) return 'rgba(255, 165, 0, 0.4)';      // 橙色
        // 超低价股 (<5元)
        return 'rgba(255, 99, 71, 0.4)';                     // 番茄红色
      },

      // 自定义函数：涨停板梯度着色
      limitUpGradient: (value, column, row, allRows) => {
        if (value === null || value === undefined) return 'transparent';
        
        const boards = parseInt(value);
        
        if (boards <= 0) return 'transparent';
        if (boards === 1) return 'rgba(255, 192, 203, 0.5)'; // 粉色 - 首板
        if (boards === 2) return 'rgba(255, 255, 0, 0.6)';   // 黄色 - 二板
        if (boards === 3) return 'rgba(255, 165, 0, 0.7)';   // 橙色 - 三板
        if (boards === 4) return 'rgba(255, 69, 0, 0.8)';    // 红橙 - 四板
        if (boards >= 5) return 'rgba(255, 0, 0, 0.9)';      // 深红 - 五板以上
        
        return 'transparent';
      },      // 自定义函数：相对表现着色 (相比同类平均值)
      relativePerformance: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const currentValue = parseFloat(value);
        const columnValues = allRows
          .map(r => parseFloat(r[column.field]))
          .filter(v => !isNaN(v));
        
        if (columnValues.length === 0) return 'transparent';
        
        // 计算平均值和标准差
        const avg = columnValues.reduce((sum, val) => sum + val, 0) / columnValues.length;
        const variance = columnValues.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / columnValues.length;
        const stdDev = Math.sqrt(variance);
        
        if (stdDev === 0) return 'transparent';
        
        // 计算Z-score (标准分数)
        const zScore = (currentValue - avg) / stdDev;
        
        // 根据Z-score着色（绿色=低于平均的小值，红色=高于平均的大值）
        if (zScore > 2) return 'rgba(255, 0, 0, 0.8)';        // 显著高于平均（大值） - 深红
        if (zScore > 1) return 'rgba(255, 69, 0, 0.6)';       // 高于平均（大值） - 橙红
        if (zScore > 0.5) return 'rgba(255, 140, 0, 0.4)';    // 略高于平均（大值） - 橙色
        if (zScore > -0.5) return 'rgba(255, 255, 224, 0.3)'; // 接近平均 - 浅黄
        if (zScore > -1) return 'rgba(144, 238, 144, 0.4)';   // 略低于平均（小值） - 浅绿
        if (zScore > -2) return 'rgba(0, 255, 0, 0.6)';       // 低于平均（小值） - 绿色
        return 'rgba(0, 128, 0, 0.8)';                        // 显著低于平均（小值） - 深绿
      },

      // 自定义函数：技术指标综合评分着色
      technicalAnalysis: (value, column, row, allRows) => {
        if (!row) return 'transparent';
        
        // 获取相关技术指标字段（适应不同字段名）
        const rsi = parseFloat(row.rsi || row.RSI || row['RSI指标'] || 50);
        const macd = parseFloat(row.macd || row.MACD || row['MACD'] || 0);
        const kdj_k = parseFloat(row.kdj_k || row.KDJ_K || row['KDJ_K'] || row.k值 || 50);
        const kdj_d = parseFloat(row.kdj_d || row.KDJ_D || row['KDJ_D'] || row.d值 || 50);
        const ma5 = parseFloat(row.ma5 || row.MA5 || row['5日线'] || 0);
        const ma20 = parseFloat(row.ma20 || row.MA20 || row['20日线'] || 0);
        const currentPrice = parseFloat(row.price || row.close || row['现价'] || row['收盘价'] || 0);
        const volumeRatio = parseFloat(row.volume_ratio || row['量比'] || row['板块量比'] || 1);
        
        let technicalScore = 0;
        
        // RSI评分 (相对强弱指标, 权重: 25%)
        if (rsi >= 70) {
          technicalScore += 3; // 超买区域，强势
        } else if (rsi >= 50) {
          technicalScore += 2; // 中性偏强
        } else if (rsi >= 30) {
          technicalScore += 1; // 中性偏弱
        } else {
          technicalScore += 0; // 超卖区域，可能反弹
        }
        
        // MACD评分 (指数平滑异同移动平均线, 权重: 20%)
        if (macd > 0.5) {
          technicalScore += 2.5; // 强势上涨
        } else if (macd > 0) {
          technicalScore += 1.5; // 温和上涨
        } else if (macd > -0.5) {
          technicalScore += 0.5; // 弱势整理
        } else {
          technicalScore -= 1; // 下跌趋势
        }
        
        // KDJ评分 (随机指标, 权重: 20%)
        if (kdj_k > kdj_d && kdj_k > 80) {
          technicalScore += 2; // 强势超买
        } else if (kdj_k > kdj_d && kdj_k > 50) {
          technicalScore += 1.5; // 上升趋势
        } else if (kdj_k > kdj_d && kdj_k < 50) {
          technicalScore += 1; // 弱势反弹
        } else if (kdj_k < 20) {
          technicalScore += 0; // 超卖区域
        } else {
          technicalScore -= 0.5; // 下降趋势
        }
        
        // 移动平均线评分 (趋势判断, 权重: 20%)
        if (ma5 > 0 && ma20 > 0 && currentPrice > 0) {
          if (currentPrice > ma5 && ma5 > ma20) {
            technicalScore += 2; // 多头排列
          } else if (currentPrice > ma5) {
            technicalScore += 1; // 短期强势
          } else if (currentPrice > ma20) {
            technicalScore += 0.5; // 中长期支撑
          } else {
            technicalScore -= 1; // 跌破均线
          }
        }
        
        // 成交量确认 (权重: 15%)
        if (volumeRatio > 3) {
          technicalScore += 1.5; // 放量确认
        } else if (volumeRatio > 1.5) {
          technicalScore += 1; // 温和放量
        } else if (volumeRatio < 0.5) {
          technicalScore -= 0.5; // 缩量
        }
        
        // 根据技术评分返回颜色
        if (technicalScore >= 8) return 'rgba(220, 20, 60, 0.9)';     // 深红 - 技术面极强
        if (technicalScore >= 6) return 'rgba(255, 69, 0, 0.8)';      // 红橙 - 技术面强势
        if (technicalScore >= 4) return 'rgba(255, 140, 0, 0.7)';     // 橙色 - 技术面偏强
        if (technicalScore >= 2) return 'rgba(255, 215, 0, 0.6)';     // 金色 - 技术面中性偏强
        if (technicalScore >= 0) return 'rgba(240, 248, 255, 0.4)';   // 浅蓝 - 技术面中性
        if (technicalScore >= -2) return 'rgba(255, 182, 193, 0.5)';  // 浅红 - 技术面偏弱
        return 'rgba(176, 196, 222, 0.7)';                            // 蓝灰 - 技术面弱势
      },

      // 自定义函数：市值规模着色
      marketCapSize: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const marketCap = parseFloat(value);
        
        // 超大盘股 (市值 > 5000亿)
        if (marketCap > 500000000000) return 'rgba(72, 61, 139, 0.5)';   // 深蓝紫 - 超大盘
        // 大盘股 (市值 1000-5000亿)
        if (marketCap > 100000000000) return 'rgba(0, 0, 205, 0.5)';     // 深蓝 - 大盘股
        // 中大盘股 (市值 500-1000亿)
        if (marketCap > 50000000000) return 'rgba(30, 144, 255, 0.4)';   // 道奇蓝 - 中大盘
        // 中盘股 (市值 100-500亿)
        if (marketCap > 10000000000) return 'rgba(0, 191, 255, 0.4)';    // 深天蓝 - 中盘股
        // 中小盘股 (市值 50-100亿)
        if (marketCap > 5000000000) return 'rgba(135, 206, 250, 0.4)';   // 天蓝 - 中小盘
        // 小盘股 (市值 20-50亿)
        if (marketCap > 2000000000) return 'rgba(255, 255, 224, 0.6)';   // 浅黄 - 小盘股
        // 微盘股 (市值 < 20亿)
        return 'rgba(255, 192, 203, 0.6)';                              // 粉色 - 微盘股
      },

      // 无背景色
      none: (value, column, row, allRows) => {
        return 'transparent';
      },

      // 高低值背景色（绿色=低值，红色=高值）
      highLow: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const numValue = parseFloat(value);
        const columnValues = allRows
          .map(r => parseFloat(r[column.field]))
          .filter(v => !isNaN(v));
        
        if (columnValues.length === 0) return 'transparent';
        
        const max = Math.max(...columnValues);
        const min = Math.min(...columnValues);
        
        if (max === min) return 'transparent';
        
        const range = max - min;
        const percentile = (numValue - min) / range;
        
        if (percentile >= 0.8) return 'rgba(255, 0, 0, 0.3)';    // 高值 - 红色
        if (percentile <= 0.2) return 'rgba(0, 255, 0, 0.3)';    // 低值 - 绿色
        return 'transparent';
      },

      // 范围背景色（绿色=小值，红色=大值的渐变）
      range: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const numValue = parseFloat(value);
        const columnValues = allRows
          .map(r => parseFloat(r[column.field]))
          .filter(v => !isNaN(v));
        
        if (columnValues.length === 0) return 'transparent';
        
        const max = Math.max(...columnValues);
        const min = Math.min(...columnValues);
        const range = max - min;
        
        if (range === 0) return 'transparent';
        
        const ratio = (numValue - min) / range; // 0为最小值，1为最大值
        
        // 从绿色到红色的渐变：绿色(0,255,0) -> 黄色(255,255,0) -> 红色(255,0,0)
        if (ratio <= 0.5) {
          // 绿到黄
          const intensity = Math.round(255 * ratio * 2);
          return `rgba(${intensity}, 255, 0, 0.4)`;
        } else {
          // 黄到红
          const intensity = Math.round(255 * (1 - (ratio - 0.5) * 2));
          return `rgba(255, ${intensity}, 0, 0.4)`;
        }
      },

      // 性能对比背景色 (与行业均值对比)
      performance: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const numValue = parseFloat(value);
        
        // 查找行业均值列（优先查找明确的字段名）
        let industryAvgValue = null;
        
        // 首先尝试查找明确的行业均值字段
        if (row['行业均值'] !== undefined) {
          industryAvgValue = row['行业均值'];
        } else if (row['industry_avg'] !== undefined) {
          industryAvgValue = row['industry_avg'];
        } else {
          // 作为后备方案，使用最后一列
          const keys = Object.keys(row);
          industryAvgValue = row[keys[keys.length - 1]];
        }
        
        if (industryAvgValue === null || industryAvgValue === undefined || isNaN(industryAvgValue)) {
          return 'transparent';
        }
        
        const avgValue = parseFloat(industryAvgValue);
        const diff = numValue - avgValue;
        const diffRatio = avgValue !== 0 ? Math.abs(diff / avgValue) : 0;
        
        if (diff > 0) {
          // 高于均值 - 红色（大值用红色）
          const intensity = Math.min(0.6, diffRatio * 2);
          return `rgba(255, 0, 0, ${intensity})`;
        } else if (diff < 0) {
          // 低于均值 - 绿色（小值用绿色）
          const intensity = Math.min(0.6, diffRatio * 2);
          return `rgba(0, 255, 0, ${intensity})`;
        }
        
        return 'transparent';
      },

      // 状态背景色
      status: (value, column, row, allRows) => {
        if (!value) return 'transparent';
        
        const status = value.toString().toLowerCase();
        
        if (status.includes('正常') || status.includes('normal')) {
          return 'rgba(0, 255, 0, 0.3)';    // 绿色
        } else if (status.includes('警告') || status.includes('warning')) {
          return 'rgba(255, 255, 0, 0.3)';  // 黄色
        } else if (status.includes('异常') || status.includes('error') || status.includes('错误')) {
          return 'rgba(255, 0, 0, 0.3)';    // 红色
        }
        
        return 'transparent';
      },

      // 阈值背景色
      threshold: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const numValue = parseFloat(value);
        const thresholds = column.thresholds || [50, 100];
        
        if (numValue <= thresholds[0]) {
          return 'rgba(0, 255, 0, 0.3)';    // 低于第一个阈值 - 绿色
        } else if (numValue <= thresholds[1]) {
          return 'rgba(255, 255, 0, 0.3)';  // 介于两个阈值之间 - 黄色
        } else {
          return 'rgba(255, 0, 0, 0.3)';    // 高于第二个阈值 - 红色
        }
      },

      // 使用率背景色
      utilization: (value, column, row, allRows) => {
        if (value === null || value === undefined || isNaN(value)) return 'transparent';
        
        const percentage = parseFloat(value);
        
        if (percentage >= 90) {
          return 'rgba(255, 0, 0, 0.5)';      // 高使用率 - 红色
        } else if (percentage >= 75) {
          return 'rgba(255, 165, 0, 0.4)';    // 较高使用率 - 橙色
        } else if (percentage >= 50) {
          return 'rgba(255, 255, 0, 0.3)';    // 中等使用率 - 黄色
        } else {
          return 'rgba(0, 255, 0, 0.3)';      // 低使用率 - 绿色
        }
      }
    };
    
    // 获取单元格背景色
    const getCellBackgroundColor = (value, column, row) => {
      // 检查列配置中是否有背景色函数设置
      const colorConfig = column.backgroundColor;
      
      if (!colorConfig) return 'transparent';
      
      let colorFunction;
      
      if (typeof colorConfig === 'string') {
        // 如果是字符串，从内置函数中查找
        colorFunction = backgroundColorFunctions[colorConfig];
      } else if (typeof colorConfig === 'function') {
        // 如果是函数，直接使用
        colorFunction = colorConfig;
      } else if (typeof colorConfig === 'object' && colorConfig.type) {
        // 如果是对象配置
        const baseFunction = backgroundColorFunctions[colorConfig.type];
        if (baseFunction) {
          // 可以在这里添加参数处理逻辑
          colorFunction = (val, col, r, allRows) => baseFunction(val, col, r, allRows, colorConfig.params);
        }
      }
      
      if (!colorFunction) return 'transparent';
      
      try {
        return colorFunction(value, column, row, apiData.value.rows || []);
      } catch (error) {
        console.warn('计算背景色时出错:', error);
        return 'transparent';
      }
    };
    
    // 排序方法
    const sortBy = (key) => {
      if (sortKey.value === key) {
        // 如果点击的是当前排序的列，切换排序顺序
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
      } else {
        // 设置新的排序列，默认升序
        sortKey.value = key;
        sortOrder.value = 'asc';
      }
    };    // 获取API返回的所有列数据（不过滤，保留隐藏列数据供后续使用）
    const apiColumns = computed(() => {
      return apiData.value.columns || [];
    });
    
    // 获取可见的列数据（仅用于模板渲染）
    const visibleColumns = computed(() => {
      const columns = apiData.value.columns || [];
      
      // 检查columns是否是字符串数组（旧格式）
      if (columns.length > 0 && typeof columns[0] === 'string') {
        // 将字符串数组转换为对象数组
        return columns.map(columnName => ({
          field: columnName,
          header: columnName,
          backgroundColor: 'none'  // 默认无背景色
        }));
      }
      
      // 如果已经是对象数组（推荐格式，直接包含backgroundColor配置）
      if (columns.length > 0 && typeof columns[0] === 'object') {
        // 直接使用对象数组，每个对象已包含field, header, backgroundColor等属性
        return columns.filter(column => column.visible !== false);
      }
      
      // 兜底情况
      return [];
    });
    
    // 基于排序条件的计算属性
    const sortedRows = computed(() => {
      if (!apiData.value.rows || !apiData.value.columns) return [];
      
      // 检查rows的格式
      if (apiData.value.rows.length === 0) return [];
      
      let objectRows;
      
      // 如果rows已经是对象数组，直接使用
      if (typeof apiData.value.rows[0] === 'object' && !Array.isArray(apiData.value.rows[0])) {
        objectRows = apiData.value.rows;
      } else {
        // 如果rows是二维数组，转换为对象数组
        objectRows = apiData.value.rows.map(row => {
          const obj = {};
          apiData.value.columns.forEach((column, index) => {
            // 无论column是字符串还是对象，都使用统一的方式处理
            const columnKey = typeof column === 'string' ? column : column.field;
            obj[columnKey] = row[index];
          });
          return obj;
        });
      }
      
      if (!sortKey.value) return objectRows;
      
      const sortedArray = [...objectRows];
      return sortedArray.sort((a, b) => {
        const valueA = a[sortKey.value];
        const valueB = b[sortKey.value];
        
        // 判断是否为数值类型
        const isNumeric = !isNaN(parseFloat(valueA)) && !isNaN(parseFloat(valueB));
        
        let comparison = 0;
        if (isNumeric) {
          // 数值比较
          comparison = parseFloat(valueA) - parseFloat(valueB);
        } else if (valueA instanceof Date && valueB instanceof Date) {
          // 日期比较
          comparison = valueA.getTime() - valueB.getTime();
        } else {
          // 字符串比较
          const stringA = String(valueA || '').toLowerCase();
          const stringB = String(valueB || '').toLowerCase();
          if (stringA < stringB) comparison = -1;
          if (stringA > stringB) comparison = 1;
        }
        
        // 根据排序顺序返回比较结果
        return sortOrder.value === 'asc' ? comparison : -comparison;
      });
    });
    
    // 判断是否是涨停数据表更新的更完善方式
    const isUpLimitTableUpdate = (update) => {
      // 检查组件ID是否匹配
      const isMatchingId =  update.componentId === 'upLimitTable';
                        
      // 多重条件判断
      return isMatchingId;
    };

    // 在处理更新事件时使用
    const handleDashboardUpdate = (event) => {
      const update = event.detail;
      if (isUpLimitTableUpdate(update)) {
        console.log('涨停数据表需要更新');
        refreshData();
      }
    };    // 获取数据的方法
    const fetchData = async (url) => {
      // 如果配置中直接包含数据，优先使用直接数据
      if (props.componentConfig.apiData) {
        console.log('使用直接传入的数据');
        apiData.value = props.componentConfig.apiData;
        loading.value = false;
        return;
      }
      
      loading.value = true;
      error.value = null;
      
      const targetUrl = url || props.componentConfig.dataSource;
      console.log('开始获取数据，URL:', targetUrl);
      
      try {
        // 构建带有componentId参数的URL
        const urlObj = new URL(targetUrl);
        
        // 添加componentId参数
        if (props.componentConfig.id) {
          urlObj.searchParams.set('componentId', props.componentConfig.id);
          console.log('添加componentId参数:', props.componentConfig.id);
        }
        
        const finalUrl = urlObj.toString();
        console.log('最终请求URL:', finalUrl);
        
        const response = await axios.get(finalUrl);
        
        console.log('获取到的原始响应数据:', response);
        console.log('响应数据类型:', typeof response.data);
        console.log('响应数据结构:', response.data);
        
        // 处理返回的数据
        if (response.data) {
          // 检查是否有标准的rows和columns结构
          if (response.data.rows && response.data.columns) {
            console.log('数据使用标准的rows/columns格式');
            apiData.value = response.data;
          } 
          // 兼容其他格式
          else if (Array.isArray(response.data)) {
            console.log('数据是纯数组格式，转换为标准格式');
            apiData.value = {
              rows: response.data,
              columns: response.data.length > 0 ? 
                Object.keys(response.data[0]).map(key => ({
                  field: key,
                  header: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
                })) : []
            };
          } 
          else if (response.data.data && Array.isArray(response.data.data)) {
            console.log('数据使用 { data: [...] } 格式，转换为标准格式');
            apiData.value = {
              rows: response.data.data,
              columns: response.data.columns || (response.data.data.length > 0 ? 
                Object.keys(response.data.data[0]).map(key => ({
                  field: key,
                  header: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
                })) : [])
            };
          } 
          else {
            console.log('无法识别的数据格式');
            apiData.value = { rows: [], columns: [] };
            error.value = '无法识别返回的数据格式';
          }
          
          console.log('处理后的表格数据:', apiData.value);
        } else {
          console.log('响应数据为空');
          apiData.value = { rows: [], columns: [] };
          error.value = '返回数据为空';
        }
      } catch (err) {
        console.error('获取表格数据失败:', err);
        error.value = '加载数据失败: ' + (err.message || '未知错误');
        apiData.value = { rows: [], columns: [] };
      } finally {
        loading.value = false;
        
        // 最终状态日志
        console.log('数据加载完成，状态:', {
          hasError: !!error.value, 
          errorMessage: error.value,
          rowsLength: (apiData.value.rows && apiData.value.rows.length) || 0,
          columnsLength: (apiData.value.columns && apiData.value.columns.length) || 0
        });
      }
    };
      const updateDashboard = async (sector) => {
      console.log(`⏱️ [${new Date().toISOString()}] 开始向服务器发送板块更新请求: ${sector}`);
      
      // 获取当前服务的端口（从组件的数据源URL中提取）
      const dataSource = props.componentConfig.dataSource;
      let baseUrl = '';
      
      if (dataSource) {
        try {
          const url = new URL(dataSource);
          baseUrl = `${url.protocol}//${url.host}`;
          console.log(`⏱️ [${new Date().toISOString()}] 从数据源提取服务地址: ${baseUrl}`);
        } catch (e) {
          console.error('解析数据源URL失败:', e);
        }
      }
      
      // 如果无法从数据源提取，使用默认端口列表
      const serverPorts = baseUrl ? [baseUrl] : [
        'http://localhost:5003', // multiplate服务器
        'http://localhost:5001', // 主服务器
        'http://localhost:5002'  // 强势服务器
      ];
      
      // 向所有相关服务器发送更新请求
      for (const serverUrl of serverPorts) {
        try {
          console.log(`⏱️ [${new Date().toISOString()}] 向 ${serverUrl} 发送更新请求...`);
          
          const response = await fetch(`${serverUrl}/api/dashboard/update`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              componentId: 'table12',  // 明确指定更新table12
              params: { sectors: sector },  // 新的板块名称
              sector_name: sector,  // 直接传递板块名称
              timestamp: Date.now()
            })
          });
          
          if (response.ok) {
            const result = await response.json();
            console.log(`⏱️ [${new Date().toISOString()}] ${serverUrl} 更新请求成功:`, result);
          } else {
            console.warn(`⏱️ [${new Date().toISOString()}] ${serverUrl} 更新请求失败: ${response.status}`);
          }
        } catch (error) {
          console.error(`⏱️ [${new Date().toISOString()}] 向 ${serverUrl} 发送更新请求失败:`, error.message);
        }
      }
      
      console.log(`⏱️ [${new Date().toISOString()}] 板块更新请求发送完成: ${sector}`);
    };// 监听组件配置变化
    watch(() => props.componentConfig.dataSource, (newVal) => {
      if (newVal) {
        fetchData(newVal);
      }
    });
    
    // 监听直接传入的数据变化
    watch(() => props.componentConfig.apiData, (newVal) => {
      if (newVal) {
        console.log('检测到直接数据变化，更新表格');
        apiData.value = newVal;
      }
    }, { deep: true });
      const refreshData = () => {
      console.log(`⏱️ [${new Date().toISOString()}] 组件 ${props.componentConfig.id} 正在刷新表格数据...`);
      console.log(`⏱️ [${new Date().toISOString()}] 当前数据源:`, props.componentConfig.dataSource);
      
      // 在数据源URL中添加时间戳防止缓存
      const currentDataSource = props.componentConfig.dataSource;
      if (currentDataSource) {
        const url = new URL(currentDataSource);
        url.searchParams.set('_refresh', Date.now().toString());
        console.log(`⏱️ [${new Date().toISOString()}] 添加刷新参数后的数据源:`, url.toString());
        fetchData(url.toString());
      } else {
        fetchData();
      }
    };
    
    
    
      onMounted(() => {
      const componentDelay = getComponentDelay(props.componentConfig.id);
      console.log(`⏱️ [${new Date().toISOString()}] 组件 ${props.componentConfig.id} 将在 ${componentDelay}ms 后开始加载数据`);
      
      setTimeout(() => {
        fetchData();
      }, componentDelay);
      
      // 设置全局函数（只在第一个组件时设置，避免重复覆盖）
      if (!window.updateSectorDashboard || !window.updateSectorDashboardSet) {
        console.log(`⏱️ [${new Date().toISOString()}] 设置全局板块更新函数`);
        
        window.updateSectorDashboard = (sector) => {
          if (sector) {
            console.log(`⏱️ [${new Date().toISOString()}] 全局函数被调用，更新板块: ${sector}`);
            updateDashboard(sector);
          }
        };
        
        window.updateSectorDashboardSet = true; // 标记已设置
      }
      
      // 添加仪表盘更新事件监听
      const handleDashboardUpdate = (event) => {
        const update = event.detail;
        console.log(`⏱️ [${new Date().toISOString()}] 组件 ${props.componentConfig.id} 接收到仪表盘更新事件:`, update);
        
        // 检查是否需要刷新当前组件
        if (update && (
          update.componentId === props.componentConfig.id || 
          update.action === 'reload_config' ||
          update.action === 'force_refresh'
        )) {
          console.log(`⏱️ [${new Date().toISOString()}] 组件 ${props.componentConfig.id} 开始刷新数据...`);
          setTimeout(() => {
            refreshData();
          }, 200); // 稍微延迟，确保配置更新完成
        }
      };
      
      // 添加配置更新事件监听
      const handleConfigUpdate = (event) => {
        const update = event.detail;
        console.log(`⏱️ [${new Date().toISOString()}] 组件 ${props.componentConfig.id} 接收到配置更新事件:`, update);
        
        // 配置更新后刷新数据
        setTimeout(() => {
          console.log(`⏱️ [${new Date().toISOString()}] 组件 ${props.componentConfig.id} 因配置更新而刷新数据...`);
          refreshData();
        }, 500); // 给配置更新更多时间
      };
      
      window.addEventListener('dashboard-update', handleDashboardUpdate);
      window.addEventListener('dashboard-config-updated', handleConfigUpdate);
      
      // 清理函数
      return () => {
        window.removeEventListener('dashboard-update', handleDashboardUpdate);
        window.removeEventListener('dashboard-config-updated', handleConfigUpdate);
      };
    });
    
    // 添加获取组件延迟的函数
    const getComponentDelay = (componentId) => {
      const delays = {
        'table1': 0,
        'table12': 200,
        'table2': 400,
        'table21': 600,
        'table22': 800,
        'table23': 1000,
        'table24': 1200,
        'upLimitTable': 1400,
        'ALLupLimitTable': 1600
      };
      return delays[componentId] || 0;
    };
    
    // 暴露方法给父组件
    expose({
      fetchData,
      refreshData
    });      return {
      apiData,
      apiColumns,
      visibleColumns,
      loading,
      error,
      sortKey,
      sortOrder,
      sortBy,
      sortedRows,
      formatCellValue,
      renderStockLink,
      renderSectorNameCell,
      getCellBackgroundColor,
      backgroundColorFunctions
    };
  }
});
</script>

<style scoped>
/* 保持原有样式 */
.table-component {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading, .error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #f44336;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
  min-height: 0px;  /* 设置最小高度 */
  display: flex;
  flex-direction: column;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  flex: 1; /* 让表格占据所有可用空间 */
}

.data-table th, .data-table td {
  padding: 10px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.data-table th {
  font-weight: 600;
  background-color: #f5f5f5;
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
  position: relative;
  padding-right: 25px; /* 为排序图标留出空间 */
}

.data-table th.sortable:hover {
  background-color: #e9e9e9;
}

.data-table th.active {
  background-color: #eef5ff;
}

.sort-icon {
  position: absolute;
  right: 8px;
  color: #606060;
}

.data-table th.asc .sort-icon {
  color: #1976d2;
}

.data-table th.desc .sort-icon {
  color: #1976d2;
}

/* 表格行的悬停效果 */
.data-table tbody tr:hover {
  background-color: #f5f9ff;
}

/* 斑马纹效果 */
.data-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

/* 允许v-html内容中的链接样式生效 */
:deep(.stock-link) {
  color: #1976d2;
  text-decoration: underline;
  cursor: pointer;
}

:deep(.stock-link:hover) {
  color: #0d47a1;
}
</style>