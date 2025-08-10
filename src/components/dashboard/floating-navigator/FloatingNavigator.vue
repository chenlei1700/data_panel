<template>
  <draggable-window
    v-if="visible && config"
    :position="position"
    :opacity="opacity"
    :size="size"
    :theme="currentTheme"
    :constrain-to-viewport="true"
    drag-handle=".navigator-header"
    @position-change="updatePosition"
    @drag-start="handleDragStart"
    @drag-end="handleDragEnd"
  >
    <div class="floating-navigator" :class="{ 'collapsed': collapsed, 'dragging': isDragging }">
      <!-- 导航器标题栏 -->
      <div class="navigator-header drag-handle">
        <div class="header-left">
          <span class="navigator-icon">🧭</span>
          <h4 class="navigator-title">{{ title }}</h4>
        </div>
        
        <div class="header-controls">
          <!-- 透明度控制 -->
          <opacity-slider
            v-model="opacity"
            :size="'small'"
            :theme="(config.settings && config.settings.theme) || 'light'"
            :show-label="false"
            @change="handleOpacityChange"
          />
          
          <!-- 控制按钮 -->
          <button 
            class="control-btn settings-btn"
            @click="showSettings = !showSettings"
            :title="showSettings ? '隐藏设置' : '显示设置'"
          >
            ⚙️
          </button>
          
          <button 
            class="control-btn collapse-btn"
            @click="toggleCollapse"
            :title="collapsed ? '展开导航器' : '折叠导航器'"
          >
            {{ collapsed ? '📖' : '📚' }}
          </button>
          
          <button 
            class="control-btn close-btn"
            @click="hide"
            title="隐藏导航器"
          >
            ✕
          </button>
        </div>
      </div>
      
      <!-- 设置面板 -->
      <transition name="settings-slide">
        <div v-if="showSettings && !collapsed" class="settings-panel">
          <div class="settings-row">
            <label class="settings-label">主题:</label>
            <select v-model="selectedTheme" class="settings-select">
              <option value="light">亮色</option>
              <option value="dark">暗色</option>
            </select>
          </div>
          
          <div class="settings-row">
            <label class="settings-label">显示描述:</label>
            <input 
              type="checkbox" 
              v-model="showComponentDescriptions"
              class="settings-checkbox"
            />
          </div>
          
          <div class="settings-row">
            <label class="settings-label">自动折叠:</label>
            <input 
              type="checkbox" 
              v-model="autoCollapseCategories"
              class="settings-checkbox"
            />
          </div>
          
          <div class="settings-actions">
            <button class="settings-action-btn" @click="expandAllCategories">
              展开全部
            </button>
            <button class="settings-action-btn" @click="collapseAllCategories">
              折叠全部
            </button>
            <button class="settings-action-btn" @click="resetPosition">
              重置位置
            </button>
          </div>
        </div>
      </transition>
      
      <!-- 导航器主体 -->
      <transition name="navigator-collapse">
        <div v-if="!collapsed" class="navigator-body">
          <!-- 搜索框 -->
          <navigator-search
            v-if="config.settings && config.settings.enable_search"
            v-model="searchQuery"
            :suggestions="searchSuggestions"
            :search-history="searchHistory"
            :result-count="filteredComponentCount"
            :placeholder="'搜索组件...'"
            @search="handleSearch"
            @suggestion-select="handleSuggestionSelect"
            @history-update="updateSearchHistory"
            @history-clear="clearSearchHistory"
            @history-remove="removeSearchHistory"
          />
          
          <!-- 统计信息 -->
          <div v-if="showStats" class="navigator-stats">
            <div class="stats-item">
              <span class="stats-label">组件:</span>
              <span class="stats-value">{{ filteredComponentCount }}/{{ totalComponentCount }}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">可见:</span>
              <span class="stats-value">{{ visibleComponentCount }}</span>
            </div>
          </div>
          
          <!-- 树形导航 -->
          <navigator-tree
            :organized-components="organizedComponents"
            :uncategorized-components="uncategorizedComponents"
            :search-query="searchQuery"
            :active-component-id="activeComponentId"
            :category-states="categoryStates"
            :uncategorized-config="config.uncategorized_section"
            :show-component-descriptions="showComponentDescriptions"
            :enable-tooltips="config.settings && config.settings.enable_tooltips"
            :highlight-color="currentTheme.text_color"
            :auto-collapse-categories="autoCollapseCategories"
            :loading="loading"
            @component-click="handleComponentClick"
            @scroll-to="handleScrollTo"
            @category-toggle="handleCategoryToggle"
            @visibility-change="handleVisibilityChange"
            @update:category-states="updateCategoryStates"
          />
        </div>
      </transition>
      
      <!-- 快捷键提示 -->
      <div v-if="showKeyboardShortcuts && !collapsed" class="keyboard-shortcuts">
        <div class="shortcuts-title">快捷键</div>
        <div class="shortcuts-list">
          <div class="shortcut-item">
            <kbd>Ctrl+F</kbd>
            <span>搜索</span>
          </div>
          <div class="shortcut-item">
            <kbd>Esc</kbd>
            <span>清除搜索</span>
          </div>
        </div>
      </div>
    </div>
  </draggable-window>
</template>

<script>
import { defineComponent, ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import DraggableWindow from '@/components/common/DraggableWindow.vue';
import OpacitySlider from '@/components/common/OpacitySlider.vue';
import NavigatorSearch from './NavigatorSearch.vue';
import NavigatorTree from './NavigatorTree.vue';
import { 
  ComponentOrganizer, 
  NavigatorStorageManager, 
  NavigatorConfigManager 
} from '@/utils/floating-navigator';

export default defineComponent({
  name: 'FloatingNavigator',
  components: {
    DraggableWindow,
    OpacitySlider,
    NavigatorSearch,
    NavigatorTree
  },
  props: {
    components: {
      type: Array,
      default: () => []
    },
    config: {
      type: Object,
      required: true
    },
    pageKey: {
      type: String,
      default: 'default'
    },
    visible: {
      type: Boolean,
      default: true
    }
  },
  emits: ['component-click', 'visibility-change', 'position-change'],
  setup(props, { emit }) {
    const route = useRoute();
    
    // 基础状态
    const position = ref({ x: 20, y: 100 });
    const opacity = ref(0.9);
    const collapsed = ref(false);
    const visible = ref(props.visible);
    const isDragging = ref(false);
    const loading = ref(false);
    
    // UI状态
    const showSettings = ref(false);
    const showStats = ref(true);
    const showKeyboardShortcuts = ref(false);
    const selectedTheme = ref('light');
    const showComponentDescriptions = ref(false);
    const autoCollapseCategories = ref(false);
    
    // 搜索和导航状态
    const searchQuery = ref('');
    const searchHistory = ref([]);
    const activeComponentId = ref('');
    const categoryStates = ref({});
    const visibleComponentCount = ref(0);
    
    // 工具实例
    const organizer = new ComponentOrganizer();
    const configManager = new NavigatorConfigManager();
    
    // 计算属性
    const size = computed(() => props.config.default_size || { width: 320, height: 450 });
    
    const title = computed(() => {
      return configManager.getPageTitle(props.pageKey) || '数据导航';
    });
    
    const currentTheme = computed(() => {
      const themes = props.config.themes || {};
      return themes[selectedTheme.value] || themes.default || {
        background_color: 'rgba(255, 255, 255, 0.95)',
        text_color: '#333333'
      };
    });
    
    // 组织化的组件
    const { organized: organizedComponents, uncategorized: uncategorizedComponents } = computed(() => {
      if (!props.components.length) return { organized: {}, uncategorized: [] };
      
      configManager.setGlobalConfig(props.config);
      configManager.setPageConfig(props.pageKey, { navigator_organization: props.config.organization_structure });
      
      const mergedConfig = configManager.getMergedConfig(props.pageKey);
      organizer.config = mergedConfig;
      
      return organizer.organizeComponents(props.components);
    }).value;
    
    // 搜索建议
    const searchSuggestions = computed(() => {
      if (!searchQuery.value) return [];
      
      const allTitles = props.components.map(comp => comp.title).filter(Boolean);
      return allTitles.filter(title => 
        title.toLowerCase().includes(searchQuery.value.toLowerCase())
      ).slice(0, 5);
    });
    
    // 过滤后的组件数量
    const filteredComponentCount = computed(() => {
      if (!searchQuery.value) return totalComponentCount.value;
      
      const organizedCount = Object.values(organizer.filterOrganizedComponents(organizedComponents, searchQuery.value))
        .reduce((sum, category) => sum + category.items.length, 0);
      const uncategorizedCount = organizer.searchComponents(uncategorizedComponents, searchQuery.value).length;
      
      return organizedCount + uncategorizedCount;
    });
    
    const totalComponentCount = computed(() => props.components.length);
    
    // 方法
    const updatePosition = (newPosition) => {
      position.value = newPosition;
      savePreferences();
      emit('position-change', newPosition);
    };
    
    const handleOpacityChange = (newOpacity) => {
      opacity.value = newOpacity;
      savePreferences();
    };
    
    const handleDragStart = () => {
      isDragging.value = true;
    };
    
    const handleDragEnd = () => {
      isDragging.value = false;
      savePreferences();
    };
    
    const toggleCollapse = () => {
      collapsed.value = !collapsed.value;
      savePreferences();
    };
    
    const hide = () => {
      visible.value = false;
      emit('visibility-change', false);
    };
    
    const show = () => {
      visible.value = true;
      emit('visibility-change', true);
    };
    
    const handleComponentClick = (component) => {
      activeComponentId.value = component.component_id || component.id;
      emit('component-click', component);
    };
    
    const handleScrollTo = (data) => {
      activeComponentId.value = data.component.component_id || data.component.id;
    };
    
    const handleSearch = (query) => {
      searchQuery.value = query;
    };
    
    const handleSuggestionSelect = (suggestion) => {
      searchQuery.value = suggestion;
      updateSearchHistory([suggestion, ...searchHistory.value.filter(h => h !== suggestion)]);
    };
    
    const handleCategoryToggle = (data) => {
      categoryStates.value = data.categoryStates;
      savePreferences();
    };
    
    const updateCategoryStates = (states) => {
      categoryStates.value = states;
      savePreferences();
    };
    
    const handleVisibilityChange = (data) => {
      visibleComponentCount.value = data.visible.length;
    };
    
    const updateSearchHistory = (history) => {
      searchHistory.value = history.slice(0, 10); // 最多保存10条
      savePreferences();
    };
    
    const clearSearchHistory = () => {
      searchHistory.value = [];
      savePreferences();
    };
    
    const removeSearchHistory = (index) => {
      searchHistory.value.splice(index, 1);
      savePreferences();
    };
    
    const expandAllCategories = () => {
      const states = {};
      Object.keys(organizedComponents).forEach(key => {
        states[key] = true;
      });
      if (uncategorizedComponents.length > 0) {
        states.uncategorized = true;
      }
      updateCategoryStates(states);
    };
    
    const collapseAllCategories = () => {
      updateCategoryStates({});
    };
    
    const resetPosition = () => {
      const defaultPos = props.config.default_position || { x: 20, y: 100 };
      updatePosition(defaultPos);
    };
    
    // 保存用户偏好
    const savePreferences = () => {
      if (!(props.config.settings && props.config.settings.remember_user_preferences)) return;
      
      const preferences = {
        position: position.value,
        opacity: opacity.value,
        collapsed: collapsed.value,
        visible: visible.value,
        selectedTheme: selectedTheme.value,
        showComponentDescriptions: showComponentDescriptions.value,
        autoCollapseCategories: autoCollapseCategories.value,
        categoryStates: categoryStates.value,
        searchHistory: searchHistory.value
      };
      
      NavigatorStorageManager.savePreferences(preferences, props.pageKey);
    };
    
    // 加载用户偏好
    const loadPreferences = () => {
      if (!(props.config.settings && props.config.settings.remember_user_preferences)) return;
      
      const saved = NavigatorStorageManager.loadPreferences(props.pageKey);
      if (!saved) return;
      
      position.value = saved.position || props.config.default_position || { x: 20, y: 100 };
      opacity.value = saved.opacity !== undefined && saved.opacity !== null ? saved.opacity : (props.config.default_opacity !== undefined && props.config.default_opacity !== null ? props.config.default_opacity : 0.9);
      collapsed.value = saved.collapsed !== undefined && saved.collapsed !== null ? saved.collapsed : false;
      selectedTheme.value = saved.selectedTheme || 'light';
      showComponentDescriptions.value = saved.showComponentDescriptions !== undefined && saved.showComponentDescriptions !== null ? saved.showComponentDescriptions : false;
      autoCollapseCategories.value = saved.autoCollapseCategories !== undefined && saved.autoCollapseCategories !== null ? saved.autoCollapseCategories : false;
      categoryStates.value = saved.categoryStates || {};
      searchHistory.value = saved.searchHistory || [];
    };
    
    // 键盘快捷键处理
    const handleKeyDown = (event) => {
      if (!(props.config.settings && props.config.settings.enable_keyboard_shortcuts)) return;
      
      // 注释掉 Ctrl+F 处理，让浏览器原生搜索功能正常工作
      // if (event.ctrlKey && event.key === 'f') {
      //   event.preventDefault();
      //   // 聚焦搜索框的逻辑
      // }
      
      // Esc 清除搜索
      if (event.key === 'Escape') {
        searchQuery.value = '';
      }
    };
    
    // 监听属性变化
    watch(() => props.visible, (newVisible) => {
      visible.value = newVisible;
    });
    
    watch(() => props.config, (newConfig) => {
      if (newConfig) {
        // 应用新配置的默认值
        if (!position.value) {
          position.value = newConfig.default_position || { x: 20, y: 100 };
        }
        if (!opacity.value) {
          opacity.value = newConfig.default_opacity || 0.9;
        }
      }
    }, { immediate: true });
    
    // 生命周期
    onMounted(() => {
      loadPreferences();
      
      // 添加键盘事件监听
      document.addEventListener('keydown', handleKeyDown);
      
      // 初始化分类展开状态
      if (Object.keys(categoryStates.value).length === 0) {
        // 默认展开前两个分类
        const categoryNames = Object.keys(organizedComponents);
        if (categoryNames.length > 0) {
          categoryStates.value[categoryNames[0]] = true;
          if (categoryNames.length > 1) {
            categoryStates.value[categoryNames[1]] = true;
          }
        }
      }
    });
    
    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleKeyDown);
      savePreferences();
    });
    
    return {
      // 状态
      position,
      opacity,
      size,
      collapsed,
      visible,
      isDragging,
      loading,
      
      // UI状态
      showSettings,
      showStats,
      showKeyboardShortcuts,
      selectedTheme,
      showComponentDescriptions,
      autoCollapseCategories,
      
      // 数据
      title,
      currentTheme,
      organizedComponents,
      uncategorizedComponents,
      searchQuery,
      searchSuggestions,
      searchHistory,
      activeComponentId,
      categoryStates,
      filteredComponentCount,
      totalComponentCount,
      visibleComponentCount,
      
      // 方法
      updatePosition,
      handleOpacityChange,
      handleDragStart,
      handleDragEnd,
      toggleCollapse,
      hide,
      show,
      handleComponentClick,
      handleScrollTo,
      handleSearch,
      handleSuggestionSelect,
      handleCategoryToggle,
      updateCategoryStates,
      handleVisibilityChange,
      updateSearchHistory,
      clearSearchHistory,
      removeSearchHistory,
      expandAllCategories,
      collapseAllCategories,
      resetPosition
    };
  }
});
</script>

<style scoped>
.floating-navigator {
  display: flex;
  flex-direction: column;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.floating-navigator.collapsed {
  height: auto;
}

.floating-navigator.dragging {
  user-select: none;
}

/* 标题栏 */
.navigator-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: move;
  border-radius: 12px 12px 0 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.navigator-icon {
  font-size: 16px;
}

.navigator-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.control-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.control-btn:active {
  transform: translateY(0);
}

/* 设置面板 */
.settings-panel {
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 8px 12px;
}

.settings-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.settings-row:last-child {
  margin-bottom: 0;
}

.settings-label {
  font-size: 11px;
  color: #666;
  font-weight: 500;
}

.settings-select {
  font-size: 10px;
  padding: 2px 4px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 3px;
  background: white;
}

.settings-checkbox {
  width: 14px;
  height: 14px;
}

.settings-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.settings-action-btn {
  flex: 1;
  background: #667eea;
  color: white;
  border: none;
  padding: 4px 6px;
  border-radius: 3px;
  font-size: 9px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.settings-action-btn:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
}

/* 导航器主体 */
.navigator-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 统计信息 */
.navigator-stats {
  display: flex;
  justify-content: space-between;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 10px;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stats-label {
  color: #666;
}

.stats-value {
  color: #333;
  font-weight: 600;
}

/* 快捷键提示 */
.keyboard-shortcuts {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  font-size: 10px;
}

.shortcuts-title {
  font-weight: 600;
  color: #666;
  margin-bottom: 4px;
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.shortcut-item kbd {
  background: rgba(0, 0, 0, 0.1);
  padding: 1px 4px;
  border-radius: 2px;
  font-size: 9px;
  font-family: monospace;
}

/* 动画 */
.settings-slide-enter-active,
.settings-slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.settings-slide-enter-from,
.settings-slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.settings-slide-enter-to,
.settings-slide-leave-from {
  max-height: 200px;
  opacity: 1;
}

.navigator-collapse-enter-active,
.navigator-collapse-leave-active {
  transition: all 0.3s ease;
}

.navigator-collapse-enter-from,
.navigator-collapse-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.navigator-collapse-enter-to,
.navigator-collapse-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* 暗色主题 */
@media (prefers-color-scheme: dark) {
  .settings-panel {
    background: rgba(255, 255, 255, 0.02);
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .settings-label {
    color: #a0aec0;
  }
  
  .settings-select {
    background: #2d3748;
    border-color: rgba(255, 255, 255, 0.2);
    color: white;
  }
  
  .navigator-stats {
    background: rgba(255, 255, 255, 0.02);
    border-bottom-color: rgba(255, 255, 255, 0.05);
  }
  
  .stats-label {
    color: #a0aec0;
  }
  
  .stats-value {
    color: #fff;
  }
  
  .keyboard-shortcuts {
    background: rgba(255, 255, 255, 0.02);
    border-top-color: rgba(255, 255, 255, 0.05);
  }
  
  .shortcuts-title {
    color: #a0aec0;
  }
  
  .shortcut-item kbd {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navigator-header {
    padding: 8px 10px;
  }
  
  .navigator-title {
    font-size: 13px;
  }
  
  .header-controls {
    gap: 4px;
  }
  
  .control-btn {
    min-width: 20px;
    height: 20px;
    font-size: 10px;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .floating-navigator,
  .control-btn,
  .settings-action-btn,
  .settings-slide-enter-active,
  .settings-slide-leave-active,
  .navigator-collapse-enter-active,
  .navigator-collapse-leave-active {
    transition: none;
  }
  
  .control-btn:hover,
  .settings-action-btn:hover {
    transform: none;
  }
}
</style>
