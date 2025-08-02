/**
 * 拖拽处理器 - 处理窗口拖拽和位置管理
 */
export class DragHandler {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      constrainToViewport: true,
      handle: null, // 如果指定，只有拖拽手柄可以触发拖拽
      onDragStart: null,
      onDrag: null,
      onDragEnd: null,
      ...options
    };

    this.isDragging = false;
    this.offset = { x: 0, y: 0 };
    this.startPosition = { x: 0, y: 0 };

    this.init();
  }

  init() {
    const dragTarget = this.options.handle 
      ? this.element.querySelector(this.options.handle)
      : this.element;

    if (!dragTarget) return;

    // 添加拖拽样式
    dragTarget.style.cursor = 'grab';
    dragTarget.style.userSelect = 'none';

    // 绑定事件
    this.bindEvents(dragTarget);
  }

  bindEvents(dragTarget) {
    // 鼠标事件
    dragTarget.addEventListener('mousedown', this.handleMouseDown.bind(this));
    document.addEventListener('mousemove', this.handleMouseMove.bind(this));
    document.addEventListener('mouseup', this.handleMouseUp.bind(this));

    // 触摸事件
    dragTarget.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
    document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
    document.addEventListener('touchend', this.handleTouchEnd.bind(this));
  }

  handleMouseDown(e) {
    e.preventDefault();
    this.startDrag(e.clientX, e.clientY);
  }

  handleTouchStart(e) {
    e.preventDefault();
    const touch = e.touches[0];
    this.startDrag(touch.clientX, touch.clientY);
  }

  startDrag(clientX, clientY) {
    this.isDragging = true;
    const rect = this.element.getBoundingClientRect();
    
    this.offset.x = clientX - rect.left;
    this.offset.y = clientY - rect.top;
    this.startPosition.x = rect.left;
    this.startPosition.y = rect.top;

    // 更新样式
    this.element.style.cursor = 'grabbing';
    this.element.style.zIndex = '9999';

    // 触发开始回调
    if (this.options.onDragStart) {
      this.options.onDragStart({ x: rect.left, y: rect.top });
    }
  }

  handleMouseMove(e) {
    if (!this.isDragging) return;
    this.drag(e.clientX, e.clientY);
  }

  handleTouchMove(e) {
    if (!this.isDragging) return;
    e.preventDefault();
    const touch = e.touches[0];
    this.drag(touch.clientX, touch.clientY);
  }

  drag(clientX, clientY) {
    const x = clientX - this.offset.x;
    const y = clientY - this.offset.y;

    const constrainedPosition = this.options.constrainToViewport 
      ? this.constrainToViewport(x, y)
      : { x, y };

    this.setPosition(constrainedPosition.x, constrainedPosition.y);

    // 触发拖拽回调
    if (this.options.onDrag) {
      this.options.onDrag(constrainedPosition);
    }
  }

  handleMouseUp() {
    this.endDrag();
  }

  handleTouchEnd() {
    this.endDrag();
  }

  endDrag() {
    if (!this.isDragging) return;

    this.isDragging = false;
    this.element.style.cursor = 'default';
    this.element.style.zIndex = '';

    // 触发结束回调
    if (this.options.onDragEnd) {
      const rect = this.element.getBoundingClientRect();
      this.options.onDragEnd({ x: rect.left, y: rect.top });
    }
  }

  constrainToViewport(x, y) {
    const rect = this.element.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    const constrainedX = Math.max(0, Math.min(viewportWidth - rect.width, x));
    const constrainedY = Math.max(0, Math.min(viewportHeight - rect.height, y));

    return { x: constrainedX, y: constrainedY };
  }

  setPosition(x, y) {
    this.element.style.position = 'fixed';
    this.element.style.left = `${x}px`;
    this.element.style.top = `${y}px`;
  }

  getPosition() {
    const rect = this.element.getBoundingClientRect();
    return { x: rect.left, y: rect.top };
  }

  destroy() {
    // 移除事件监听器
    const dragTarget = this.options.handle 
      ? this.element.querySelector(this.options.handle)
      : this.element;

    if (dragTarget) {
      dragTarget.style.cursor = '';
      dragTarget.style.userSelect = '';
    }
  }
}
