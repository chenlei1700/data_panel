/**
 * 拖拽处理逻辑
 */
export class DragHandler {
  constructor() {
    this.isDragging = false;
    this.dragOffset = { x: 0, y: 0 };
    this.onMouseMove = null;
    this.onMouseUp = null;
  }
  
  /**
   * 开始拖拽
   * @param {MouseEvent} event - 鼠标按下事件
   * @param {Object} currentPosition - 当前位置 {x, y}
   * @param {Function} onPositionChange - 位置变化回调
   */
  startDrag(event, currentPosition, onPositionChange) {
    this.isDragging = true;
    
    // 计算鼠标相对于元素左上角的偏移
    this.dragOffset = {
      x: event.clientX - currentPosition.x,
      y: event.clientY - currentPosition.y
    };
    
    // 创建鼠标移动处理函数
    this.onMouseMove = (moveEvent) => {
      if (!this.isDragging) return;
      
      const newPosition = {
        x: moveEvent.clientX - this.dragOffset.x,
        y: moveEvent.clientY - this.dragOffset.y
      };
      
      // 边界检查
      const constrainedPosition = this.constrainToViewport(newPosition);
      onPositionChange(constrainedPosition);
    };
    
    // 创建鼠标释放处理函数
    this.onMouseUp = () => {
      this.stopDrag();
    };
    
    // 添加全局事件监听器
    document.addEventListener('mousemove', this.onMouseMove);
    document.addEventListener('mouseup', this.onMouseUp);
    
    // 防止文本选择
    event.preventDefault();
    document.body.style.userSelect = 'none';
  }
  
  /**
   * 停止拖拽
   */
  stopDrag() {
    this.isDragging = false;
    
    // 移除事件监听器
    if (this.onMouseMove) {
      document.removeEventListener('mousemove', this.onMouseMove);
      this.onMouseMove = null;
    }
    
    if (this.onMouseUp) {
      document.removeEventListener('mouseup', this.onMouseUp);
      this.onMouseUp = null;
    }
    
    // 恢复文本选择
    document.body.style.userSelect = '';
  }
  
  /**
   * 将位置限制在视窗范围内
   * @param {Object} position - 位置 {x, y}
   * @param {Object} elementSize - 元素尺寸 {width, height}
   * @returns {Object} - 受限制的位置
   */
  constrainToViewport(position, elementSize = { width: 320, height: 450 }) {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    // 确保元素不会完全移出视窗
    const minX = -elementSize.width + 50; // 至少保留50px可见
    const maxX = viewportWidth - 50;
    const minY = 0;
    const maxY = viewportHeight - 50;
    
    return {
      x: Math.max(minX, Math.min(maxX, position.x)),
      y: Math.max(minY, Math.min(maxY, position.y))
    };
  }
  
  /**
   * 检查位置是否在视窗范围内
   * @param {Object} position - 位置 {x, y}
   * @param {Object} elementSize - 元素尺寸 {width, height}
   * @returns {Boolean} - 是否在范围内
   */
  isPositionValid(position, elementSize = { width: 320, height: 450 }) {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    return position.x >= 0 && 
           position.y >= 0 && 
           position.x + elementSize.width <= viewportWidth &&
           position.y + elementSize.height <= viewportHeight;
  }
  
  /**
   * 获取默认位置（右上角）
   * @param {Object} elementSize - 元素尺寸 {width, height}
   * @returns {Object} - 默认位置
   */
  getDefaultPosition(elementSize = { width: 320, height: 450 }) {
    const viewportWidth = window.innerWidth;
    const padding = 20;
    
    return {
      x: Math.max(padding, viewportWidth - elementSize.width - padding),
      y: padding + 60 // 留出顶部导航空间
    };
  }
  
  /**
   * 销毁拖拽处理器
   */
  destroy() {
    this.stopDrag();
  }
}

/**
 * 触摸设备拖拽处理
 */
export class TouchDragHandler extends DragHandler {
  /**
   * 开始触摸拖拽
   * @param {TouchEvent} event - 触摸开始事件
   * @param {Object} currentPosition - 当前位置
   * @param {Function} onPositionChange - 位置变化回调
   */
  startDrag(event, currentPosition, onPositionChange) {
    this.isDragging = true;
    
    const touch = event.touches[0];
    this.dragOffset = {
      x: touch.clientX - currentPosition.x,
      y: touch.clientY - currentPosition.y
    };
    
    this.onTouchMove = (moveEvent) => {
      if (!this.isDragging) return;
      
      const touch = moveEvent.touches[0];
      const newPosition = {
        x: touch.clientX - this.dragOffset.x,
        y: touch.clientY - this.dragOffset.y
      };
      
      const constrainedPosition = this.constrainToViewport(newPosition);
      onPositionChange(constrainedPosition);
      
      moveEvent.preventDefault(); // 防止页面滚动
    };
    
    this.onTouchEnd = () => {
      this.stopDrag();
    };
    
    document.addEventListener('touchmove', this.onTouchMove, { passive: false });
    document.addEventListener('touchend', this.onTouchEnd);
    
    event.preventDefault();
  }
  
  /**
   * 停止触摸拖拽
   */
  stopDrag() {
    this.isDragging = false;
    
    if (this.onTouchMove) {
      document.removeEventListener('touchmove', this.onTouchMove);
      this.onTouchMove = null;
    }
    
    if (this.onTouchEnd) {
      document.removeEventListener('touchend', this.onTouchEnd);
      this.onTouchEnd = null;
    }
  }
}

export default DragHandler;
