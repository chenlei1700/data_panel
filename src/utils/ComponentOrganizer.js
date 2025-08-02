/**
 * 组件组织器 - 负责根据配置文件组织和分类页面组件
 */
export class ComponentOrganizer {
  constructor(config = {}) {
    this.config = config;
    this.defaultCategory = '其他组件';
  }

  /**
   * 根据配置组织组件
   * @param {Array} components - 页面中的组件元素
   * @param {Object} organizationConfig - 组织结构配置
   * @returns {Array} 组织后的分类结构
   */
  organizeComponents(components, organizationConfig = {}) {
    const organized = {};
    const usedComponentIds = new Set();
    const seenElements = new Set(); // 跟踪已经处理过的DOM元素

    // 根据配置分类已定义的组件
    if (organizationConfig.categories) {
      organizationConfig.categories.forEach(category => {
        organized[category.name] = {
          ...category,
          components: [],
          items: []
        };

        if (category.components) {
          category.components.forEach(componentId => {
            // 查找所有匹配的元素，但只使用第一个
            const elements = components.filter(comp => 
              comp.dataset.componentId === componentId && !seenElements.has(comp)
            );
            
            if (elements.length > 0) {
              const element = elements[0]; // 只使用第一个匹配的元素
              
              // 如果找到多个相同ID的元素，发出警告
              if (elements.length > 1) {
                console.warn(`🧭 发现重复的组件ID "${componentId}"，只使用第一个元素`);
              }
              
              organized[category.name].components.push(element);
              organized[category.name].items.push({
                id: componentId,
                title: this.getComponentTitle(element),
                element: element,
                icon: this.getComponentTypeIcon(componentId)
              });
              usedComponentIds.add(componentId);
              seenElements.add(element); // 标记此元素已被处理
            }
          });
        }
      });
    }

    // 处理未分类的组件
    const uncategorizedComponents = components.filter(comp => 
      comp.dataset.componentId && 
      !usedComponentIds.has(comp.dataset.componentId) &&
      !seenElements.has(comp) // 确保没有被处理过
    );

    if (uncategorizedComponents.length > 0) {
      organized[this.defaultCategory] = {
        name: this.defaultCategory,
        icon: '📋',
        color: '#8e8e93',
        components: uncategorizedComponents,
        items: uncategorizedComponents.map(element => ({
          id: element.dataset.componentId,
          title: this.getComponentTitle(element),
          element: element,
          icon: this.getComponentTypeIcon(element.dataset.componentId)
        }))
      };
    }

    return Object.values(organized).filter(category => category.items.length > 0);
  }

  /**
   * 搜索组件
   * @param {Array} categories - 分类后的组件
   * @param {string} searchTerm - 搜索关键词
   * @returns {Array} 搜索结果
   */
  searchComponents(categories, searchTerm) {
    if (!searchTerm.trim()) {
      return categories;
    }

    const term = searchTerm.toLowerCase();
    const filteredCategories = [];

    categories.forEach(category => {
      const matchedItems = category.items.filter(item => 
        item.title.toLowerCase().includes(term) ||
        item.id.toLowerCase().includes(term)
      );

      if (matchedItems.length > 0) {
        filteredCategories.push({
          ...category,
          items: matchedItems,
          components: matchedItems.map(item => item.element)
        });
      }
    });

    return filteredCategories;
  }

  /**
   * 获取组件标题
   * @param {Element} element - DOM元素
   * @returns {string} 组件标题
   */
  getComponentTitle(element) {
    // 尝试从多个位置获取标题
    const titleSelectors = [
      '.component-title',
      '.chart-title', 
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      '[data-title]'
    ];

    for (const selector of titleSelectors) {
      const titleElement = element.querySelector(selector);
      if (titleElement) {
        return titleElement.textContent?.trim() || titleElement.dataset.title;
      }
    }

    // 使用 data-component-id 作为后备
    return element.dataset.componentId || '未命名组件';
  }

  /**
   * 根据组件ID获取图标
   * @param {string} componentId - 组件ID
   * @returns {string} 图标
   */
  getComponentTypeIcon(componentId) {
    const iconMap = {
      // 图表类
      chart: '📊',
      line: '📈',
      bar: '📊', 
      pie: '🥧',
      scatter: '⭐',
      area: '🌊',
      
      // 表格类
      table: '📋',
      grid: '⚏',
      list: '📝',
      
      // 数据类
      data: '💾',
      info: 'ℹ️',
      stats: '📊',
      
      // 特殊功能
      upload: '📤',
      download: '📥',
      search: '🔍',
      filter: '🔧',
      
      // 板块相关
      plate: '🏢',
      sector: '🏭',
      stock: '💰',
      limit: '🚀',
      speed: '⚡'
    };

    // 检查ID中包含的关键词
    const id = componentId.toLowerCase();
    for (const [key, icon] of Object.entries(iconMap)) {
      if (id.includes(key)) {
        return icon;
      }
    }

    return '📄'; // 默认图标
  }

  /**
   * 获取组件在页面中的位置信息
   * @param {Element} element - DOM元素
   * @returns {Object} 位置信息
   */
  getComponentPosition(element) {
    const rect = element.getBoundingClientRect();
    return {
      top: rect.top + window.scrollY,
      left: rect.left + window.scrollX,
      width: rect.width,
      height: rect.height,
      visible: rect.top >= 0 && rect.top <= window.innerHeight
    };
  }

  /**
   * 滚动到指定组件
   * @param {Element} element - 目标元素
   * @param {Object} options - 滚动选项
   */
  scrollToComponent(element, options = {}) {
    const defaultOptions = {
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest'
    };

    element.scrollIntoView({ ...defaultOptions, ...options });

    // 添加高亮效果
    if (options.highlight !== false) {
      this.highlightComponent(element);
    }
  }

  /**
   * 高亮显示组件
   * @param {Element} element - 要高亮的元素
   */
  highlightComponent(element) {
    const originalStyle = {
      transition: element.style.transition,
      border: element.style.border,
      boxShadow: element.style.boxShadow
    };

    // 应用高亮样式
    element.style.transition = 'all 0.3s ease';
    element.style.border = '2px solid #007AFF';
    element.style.boxShadow = '0 4px 12px rgba(0, 122, 255, 0.3)';

    // 恢复原始样式
    setTimeout(() => {
      Object.keys(originalStyle).forEach(key => {
        element.style[key] = originalStyle[key];
      });
    }, 2000);
  }
}
