/**
 * 组件分类和组织逻辑
 */
export class ComponentOrganizer {
  constructor(organizationConfig) {
    this.config = organizationConfig || {};
  }
  
  /**
   * 将组件按配置分类
   * @param {Array} components - 组件列表
   * @returns {Object} - { organized, uncategorized }
   */
  organizeComponents(components) {
    const organized = {};
    const uncategorized = [];
    
    // 按配置分类
    Object.entries(this.config.organization_structure || {}).forEach(([categoryName, categoryConfig]) => {
      organized[categoryName] = {
        ...categoryConfig,
        items: components.filter(comp => categoryConfig.components.includes(comp.component_id || comp.id))
      };
    });
    
    // 按order排序分类
    const sortedOrganized = {};
    Object.entries(organized)
      .sort(([,a], [,b]) => (a.order || 0) - (b.order || 0))
      .forEach(([key, value]) => {
        sortedOrganized[key] = value;
      });
    
    // 找出未分类的组件
    const categorizedIds = Object.values(this.config.organization_structure || {})
      .flatMap(config => config.components);
    uncategorized.push(...components.filter(comp => 
      !categorizedIds.includes(comp.component_id || comp.id)
    ));
    
    return { organized: sortedOrganized, uncategorized };
  }
  
  /**
   * 搜索组件
   * @param {Array} components - 组件列表
   * @param {String} query - 搜索关键词
   * @returns {Array} - 匹配的组件列表
   */
  searchComponents(components, query) {
    if (!query || !query.trim()) return components;
    
    const lowerQuery = query.toLowerCase().trim();
    return components.filter(comp => 
      (comp.title && comp.title.toLowerCase().includes(lowerQuery)) ||
      (comp.description && comp.description.toLowerCase().includes(lowerQuery)) ||
      (comp.component_id && comp.component_id.toLowerCase().includes(lowerQuery)) ||
      (comp.id && comp.id.toLowerCase().includes(lowerQuery))
    );
  }
  
  /**
   * 过滤分类中的组件
   * @param {Object} organized - 已分类的组件
   * @param {String} query - 搜索关键词
   * @returns {Object} - 过滤后的分类组件
   */
  filterOrganizedComponents(organized, query) {
    if (!query || !query.trim()) return organized;
    
    const filtered = {};
    Object.entries(organized).forEach(([categoryName, categoryData]) => {
      const filteredItems = this.searchComponents(categoryData.items, query);
      if (filteredItems.length > 0) {
        filtered[categoryName] = {
          ...categoryData,
          items: filteredItems
        };
      }
    });
    
    return filtered;
  }
  
  /**
   * 获取组件类型图标
   * @param {String} type - 组件类型
   * @returns {String} - 对应的图标
   */
  getComponentTypeIcon(type) {
    const iconMap = {
      'chart': '📊',
      'table': '📋',
      'stackedAreaChart': '📈',
      'lineChart': '📉',
      'barChart': '📊',
      'pieChart': '🥧',
      'scatterChart': '🎯',
      'heatMap': '🔥'
    };
    
    return iconMap[type] || '📄';
  }
  
  /**
   * 获取位置文本描述
   * @param {Object} position - 位置对象 {row, col, rowSpan, colSpan}
   * @returns {String} - 位置描述文本
   */
  getPositionText(position) {
    if (!position) return '';
    
    const { row, col, rowSpan = 1, colSpan = 1 } = position;
    const rowText = rowSpan > 1 ? `${row + 1}-${row + rowSpan}` : `${row + 1}`;
    const colText = colSpan > 1 ? `${col + 1}-${col + colSpan}` : `${col + 1}`;
    
    return `R${rowText}C${colText}`;
  }
}

export default ComponentOrganizer;
