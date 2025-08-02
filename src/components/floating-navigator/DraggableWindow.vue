<template>
  <div
    ref="windowRef"
    class="draggable-window"
    :class="windowClasses"
    :style="windowStyle"
    @mousedown="handleMouseDown"
    @touchstart="handleTouchStart"
  >
    <!-- 窗口头部 -->
    <div
      class="window-header"
      :class="{ 'dragging': isDragging }"
    >
      <div class="window-title">
        <slot name="title">{{ title }}</slot>
      </div>
      <div class="window-controls">
        <slot name="controls">
          <button
            v-if="minimizable"
            @click="toggleMinimize"
            class="control-button minimize-button"
            :title="isMinimized ? '展开' : '最小化'"
          >
            {{ isMinimized ? '▢' : '−' }}
          </button>
          <button
            v-if="closable"
            @click="close"
            class="control-button close-button"
            title="关闭"
          >
            ×
          </button>
        </slot>
      </div>
    </div>

    <!-- 窗口内容 -->
    <div
      v-show="!isMinimized"
      class="window-content"
      :style="contentStyle"
    >
      <slot></slot>
    </div>

    <!-- 调整大小手柄 -->
    <div
      v-if="resizable && !isMinimized"
      class="resize-handle"
      @mousedown="handleResizeStart"
      @touchstart="handleResizeStart"
    >
      ⋰
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'DraggableWindow',
  emits: ['position-change', 'size-change', 'minimize', 'close'],
  props: {
    title: {
      type: String,
      default: '窗口'
    },
    initialPosition: {
      type: Object,
      default: () => ({ x: 50, y: 50 })
    },
    initialSize: {
      type: Object,
      default: () => ({ width: 300, height: 400 })
    },
    minWidth: {
      type: Number,
      default: 200
    },
    minHeight: {
      type: Number,
      default: 150
    },
    maxWidth: {
      type: Number,
      default: null
    },
    maxHeight: {
      type: Number,
      default: null
    },
    constrainToViewport: {
      type: Boolean,
      default: true
    },
    resizable: {
      type: Boolean,
      default: true
    },
    minimizable: {
      type: Boolean,
      default: true
    },
    closable: {
      type: Boolean,
      default: true
    },
    opacity: {
      type: Number,
      default: 0.95,
      validator: value => value >= 0 && value <= 1
    },
    theme: {
      type: String,
      default: 'light',
      validator: value => ['light', 'dark', 'auto'].includes(value)
    },
    zIndex: {
      type: Number,
      default: 1000
    }
  },
  setup(props, { emit }) {
    const windowRef = ref(null)
    const isDragging = ref(false)
    const isResizing = ref(false)
    const isMinimized = ref(false)
    
    const position = ref({ ...props.initialPosition })
    const size = ref({ ...props.initialSize })
    
    const dragOffset = ref({ x: 0, y: 0 })
    const resizeStartSize = ref({ width: 0, height: 0 })
    const resizeStartPosition = ref({ x: 0, y: 0 })

    // 计算样式
    const windowClasses = computed(() => ({
      'draggable-window--dragging': isDragging.value,
      'draggable-window--resizing': isResizing.value,
      'draggable-window--minimized': isMinimized.value,
      [`draggable-window--${props.theme}`]: true
    }))

    const windowStyle = computed(() => ({
      left: `${position.value.x}px`,
      top: `${position.value.y}px`,
      width: `${size.value.width}px`,
      height: isMinimized.value ? 'auto' : `${size.value.height}px`,
      opacity: props.opacity,
      zIndex: isDragging.value || isResizing.value ? props.zIndex + 1000 : props.zIndex
    }))

    const contentStyle = computed(() => ({
      height: props.resizable ? `${size.value.height - 40}px` : 'auto' // 40px for header
    }))

    // 拖拽处理
    const handleMouseDown = (e) => {
      if (e.target.closest('.window-controls') || e.target.closest('.resize-handle')) {
        return
      }
      startDrag(e.clientX, e.clientY)
    }

    const handleTouchStart = (e) => {
      if (e.target.closest('.window-controls') || e.target.closest('.resize-handle')) {
        return
      }
      e.preventDefault()
      const touch = e.touches[0]
      startDrag(touch.clientX, touch.clientY)
    }

    const startDrag = (clientX, clientY) => {
      isDragging.value = true
      const rect = windowRef.value.getBoundingClientRect()
      dragOffset.value = {
        x: clientX - rect.left,
        y: clientY - rect.top
      }
      
      document.addEventListener('mousemove', handleDragMove)
      document.addEventListener('mouseup', handleDragEnd)
      document.addEventListener('touchmove', handleDragMove, { passive: false })
      document.addEventListener('touchend', handleDragEnd)
    }

    const handleDragMove = (e) => {
      if (!isDragging.value) return
      
      const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX
      const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY
      
      if (e.type.startsWith('touch')) {
        e.preventDefault()
      }

      let newX = clientX - dragOffset.value.x
      let newY = clientY - dragOffset.value.y

      if (props.constrainToViewport) {
        const rect = windowRef.value.getBoundingClientRect()
        newX = Math.max(0, Math.min(window.innerWidth - rect.width, newX))
        newY = Math.max(0, Math.min(window.innerHeight - rect.height, newY))
      }

      position.value = { x: newX, y: newY }
      emit('position-change', { x: newX, y: newY })
    }

    const handleDragEnd = () => {
      isDragging.value = false
      document.removeEventListener('mousemove', handleDragMove)
      document.removeEventListener('mouseup', handleDragEnd)
      document.removeEventListener('touchmove', handleDragMove)
      document.removeEventListener('touchend', handleDragEnd)
    }

    // 调整大小处理
    const handleResizeStart = (e) => {
      e.stopPropagation()
      isResizing.value = true
      
      resizeStartSize.value = { ...size.value }
      resizeStartPosition.value = {
        x: e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX,
        y: e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY
      }

      document.addEventListener('mousemove', handleResizeMove)
      document.addEventListener('mouseup', handleResizeEnd)
      document.addEventListener('touchmove', handleResizeMove, { passive: false })
      document.addEventListener('touchend', handleResizeEnd)
    }

    const handleResizeMove = (e) => {
      if (!isResizing.value) return

      const clientX = e.type.startsWith('touch') ? e.touches[0].clientX : e.clientX
      const clientY = e.type.startsWith('touch') ? e.touches[0].clientY : e.clientY

      if (e.type.startsWith('touch')) {
        e.preventDefault()
      }

      const deltaX = clientX - resizeStartPosition.value.x
      const deltaY = clientY - resizeStartPosition.value.y

      let newWidth = resizeStartSize.value.width + deltaX
      let newHeight = resizeStartSize.value.height + deltaY

      // 应用最小/最大尺寸约束
      newWidth = Math.max(props.minWidth, newWidth)
      newHeight = Math.max(props.minHeight, newHeight)

      if (props.maxWidth) {
        newWidth = Math.min(props.maxWidth, newWidth)
      }
      if (props.maxHeight) {
        newHeight = Math.min(props.maxHeight, newHeight)
      }

      size.value = { width: newWidth, height: newHeight }
      emit('size-change', { width: newWidth, height: newHeight })
    }

    const handleResizeEnd = () => {
      isResizing.value = false
      document.removeEventListener('mousemove', handleResizeMove)
      document.removeEventListener('mouseup', handleResizeEnd)
      document.removeEventListener('touchmove', handleResizeMove)
      document.removeEventListener('touchend', handleResizeEnd)
    }

    // 窗口控制
    const toggleMinimize = () => {
      isMinimized.value = !isMinimized.value
      emit('minimize', isMinimized.value)
    }

    const close = () => {
      emit('close')
    }

    // 公开方法
    const setPosition = (x, y) => {
      position.value = { x, y }
      emit('position-change', { x, y })
    }

    const setSize = (width, height) => {
      size.value = { width, height }
      emit('size-change', { width, height })
    }

    const minimize = () => {
      isMinimized.value = true
      emit('minimize', true)
    }

    const restore = () => {
      isMinimized.value = false
      emit('minimize', false)
    }

    // 清理事件监听器
    onUnmounted(() => {
      document.removeEventListener('mousemove', handleDragMove)
      document.removeEventListener('mouseup', handleDragEnd)
      document.removeEventListener('touchmove', handleDragMove)
      document.removeEventListener('touchend', handleDragEnd)
      document.removeEventListener('mousemove', handleResizeMove)
      document.removeEventListener('mouseup', handleResizeEnd)
      document.removeEventListener('touchmove', handleResizeMove)
      document.removeEventListener('touchend', handleResizeEnd)
    })

    return {
      windowRef,
      isDragging,
      isResizing,
      isMinimized,
      windowClasses,
      windowStyle,
      contentStyle,
      handleMouseDown,
      handleTouchStart,
      handleResizeStart,
      toggleMinimize,
      close,
      setPosition,
      setSize,
      minimize,
      restore
    }
  }
}
</script>

<style lang="scss" scoped>
.draggable-window {
  position: fixed;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  overflow: hidden;
  user-select: none;
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }

  &--dragging {
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
    transform: scale(1.02);
  }

  &--resizing {
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
  }

  &--minimized {
    .window-header {
      border-radius: 12px;
    }
  }

  &--dark {
    background: rgba(30, 30, 30, 0.95);
    border-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;

    .window-header {
      background: rgba(40, 40, 40, 0.8);
      border-bottom-color: rgba(255, 255, 255, 0.1);
    }

    .control-button {
      color: #ffffff;
      
      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }
    }

    .close-button:hover {
      background: #ff4757;
    }
  }
}

.window-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(248, 250, 252, 0.8);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  cursor: grab;
  
  &.dragging {
    cursor: grabbing;
  }
}

.window-title {
  font-weight: 600;
  font-size: 14px;
  color: #1a202c;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.window-controls {
  display: flex;
  gap: 4px;
}

.control-button {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #64748b;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #1a202c;
  }

  &:active {
    transform: scale(0.95);
  }
}

.close-button:hover {
  background: #ef4444;
  color: white;
}

.window-content {
  padding: 16px;
  overflow: auto;
  max-height: calc(100vh - 100px);
}

.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  cursor: se-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #94a3b8;
  background: linear-gradient(135deg, transparent 40%, rgba(0, 0, 0, 0.05) 40%);
  
  &:hover {
    color: #64748b;
    background: linear-gradient(135deg, transparent 40%, rgba(0, 0, 0, 0.1) 40%);
  }
}

// 响应式适配
@media (max-width: 768px) {
  .draggable-window {
    max-width: calc(100vw - 20px);
    max-height: calc(100vh - 20px);
  }

  .window-content {
    padding: 12px;
  }
}
</style>
