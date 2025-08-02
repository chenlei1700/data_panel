<template>
  <div class="opacity-slider-container">
    <label v-if="showLabel" class="opacity-label" :for="sliderId">
      {{ label }}
    </label>
    <div class="opacity-slider-wrapper">
      <span v-if="showIcons" class="opacity-icon opacity-low">🌫️</span>
      <input
        :id="sliderId"
        ref="sliderRef"
        type="range"
        class="opacity-slider"
        :min="min"
        :max="max"
        :step="step"
        :value="modelValue"
        @input="handleInput"
        @change="handleChange"
        :style="sliderStyle"
      />
      <span v-if="showIcons" class="opacity-icon opacity-high">🔆</span>
    </div>
    <span v-if="showValue" class="opacity-value">
      {{ displayValue }}
    </span>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted } from 'vue';

export default defineComponent({
  name: 'OpacitySlider',
  props: {
    modelValue: {
      type: Number,
      default: 0.9
    },
    min: {
      type: Number,
      default: 0.1
    },
    max: {
      type: Number,
      default: 1.0
    },
    step: {
      type: Number,
      default: 0.05
    },
    label: {
      type: String,
      default: '透明度'
    },
    showLabel: {
      type: Boolean,
      default: false
    },
    showValue: {
      type: Boolean,
      default: true
    },
    showIcons: {
      type: Boolean,
      default: true
    },
    size: {
      type: String,
      default: 'medium', // small, medium, large
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    theme: {
      type: String,
      default: 'light', // light, dark
      validator: (value) => ['light', 'dark'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const sliderRef = ref(null);
    
    // 生成唯一ID
    const sliderId = computed(() => `opacity-slider-${Math.random().toString(36).substr(2, 9)}`);
    
    // 显示值（百分比）
    const displayValue = computed(() => {
      return Math.round(props.modelValue * 100) + '%';
    });
    
    // 滑块样式
    const sliderStyle = computed(() => {
      const percentage = ((props.modelValue - props.min) / (props.max - props.min)) * 100;
      
      const sizeMap = {
        small: { width: '60px', height: '4px' },
        medium: { width: '80px', height: '5px' },
        large: { width: '100px', height: '6px' }
      };
      
      const size = sizeMap[props.size];
      
      const themeColors = {
        light: {
          track: '#e2e8f0',
          fill: '#667eea',
          thumb: '#ffffff'
        },
        dark: {
          track: '#4a5568',
          fill: '#90cdf4',
          thumb: '#ffffff'
        }
      };
      
      const colors = themeColors[props.theme];
      
      return {
        '--slider-width': size.width,
        '--slider-height': size.height,
        '--slider-percentage': `${percentage}%`,
        '--track-color': colors.track,
        '--fill-color': colors.fill,
        '--thumb-color': colors.thumb,
        opacity: props.disabled ? 0.5 : 1,
        pointerEvents: props.disabled ? 'none' : 'auto'
      };
    });
    
    // 处理输入
    const handleInput = (event) => {
      const value = parseFloat(event.target.value);
      emit('update:modelValue', value);
    };
    
    // 处理变化
    const handleChange = (event) => {
      const value = parseFloat(event.target.value);
      emit('change', value);
    };
    
    // 设置值
    const setValue = (value) => {
      const clampedValue = Math.max(props.min, Math.min(props.max, value));
      emit('update:modelValue', clampedValue);
    };
    
    // 增加透明度
    const increase = () => {
      const newValue = Math.min(props.max, props.modelValue + props.step);
      setValue(newValue);
    };
    
    // 减少透明度
    const decrease = () => {
      const newValue = Math.max(props.min, props.modelValue - props.step);
      setValue(newValue);
    };
    
    // 键盘事件处理
    const handleKeyDown = (event) => {
      switch (event.key) {
        case 'ArrowUp':
        case 'ArrowRight':
          event.preventDefault();
          increase();
          break;
        case 'ArrowDown':
        case 'ArrowLeft':
          event.preventDefault();
          decrease();
          break;
        case 'Home':
          event.preventDefault();
          setValue(props.min);
          break;
        case 'End':
          event.preventDefault();
          setValue(props.max);
          break;
      }
    };
    
    onMounted(() => {
      if (sliderRef.value) {
        sliderRef.value.addEventListener('keydown', handleKeyDown);
      }
    });
    
    return {
      sliderRef,
      sliderId,
      displayValue,
      sliderStyle,
      handleInput,
      handleChange,
      setValue,
      increase,
      decrease
    };
  }
});
</script>

<style scoped>
.opacity-slider-container {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.opacity-label {
  font-weight: 500;
  color: inherit;
  white-space: nowrap;
}

.opacity-slider-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
}

.opacity-icon {
  font-size: 12px;
  opacity: 0.7;
}

.opacity-slider {
  width: var(--slider-width, 80px);
  height: var(--slider-height, 5px);
  background: var(--track-color, #e2e8f0);
  border-radius: 3px;
  outline: none;
  appearance: none;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.opacity-slider::-webkit-slider-track {
  height: var(--slider-height, 5px);
  background: var(--track-color, #e2e8f0);
  border-radius: 3px;
}

.opacity-slider::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  background: var(--thumb-color, #ffffff);
  border: 2px solid var(--fill-color, #667eea);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.opacity-slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

.opacity-slider::-moz-range-track {
  height: var(--slider-height, 5px);
  background: var(--track-color, #e2e8f0);
  border-radius: 3px;
  border: none;
}

.opacity-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: var(--thumb-color, #ffffff);
  border: 2px solid var(--fill-color, #667eea);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 填充效果 */
.opacity-slider::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: var(--slider-percentage, 90%);
  background: var(--fill-color, #667eea);
  border-radius: 3px;
  pointer-events: none;
}

.opacity-value {
  font-weight: 500;
  color: inherit;
  min-width: 30px;
  text-align: right;
  font-size: 11px;
}

/* 聚焦状态 */
.opacity-slider:focus {
  box-shadow: 0 0 0 2px var(--fill-color, #667eea), 0 0 0 4px rgba(102, 126, 234, 0.2);
}

/* 禁用状态 */
.opacity-slider:disabled {
  cursor: not-allowed;
}

/* 小尺寸 */
.opacity-slider-container.small {
  font-size: 11px;
}

.opacity-slider-container.small .opacity-slider::-webkit-slider-thumb {
  width: 12px;
  height: 12px;
}

.opacity-slider-container.small .opacity-slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
}

/* 大尺寸 */
.opacity-slider-container.large {
  font-size: 13px;
}

.opacity-slider-container.large .opacity-slider::-webkit-slider-thumb {
  width: 16px;
  height: 16px;
}

.opacity-slider-container.large .opacity-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .opacity-slider-container {
    font-size: 11px;
  }
  
  .opacity-slider {
    width: 60px;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .opacity-slider {
    border: 1px solid currentColor;
  }
  
  .opacity-slider::-webkit-slider-thumb {
    border-width: 3px;
  }
  
  .opacity-slider::-moz-range-thumb {
    border-width: 3px;
  }
}
</style>
