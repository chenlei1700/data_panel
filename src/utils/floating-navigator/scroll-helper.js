/**
 * 滚动和跳转辅助工具
 */
export class ScrollHelper {
  /**
   * 平滑滚动到指定组件
   * @param {String} componentId - 组件ID
   * @param {Object} options - 滚动选项
   * @returns {Boolean} - 是否成功找到并滚动到组件
   */
  static scrollToComponent(componentId, options = {}) {
    // 尝试多种选择器查找组件
    const selectors = [
      `[data-component-id="${componentId}"]`,
      `#${componentId}`,
      `.component-${componentId}`,
      `[id*="${componentId}"]`
    ];
    
    let element = null;
    for (const selector of selectors) {
      element = document.querySelector(selector);
      if (element) break;
    }
    
    if (!element) {
      console.warn(`Component with id "${componentId}" not found`);
      return false;
    }
    
    // 计算滚动位置，确保组件完全可见
    const rect = element.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const elementHeight = rect.height;
    
    // 如果元素高度超过视窗高度，滚动到顶部
    // 否则滚动到中心
    const block = elementHeight > viewportHeight * 0.8 ? 'start' : 'center';
    
    element.scrollIntoView({
      behavior: 'smooth',
      block: options.block || block,
      inline: options.inline || 'nearest'
    });
    
    // 添加高亮效果
    this.highlightElement(element, options.highlightDuration || 2000);
    
    // 触发自定义事件
    this.dispatchScrollEvent(componentId, element);
    
    return true;
  }
  
  /**
   * 高亮元素
   * @param {HTMLElement} element - 要高亮的元素
   * @param {Number} duration - 高亮持续时间
   */
  static highlightElement(element, duration = 2000) {
    // 移除之前的高亮类
    element.classList.remove('navigator-highlight');
    
    // 强制重排以确保类被移除
    element.offsetHeight;
    
    // 添加高亮类
    element.classList.add('navigator-highlight');
    
    // 设置定时器移除高亮
    setTimeout(() => {
      element.classList.remove('navigator-highlight');
    }, duration);
  }
  
  /**
   * 获取组件在页面中的位置信息
   * @param {String} componentId - 组件ID
   * @returns {Object|null} - 位置信息对象
   */
  static getComponentPosition(componentId) {
    const selectors = [
      `[data-component-id="${componentId}"]`,
      `#${componentId}`,
      `.component-${componentId}`
    ];
    
    let element = null;
    for (const selector of selectors) {
      element = document.querySelector(selector);
      if (element) break;
    }
    
    if (!element) return null;
    
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
    return {
      top: rect.top + scrollTop,
      left: rect.left + scrollLeft,
      width: rect.width,
      height: rect.height,
      visible: rect.top >= 0 && rect.bottom <= window.innerHeight,
      inViewport: rect.top < window.innerHeight && rect.bottom > 0,
      element: element
    };
  }
  
  /**
   * 检查组件是否在视窗中可见
   * @param {String} componentId - 组件ID
   * @returns {Boolean} - 是否可见
   */
  static isComponentVisible(componentId) {
    const position = this.getComponentPosition(componentId);
    return position ? position.inViewport : false;
  }
  
  /**
   * 获取当前视窗中可见的组件列表
   * @param {Array} componentIds - 组件ID列表
   * @returns {Array} - 可见的组件ID列表
   */
  static getVisibleComponents(componentIds) {
    return componentIds.filter(id => this.isComponentVisible(id));
  }
  
  /**
   * 派发滚动事件
   * @param {String} componentId - 组件ID
   * @param {HTMLElement} element - DOM元素
   */
  static dispatchScrollEvent(componentId, element) {
    const event = new CustomEvent('navigator-scroll', {
      detail: {
        componentId,
        element,
        timestamp: Date.now()
      }
    });
    
    document.dispatchEvent(event);
  }
  
  /**
   * 平滑滚动到页面顶部
   */
  static scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
  
  /**
   * 平滑滚动到页面底部
   */
  static scrollToBottom() {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth'
    });
  }
  
  /**
   * 获取页面滚动信息
   * @returns {Object} - 滚动信息
   */
  static getScrollInfo() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = document.documentElement.clientHeight;
    
    return {
      scrollTop,
      scrollHeight,
      clientHeight,
      scrollPercentage: Math.round((scrollTop / (scrollHeight - clientHeight)) * 100) || 0,
      isAtTop: scrollTop === 0,
      isAtBottom: scrollTop + clientHeight >= scrollHeight - 5 // 5px tolerance
    };
  }
}

export default ScrollHelper;
