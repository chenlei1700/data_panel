<template>
  <div class="opacity-slider">
    <label class="slider-label">
      <span class="label-text">透明度</span>
      <span class="label-value">{{ displayValue }}%</span>
    </label>
    <div class="slider-container">
      <input
        ref="sliderRef"
        type="range"
        :min="min * 100"
        :max="max * 100"
        :value="internalValue * 100"
        @input="handleInput"
        @change="handleChange"
        class="slider-input"
        :style="sliderStyle"
      />
      <div class="slider-track" :style="trackStyle">
        <div class="slider-progress" :style="progressStyle"></div>
      </div>
    </div>
    <div class="slider-presets">
      <button
        v-for="preset in presets"
        :key="preset.value"
        @click="setPreset(preset.value)"
        :class="['preset-button', { active: isNearPreset(preset.value) }]"
        :title="`设置为 ${preset.label}`"
      >
        {{ preset.label }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'OpacitySlider',
  emits: ['update:modelValue', 'change'],
  props: {
    modelValue: {
      type: Number,
      default: 0.95,
      validator: value => value >= 0 && value <= 1
    },
    min: {
      type: Number,
      default: 0.1,
      validator: value => value >= 0 && value <= 1
    },
    max: {
      type: Number,
      default: 1,
      validator: value => value >= 0 && value <= 1
    },
    step: {
      type: Number,
      default: 0.05
    },
    presets: {
      type: Array,
      default: () => [
        { label: '30%', value: 0.3 },
        { label: '50%', value: 0.5 },
        { label: '70%', value: 0.7 },
        { label: '90%', value: 0.9 },
        { label: '100%', value: 1.0 }
      ]
    },
    theme: {
      type: String,
      default: 'light',
      validator: value => ['light', 'dark'].includes(value)
    },
    showPresets: {
      type: Boolean,
      default: true
    },
    showPercentage: {
      type: Boolean,
      default: true
    }
  },
  setup(props, { emit }) {
    const sliderRef = ref(null)
    const internalValue = ref(props.modelValue)

    // 监听外部值变化
    watch(() => props.modelValue, (newValue) => {
      internalValue.value = newValue
    })

    // 显示值（百分比）
    const displayValue = computed(() => {
      return Math.round(internalValue.value * 100)
    })

    // 滑块样式
    const sliderStyle = computed(() => ({
      '--slider-progress': `${(internalValue.value - props.min) / (props.max - props.min) * 100}%`,
      '--theme-primary': props.theme === 'dark' ? '#64b5f6' : '#2196f3',
      '--theme-track': props.theme === 'dark' ? '#424242' : '#e0e0e0',
      '--theme-thumb': props.theme === 'dark' ? '#ffffff' : '#2196f3'
    }))

    const trackStyle = computed(() => ({
      background: props.theme === 'dark' ? '#424242' : '#e0e0e0'
    }))

    const progressStyle = computed(() => ({
      width: `${(internalValue.value - props.min) / (props.max - props.min) * 100}%`,
      background: props.theme === 'dark' ? '#64b5f6' : '#2196f3'
    }))

    // 事件处理
    const handleInput = (e) => {
      const value = parseFloat(e.target.value) / 100
      internalValue.value = value
      emit('update:modelValue', value)
    }

    const handleChange = (e) => {
      const value = parseFloat(e.target.value) / 100
      emit('change', value)
    }

    const setPreset = (value) => {
      internalValue.value = value
      emit('update:modelValue', value)
      emit('change', value)
    }

    const isNearPreset = (presetValue) => {
      return Math.abs(internalValue.value - presetValue) < 0.01
    }

    return {
      sliderRef,
      internalValue,
      displayValue,
      sliderStyle,
      trackStyle,
      progressStyle,
      handleInput,
      handleChange,
      setPreset,
      isNearPreset
    }
  }
}
</script>

<style lang="scss" scoped>
.opacity-slider {
  width: 100%;
  padding: 8px 0;
}

.slider-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #64748b;
}

.label-text {
  font-weight: 500;
}

.label-value {
  font-weight: 600;
  color: #2196f3;
}

.slider-container {
  position: relative;
  height: 20px;
  margin-bottom: 8px;
}

.slider-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;

  &::-webkit-slider-thumb {
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--theme-thumb);
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  &::-webkit-slider-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }

  &::-webkit-slider-thumb:active {
    transform: scale(1.2);
  }

  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--theme-thumb);
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  &::-moz-range-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
}

.slider-track {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 4px;
  border-radius: 2px;
  transform: translateY(-50%);
  overflow: hidden;
  z-index: 1;
}

.slider-progress {
  height: 100%;
  border-radius: 2px;
  transition: width 0.2s ease;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 20px;
    height: 100%;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    transform: translateX(50%);
  }
}

.slider-presets {
  display: flex;
  gap: 4px;
  justify-content: space-between;
  margin-top: 8px;
}

.preset-button {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 4px;
  font-size: 11px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #2196f3;
    color: #2196f3;
    background: rgba(33, 150, 243, 0.05);
  }

  &.active {
    border-color: #2196f3;
    background: #2196f3;
    color: white;
  }

  &:active {
    transform: scale(0.95);
  }
}

// 深色主题
.opacity-slider[data-theme="dark"] {
  .slider-label {
    color: #94a3b8;
  }

  .label-value {
    color: #64b5f6;
  }

  .preset-button {
    border-color: #374151;
    background: #1f2937;
    color: #9ca3af;

    &:hover {
      border-color: #64b5f6;
      color: #64b5f6;
      background: rgba(100, 181, 246, 0.1);
    }

    &.active {
      border-color: #64b5f6;
      background: #64b5f6;
      color: #1f2937;
    }
  }
}

// 响应式适配
@media (max-width: 480px) {
  .slider-presets {
    flex-wrap: wrap;
    gap: 2px;
  }

  .preset-button {
    font-size: 10px;
    padding: 3px 6px;
  }
}
</style>
