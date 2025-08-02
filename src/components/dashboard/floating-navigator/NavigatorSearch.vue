<template>
  <div class="navigator-search">
    <div class="search-input-wrapper">
      <span class="search-icon">🔍</span>
      <input
        ref="searchInput"
        type="text"
        class="search-input"
        :placeholder="placeholder"
        :value="modelValue"
        @input="handleInput"
        @keydown="handleKeyDown"
        @focus="handleFocus"
        @blur="handleBlur"
        :disabled="disabled"
      />
      <button
        v-if="modelValue && showClearButton"
        class="clear-button"
        @click="clearSearch"
        :title="'清除搜索'"
      >
        ✕
      </button>
    </div>
    
    <!-- 搜索建议/历史 -->
    <div 
      v-if="showSuggestions && (suggestions.length > 0 || searchHistory.length > 0)"
      class="search-suggestions"
    >
      <!-- 搜索建议 -->
      <div v-if="suggestions.length > 0" class="suggestions-section">
        <div class="suggestions-header">建议</div>
        <div
          v-for="(suggestion, index) in suggestions"
          :key="`suggestion-${index}`"
          class="suggestion-item"
          @click="selectSuggestion(suggestion)"
        >
          <span class="suggestion-icon">💡</span>
          <span class="suggestion-text">{{ suggestion }}</span>
        </div>
      </div>
      
      <!-- 搜索历史 -->
      <div v-if="searchHistory.length > 0 && !modelValue" class="history-section">
        <div class="suggestions-header">
          <span>最近搜索</span>
          <button 
            class="clear-history-btn"
            @click="clearHistory"
            :title="'清除历史'"
          >
            🗑️
          </button>
        </div>
        <div
          v-for="(item, index) in searchHistory"
          :key="`history-${index}`"
          class="suggestion-item history-item"
          @click="selectSuggestion(item)"
        >
          <span class="suggestion-icon">🕒</span>
          <span class="suggestion-text">{{ item }}</span>
          <button
            class="remove-history-item"
            @click.stop="removeHistoryItem(index)"
            :title="'删除此项'"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
    
    <!-- 搜索统计 -->
    <div v-if="showStats && modelValue" class="search-stats">
      找到 {{ resultCount }} 个结果
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, watch, nextTick } from 'vue';

export default defineComponent({
  name: 'NavigatorSearch',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: '搜索组件...'
    },
    suggestions: {
      type: Array,
      default: () => []
    },
    searchHistory: {
      type: Array,
      default: () => []
    },
    disabled: {
      type: Boolean,
      default: false
    },
    showClearButton: {
      type: Boolean,
      default: true
    },
    showSuggestions: {
      type: Boolean,
      default: true
    },
    showStats: {
      type: Boolean,
      default: true
    },
    resultCount: {
      type: Number,
      default: 0
    },
    debounceDelay: {
      type: Number,
      default: 300
    },
    maxHistoryItems: {
      type: Number,
      default: 10
    }
  },
  emits: [
    'update:modelValue', 
    'search', 
    'clear', 
    'focus', 
    'blur',
    'suggestion-select',
    'history-clear',
    'history-remove'
  ],
  setup(props, { emit }) {
    const searchInput = ref(null);
    const isFocused = ref(false);
    const debounceTimer = ref(null);
    
    // 处理输入
    const handleInput = (event) => {
      const value = event.target.value;
      emit('update:modelValue', value);
      
      // 防抖搜索
      if (debounceTimer.value) {
        clearTimeout(debounceTimer.value);
      }
      
      debounceTimer.value = setTimeout(() => {
        emit('search', value);
      }, props.debounceDelay);
    };
    
    // 处理键盘事件
    const handleKeyDown = (event) => {
      switch (event.key) {
        case 'Enter':
          event.preventDefault();
          if (props.modelValue.trim()) {
            addToHistory(props.modelValue.trim());
            emit('search', props.modelValue.trim());
          }
          break;
        case 'Escape':
          event.preventDefault();
          clearSearch();
          searchInput.value?.blur();
          break;
      }
    };
    
    // 处理聚焦
    const handleFocus = () => {
      isFocused.value = true;
      emit('focus');
    };
    
    // 处理失焦
    const handleBlur = () => {
      // 延迟失焦以允许点击建议项
      setTimeout(() => {
        isFocused.value = false;
        emit('blur');
      }, 150);
    };
    
    // 清除搜索
    const clearSearch = () => {
      emit('update:modelValue', '');
      emit('clear');
      if (debounceTimer.value) {
        clearTimeout(debounceTimer.value);
      }
    };
    
    // 选择建议
    const selectSuggestion = (suggestion) => {
      emit('update:modelValue', suggestion);
      emit('suggestion-select', suggestion);
      addToHistory(suggestion);
      nextTick(() => {
        searchInput.value?.focus();
      });
    };
    
    // 添加到历史记录
    const addToHistory = (query) => {
      if (!query || !query.trim()) return;
      
      const trimmedQuery = query.trim();
      const currentHistory = [...props.searchHistory];
      
      // 移除重复项
      const existingIndex = currentHistory.indexOf(trimmedQuery);
      if (existingIndex > -1) {
        currentHistory.splice(existingIndex, 1);
      }
      
      // 添加到开头
      currentHistory.unshift(trimmedQuery);
      
      // 限制历史记录数量
      if (currentHistory.length > props.maxHistoryItems) {
        currentHistory.splice(props.maxHistoryItems);
      }
      
      emit('history-update', currentHistory);
    };
    
    // 清除历史记录
    const clearHistory = () => {
      emit('history-clear');
    };
    
    // 删除历史记录项
    const removeHistoryItem = (index) => {
      emit('history-remove', index);
    };
    
    // 聚焦输入框
    const focus = () => {
      nextTick(() => {
        searchInput.value?.focus();
      });
    };
    
    // 失焦输入框
    const blur = () => {
      searchInput.value?.blur();
    };
    
    // 监听modelValue变化
    watch(() => props.modelValue, (newValue) => {
      if (debounceTimer.value) {
        clearTimeout(debounceTimer.value);
      }
      
      if (newValue) {
        debounceTimer.value = setTimeout(() => {
          emit('search', newValue);
        }, props.debounceDelay);
      }
    });
    
    return {
      searchInput,
      isFocused,
      handleInput,
      handleKeyDown,
      handleFocus,
      handleBlur,
      clearSearch,
      selectSuggestion,
      clearHistory,
      removeHistoryItem,
      focus,
      blur
    };
  }
});
</script>

<style scoped>
.navigator-search {
  position: relative;
  margin-bottom: 8px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  padding: 6px 8px;
  transition: all 0.2s ease;
}

.search-input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.search-icon {
  font-size: 12px;
  margin-right: 6px;
  opacity: 0.6;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 12px;
  color: #333;
  padding: 0;
}

.search-input::placeholder {
  color: #999;
}

.search-input:disabled {
  color: #999;
  cursor: not-allowed;
}

.clear-button {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 11px;
  padding: 2px;
  border-radius: 2px;
  transition: all 0.2s ease;
}

.clear-button:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #666;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 2px;
}

.suggestions-section,
.history-section {
  padding: 4px 0;
}

.suggestions-section:not(:last-child) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 12px;
  font-size: 10px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.clear-history-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 10px;
  padding: 2px;
  border-radius: 2px;
  transition: all 0.2s ease;
}

.clear-history-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #666;
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 12px;
}

.suggestion-item:hover {
  background: rgba(102, 126, 234, 0.1);
}

.history-item {
  color: #666;
}

.suggestion-icon {
  font-size: 10px;
  margin-right: 8px;
  opacity: 0.7;
}

.suggestion-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.remove-history-item {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 10px;
  padding: 2px 4px;
  border-radius: 2px;
  margin-left: 4px;
  opacity: 0;
  transition: all 0.2s ease;
}

.history-item:hover .remove-history-item {
  opacity: 1;
}

.remove-history-item:hover {
  background: rgba(255, 0, 0, 0.1);
  color: #e53e3e;
}

.search-stats {
  padding: 4px 8px;
  font-size: 10px;
  color: #666;
  text-align: center;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
  margin-top: 4px;
}

/* 滚动条样式 */
.search-suggestions::-webkit-scrollbar {
  width: 4px;
}

.search-suggestions::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
}

.search-suggestions::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.search-suggestions::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 暗色主题 */
@media (prefers-color-scheme: dark) {
  .search-input-wrapper {
    background: rgba(30, 30, 30, 0.9);
    border-color: rgba(255, 255, 255, 0.2);
  }
  
  .search-input {
    color: #fff;
  }
  
  .search-input::placeholder {
    color: #999;
  }
  
  .search-suggestions {
    background: #2d3748;
    border-color: rgba(255, 255, 255, 0.2);
  }
  
  .suggestion-item:hover {
    background: rgba(102, 126, 234, 0.2);
  }
  
  .suggestions-header,
  .history-item {
    color: #a0aec0;
  }
  
  .search-stats {
    background: rgba(255, 255, 255, 0.05);
    color: #a0aec0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-suggestions {
    position: fixed;
    left: 10px;
    right: 10px;
    top: auto;
    max-height: 150px;
  }
}
</style>
