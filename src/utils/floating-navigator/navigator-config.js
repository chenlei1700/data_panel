/**
 * 导航器配置处理逻辑
 */
export class NavigatorConfigManager {
  constructor() {
    this.globalConfig = null;
    this.pageConfigs = new Map();
  }
  
  /**
   * 设置全局配置
   * @param {Object} config - 全局配置对象
   */
  setGlobalConfig(config) {
    this.globalConfig = config;
    console.log('🔧 Navigator global config set:', config);
  }
  
  /**
   * 设置页面配置
   * @param {String} pageKey - 页面标识
   * @param {Object} pageConfig - 页面配置对象
   */
  setPageConfig(pageKey, pageConfig) {
    this.pageConfigs.set(pageKey, pageConfig);
    console.log(`🔧 Navigator page config set for ${pageKey}:`, pageConfig);
  }
  
  /**
   * 获取合并后的配置
   * @param {String} pageKey - 页面标识
   * @returns {Object} - 合并后的配置
   */
  getMergedConfig(pageKey) {
    const globalConfig = this.globalConfig || {};
    const pageConfig = this.pageConfigs.get(pageKey) || {};
    
    // 合并配置，页面配置优先
    const merged = {
      ...globalConfig,
      organization_structure: pageConfig.navigator_organization || {},
      page_key: pageKey,
      title: this.getPageTitle(pageKey)
    };
    
    return merged;
  }
  
  /**
   * 获取页面标题
   * @param {String} pageKey - 页面标识
   * @returns {String} - 页面标题
   */
  getPageTitle(pageKey) {
    const titleMap = {
      'multiplate': '多板块分析',
      'market_review': '市场复盘',
      'demo': '演示页面',
      'strong': '强势分析'
    };
    
    return titleMap[pageKey] || '数据导航';
  }
  
  /**
   * 验证配置有效性
   * @param {Object} config - 配置对象
   * @returns {Object} - 验证结果 {valid, errors}
   */
  validateConfig(config) {
    const errors = [];
    
    if (!config) {
      errors.push('Configuration is null or undefined');
      return { valid: false, errors };
    }
    
    // 验证必需字段
    if (!config.default_position || typeof config.default_position !== 'object') {
      errors.push('default_position is required and must be an object');
    }
    
    if (typeof config.default_opacity !== 'number' || config.default_opacity < 0 || config.default_opacity > 1) {
      errors.push('default_opacity must be a number between 0 and 1');
    }
    
    if (!config.default_size || typeof config.default_size !== 'object') {
      errors.push('default_size is required and must be an object');
    }
    
    // 验证组织结构
    if (config.organization_structure) {
      for (const [categoryName, categoryConfig] of Object.entries(config.organization_structure)) {
        if (!categoryConfig.components || !Array.isArray(categoryConfig.components)) {
          errors.push(`Category "${categoryName}" must have a components array`);
        }
        
        if (typeof categoryConfig.order !== 'number') {
          errors.push(`Category "${categoryName}" must have a numeric order`);
        }
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
  
  /**
   * 获取组件图标映射
   * @returns {Object} - 图标映射对象
   */
  getComponentTypeIcons() {
    return {
      'chart': '📊',
      'table': '📋',
      'stackedAreaChart': '📈',
      'lineChart': '📉',
      'barChart': '📊',
      'pieChart': '🥧',
      'scatterChart': '🎯',
      'heatMap': '🔥',
      'gauge': '⏲️',
      'treemap': '🗂️',
      'sankey': '🌊',
      'radar': '🎯',
      'funnel': '🔺',
      'calendar': '📅'
    };
  }
  
  /**
   * 获取默认分类图标
   * @returns {Object} - 默认分类图标
   */
  getDefaultCategoryIcons() {
    return {
      '图表': '📊',
      '表格': '📋',
      '分析': '📈',
      '数据': '💾',
      '统计': '📊',
      '报告': '📄',
      '监控': '👁️',
      '实时': '⚡',
      '历史': '🕒',
      '趋势': '📈',
      '对比': '⚖️',
      '分布': '📊',
      '排名': '🏆',
      '预测': '🔮',
      '风险': '⚠️',
      '收益': '💰',
      '成交': '💹',
      '价格': '💰',
      '成交量': '📊',
      '板块': '🏢',
      '个股': '📈',
      '指数': '📊',
      '基金': '💼',
      '债券': '📊',
      '期货': '📈',
      '外汇': '💱',
      '商品': '📦'
    };
  }
  
  /**
   * 自动分配分类图标
   * @param {String} categoryName - 分类名称
   * @returns {String} - 图标
   */
  autoAssignCategoryIcon(categoryName) {
    const defaultIcons = this.getDefaultCategoryIcons();
    
    // 精确匹配
    if (defaultIcons[categoryName]) {
      return defaultIcons[categoryName];
    }
    
    // 模糊匹配
    for (const [key, icon] of Object.entries(defaultIcons)) {
      if (categoryName.includes(key) || key.includes(categoryName)) {
        return icon;
      }
    }
    
    // 默认图标
    return '📁';
  }
  
  /**
   * 生成配置模板
   * @param {String} pageKey - 页面标识
   * @param {Array} components - 组件列表
   * @returns {Object} - 配置模板
   */
  generateConfigTemplate(pageKey, components) {
    const template = {
      navigator_organization: {}
    };
    
    // 根据组件类型自动分组
    const typeGroups = {};
    components.forEach(comp => {
      const type = comp.component_type || comp.type || 'unknown';
      if (!typeGroups[type]) {
        typeGroups[type] = [];
      }
      typeGroups[type].push(comp.component_id || comp.id);
    });
    
    let order = 1;
    Object.entries(typeGroups).forEach(([type, componentIds]) => {
      const categoryName = this.getTypeCategoryName(type);
      template.navigator_organization[categoryName] = {
        order: order++,
        components: componentIds,
        icon: this.getComponentTypeIcons()[type] || '📄',
        collapsible: true,
        description: `${categoryName}相关组件`
      };
    });
    
    return template;
  }
  
  /**
   * 根据组件类型获取分类名称
   * @param {String} type - 组件类型
   * @returns {String} - 分类名称
   */
  getTypeCategoryName(type) {
    const nameMap = {
      'chart': '图表分析',
      'table': '数据表格',
      'stackedAreaChart': '面积图表',
      'lineChart': '折线图表',
      'barChart': '柱状图表',
      'pieChart': '饼图分析',
      'scatterChart': '散点图表',
      'heatMap': '热力图表'
    };
    
    return nameMap[type] || '其他组件';
  }
  
  /**
   * 导出配置为JSON
   * @param {String} pageKey - 页面标识
   * @returns {String} - JSON字符串
   */
  exportConfig(pageKey) {
    const config = this.getMergedConfig(pageKey);
    return JSON.stringify(config, null, 2);
  }
  
  /**
   * 重置配置
   */
  reset() {
    this.globalConfig = null;
    this.pageConfigs.clear();
    console.log('🔄 Navigator config manager reset');
  }
}

export default NavigatorConfigManager;
