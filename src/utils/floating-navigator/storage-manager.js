/**
 * 本地存储管理
 */

// 静态常�?
const STORAGE_KEY = 'floating-navigator-preferences';
const VERSION = '1.0.0';

export class NavigatorStorageManager {
  /**
   * 保存用户偏好设置
   * @param {Object} preferences - 偏好设置对象
   * @param {String} pageKey - 页面标识�?
   */
  static savePreferences(preferences, pageKey = 'default') {
    try {
      const existingData = this.loadAllPreferences() || {};
      
      existingData[pageKey] = {
        ...preferences,
        version: VERSION,
        timestamp: Date.now(),
        pageKey
      };
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(existingData));
      console.log(`💾 Navigator preferences saved for page: ${pageKey}`);
    } catch (error) {
      console.warn('Failed to save navigator preferences:', error);
    }
  }
  
  /**
   * 加载指定页面的用户偏好设�?
   * @param {String} pageKey - 页面标识�?
   * @returns {Object|null} - 偏好设置对象
   */
  static loadPreferences(pageKey = 'default') {
    try {
      const allData = this.loadAllPreferences();
      if (!allData || !allData[pageKey]) return null;
      
      const preferences = allData[pageKey];
      
      // 检查版本兼容�?
      if (preferences.version !== VERSION) {
        console.log(`🔄 Preferences version mismatch for ${pageKey}, clearing...`);
        this.clearPreferences(pageKey);
        return null;
      }
      
      // 检查是否过期（30天）
      const isExpired = Date.now() - preferences.timestamp > 30 * 24 * 60 * 60 * 1000;
      if (isExpired) {
        console.log(`�?Preferences expired for ${pageKey}, clearing...`);
        this.clearPreferences(pageKey);
        return null;
      }
      
      console.log(`📂 Navigator preferences loaded for page: ${pageKey}`);
      return preferences;
    } catch (error) {
      console.warn('Failed to load navigator preferences:', error);
      return null;
    }
  }
  
  /**
   * 加载所有页面的偏好设置
   * @returns {Object|null} - 所有偏好设�?
   */
  static loadAllPreferences() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.warn('Failed to load all navigator preferences:', error);
      return null;
    }
  }
  
  /**
   * 清除指定页面的偏好设�?
   * @param {String} pageKey - 页面标识�?
   */
  static clearPreferences(pageKey = 'default') {
    try {
      const allData = this.loadAllPreferences() || {};
      delete allData[pageKey];
      
      if (Object.keys(allData).length === 0) {
        localStorage.removeItem(STORAGE_KEY);
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(allData));
      }
      
      console.log(`🗑�?Navigator preferences cleared for page: ${pageKey}`);
    } catch (error) {
      console.warn('Failed to clear navigator preferences:', error);
    }
  }
  
  /**
   * 清除所有偏好设�?
   */
  static clearAllPreferences() {
    try {
      localStorage.removeItem(STORAGE_KEY);
      console.log('🗑�?All navigator preferences cleared');
    } catch (error) {
      console.warn('Failed to clear all navigator preferences:', error);
    }
  }
  
  /**
   * 获取存储使用情况
   * @returns {Object} - 存储信息
   */
  static getStorageInfo() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      const allData = data ? JSON.parse(data) : {};
      
      return {
        totalSize: new Blob([data || '']).size,
        pageCount: Object.keys(allData).length,
        pages: Object.keys(allData),
        lastModified: Math.max(...Object.values(allData).map(p => p.timestamp || 0)),
        version: VERSION
      };
    } catch (error) {
      console.warn('Failed to get storage info:', error);
      return {
        totalSize: 0,
        pageCount: 0,
        pages: [],
        lastModified: 0,
        version: VERSION
      };
    }
  }
  
  /**
   * 导出偏好设置
   * @returns {String} - JSON字符�?
   */
  static exportPreferences() {
    try {
      const allData = this.loadAllPreferences() || {};
      return JSON.stringify(allData, null, 2);
    } catch (error) {
      console.warn('Failed to export preferences:', error);
      return '{}';
    }
  }
  
  /**
   * 导入偏好设置
   * @param {String} jsonString - JSON字符�?
   * @returns {Boolean} - 是否成功
   */
  static importPreferences(jsonString) {
    try {
      const data = JSON.parse(jsonString);
      
      // 验证数据格式
      if (typeof data !== 'object' || data === null) {
        throw new Error('Invalid data format');
      }
      
      // 更新时间戳和版本
      Object.keys(data).forEach(pageKey => {
        if (data[pageKey] && typeof data[pageKey] === 'object') {
          data[pageKey].timestamp = Date.now();
          data[pageKey].version = VERSION;
        }
      });
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      console.log('📥 Navigator preferences imported successfully');
      return true;
    } catch (error) {
      console.warn('Failed to import preferences:', error);
      return false;
    }
  }
  
  /**
   * 检查本地存储可用�?
   * @returns {Boolean} - 是否可用
   */
  static isStorageAvailable() {
    try {
      const test = '__storage_test__';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch (error) {
      return false;
    }
  }
  
  /**
   * 获取默认偏好设置
   * @param {Object} config - 配置对象
   * @returns {Object} - 默认偏好设置
   */
  static getDefaultPreferences(config = {}) {
    return {
      position: config.default_position || { x: 20, y: 100 },
      opacity: config.default_opacity || 0.9,
      collapsed: false,
      visible: true,
      theme: 'default',
      categoryStates: {}, // 记录各分类的展开/折叠状�?
      searchHistory: [], // 搜索历史
      lastScrollPosition: 0,
      version: VERSION,
      timestamp: Date.now()
    };
  }
}

export default NavigatorStorageManager;
