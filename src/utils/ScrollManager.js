/**
 * 滚动管理器 - 处理平滑滚动和元素定位
 */
export class ScrollManager {
  constructor(options = {}) {
    this.options = {
      behavior: 'smooth',
      block: 'center',
      inline: 'nearest',
      highlightDuration: 2000,
      highlightStyle: {
        border: '2px solid #007AFF',
        boxShadow: '0 4px 12px rgba(0, 122, 255, 0.3)',
        transition: 'all 0.3s ease'
      },
      ...options
    };
  }

  /**
   * 滚动到指定元素
   * @param {Element|string} target - 目标元素或选择器
   * @param {Object} options - 滚动选项
   * @returns {Promise} 滚动完成的Promise
   */
  scrollToElement(target, options = {}) {
    return new Promise((resolve, reject) => {
      const element = typeof target === 'string' 
        ? document.querySelector(target)
        : target;

      if (!element) {
        reject(new Error('目标元素未找到'));
        return;
      }

      const scrollOptions = { ...this.options, ...options };

      try {
        element.scrollIntoView({
          behavior: scrollOptions.behavior,
          block: scrollOptions.block,
          inline: scrollOptions.inline
        });

        // 等待滚动完成后高亮
        setTimeout(() => {
          if (scrollOptions.highlight !== false) {
            this.highlightElement(element, scrollOptions.highlightStyle);
          }
          resolve(element);
        }, scrollOptions.behavior === 'smooth' ? 500 : 100);

      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 滚动到指定组件ID
   * @param {string} componentId - 组件ID
   * @param {Object} options - 滚动选项
   * @returns {Promise} 滚动完成的Promise
   */
  scrollToComponent(componentId, options = {}) {
    const selector = `[data-component-id="${componentId}"]`;
    return this.scrollToElement(selector, options);
  }

  /**
   * 高亮显示元素
   * @param {Element} element - 要高亮的元素
   * @param {Object} style - 高亮样式
   */
  highlightElement(element, style = {}) {
    if (!element) return;

    const highlightStyle = { ...this.options.highlightStyle, ...style };
    
    // 保存原始样式
    const originalStyle = {};
    Object.keys(highlightStyle).forEach(property => {
      originalStyle[property] = element.style[property] || '';
    });

    // 应用高亮样式
    Object.keys(highlightStyle).forEach(property => {
      element.style[property] = highlightStyle[property];
    });

    // 恢复原始样式
    setTimeout(() => {
      Object.keys(originalStyle).forEach(property => {
        element.style[property] = originalStyle[property];
      });
    }, this.options.highlightDuration);
  }

  /**
   * 获取元素在视口中的位置
   * @param {Element} element - 目标元素
   * @returns {Object} 位置信息
   */
  getElementViewportPosition(element) {
    if (!element) return null;

    const rect = element.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    return {
      top: rect.top,
      left: rect.left,
      bottom: rect.bottom,
      right: rect.right,
      width: rect.width,
      height: rect.height,
      isVisible: rect.top >= 0 && rect.left >= 0 && 
                rect.bottom <= viewportHeight && rect.right <= viewportWidth,
      isPartiallyVisible: rect.top < viewportHeight && rect.bottom > 0 &&
                         rect.left < viewportWidth && rect.right > 0,
      visibilityPercentage: this.calculateVisibilityPercentage(rect, viewportWidth, viewportHeight)
    };
  }

  /**
   * 计算元素可见性百分比
   * @param {DOMRect} rect - 元素的边界矩形
   * @param {number} viewportWidth - 视口宽度
   * @param {number} viewportHeight - 视口高度
   * @returns {number} 可见性百分比 (0-100)
   */
  calculateVisibilityPercentage(rect, viewportWidth, viewportHeight) {
    const visibleWidth = Math.min(rect.right, viewportWidth) - Math.max(rect.left, 0);
    const visibleHeight = Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0);
    
    if (visibleWidth <= 0 || visibleHeight <= 0) {
      return 0;
    }

    const visibleArea = visibleWidth * visibleHeight;
    const totalArea = rect.width * rect.height;
    
    return Math.round((visibleArea / totalArea) * 100);
  }

  /**
   * 获取页面中所有带有组件ID的元素
   * @returns {Array} 组件元素数组
   */
  getAllComponents() {
    return Array.from(document.querySelectorAll('[data-component-id]'));
  }

  /**
   * 获取当前视口中可见的组件
   * @returns {Array} 可见组件数组
   */
  getVisibleComponents() {
    const components = this.getAllComponents();
    return components.filter(component => {
      const position = this.getElementViewportPosition(component);
      return position && position.isPartiallyVisible;
    });
  }

  /**
   * 获取最靠近视口中心的组件
   * @returns {Element|null} 最近的组件元素
   */
  getNearestComponent() {
    const components = this.getAllComponents();
    const viewportCenterY = window.innerHeight / 2;
    
    let nearestComponent = null;
    let minDistance = Infinity;

    components.forEach(component => {
      const rect = component.getBoundingClientRect();
      const componentCenterY = rect.top + rect.height / 2;
      const distance = Math.abs(componentCenterY - viewportCenterY);

      if (distance < minDistance) {
        minDistance = distance;
        nearestComponent = component;
      }
    });

    return nearestComponent;
  }

  /**
   * 平滑滚动到页面顶部
   * @param {Object} options - 滚动选项
   */
  scrollToTop(options = {}) {
    const scrollOptions = { 
      top: 0, 
      behavior: this.options.behavior,
      ...options 
    };
    
    window.scrollTo(scrollOptions);
  }

  /**
   * 平滑滚动到页面底部
   * @param {Object} options - 滚动选项
   */
  scrollToBottom(options = {}) {
    const scrollOptions = { 
      top: document.documentElement.scrollHeight, 
      behavior: this.options.behavior,
      ...options 
    };
    
    window.scrollTo(scrollOptions);
  }

  /**
   * 监听滚动事件
   * @param {Function} callback - 回调函数
   * @param {Object} options - 选项
   * @returns {Function} 取消监听的函数
   */
  onScroll(callback, options = {}) {
    const { throttle = 100 } = options;
    let timeoutId = null;

    const throttledCallback = () => {
      if (timeoutId) clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const visibleComponents = this.getVisibleComponents();
        const nearestComponent = this.getNearestComponent();
        callback({
          visibleComponents,
          nearestComponent,
          scrollY: window.scrollY,
          scrollX: window.scrollX
        });
      }, throttle);
    };

    window.addEventListener('scroll', throttledCallback);

    // 返回取消监听的函数
    return () => {
      window.removeEventListener('scroll', throttledCallback);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }
}
