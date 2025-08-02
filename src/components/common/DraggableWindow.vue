<template>
  <div 
    ref="windowRef"
    class="draggable-window"
    :style="windowStyle"
    @mousedown="handleMouseDown"
    @touchstart="handleTouchStart"
  >
    <slot />
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { DragHandler, TouchDragHandler } from '@/utils/floating-navigator';

export default defineComponent({
  name: 'DraggableWindow',
  props: {
    position: {
      type: Object,
      default: () => ({ x: 20, y: 100 })
    },
    opacity: {
      type: Number,
      default: 0.9
    },
    size: {
      type: Object,
      default: () => ({ width: 320, height: 450 })
    },
    zIndex: {
      type: Number,
      default: 9999
    },
    constrainToViewport: {
      type: Boolean,
      default: true
    },
    dragHandle: {
      type: String,
      default: '.drag-handle'
    },
    theme: {
      type: Object,
      default: () => ({
        background_color: 'rgba(255, 255, 255, 0.95)',
        border_color: 'rgba(255, 255, 255, 0.3)'
      })
    }
  },
  emits: ['position-change', 'opacity-change', 'drag-start', 'drag-end'],
  setup(props, { emit }) {
    const windowRef = ref(null);
    const dragHandler = ref(null);
    const touchDragHandler = ref(null);
    const isDragging = ref(false);
    
    // 计算窗口样式
    const windowStyle = computed(() => ({
      position: 'fixed',
      left: `${props.position.x}px`,
      top: `${props.position.y}px`,
      width: `${props.size.width}px`,
      height: `${props.size.height}px`,
      zIndex: props.zIndex,
      backgroundColor: props.theme.background_color,
      border: `1px solid ${props.theme.border_color}`,
      borderRadius: '12px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
      backdropFilter: 'blur(10px)',
      overflow: 'hidden',
      userSelect: isDragging.value ? 'none' : 'auto',
      transition: isDragging.value ? 'none' : 'all 0.2s ease'
    }));
    
    // 鼠标按下处理
    const handleMouseDown = (event) => {
      // 检查是否点击在拖拽句柄上
      if (props.dragHandle) {
        const dragElement = event.target.closest(props.dragHandle);
        if (!dragElement) return;
      }
      
      isDragging.value = true;
      emit('drag-start', { event, position: props.position });
      
      dragHandler.value.startDrag(
        event,
        props.position,
        (newPosition) => {
          emit('position-change', newPosition);
        }
      );
    };
    
    // 触摸开始处理
    const handleTouchStart = (event) => {
      if (props.dragHandle) {
        const dragElement = event.target.closest(props.dragHandle);
        if (!dragElement) return;
      }
      
      isDragging.value = true;
      emit('drag-start', { event, position: props.position });
      
      touchDragHandler.value.startDrag(
        event,
        props.position,
        (newPosition) => {
          emit('position-change', newPosition);
        }
      );
    };
    
    // 监听拖拽结束事件
    const handleDragEnd = () => {
      isDragging.value = false;
      emit('drag-end', { position: props.position });
    };
    
    // 检查位置是否有效
    const validatePosition = (position) => {
      if (!props.constrainToViewport) return position;
      
      return dragHandler.value.constrainToViewport(position, props.size);
    };
    
    // 获取窗口边界
    const getWindowBounds = () => {
      if (!windowRef.value) return null;
      
      const rect = windowRef.value.getBoundingClientRect();
      return {
        left: rect.left,
        top: rect.top,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height
      };
    };
    
    // 居中窗口
    const centerWindow = () => {
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      
      const newPosition = {
        x: (viewportWidth - props.size.width) / 2,
        y: (viewportHeight - props.size.height) / 2
      };
      
      emit('position-change', validatePosition(newPosition));
    };
    
    // 响应式布局处理
    const handleResize = () => {
      const validatedPosition = validatePosition(props.position);
      if (validatedPosition.x !== props.position.x || validatedPosition.y !== props.position.y) {
        emit('position-change', validatedPosition);
      }
    };
    
    onMounted(() => {
      // 初始化拖拽处理器
      dragHandler.value = new DragHandler();
      touchDragHandler.value = new TouchDragHandler();
      
      // 监听拖拽结束事件
      document.addEventListener('mouseup', handleDragEnd);
      document.addEventListener('touchend', handleDragEnd);
      
      // 监听窗口大小变化
      window.addEventListener('resize', handleResize);
      
      // 验证初始位置
      const validatedPosition = validatePosition(props.position);
      if (validatedPosition.x !== props.position.x || validatedPosition.y !== props.position.y) {
        emit('position-change', validatedPosition);
      }
    });
    
    onBeforeUnmount(() => {
      // 清理拖拽处理器
      if (dragHandler.value) {
        dragHandler.value.destroy();
      }
      if (touchDragHandler.value) {
        touchDragHandler.value.destroy();
      }
      
      // 移除事件监听器
      document.removeEventListener('mouseup', handleDragEnd);
      document.removeEventListener('touchend', handleDragEnd);
      window.removeEventListener('resize', handleResize);
    });
    
    return {
      windowRef,
      windowStyle,
      isDragging,
      handleMouseDown,
      handleTouchStart,
      centerWindow,
      getWindowBounds,
      validatePosition
    };
  }
});
</script>

<style scoped>
.draggable-window {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  cursor: default;
}

.draggable-window * {
  box-sizing: border-box;
}

/* 拖拽状态下的样式 */
.dragging {
  cursor: grabbing !important;
}

.dragging * {
  pointer-events: none !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .draggable-window {
    max-width: calc(100vw - 20px);
    max-height: calc(100vh - 20px);
  }
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .draggable-window {
    border-width: 2px;
    border-style: solid;
  }
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .draggable-window {
    transition: none !important;
  }
}
</style>
