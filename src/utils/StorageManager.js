/**
 * 存储管理器 - 处理用户偏好设置的本地存储
 */
export class StorageManager {
  constructor(prefix = 'floating-navigator') {
    this.prefix = prefix;
  }

  /**
   * 保存用户偏好设置
   * @param {Object} preferences - 偏好设置对象
   */
  savePreferences(preferences) {
    try {
      const key = `${this.prefix}-preferences`;
      localStorage.setItem(key, JSON.stringify(preferences));
    } catch (error) {
      console.warn('无法保存用户偏好设置:', error);
    }
  }

  /**
   * 加载用户偏好设置
   * @returns {Object} 偏好设置对象
   */
  loadPreferences() {
    try {
      const key = `${this.prefix}-preferences`;
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : this.getDefaultPreferences();
    } catch (error) {
      console.warn('无法加载用户偏好设置:', error);
      return this.getDefaultPreferences();
    }
  }

  /**
   * 获取默认偏好设置
   * @returns {Object} 默认设置
   */
  getDefaultPreferences() {
    return {
      position: { x: 20, y: 20 },
      opacity: 0.95,
      isVisible: true,
      isMinimized: false,
      theme: 'light',
      autoHide: false,
      showSearch: true,
      expandedCategories: [],
      lastOpenTime: Date.now()
    };
  }

  /**
   * 保存窗口位置
   * @param {Object} position - 位置对象 {x, y}
   */
  savePosition(position) {
    const preferences = this.loadPreferences();
    preferences.position = position;
    this.savePreferences(preferences);
  }

  /**
   * 加载窗口位置
   * @returns {Object} 位置对象
   */
  loadPosition() {
    const preferences = this.loadPreferences();
    return preferences.position || { x: 20, y: 20 };
  }

  /**
   * 保存透明度设置
   * @param {number} opacity - 透明度值 (0-1)
   */
  saveOpacity(opacity) {
    const preferences = this.loadPreferences();
    preferences.opacity = opacity;
    this.savePreferences(preferences);
  }

  /**
   * 加载透明度设置
   * @returns {number} 透明度值
   */
  loadOpacity() {
    const preferences = this.loadPreferences();
    return preferences.opacity !== undefined ? preferences.opacity : 0.95;
  }

  /**
   * 保存可见性状态
   * @param {boolean} isVisible - 是否可见
   */
  saveVisibility(isVisible) {
    const preferences = this.loadPreferences();
    preferences.isVisible = isVisible;
    this.savePreferences(preferences);
  }

  /**
   * 加载可见性状态
   * @returns {boolean} 是否可见
   */
  loadVisibility() {
    const preferences = this.loadPreferences();
    return preferences.isVisible !== undefined ? preferences.isVisible : true;
  }

  /**
   * 保存最小化状态
   * @param {boolean} isMinimized - 是否最小化
   */
  saveMinimizedState(isMinimized) {
    const preferences = this.loadPreferences();
    preferences.isMinimized = isMinimized;
    this.savePreferences(preferences);
  }

  /**
   * 加载最小化状态
   * @returns {boolean} 是否最小化
   */
  loadMinimizedState() {
    const preferences = this.loadPreferences();
    return preferences.isMinimized || false;
  }

  /**
   * 保存展开的分类
   * @param {Array} expandedCategories - 展开的分类名称数组
   */
  saveExpandedCategories(expandedCategories) {
    const preferences = this.loadPreferences();
    preferences.expandedCategories = expandedCategories;
    this.savePreferences(preferences);
  }

  /**
   * 加载展开的分类
   * @returns {Array} 展开的分类名称数组
   */
  loadExpandedCategories() {
    const preferences = this.loadPreferences();
    return preferences.expandedCategories || [];
  }

  /**
   * 保存主题设置
   * @param {string} theme - 主题名称
   */
  saveTheme(theme) {
    const preferences = this.loadPreferences();
    preferences.theme = theme;
    this.savePreferences(preferences);
  }

  /**
   * 加载主题设置
   * @returns {string} 主题名称
   */
  loadTheme() {
    const preferences = this.loadPreferences();
    return preferences.theme || 'light';
  }

  /**
   * 清除所有存储的数据
   */
  clearAll() {
    try {
      const keys = Object.keys(localStorage).filter(key => 
        key.startsWith(this.prefix)
      );
      keys.forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.warn('无法清除存储数据:', error);
    }
  }

  /**
   * 导出设置
   * @returns {Object} 所有设置
   */
  exportSettings() {
    return this.loadPreferences();
  }

  /**
   * 导入设置
   * @param {Object} settings - 设置对象
   */
  importSettings(settings) {
    if (typeof settings === 'object' && settings !== null) {
      const currentSettings = this.loadPreferences();
      const mergedSettings = { ...currentSettings, ...settings };
      this.savePreferences(mergedSettings);
    }
  }

  /**
   * 获取存储使用情况
   * @returns {Object} 存储信息
   */
  getStorageInfo() {
    try {
      const keys = Object.keys(localStorage).filter(key => 
        key.startsWith(this.prefix)
      );
      
      let totalSize = 0;
      keys.forEach(key => {
        totalSize += localStorage.getItem(key).length;
      });

      return {
        keys: keys.length,
        size: totalSize,
        sizeKB: (totalSize / 1024).toFixed(2)
      };
    } catch (error) {
      return { keys: 0, size: 0, sizeKB: '0.00' };
    }
  }
}
