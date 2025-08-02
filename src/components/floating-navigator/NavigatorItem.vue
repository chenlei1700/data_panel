<template>
  <div
    class="navigator-item"
    :class="itemClasses"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- 项目图标 -->
    <div class="item-icon">
      <span v-if="typeof icon === 'string'">{{ icon }}</span>
      <component v-else-if="icon" :is="icon" />
      <span v-else>📄</span>
    </div>

    <!-- 项目内容 -->
    <div class="item-content">
      <div class="item-title" :title="fullTitle">
        <span v-if="searchTerm" v-html="highlightedTitle"></span>
        <span v-else>{{ title }}</span>
      </div>
      
      <div v-if="showDescription && description" class="item-description">
        {{ description }}
      </div>
      
      <div v-if="showMeta && (componentId || tags?.length)" class="item-meta">
        <span v-if="componentId" class="meta-id">{{ componentId }}</span>
        <span v-if="tags?.length" class="meta-tags">
          <span
            v-for="tag in tags"
            :key="tag"
            class="tag"
          >
            {{ tag }}
          </span>
        </span>
      </div>
    </div>

    <!-- 状态指示器 -->
    <div class="item-status">
      <div
        v-if="showVisibility"
        class="visibility-indicator"
        :class="{ visible: isVisible }"
        :title="isVisible ? '在视口中可见' : '不在视口中'"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path v-if="isVisible" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
          <circle v-if="isVisible" cx="12" cy="12" r="3"></circle>
          <path v-else d="m9.88 9.88a3 3 0 1 0 4.24 4.24"></path>
          <path v-else d="m10.73 5.08a10.94 10.94 0 0 1 1.27-.08c7 0 11 8 11 8a18.498 18.498 0 0 1-2.16 3.08"></path>
          <path v-else d="m6.61 6.61a13.526 13.526 0 0 0-3.61 5.39s4 8 11 8a9.74 9.74 0 0 0 5.39-1.61"></path>
          <line v-else x1="2" y1="2" x2="22" y2="22"></line>
        </svg>
      </div>

      <div
        v-if="showPosition"
        class="position-indicator"
        :title="`距离顶部 ${Math.round(scrollPosition)}px`"
      >
        <div class="position-bar">
          <div 
            class="position-fill"
            :style="{ height: `${positionPercentage}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div v-if="showActions" class="item-actions">
      <button
        @click.stop="scrollToComponent"
        class="action-button"
        title="滚动到此组件"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>
      
      <button
        v-if="copyable"
        @click.stop="copyComponentId"
        class="action-button"
        title="复制组件ID"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'NavigatorItem',
  emits: ['click', 'scroll-to'],
  props: {
    componentId: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    icon: {
      type: [String, Object],
      default: '📄'
    },
    tags: {
      type: Array,
      default: () => []
    },
    element: {
      type: Object, // DOM Element
      default: null
    },
    searchTerm: {
      type: String,
      default: ''
    },
    showDescription: {
      type: Boolean,
      default: true
    },
    showMeta: {
      type: Boolean,
      default: true
    },
    showVisibility: {
      type: Boolean,
      default: true
    },
    showPosition: {
      type: Boolean,
      default: true
    },
    showActions: {
      type: Boolean,
      default: true
    },
    copyable: {
      type: Boolean,
      default: true
    },
    highlightMatches: {
      type: Boolean,
      default: true
    },
    theme: {
      type: String,
      default: 'light'
    }
  },
  setup(props, { emit }) {
    const isHovered = ref(false)
    const isVisible = ref(false)
    const scrollPosition = ref(0)
    const documentHeight = ref(0)

    // 计算类名
    const itemClasses = computed(() => ({
      'navigator-item--hovered': isHovered.value,
      'navigator-item--visible': isVisible.value,
      'navigator-item--has-description': props.showDescription && props.description,
      [`navigator-item--${props.theme}`]: true
    }))

    // 完整标题（用于 tooltip）
    const fullTitle = computed(() => {
      return props.title + (props.description ? ` - ${props.description}` : '')
    })

    // 高亮标题
    const highlightedTitle = computed(() => {
      if (!props.searchTerm || !props.highlightMatches) {
        return props.title
      }
      
      const regex = new RegExp(`(${props.searchTerm})`, 'gi')
      return props.title.replace(regex, '<mark>$1</mark>')
    })

    // 位置百分比
    const positionPercentage = computed(() => {
      if (documentHeight.value === 0) return 0
      return Math.min(100, Math.max(0, (scrollPosition.value / documentHeight.value) * 100))
    })

    // 更新可见性和位置
    const updateElementInfo = () => {
      if (!props.element) return

      const rect = props.element.getBoundingClientRect()
      const viewportHeight = window.innerHeight

      // 更新可见性
      isVisible.value = rect.top >= 0 && rect.top <= viewportHeight

      // 更新位置
      scrollPosition.value = rect.top + window.scrollY
      documentHeight.value = document.documentElement.scrollHeight
    }

    // 事件处理
    const handleClick = () => {
      emit('click', {
        componentId: props.componentId,
        element: props.element
      })
      scrollToComponent()
    }

    const handleMouseEnter = () => {
      isHovered.value = true
    }

    const handleMouseLeave = () => {
      isHovered.value = false
    }

    const scrollToComponent = () => {
      if (props.element) {
        props.element.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        })

        // 高亮效果
        highlightElement()
        
        emit('scroll-to', {
          componentId: props.componentId,
          element: props.element
        })
      }
    }

    const highlightElement = () => {
      if (!props.element) return

      const originalStyle = {
        transition: props.element.style.transition,
        border: props.element.style.border,
        boxShadow: props.element.style.boxShadow
      }

      // 应用高亮样式
      props.element.style.transition = 'all 0.3s ease'
      props.element.style.border = '2px solid #3b82f6'
      props.element.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)'

      // 恢复原始样式
      setTimeout(() => {
        Object.keys(originalStyle).forEach(key => {
          props.element.style[key] = originalStyle[key]
        })
      }, 2000)
    }

    const copyComponentId = async () => {
      try {
        await navigator.clipboard.writeText(props.componentId)
        // 可以添加一个简单的提示
        console.log(`已复制组件ID: ${props.componentId}`)
      } catch (error) {
        console.warn('无法复制到剪贴板:', error)
        // 回退方案
        const textArea = document.createElement('textarea')
        textArea.value = props.componentId
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
      }
    }

    // 滚动监听
    const handleScroll = () => {
      updateElementInfo()
    }

    // 生命周期
    onMounted(() => {
      updateElementInfo()
      window.addEventListener('scroll', handleScroll, { passive: true })
      window.addEventListener('resize', updateElementInfo)
    })

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('resize', updateElementInfo)
    })

    return {
      isHovered,
      isVisible,
      scrollPosition,
      itemClasses,
      fullTitle,
      highlightedTitle,
      positionPercentage,
      handleClick,
      handleMouseEnter,
      handleMouseLeave,
      scrollToComponent,
      copyComponentId
    }
  }
}
</script>

<style lang="scss" scoped>
.navigator-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  position: relative;

  &:hover,
  &.navigator-item--hovered {
    background: rgba(59, 130, 246, 0.05);
    border-color: rgba(59, 130, 246, 0.1);
  }

  &:active {
    transform: scale(0.98);
    background: rgba(59, 130, 246, 0.1);
  }

  &.navigator-item--visible {
    .visibility-indicator {
      color: #10b981;
    }
  }

  &.navigator-item--has-description {
    align-items: flex-start;
    padding: 10px 8px;
  }
}

.item-icon {
  font-size: 16px;
  line-height: 1;
  margin-top: 2px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  line-height: 1.4;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  :deep(mark) {
    background: #fef3c7;
    color: #92400e;
    padding: 0 2px;
    border-radius: 2px;
  }
}

.item-description {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.3;
  margin-bottom: 4px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.meta-id {
  font-size: 11px;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.meta-tags {
  display: flex;
  gap: 4px;
}

.tag {
  font-size: 10px;
  color: #6b7280;
  background: #e5e7eb;
  padding: 1px 4px;
  border-radius: 3px;
}

.item-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.visibility-indicator {
  color: #9ca3af;
  transition: color 0.2s ease;

  &.visible {
    color: #10b981;
  }
}

.position-indicator {
  width: 3px;
  height: 20px;
  position: relative;
}

.position-bar {
  width: 100%;
  height: 100%;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.position-fill {
  width: 100%;
  background: #3b82f6;
  transition: height 0.2s ease;
  border-radius: 2px;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s ease;
  flex-shrink: 0;

  .navigator-item:hover & {
    opacity: 1;
  }
}

.action-button {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
  }

  &:active {
    transform: scale(0.9);
  }
}

// 深色主题
.navigator-item--dark {
  &:hover,
  &.navigator-item--hovered {
    background: rgba(96, 165, 250, 0.1);
    border-color: rgba(96, 165, 250, 0.2);
  }

  &:active {
    background: rgba(96, 165, 250, 0.15);
  }

  .item-title {
    color: #f9fafb;

    :deep(mark) {
      background: #fbbf24;
      color: #92400e;
    }
  }

  .item-description {
    color: #d1d5db;
  }

  .meta-id {
    color: #d1d5db;
    background: #374151;
  }

  .tag {
    color: #d1d5db;
    background: #4b5563;
  }

  .position-bar {
    background: #4b5563;
  }

  .position-fill {
    background: #60a5fa;
  }

  .action-button {
    color: #d1d5db;

    &:hover {
      background: rgba(96, 165, 250, 0.2);
      color: #60a5fa;
    }
  }
}

// 响应式适配
@media (max-width: 480px) {
  .navigator-item {
    padding: 6px;
  }

  .item-title {
    font-size: 13px;
  }

  .item-description {
    font-size: 11px;
  }

  .item-actions {
    opacity: 1; // 在移动设备上始终显示
  }

  .action-button {
    width: 20px;
    height: 20px;
  }
}
</style>
