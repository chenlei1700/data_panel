/**
 * 表格背景色自定义函数库
 * 这个文件包含了各种常用的背景色计算函数
 */

// 股票相关的背景色函数
export const stockColorFunctions = {
  /**
   * 价格区间着色
   * @param {number} value - 股价
   * @param {object} column - 列配置
   * @param {object} row - 行数据
   * @param {array} allRows - 所有行数据
   * @returns {string} 颜色值
   */
  priceRange: (value, column, row, allRows) => {
    const price = parseFloat(value);
    if (price > 1000) return 'rgba(138, 43, 226, 0.3)';  // 紫色 - 超高价股
    if (price > 100) return 'rgba(255, 215, 0, 0.3)';    // 金色 - 高价股
    if (price > 50) return 'rgba(0, 255, 0, 0.3)';       // 绿色 - 中价股
    if (price > 20) return 'rgba(255, 255, 0, 0.3)';     // 黄色 - 中低价股
    return 'rgba(255, 165, 0, 0.3)';                     // 橙色 - 低价股
  },

  /**
   * PE估值着色
   * @param {number} value - PE值
   */
  peValuation: (value, column, row, allRows) => {
    const pe = parseFloat(value);
    if (pe < 0) return 'rgba(128, 128, 128, 0.3)';       // 灰色 - 亏损
    if (pe < 15) return 'rgba(0, 255, 0, 0.5)';          // 绿色 - 低估值
    if (pe <= 25) return 'rgba(255, 255, 0, 0.3)';       // 黄色 - 合理估值
    if (pe <= 40) return 'rgba(255, 165, 0, 0.4)';       // 橙色 - 偏高估值
    return 'rgba(255, 0, 0, 0.5)';                       // 红色 - 高估值
  },

  /**
   * 涨停板数着色
   * @param {number} value - 连板数
   */
  limitUpBoards: (value, column, row, allRows) => {
    const boards = parseInt(value);
    if (boards <= 0) return 'transparent';
    if (boards === 1) return 'rgba(255, 192, 203, 0.4)'; // 粉色 - 首板
    if (boards === 2) return 'rgba(255, 255, 0, 0.5)';   // 黄色 - 二板
    if (boards === 3) return 'rgba(255, 165, 0, 0.6)';   // 橙色 - 三板
    if (boards >= 4) return 'rgba(255, 0, 0, 0.7)';      // 红色 - 四板以上
    return 'transparent';
  },

  /**
   * 成交量相对排名着色
   * @param {number} value - 成交量
   */
  volumeRank: (value, column, row, allRows) => {
    const volumes = allRows.map(r => parseFloat(r[column.field])).sort((a, b) => b - a);
    const currentVolume = parseFloat(value);
    const rank = volumes.indexOf(currentVolume);
    const percentile = rank / (volumes.length - 1);
    
    if (percentile <= 0.1) return 'rgba(255, 0, 0, 0.8)';      // 前10% - 深红
    if (percentile <= 0.3) return 'rgba(255, 165, 0, 0.6)';    // 前30% - 橙色
    if (percentile <= 0.6) return 'rgba(255, 255, 0, 0.4)';    // 前60% - 黄色
    return 'rgba(211, 211, 211, 0.2)';                         // 其他 - 浅灰
  },

  /**
   * 综合强势度着色（多因子综合）
   * @param {any} value - 当前值
   * @param {object} column - 列配置
   * @param {object} row - 行数据
   */
  strengthScore: (value, column, row, allRows) => {
    const change = parseFloat(row.change || 0);
    const volume = parseFloat(row.volume || 0);
    const pe = parseFloat(row.pe || 0);
    const boards = parseInt(row.boards || 0);
    
    let score = 0;
    
    // 涨幅权重
    if (change > 5) score += 3;
    else if (change > 2) score += 2;
    else if (change > 0) score += 1;
    else if (change < -3) score -= 2;
    else if (change < 0) score -= 1;
    
    // 成交量权重
    if (volume > 20000000) score += 2;
    else if (volume > 10000000) score += 1;
    
    // PE权重
    if (pe > 0 && pe < 20) score += 1;
    else if (pe > 40) score -= 1;
    
    // 连板权重
    score += boards;
    
    // 根据综合评分着色
    if (score >= 6) return 'rgba(255, 0, 0, 0.8)';       // 深红 - 超强势
    if (score >= 4) return 'rgba(255, 165, 0, 0.6)';     // 橙色 - 强势
    if (score >= 2) return 'rgba(255, 255, 0, 0.4)';     // 黄色 - 偏强势
    if (score >= 0) return 'rgba(144, 238, 144, 0.3)';   // 浅绿 - 中性
    if (score >= -2) return 'rgba(255, 182, 193, 0.4)';  // 浅红 - 偏弱势
    return 'rgba(220, 20, 60, 0.6)';                     // 深红 - 弱势
  }
};

// 板块相关的背景色函数
export const sectorColorFunctions = {
  /**
   * 板块热度着色
   * @param {number} value - 板块涨幅
   */
  sectorHeat: (value, column, row, allRows) => {
    const change = parseFloat(value);
    if (change > 8) return 'rgba(255, 0, 0, 0.8)';       // 深红 - 超热
    if (change > 5) return 'rgba(255, 69, 0, 0.6)';      // 红橙 - 很热
    if (change > 3) return 'rgba(255, 165, 0, 0.5)';     // 橙色 - 热
    if (change > 1) return 'rgba(255, 255, 0, 0.4)';     // 黄色 - 温热
    if (change > -1) return 'rgba(144, 238, 144, 0.3)';  // 浅绿 - 中性
    if (change > -3) return 'rgba(255, 182, 193, 0.4)';  // 浅红 - 偏冷
    return 'rgba(176, 196, 222, 0.5)';                   // 浅蓝 - 冷
  },

  /**
   * 量比着色
   * @param {number} value - 量比值
   */
  volumeRatio: (value, column, row, allRows) => {
    const ratio = parseFloat(value);
    if (ratio > 5) return 'rgba(255, 0, 0, 0.7)';        // 深红 - 巨量
    if (ratio > 3) return 'rgba(255, 69, 0, 0.5)';       // 红橙 - 放量
    if (ratio > 1.5) return 'rgba(255, 165, 0, 0.4)';    // 橙色 - 温和放量
    if (ratio > 0.8) return 'rgba(144, 238, 144, 0.3)';  // 浅绿 - 正常
    return 'rgba(211, 211, 211, 0.2)';                   // 灰色 - 缩量
  }
};

// 通用的背景色函数
export const commonColorFunctions = {
  /**
   * 动态范围着色（根据数据自动计算范围）
   * @param {number} value - 当前值
   * @param {object} column - 列配置
   * @param {object} row - 行数据
   * @param {array} allRows - 所有行数据
   */
  dynamicRange: (value, column, row, allRows) => {
    const values = allRows.map(r => parseFloat(r[column.field])).filter(v => !isNaN(v));
    if (values.length === 0) return 'transparent';
    
    const min = Math.min(...values);
    const max = Math.max(...values);
    const current = parseFloat(value);
    
    if (min === max) return 'transparent';
    
    const ratio = (current - min) / (max - min);
    const intensity = Math.round(255 * (1 - ratio * 0.8));
    
    return `rgb(255, ${intensity}, ${intensity})`;
  },

  /**
   * 条件组合着色
   * @param {any} value - 当前值
   * @param {object} column - 列配置
   * @param {object} row - 行数据
   * @param {array} conditions - 条件配置数组
   */
  conditionalColor: (value, column, row, allRows, conditions = []) => {
    for (const condition of conditions) {
      const fieldValue = row[condition.field];
      if (evaluateCondition(fieldValue, condition.operator, condition.value)) {
        return condition.color;
      }
    }
    return 'transparent';
  }
};

// 辅助函数
function evaluateCondition(fieldValue, operator, conditionValue) {
  const numFieldValue = parseFloat(fieldValue);
  const numConditionValue = parseFloat(conditionValue);
  
  switch (operator) {
    case '>': return numFieldValue > numConditionValue;
    case '<': return numFieldValue < numConditionValue;
    case '>=': return numFieldValue >= numConditionValue;
    case '<=': return numFieldValue <= numConditionValue;
    case '==': return numFieldValue === numConditionValue;
    case '!=': return numFieldValue !== numConditionValue;
    case 'contains': return String(fieldValue).includes(String(conditionValue));
    case 'startsWith': return String(fieldValue).startsWith(String(conditionValue));
    case 'endsWith': return String(fieldValue).endsWith(String(conditionValue));
    default: return false;
  }
}

// 导出所有函数
export default {
  ...stockColorFunctions,
  ...sectorColorFunctions,
  ...commonColorFunctions
};
