<template>
  <div 
    class="navigator-item"
    :class="{ 
      'highlighted': isHighlighted,
      'visible': isVisible,
      'active': isActive
    }"
    @click="handleClick"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
  >
    <div class="item-content">
      <span class="item-type-icon">{{ componentTypeIcon }}</span>
      <div class="item-text">
        <span class="item-title" v-html="highlightedTitle"></span>
        <span v-if="showDescription && component.description" class="item-description">
          {{ component.description }}
        </span>
      </div>
      <div class="item-meta">
        <span class="item-position">{{ positionText }}</span>
        <span v-if="isVisible" class="visibility-indicator" title="当前可见">👁️</span>
      </div>
    </div>
    
    <!-- 工具提示 -->
    <div 
      v-if="showTooltip && enableTooltips" 
      class="item-tooltip"
      :class="{ 'tooltip-right': tooltipPosition === 'right' }"
    >
      <div class="tooltip-content">
        <div class="tooltip-header">
          <strong>{{ component.title }}</strong>
          <span class="tooltip-type">{{ component.component_type || component.type }}</span>
        </div>
        <div v-if="component.description" class="tooltip-description">
          {{ component.description }}
        </div>
        <div class="tooltip-details">
          <div class="tooltip-detail">
            <span class="detail-label">位置:</span>
            <span class="detail-value">第{{ component.position.row + 1 }}行, 第{{ component.position.col + 1 }}列</span>
          </div>
          <div v-if="component.position.rowSpan > 1 || component.position.colSpan > 1" class="tooltip-detail">
            <span class="detail-label">跨度:</span>
            <span class="detail-value">{{ component.position.rowSpan }}行 × {{ component.position.colSpan }}列</span>
          </div>
          <div v-if="component.api_path" class="tooltip-detail">
            <span class="detail-label">API:</span>
            <span class="detail-value">{{ component.api_path }}</span>
          </div>
        </div>
        <div class="tooltip-actions">
          <button class="tooltip-action" @click.stop="scrollToComponent">
            📍 跳转到组件
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed, ref } from 'vue';
import { ComponentOrganizer, ScrollHelper } from '@/utils/floating-navigator';

export default defineComponent({
  name: 'NavigatorItem',
  props: {
    component: {
      type: Object,
      required: true
    },
    searchQuery: {
      type: String,
      default: ''
    },
    isVisible: {
      type: Boolean,
      default: false
    },
    isActive: {
      type: Boolean,
      default: false
    },
    showDescription: {
      type: Boolean,
      default: false
    },
    enableTooltips: {
      type: Boolean,
      default: true
    },
    tooltipPosition: {
      type: String,
      default: 'right',
      validator: (value) => ['left', 'right', 'auto'].includes(value)
    },
    highlightColor: {
      type: String,
      default: '#667eea'
    }
  },
  emits: ['click', 'scroll-to'],
  setup(props, { emit }) {
    const showTooltip = ref(false);
    const organizer = new ComponentOrganizer();
    
    // 是否高亮显示
    const isHighlighted = computed(() => {
      if (!props.searchQuery) return false;
      
      const query = props.searchQuery.toLowerCase();
      const title = (props.component.title || '').toLowerCase();
      const description = (props.component.description || '').toLowerCase();
      const id = (props.component.component_id || props.component.id || '').toLowerCase();
      
      return title.includes(query) || description.includes(query) || id.includes(query);
    });
    
    // 组件类型图标
    const componentTypeIcon = computed(() => {
      return organizer.getComponentTypeIcon(props.component.component_type || props.component.type);
    });
    
    // 位置文本
    const positionText = computed(() => {
      return organizer.getPositionText(props.component.position);
    });
    
    // 高亮显示的标题
    const highlightedTitle = computed(() => {
      if (!props.searchQuery) {
        return props.component.title;
      }
      
      const query = props.searchQuery.toLowerCase();
      const title = props.component.title || '';
      const index = title.toLowerCase().indexOf(query);
      
      if (index === -1) {
        return title;
      }
      
      const before = title.substring(0, index);
      const match = title.substring(index, index + query.length);
      const after = title.substring(index + query.length);
      
      return `${before}<mark style="background-color: ${props.highlightColor}; color: white; padding: 1px 2px; border-radius: 2px;">${match}</mark>${after}`;
    });
    
    // 处理点击
    const handleClick = () => {
      emit('click', props.component);
      scrollToComponent();
    };
    
    // 滚动到组件
    const scrollToComponent = () => {
      const componentId = props.component.component_id || props.component.id;
      const success = ScrollHelper.scrollToComponent(componentId);
      
      emit('scroll-to', {
        component: props.component,
        success
      });
      
      if (!success) {
        console.warn(`Unable to scroll to component: ${componentId}`);
      }
    };
    
    // 获取组件状态信息
    const getComponentStatus = () => {
      const componentId = props.component.component_id || props.component.id;
      const position = ScrollHelper.getComponentPosition(componentId);
      
      return {
        exists: position !== null,
        visible: position ? position.inViewport : false,
        position: position
      };
    };
    
    return {
      showTooltip,
      isHighlighted,
      componentTypeIcon,
      positionText,
      highlightedTitle,
      handleClick,
      scrollToComponent,
      getComponentStatus
    };
  }
});
</script>

<style scoped>
.navigator-item {
  position: relative;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.navigator-item:hover {
  background-color: rgba(102, 126, 234, 0.1);
  border-left-color: #667eea;
}

.navigator-item.highlighted {
  background-color: rgba(255, 193, 7, 0.1);
  border-left-color: #ffc107;
}

.navigator-item.active {
  background-color: rgba(102, 126, 234, 0.2);
  border-left-color: #667eea;
}

.navigator-item.visible {
  border-right: 2px solid #10b981;
}

.item-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.item-type-icon {
  font-size: 14px;
  margin-top: 1px;
  flex-shrink: 0;
}

.item-text {
  flex: 1;
  min-width: 0;
}

.item-title {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #333;
  word-break: break-word;
  line-height: 1.3;
}

.item-description {
  display: block;
  font-size: 10px;
  color: #666;
  margin-top: 2px;
  line-height: 1.2;
  word-break: break-word;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  flex-shrink: 0;
}

.item-position {
  font-size: 9px;
  color: #999;
  background: rgba(0, 0, 0, 0.05);
  padding: 1px 4px;
  border-radius: 2px;
  white-space: nowrap;
}

.visibility-indicator {
  font-size: 8px;
  opacity: 0.7;
}

/* 工具提示 */
.item-tooltip {
  position: absolute;
  left: 100%;
  top: 0;
  margin-left: 8px;
  z-index: 1000;
  pointer-events: none;
}

.item-tooltip.tooltip-right {
  left: 100%;
  margin-left: 8px;
}

.tooltip-content {
  background: rgba(30, 30, 30, 0.95);
  color: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  min-width: 200px;
  max-width: 300px;
  font-size: 11px;
  backdrop-filter: blur(10px);
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.tooltip-header strong {
  font-size: 12px;
  color: #fff;
}

.tooltip-type {
  font-size: 9px;
  color: #a0aec0;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
}

.tooltip-description {
  margin-bottom: 8px;
  color: #e2e8f0;
  line-height: 1.3;
}

.tooltip-details {
  margin-bottom: 8px;
}

.tooltip-detail {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.detail-label {
  color: #a0aec0;
  margin-right: 8px;
}

.detail-value {
  color: #fff;
  font-weight: 500;
}

.tooltip-actions {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 8px;
}

.tooltip-action {
  background: rgba(102, 126, 234, 0.8);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  pointer-events: auto;
}

.tooltip-action:hover {
  background: rgba(102, 126, 234, 1);
  transform: translateY(-1px);
}

/* 高亮标记样式 */
.navigator-item :deep(mark) {
  background-color: #667eea;
  color: white;
  padding: 1px 2px;
  border-radius: 2px;
  font-weight: 500;
}

/* 暗色主题 */
@media (prefers-color-scheme: dark) {
  .navigator-item {
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .navigator-item:hover {
    background-color: rgba(102, 126, 234, 0.2);
  }
  
  .item-title {
    color: #fff;
  }
  
  .item-description {
    color: #a0aec0;
  }
  
  .item-position {
    color: #718096;
    background: rgba(255, 255, 255, 0.1);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navigator-item {
    padding: 10px 12px;
  }
  
  .item-tooltip {
    position: fixed;
    left: 10px;
    right: 10px;
    top: auto;
    bottom: 10px;
    margin-left: 0;
  }
  
  .tooltip-content {
    max-width: none;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .navigator-item {
    border-left-width: 4px;
  }
  
  .navigator-item:hover {
    background-color: rgba(102, 126, 234, 0.3);
  }
  
  .tooltip-content {
    border: 2px solid #667eea;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .navigator-item {
    transition: none;
  }
  
  .tooltip-action:hover {
    transform: none;
  }
}
</style>
