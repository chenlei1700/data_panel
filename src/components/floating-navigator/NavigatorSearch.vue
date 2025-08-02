<template>
  <div class="navigator-search">
    <div class="search-container">
      <div class="search-input-wrapper">
        <input
          ref="searchInput"
          v-model="searchTerm"
          type="text"
          :placeholder="placeholder"
          class="search-input"
          @input="handleInput"
          @keydown="handleKeyDown"
          @focus="handleFocus"
          @blur="handleBlur"
        />
        <div class="search-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
        </div>
        <button
          v-if="searchTerm"
          @click="clearSearch"
          class="clear-button"
          title="清除搜索"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <!-- 搜索建议/历史 -->
      <div
        v-if="showSuggestions && (suggestions.length > 0 || searchHistory.length > 0)"
        class="search-suggestions"
      >
        <!-- 搜索建议 -->
        <div v-if="suggestions.length > 0" class="suggestion-group">
          <div class="suggestion-header">搜索建议</div>
          <button
            v-for="(suggestion, index) in suggestions"
            :key="`suggestion-${index}`"
            @click="selectSuggestion(suggestion)"
            class="suggestion-item"
            :class="{ active: selectedSuggestionIndex === index }"
          >
            <span class="suggestion-icon">🔍</span>
            <span class="suggestion-text" v-html="highlightMatch(suggestion, searchTerm)"></span>
          </button>
        </div>

        <!-- 搜索历史 -->
        <div v-if="searchHistory.length > 0 && !searchTerm" class="suggestion-group">
          <div class="suggestion-header">
            <span>搜索历史</span>
            <button @click="clearHistory" class="clear-history">清除</button>
          </div>
          <div
            v-for="(historyItem, index) in searchHistory"
            :key="`history-${index}`"
            class="suggestion-item history-item"
          >
            <span class="suggestion-icon">🕒</span>
            <span class="suggestion-text" @click="selectSuggestion(historyItem)">{{ historyItem }}</span>
            <button
              @click.stop="removeFromHistory(historyItem)"
              class="remove-history"
              title="从历史中移除"
            >
              ×
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索快捷键提示 -->
    <div v-if="showShortcuts" class="search-shortcuts">
      <span class="shortcut-item">
        <kbd>Enter</kbd> 搜索
      </span>
      <span class="shortcut-item">
        <kbd>Esc</kbd> 清除
      </span>
      <span class="shortcut-item">
        <kbd>↑↓</kbd> 选择
      </span>
    </div>

    <!-- 搜索结果统计 -->
    <div v-if="showStats && searchTerm" class="search-stats">
      找到 {{ resultCount }} 个结果
      <span v-if="searchTime > 0">（{{ searchTime }}ms）</span>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'

export default {
  name: 'NavigatorSearch',
  emits: ['search', 'select', 'clear'],
  props: {
    placeholder: {
      type: String,
      default: '搜索组件...'
    },
    suggestions: {
      type: Array,
      default: () => []
    },
    debounceTime: {
      type: Number,
      default: 300
    },
    maxHistory: {
      type: Number,
      default: 10
    },
    showShortcuts: {
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
    theme: {
      type: String,
      default: 'light'
    }
  },
  setup(props, { emit }) {
    const searchInput = ref(null)
    const searchTerm = ref('')
    const showSuggestions = ref(false)
    const selectedSuggestionIndex = ref(-1)
    const searchHistory = ref([])
    const searchTime = ref(0)
    let debounceTimer = null

    // 加载搜索历史
    const loadSearchHistory = () => {
      try {
        const stored = localStorage.getItem('navigator-search-history')
        if (stored) {
          searchHistory.value = JSON.parse(stored)
        }
      } catch (error) {
        console.warn('无法加载搜索历史:', error)
      }
    }

    // 保存搜索历史
    const saveSearchHistory = () => {
      try {
        localStorage.setItem('navigator-search-history', JSON.stringify(searchHistory.value))
      } catch (error) {
        console.warn('无法保存搜索历史:', error)
      }
    }

    // 添加到搜索历史
    const addToHistory = (term) => {
      if (!term.trim()) return

      // 移除已存在的项
      const index = searchHistory.value.indexOf(term)
      if (index > -1) {
        searchHistory.value.splice(index, 1)
      }

      // 添加到开头
      searchHistory.value.unshift(term)

      // 限制历史数量
      if (searchHistory.value.length > props.maxHistory) {
        searchHistory.value = searchHistory.value.slice(0, props.maxHistory)
      }

      saveSearchHistory()
    }

    // 从历史中移除
    const removeFromHistory = (term) => {
      const index = searchHistory.value.indexOf(term)
      if (index > -1) {
        searchHistory.value.splice(index, 1)
        saveSearchHistory()
      }
    }

    // 清除历史
    const clearHistory = () => {
      searchHistory.value = []
      saveSearchHistory()
    }

    // 输入处理
    const handleInput = () => {
      if (debounceTimer) {
        clearTimeout(debounceTimer)
      }

      debounceTimer = setTimeout(() => {
        const startTime = performance.now()
        emit('search', searchTerm.value)
        searchTime.value = Math.round(performance.now() - startTime)
      }, props.debounceTime)
    }

    // 键盘事件处理
    const handleKeyDown = (e) => {
      switch (e.key) {
        case 'Enter':
          e.preventDefault()
          if (selectedSuggestionIndex.value >= 0) {
            const suggestion = props.suggestions[selectedSuggestionIndex.value]
            selectSuggestion(suggestion)
          } else if (searchTerm.value.trim()) {
            addToHistory(searchTerm.value.trim())
            emit('search', searchTerm.value)
          }
          break

        case 'Escape':
          clearSearch()
          break

        case 'ArrowUp':
          e.preventDefault()
          if (props.suggestions.length > 0) {
            selectedSuggestionIndex.value = Math.max(-1, selectedSuggestionIndex.value - 1)
          }
          break

        case 'ArrowDown':
          e.preventDefault()
          if (props.suggestions.length > 0) {
            selectedSuggestionIndex.value = Math.min(
              props.suggestions.length - 1,
              selectedSuggestionIndex.value + 1
            )
          }
          break
      }
    }

    // 焦点处理
    const handleFocus = () => {
      showSuggestions.value = true
    }

    const handleBlur = () => {
      // 延迟隐藏，以允许点击建议项
      setTimeout(() => {
        showSuggestions.value = false
        selectedSuggestionIndex.value = -1
      }, 200)
    }

    // 选择建议
    const selectSuggestion = (suggestion) => {
      searchTerm.value = suggestion
      showSuggestions.value = false
      selectedSuggestionIndex.value = -1
      addToHistory(suggestion)
      emit('select', suggestion)
      emit('search', suggestion)
    }

    // 清除搜索
    const clearSearch = () => {
      searchTerm.value = ''
      selectedSuggestionIndex.value = -1
      emit('clear')
      searchInput.value?.focus()
    }

    // 高亮匹配文本
    const highlightMatch = (text, search) => {
      if (!search) return text
      const regex = new RegExp(`(${search})`, 'gi')
      return text.replace(regex, '<mark>$1</mark>')
    }

    // 聚焦搜索框
    const focus = () => {
      nextTick(() => {
        searchInput.value?.focus()
      })
    }

    // 监听建议变化
    watch(() => props.suggestions, () => {
      selectedSuggestionIndex.value = -1
    })

    // 初始化
    loadSearchHistory()

    return {
      searchInput,
      searchTerm,
      showSuggestions,
      selectedSuggestionIndex,
      searchHistory,
      searchTime,
      handleInput,
      handleKeyDown,
      handleFocus,
      handleBlur,
      selectSuggestion,
      clearSearch,
      removeFromHistory,
      clearHistory,
      highlightMatch,
      focus
    }
  }
}
</script>

<style lang="scss" scoped>
.navigator-search {
  margin-bottom: 12px;
}

.search-container {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 8px 32px 8px 36px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  color: #1a202c;
  transition: all 0.2s ease;

  &::placeholder {
    color: #94a3b8;
  }

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
}

.search-icon {
  position: absolute;
  left: 10px;
  color: #94a3b8;
  pointer-events: none;
}

.clear-button {
  position: absolute;
  right: 8px;
  padding: 4px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    color: #64748b;
    background: rgba(0, 0, 0, 0.05);
  }

  &:active {
    transform: scale(0.95);
  }
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 4px;
}

.suggestion-group {
  &:not(:last-child) {
    border-bottom: 1px solid #f1f5f9;
  }
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
}

.clear-history {
  font-size: 11px;
  color: #94a3b8;
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  
  &:hover {
    color: #64748b;
    background: rgba(0, 0, 0, 0.05);
  }
}

.suggestion-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s ease;
  gap: 8px;

  &:hover,
  &.active {
    background: #f1f5f9;
  }

  &:active {
    background: #e2e8f0;
  }
  
  &.history-item {
    .suggestion-text {
      color: #64748b;
      cursor: pointer;
      flex: 1;
    }
  }
}

.suggestion-icon {
  font-size: 14px;
  opacity: 0.7;
}

.suggestion-text {
  flex: 1;
  font-size: 14px;
  color: #1a202c;

  :deep(mark) {
    background: #fef3c7;
    color: #92400e;
    padding: 0 2px;
    border-radius: 2px;
  }
}

.history-item {
  .suggestion-text {
    color: #64748b;
  }
}

.remove-history {
  padding: 2px 6px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  border-radius: 3px;
  font-size: 16px;
  line-height: 1;

  &:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }
}

.search-shortcuts {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  font-size: 11px;
  color: #94a3b8;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 4px;

  kbd {
    padding: 2px 4px;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    font-size: 10px;
    color: #64748b;
  }
}

.search-stats {
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}

// 深色主题
[data-theme="dark"] {
  .search-input {
    background: #374151;
    border-color: #4b5563;
    color: #f9fafb;

    &::placeholder {
      color: #9ca3af;
    }

    &:focus {
      border-color: #60a5fa;
      box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
    }
  }

  .search-suggestions {
    background: #374151;
    border-color: #4b5563;
  }

  .suggestion-header {
    background: #4b5563;
    color: #d1d5db;
    border-bottom-color: #6b7280;
  }

  .suggestion-item {
    &:hover,
    &.active {
      background: #4b5563;
    }

    &:active {
      background: #6b7280;
    }
  }

  .suggestion-text {
    color: #f9fafb;

    :deep(mark) {
      background: #fbbf24;
      color: #92400e;
    }
  }

  .history-item .suggestion-text {
    color: #d1d5db;
  }

  .shortcut-item kbd {
    background: #4b5563;
    border-color: #6b7280;
    color: #d1d5db;
  }
}

// 响应式适配
@media (max-width: 480px) {
  .search-shortcuts {
    display: none;
  }

  .search-suggestions {
    max-height: 150px;
  }
}
</style>
