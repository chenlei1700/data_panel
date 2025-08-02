<template>
  <div class="navigator-tree">
    <!-- 分类组件 -->
    <div 
      v-for="(category, categoryName) in filteredOrganizedComponents" 
      :key="categoryName"
      class="category-section"
    >
      <div 
        class="category-header"
        @click="toggleCategory(categoryName)"
        :class="{ 'expanded': categoryStates[categoryName] }"
      >
        <span class="category-icon">{{ category.icon }}</span>
        <span class="category-title">{{ categoryName }}</span>
        <span class="category-count">({{ category.items.length }})</span>
        <span class="collapse-icon">{{ categoryStates[categoryName] ? '▼' : '▶' }}</span>
      </div>
      
      <transition name="category-expand">
        <div v-show="categoryStates[categoryName]" class="category-items">
          <navigator-item
            v-for="component in category.items"
            :key="component.component_id || component.id"
            :component="component"
            :search-query="searchQuery"
            :is-visible="isComponentVisible(component.component_id || component.id)"
            :is-active="activeComponentId === (component.component_id || component.id)"
            :show-description="showComponentDescriptions"
            :enable-tooltips="enableTooltips"
            :highlight-color="highlightColor"
            @click="handleComponentClick"
            @scroll-to="handleScrollTo"
          />
        </div>
      </transition>
    </div>
    
    <!-- 未分类组件 -->
    <div 
      v-if="filteredUncategorizedComponents.length > 0" 
      class="category-section uncategorized-section"
    >
      <div 
        class="category-header"
        @click="toggleCategory('uncategorized')"
        :class="{ 'expanded': categoryStates.uncategorized }"
      >
        <span class="category-icon">{{ uncategorizedConfig.icon }}</span>
        <span class="category-title">{{ uncategorizedConfig.title }}</span>
        <span class="category-count">({{ filteredUncategorizedComponents.length }})</span>
        <span class="collapse-icon">{{ categoryStates.uncategorized ? '▼' : '▶' }}</span>
      </div>
      
      <transition name="category-expand">
        <div v-show="categoryStates.uncategorized" class="category-items">
          <navigator-item
            v-for="component in filteredUncategorizedComponents"
            :key="component.component_id || component.id"
            :component="component"
            :search-query="searchQuery"
            :is-visible="isComponentVisible(component.component_id || component.id)"
            :is-active="activeComponentId === (component.component_id || component.id)"
            :show-description="showComponentDescriptions"
            :enable-tooltips="enableTooltips"
            :highlight-color="highlightColor"
            @click="handleComponentClick"
            @scroll-to="handleScrollTo"
          />
        </div>
      </transition>
    </div>
    
    <!-- 空状态 -->
    <div v-if="isEmpty" class="empty-state">
      <div class="empty-icon">🔍</div>
      <div class="empty-text">
        <div class="empty-title">未找到组件</div>
        <div class="empty-description">
          {{ searchQuery ? `没有找到包含 "${searchQuery}" 的组件` : '当前页面没有可用的组件' }}
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载组件中...</div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, ref, watch, onMounted } from 'vue';
import NavigatorItem from './NavigatorItem.vue';
import { ComponentOrganizer, ScrollHelper } from '@/utils/floating-navigator';

export default defineComponent({
  name: 'NavigatorTree',
  components: {
    NavigatorItem
  },
  props: {
    organizedComponents: {
      type: Object,
      default: () => ({})
    },
    uncategorizedComponents: {
      type: Array,
      default: () => []
    },
    searchQuery: {
      type: String,
      default: ''
    },
    activeComponentId: {
      type: String,
      default: ''
    },
    categoryStates: {
      type: Object,
      default: () => ({})
    },
    uncategorizedConfig: {
      type: Object,
      default: () => ({
        title: '其他组件',
        icon: '📦',
        description: '未分类的组件'
      })
    },
    showComponentDescriptions: {
      type: Boolean,
      default: false
    },
    enableTooltips: {
      type: Boolean,
      default: true
    },
    highlightColor: {
      type: String,
      default: '#667eea'
    },
    autoCollapseCategories: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'component-click', 
    'scroll-to', 
    'category-toggle',
    'visibility-change',
    'update:category-states'
  ],
  setup(props, { emit }) {
    const organizer = new ComponentOrganizer();
    const visibilityTimer = ref(null);
    const visibleComponents = ref(new Set());
    
    // 过滤后的分类组件
    const filteredOrganizedComponents = computed(() => {
      if (!props.searchQuery) return props.organizedComponents;
      
      return organizer.filterOrganizedComponents(props.organizedComponents, props.searchQuery);
    });
    
    // 过滤后的未分类组件
    const filteredUncategorizedComponents = computed(() => {
      if (!props.searchQuery) return props.uncategorizedComponents;
      
      return organizer.searchComponents(props.uncategorizedComponents, props.searchQuery);
    });
    
    // 是否为空状态
    const isEmpty = computed(() => {
      const hasOrganized = Object.keys(filteredOrganizedComponents.value).length > 0;
      const hasUncategorized = filteredUncategorizedComponents.value.length > 0;
      return !props.loading && !hasOrganized && !hasUncategorized;
    });
    
    // 总组件数量
    const totalComponentCount = computed(() => {
      const organizedCount = Object.values(filteredOrganizedComponents.value)
        .reduce((sum, category) => sum + category.items.length, 0);
      return organizedCount + filteredUncategorizedComponents.value.length;
    });
    
    // 切换分类展开/折叠状态
    const toggleCategory = (categoryName) => {
      const newStates = { ...props.categoryStates };
      newStates[categoryName] = !newStates[categoryName];
      
      // 自动折叠其他分类
      if (props.autoCollapseCategories && newStates[categoryName]) {
        Object.keys(newStates).forEach(key => {
          if (key !== categoryName) {
            newStates[key] = false;
          }
        });
      }
      
      emit('update:category-states', newStates);
      emit('category-toggle', {
        categoryName,
        expanded: newStates[categoryName],
        categoryStates: newStates
      });
    };
    
    // 展开所有分类
    const expandAllCategories = () => {
      const newStates = {};
      
      // 展开所有有组件的分类
      Object.keys(filteredOrganizedComponents.value).forEach(categoryName => {
        newStates[categoryName] = true;
      });
      
      if (filteredUncategorizedComponents.value.length > 0) {
        newStates.uncategorized = true;
      }
      
      emit('update:category-states', newStates);
    };
    
    // 折叠所有分类
    const collapseAllCategories = () => {
      const newStates = {};
      
      Object.keys(props.categoryStates).forEach(categoryName => {
        newStates[categoryName] = false;
      });
      
      emit('update:category-states', newStates);
    };
    
    // 检查组件是否可见
    const isComponentVisible = (componentId) => {
      return visibleComponents.value.has(componentId);
    };
    
    // 更新组件可见性状态
    const updateComponentVisibility = () => {
      const allComponentIds = [
        ...Object.values(props.organizedComponents).flatMap(cat => 
          cat.items.map(comp => comp.component_id || comp.id)
        ),
        ...props.uncategorizedComponents.map(comp => comp.component_id || comp.id)
      ];
      
      const newVisibleComponents = new Set(
        ScrollHelper.getVisibleComponents(allComponentIds)
      );
      
      // 检查是否有变化
      const hasChanges = newVisibleComponents.size !== visibleComponents.value.size ||
        [...newVisibleComponents].some(id => !visibleComponents.value.has(id));
      
      if (hasChanges) {
        visibleComponents.value = newVisibleComponents;
        emit('visibility-change', {
          visible: [...newVisibleComponents],
          total: allComponentIds.length
        });
      }
    };
    
    // 处理组件点击
    const handleComponentClick = (component) => {
      emit('component-click', component);
    };
    
    // 处理滚动到组件
    const handleScrollTo = (data) => {
      emit('scroll-to', data);
    };
    
    // 获取分类统计信息
    const getCategoryStats = () => {
      const stats = {
        totalCategories: Object.keys(props.organizedComponents).length,
        expandedCategories: Object.values(props.categoryStates).filter(Boolean).length,
        totalComponents: totalComponentCount.value,
        visibleComponents: visibleComponents.value.size
      };
      
      if (props.uncategorizedComponents.length > 0) {
        stats.totalCategories += 1;
      }
      
      return stats;
    };
    
    // 搜索时自动展开相关分类
    watch(() => props.searchQuery, (newQuery) => {
      if (newQuery && newQuery.trim()) {
        // 搜索时展开有匹配结果的分类
        const newStates = { ...props.categoryStates };
        
        Object.entries(filteredOrganizedComponents.value).forEach(([categoryName, category]) => {
          if (category.items.length > 0) {
            newStates[categoryName] = true;
          }
        });
        
        if (filteredUncategorizedComponents.value.length > 0) {
          newStates.uncategorized = true;
        }
        
        emit('update:category-states', newStates);
      }
    });
    
    // 定期更新组件可见性
    onMounted(() => {
      updateComponentVisibility();
      
      // 设置定时器定期检查可见性
      visibilityTimer.value = setInterval(updateComponentVisibility, 1000);
      
      // 监听滚动事件
      const handleScroll = () => {
        if (visibilityTimer.value) {
          clearTimeout(visibilityTimer.value);
        }
        visibilityTimer.value = setTimeout(updateComponentVisibility, 100);
      };
      
      window.addEventListener('scroll', handleScroll, { passive: true });
      
      // 清理
      return () => {
        if (visibilityTimer.value) {
          clearInterval(visibilityTimer.value);
        }
        window.removeEventListener('scroll', handleScroll);
      };
    });
    
    return {
      filteredOrganizedComponents,
      filteredUncategorizedComponents,
      isEmpty,
      totalComponentCount,
      toggleCategory,
      expandAllCategories,
      collapseAllCategories,
      isComponentVisible,
      handleComponentClick,
      handleScrollTo,
      getCategoryStats
    };
  }
});
</script>

<style scoped>
.navigator-tree {
  font-size: 12px;
  overflow-y: auto;
  max-height: 100%;
}

.category-section {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.category-section:last-child {
  border-bottom: none;
}

.category-header {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.02);
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  user-select: none;
}

.category-header:hover {
  background: rgba(102, 126, 234, 0.1);
  border-left-color: #667eea;
}

.category-header.expanded {
  background: rgba(102, 126, 234, 0.05);
  border-left-color: #667eea;
}

.category-icon {
  font-size: 14px;
  margin-right: 8px;
}

.category-title {
  flex: 1;
  font-weight: 600;
  color: #333;
}

.category-count {
  font-size: 10px;
  color: #666;
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
  margin-right: 8px;
}

.collapse-icon {
  font-size: 10px;
  color: #999;
  transition: transform 0.2s ease;
}

.category-header.expanded .collapse-icon {
  transform: rotate(0deg);
}

.category-items {
  background: white;
}

/* 分类展开/折叠动画 */
.category-expand-enter-active,
.category-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.category-expand-enter-from,
.category-expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.category-expand-enter-to,
.category-expand-leave-from {
  max-height: 1000px;
  opacity: 1;
}

/* 未分类区域样式 */
.uncategorized-section .category-header {
  background: rgba(255, 193, 7, 0.05);
}

.uncategorized-section .category-header:hover {
  background: rgba(255, 193, 7, 0.1);
  border-left-color: #ffc107;
}

.uncategorized-section .category-header.expanded {
  background: rgba(255, 193, 7, 0.1);
  border-left-color: #ffc107;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #333;
}

.empty-description {
  font-size: 11px;
  line-height: 1.4;
  color: #999;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 30px 20px;
  color: #666;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 11px;
  color: #999;
}

/* 滚动条样式 */
.navigator-tree::-webkit-scrollbar {
  width: 4px;
}

.navigator-tree::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
}

.navigator-tree::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.navigator-tree::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 暗色主题 */
@media (prefers-color-scheme: dark) {
  .category-section {
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .category-header {
    background: rgba(255, 255, 255, 0.02);
  }
  
  .category-header:hover {
    background: rgba(102, 126, 234, 0.2);
  }
  
  .category-header.expanded {
    background: rgba(102, 126, 234, 0.1);
  }
  
  .category-title {
    color: #fff;
  }
  
  .category-count {
    background: rgba(255, 255, 255, 0.1);
    color: #a0aec0;
  }
  
  .category-items {
    background: #2d3748;
  }
  
  .empty-title {
    color: #fff;
  }
  
  .loading-spinner {
    border-color: rgba(255, 255, 255, 0.2);
    border-top-color: #90cdf4;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .category-header {
    padding: 12px;
  }
  
  .category-title {
    font-size: 13px;
  }
  
  .empty-state {
    padding: 30px 15px;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .category-header {
    border-left-width: 4px;
  }
  
  .category-header:hover,
  .category-header.expanded {
    background: rgba(102, 126, 234, 0.3);
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .category-header,
  .collapse-icon,
  .category-expand-enter-active,
  .category-expand-leave-active {
    transition: none;
  }
  
  .loading-spinner {
    animation: none;
  }
}
</style>
