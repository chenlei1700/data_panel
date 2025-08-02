<template>
  <div class="navigator-tree">
    <div v-if="categories.length === 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <div class="empty-title">{{ emptyTitle }}</div>
      <div class="empty-description">{{ emptyDescription }}</div>
    </div>

    <div
      v-for="category in categories"
      :key="category.name"
      class="category-group"
      :class="{ 'category-group--expanded': isCategoryExpanded(category.name) }"
    >
      <!-- 分类头部 -->
      <div
        class="category-header"
        @click="toggleCategory(category.name)"
        :style="{ '--category-color': category.color || '#6b7280' }"
      >
        <div class="category-icon">
          <span v-if="typeof category.icon === 'string'">{{ category.icon }}</span>
          <component v-else-if="category.icon" :is="category.icon" />
          <span v-else>📂</span>
        </div>
        
        <div class="category-info">
          <div class="category-name">{{ category.name }}</div>
          <div class="category-count">{{ category.items.length }} 个组件</div>
        </div>
        
        <div class="category-toggle">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="toggle-icon"
            :class="{ 'toggle-icon--expanded': isCategoryExpanded(category.name) }"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>

      <!-- 分类内容 -->
      <div
        v-show="isCategoryExpanded(category.name)"
        class="category-content"
      >
        <div
          v-for="item in category.items"
          :key="item.id"
          class="category-item"
        >
          <NavigatorItem
            :component-id="item.id"
            :title="item.title"
            :description="item.description"
            :icon="item.icon"
            :tags="item.tags"
            :element="item.element"
            :search-term="searchTerm"
            :show-description="showItemDescription"
            :show-meta="showItemMeta"
            :show-visibility="showItemVisibility"
            :show-position="showItemPosition"
            :show-actions="showItemActions"
            :copyable="itemCopyable"
            :highlight-matches="highlightMatches"
            :theme="theme"
            @click="handleItemClick"
            @scroll-to="handleItemScrollTo"
          />
        </div>
      </div>
    </div>

    <!-- 展开/折叠全部按钮 -->
    <div v-if="categories.length > 1" class="tree-actions">
      <button
        @click="expandAll"
        class="tree-action-button"
        :disabled="allExpanded"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
          <polyline points="6 3 12 9 18 3"></polyline>
        </svg>
        展开全部
      </button>
      
      <button
        @click="collapseAll"
        class="tree-action-button"
        :disabled="allCollapsed"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="18 15 12 9 6 15"></polyline>
          <polyline points="18 21 12 15 6 21"></polyline>
        </svg>
        折叠全部
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'
import NavigatorItem from './NavigatorItem.vue'

export default {
  name: 'NavigatorTree',
  components: {
    NavigatorItem
  },
  emits: ['item-click', 'item-scroll-to', 'category-toggle'],
  props: {
    categories: {
      type: Array,
      default: () => []
    },
    searchTerm: {
      type: String,
      default: ''
    },
    initialExpandedCategories: {
      type: Array,
      default: () => []
    },
    autoExpandSingleCategory: {
      type: Boolean,
      default: true
    },
    autoExpandOnSearch: {
      type: Boolean,
      default: true
    },
    showItemDescription: {
      type: Boolean,
      default: true
    },
    showItemMeta: {
      type: Boolean,
      default: false
    },
    showItemVisibility: {
      type: Boolean,
      default: true
    },
    showItemPosition: {
      type: Boolean,
      default: false
    },
    showItemActions: {
      type: Boolean,
      default: true
    },
    itemCopyable: {
      type: Boolean,
      default: true
    },
    highlightMatches: {
      type: Boolean,
      default: true
    },
    emptyTitle: {
      type: String,
      default: '未找到组件'
    },
    emptyDescription: {
      type: String,
      default: '尝试调整搜索条件或检查页面是否包含组件'
    },
    theme: {
      type: String,
      default: 'light'
    }
  },
  setup(props, { emit }) {
    const expandedCategories = ref(new Set(props.initialExpandedCategories))
    const isUpdatingFromProps = ref(false) // 标志：是否正在从props更新

    // 计算属性
    const allExpanded = computed(() => {
      return props.categories.length > 0 && 
             props.categories.every(cat => expandedCategories.value.has(cat.name))
    })

    const allCollapsed = computed(() => {
      return expandedCategories.value.size === 0
    })

    // 方法
    const isCategoryExpanded = (categoryName) => {
      return expandedCategories.value.has(categoryName)
    }

    const toggleCategory = (categoryName) => {
      if (expandedCategories.value.has(categoryName)) {
        expandedCategories.value.delete(categoryName)
      } else {
        expandedCategories.value.add(categoryName)
      }
      
      // 只有在不是从props更新时才发出事件
      if (!isUpdatingFromProps.value) {
        emit('category-toggle', {
          categoryName,
          expanded: expandedCategories.value.has(categoryName),
          expandedCategories: Array.from(expandedCategories.value)
        })
      }
    }

    const expandAll = () => {
      props.categories.forEach(category => {
        expandedCategories.value.add(category.name)
      })
      
      if (!isUpdatingFromProps.value) {
        emit('category-toggle', {
          categoryName: 'all',
          expanded: true,
          expandedCategories: Array.from(expandedCategories.value)
        })
      }
    }

    const collapseAll = () => {
      expandedCategories.value.clear()
      
      if (!isUpdatingFromProps.value) {
        emit('category-toggle', {
          categoryName: 'all',
          expanded: false,
          expandedCategories: []
        })
      }
    }

    const expandCategory = (categoryName) => {
      if (!expandedCategories.value.has(categoryName)) {
        expandedCategories.value.add(categoryName)
        if (!isUpdatingFromProps.value) {
          emit('category-toggle', {
            categoryName,
            expanded: true,
            expandedCategories: Array.from(expandedCategories.value)
          })
        }
      }
    }

    const collapseCategory = (categoryName) => {
      if (expandedCategories.value.has(categoryName)) {
        expandedCategories.value.delete(categoryName)
        if (!isUpdatingFromProps.value) {
          emit('category-toggle', {
            categoryName,
            expanded: false,
            expandedCategories: Array.from(expandedCategories.value)
          })
        }
      }
    }

    // 事件处理
    const handleItemClick = (event) => {
      emit('item-click', event)
    }

    const handleItemScrollTo = (event) => {
      emit('item-scroll-to', event)
    }

    // 监听器
    watch(() => props.categories, (newCategories) => {
      // 自动展开单个分类
      if (props.autoExpandSingleCategory && newCategories.length === 1) {
        expandedCategories.value.add(newCategories[0].name)
      }
    }, { immediate: true })

    watch(() => props.searchTerm, (newSearchTerm) => {
      // 搜索时自动展开所有分类
      if (props.autoExpandOnSearch && newSearchTerm.trim()) {
        props.categories.forEach(category => {
          expandedCategories.value.add(category.name)
        })
      }
    })

    // 监听初始展开分类的变化（用于双击展开功能）
    watch(() => props.initialExpandedCategories, (newExpandedCategories) => {
      if (newExpandedCategories && newExpandedCategories.length > 0) {
        isUpdatingFromProps.value = true // 设置标志
        
        // 清空当前展开状态
        expandedCategories.value.clear()
        // 设置新的展开状态
        newExpandedCategories.forEach(categoryName => {
          expandedCategories.value.add(categoryName)
        })
        console.log('🌲 NavigatorTree: 更新展开分类', Array.from(expandedCategories.value))
        
        // 使用 nextTick 在下一个周期重置标志
        nextTick(() => {
          isUpdatingFromProps.value = false
        })
      }
    }, { deep: true })

    // 公开方法
    const getExpandedCategories = () => {
      return Array.from(expandedCategories.value)
    }

    const setExpandedCategories = (categories) => {
      expandedCategories.value = new Set(categories)
    }

    return {
      expandedCategories,
      allExpanded,
      allCollapsed,
      isCategoryExpanded,
      toggleCategory,
      expandAll,
      collapseAll,
      expandCategory,
      collapseCategory,
      handleItemClick,
      handleItemScrollTo,
      getExpandedCategories,
      setExpandedCategories
    }
  }
}
</script>

<style lang="scss" scoped>
.navigator-tree {
  width: 100%;
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: #6b7280;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #374151;
}

.empty-description {
  font-size: 14px;
  line-height: 1.5;
  color: #6b7280;
}

.category-group {
  margin-bottom: 8px;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;

  &:hover {
    border-color: #e2e8f0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  &.category-group--expanded {
    border-color: var(--category-color, #6b7280);
    box-shadow: 0 0 0 1px rgba(var(--category-color-rgb, 107, 114, 128), 0.1);
  }
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fafbfc;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid transparent;

  &:hover {
    background: #f1f5f9;
  }

  .category-group--expanded & {
    background: rgba(var(--category-color-rgb, 107, 114, 128), 0.05);
    border-bottom-color: #f1f5f9;
  }
}

.category-icon {
  font-size: 18px;
  color: var(--category-color, #6b7280);
  flex-shrink: 0;
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-name {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.category-count {
  font-size: 12px;
  color: #6b7280;
}

.category-toggle {
  color: #9ca3af;
  transition: color 0.2s ease;

  .category-header:hover & {
    color: #6b7280;
  }
}

.toggle-icon {
  transition: transform 0.2s ease;

  &.toggle-icon--expanded {
    transform: rotate(180deg);
  }
}

.category-content {
  background: white;
  border-top: 1px solid #f1f5f9;
}

.category-item {
  border-bottom: 1px solid #f8fafc;

  &:last-child {
    border-bottom: none;
  }
}

.tree-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 0;
  border-top: 1px solid #f1f5f9;
}

.tree-action-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #6b7280;
  font-size: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    border-color: #3b82f6;
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.05);
  }

  &:active:not(:disabled) {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// 深色主题
[data-theme="dark"] {
  .empty-title {
    color: #f9fafb;
  }

  .empty-description {
    color: #d1d5db;
  }

  .category-group {
    border-color: #374151;

    &:hover {
      border-color: #4b5563;
    }

    &.category-group--expanded {
      border-color: var(--category-color, #9ca3af);
    }
  }

  .category-header {
    background: #374151;

    &:hover {
      background: #4b5563;
    }

    .category-group--expanded & {
      background: rgba(var(--category-color-rgb, 156, 163, 175), 0.1);
      border-bottom-color: #4b5563;
    }
  }

  .category-name {
    color: #f9fafb;
  }

  .category-count {
    color: #d1d5db;
  }

  .category-content {
    background: #1f2937;
    border-top-color: #374151;
  }

  .category-item {
    border-bottom-color: #374151;
  }

  .tree-actions {
    border-top-color: #374151;
  }

  .tree-action-button {
    border-color: #4b5563;
    background: #374151;
    color: #d1d5db;

    &:hover:not(:disabled) {
      border-color: #60a5fa;
      color: #60a5fa;
      background: rgba(96, 165, 250, 0.1);
    }
  }
}

// 响应式适配
@media (max-width: 480px) {
  .category-header {
    padding: 10px;
  }

  .category-name {
    font-size: 13px;
  }

  .category-count {
    font-size: 11px;
  }

  .tree-action-button {
    font-size: 11px;
    padding: 5px 8px;
  }
}
</style>
