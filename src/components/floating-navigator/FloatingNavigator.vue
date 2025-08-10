<template>
  <DraggableWindow
    ref="windowRef"
    :title="windowTitle"
    :initial-position="initialPosition"
    :initial-size="windowSize"
    :min-width="minWidth"
    :min-height="minHeight"
    :opacity="windowOpacity"
    :theme="currentTheme"
    :minimizable="true"
    :closable="true"
    :resizable="true"
    @position-change="handlePositionChange"
    @size-change="handleSizeChange"
    @minimize="handleMinimize"
    @close="handleClose"
  >
    <template #title>
      <div class="navigator-title" @click="handleTitleClick" @mousedown.stop>
        <span class="title-icon">🧭</span>
        <span class="title-text">{{ title }}</span>
        <span v-if="componentCount > 0" class="title-count">{{ componentCount }}</span>
        <span v-if="isMinimized" class="minimize-hint" title="双击展开到可视区域右下角">📍</span>
      </div>
    </template>

    <template #controls>
      <button
        @click="toggleSettings"
        class="control-button settings-button"
        :class="{ active: showSettings }"
        title="设置"
      >
        ⚙️
      </button>
      <button
        @click="refreshComponents"
        class="control-button refresh-button"
        title="刷新组件"
      >
        🔄
      </button>
    </template>

    <div class="navigator-content" v-show="!isMinimized">
      <!-- 设置面板 -->
      <div v-if="showSettings" class="settings-panel">
        <div class="settings-section">
          <label class="settings-label">透明度</label>
          <OpacitySlider
            v-model="windowOpacity"
            :theme="currentTheme"
            @change="handleOpacityChange"
          />
        </div>

        <div class="settings-section">
          <label class="settings-label">主题</label>
          <div class="theme-selector">
            <button
              v-for="theme in themes"
              :key="theme.value"
              @click="setTheme(theme.value)"
              :class="['theme-button', { active: currentTheme === theme.value }]"
            >
              {{ theme.icon }} {{ theme.label }}
            </button>
          </div>
        </div>

        <div class="settings-section">
          <label class="settings-label">显示选项</label>
          <div class="checkbox-group">
            <label class="checkbox-item">
              <input
                v-model="showSearch"
                type="checkbox"
                @change="handleSettingsChange"
              />
              <span>显示搜索</span>
            </label>
            <label class="checkbox-item">
              <input
                v-model="showItemDescription"
                type="checkbox"
                @change="handleSettingsChange"
              />
              <span>显示描述</span>
            </label>
            <label class="checkbox-item">
              <input
                v-model="showItemVisibility"
                type="checkbox"
                @change="handleSettingsChange"
              />
              <span>显示可见性</span>
            </label>
          </div>
        </div>

        <div class="settings-actions">
          <button @click="resetSettings" class="reset-button">
            重置设置
          </button>
          <button @click="exportSettings" class="export-button">
            导出配置
          </button>
        </div>
      </div>

      <!-- 搜索组件 -->
      <NavigatorSearch
        v-if="showSearch && !showSettings"
        ref="searchRef"
        :suggestions="searchSuggestions"
        :result-count="filteredCategories.length"
        :theme="currentTheme"
        @search="handleSearch"
        @select="handleSearchSelect"
        @clear="handleSearchClear"
      />

      <!-- 导航树 -->
      <NavigatorTree
        v-if="!showSettings"
        :categories="filteredCategories"
        :search-term="searchTerm"
        :initial-expanded-categories="expandedCategories"
        :show-item-description="showItemDescription"
        :show-item-visibility="showItemVisibility"
        :show-item-position="showItemPosition"
        :show-item-actions="showItemActions"
        :theme="currentTheme"
        @item-click="handleItemClick"
        @item-scroll-to="handleItemScrollTo"
        @category-toggle="handleCategoryToggle"
      />

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <div class="loading-text">正在扫描组件...</div>
      </div>

      <!-- 快捷键提示 -->
      <div v-if="showShortcuts && !showSettings" class="shortcuts-hint">
        <div class="shortcuts-title">快捷键</div>
        <div class="shortcuts-list">
          <span class="shortcut"><kbd>Ctrl</kbd>+<kbd>F</kbd> 搜索</span>
          <span class="shortcut"><kbd>Esc</kbd> 关闭</span>
        </div>
      </div>
    </div>
  </DraggableWindow>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import DraggableWindow from './DraggableWindow.vue'
import NavigatorSearch from './NavigatorSearch.vue'
import NavigatorTree from './NavigatorTree.vue'
import OpacitySlider from './OpacitySlider.vue'
import { ComponentOrganizer } from '../../utils/ComponentOrganizer.js'
import { StorageManager } from '../../utils/StorageManager.js'
import { ScrollManager } from '../../utils/ScrollManager.js'

export default {
  name: 'FloatingNavigator',
  components: {
    DraggableWindow,
    NavigatorSearch,
    NavigatorTree,
    OpacitySlider
  },
  emits: ['component-click', 'component-scroll-to', 'close'],
  props: {
    title: {
      type: String,
      default: '页面导航'
    },
    config: {
      type: Object,
      default: () => ({})
    },
    organizationConfig: {
      type: Object,
      default: () => ({})
    },
    autoScan: {
      type: Boolean,
      default: true
    },
    scanInterval: {
      type: Number,
      default: 5000 // 5秒扫描一次
    },
    showShortcuts: {
      type: Boolean,
      default: true
    }
  },
  setup(props, { emit }) {
    // 引用
    const windowRef = ref(null)
    const searchRef = ref(null)

    // 状态
    const isLoading = ref(false)
    const showSettings = ref(false)
    const searchTerm = ref('')
    const components = ref([])
    const categories = ref([])
    const expandedCategories = ref([])
    
    // 双击展开/最小化状态 - 默认为展开状态
    const isExpanded = ref(true)  // 改为true，初次启动时展开
    const isMinimized = ref(false)
    const originalWindowSize = ref({ width: 300, height: 400 })
    // 计算右下角位置作为默认位置
    const getDefaultExpandedPosition = () => {
      const viewportWidth = window.innerWidth || 1920
      const viewportHeight = window.innerHeight || 1080
      const expandedSize = { width: 450, height: 600 }
      return {
        x: viewportWidth - expandedSize.width - 20,
        y: viewportHeight - expandedSize.height - 50
      }
    }
    const originalPosition = ref(getDefaultExpandedPosition())
    const currentPosition = ref(getDefaultExpandedPosition()) // 跟踪当前位置
    const minimizedPosition = ref(null) // 将在mounted时计算
    
    // 双击检测状态
    const lastClickTime = ref(0)
    const doubleClickDelay = 300 // 双击检测延迟（毫秒）

    // 设置
    const windowOpacity = ref(0.95)
    const currentTheme = ref('light')
    const showSearch = ref(true)
    const showItemDescription = ref(true)
    const showItemVisibility = ref(true)
    const showItemPosition = ref(false)
    const showItemActions = ref(true)

    // 工具类实例
    const storageManager = new StorageManager('floating-navigator')
    const componentOrganizer = new ComponentOrganizer()
    const scrollManager = new ScrollManager()

    // 配置
    const themes = [
      { value: 'light', label: '浅色', icon: '☀️' },
      { value: 'dark', label: '深色', icon: '🌙' },
      { value: 'auto', label: '自动', icon: '🔄' }
    ]

    const minWidth = 280
    const minHeight = 200
    const windowSize = computed(() => {
      if (isMinimized.value) {
        return { width: 100, height: 40 } // 最小化时的尺寸
      }
      
      if (isExpanded.value) {
        // 展开时根据分类数量动态计算高度
        const categoriesHeight = categories.value.length * 50 // 每个分类标题约50px
        const itemsHeight = categories.value.reduce((total, cat) => 
          total + (cat.items ? cat.items.length * 35 : 0), 0) // 每个项目约35px
        const baseHeight = 150 // 基础高度（标题、搜索框等）
        const calculatedHeight = Math.max(400, Math.min(800, baseHeight + categoriesHeight + itemsHeight))
        
        return {
          width: showSettings.value ? 400 : 380,
          height: calculatedHeight
        }
      }
      
      return {
        width: showSettings.value ? 320 : 300,
        height: 400
      }
    })

    // 计算属性
    const componentCount = computed(() => {
      return categories.value.reduce((total, category) => total + category.items.length, 0)
    })

    const windowTitle = computed(() => {
      return componentCount.value > 0 
        ? `${props.title} (${componentCount.value})`
        : props.title
    })

    const initialPosition = computed(() => {
      const saved = storageManager.loadPosition()
      return saved || { x: 20, y: 20 }
    })

    const filteredCategories = computed(() => {
      if (!searchTerm.value.trim()) {
        return categories.value
      }
      return componentOrganizer.searchComponents(categories.value, searchTerm.value)
    })

    const searchSuggestions = computed(() => {
      if (!searchTerm.value.trim()) return []
      
      const suggestions = new Set()
      
      categories.value.forEach(category => {
        category.items.forEach(item => {
          if (item.title.toLowerCase().includes(searchTerm.value.toLowerCase())) {
            suggestions.add(item.title)
          }
          if (item.id.toLowerCase().includes(searchTerm.value.toLowerCase())) {
            suggestions.add(item.id)
          }
        })
      })
      
      return Array.from(suggestions).slice(0, 5)
    })

    // 方法
    const scanComponents = () => {
      isLoading.value = true
      
      nextTick(() => {
        try {
          // 扫描页面中的组件
          const pageComponents = Array.from(document.querySelectorAll('[data-component-id]'))
          components.value = pageComponents

          console.log('🧭 扫描到的组件:', pageComponents.map(el => ({
            id: el.dataset.componentId,
            title: el.querySelector('.component-header h3')?.textContent || '无标题',
            element: el
          })))

          // 使用组织器组织组件
          const organized = componentOrganizer.organizeComponents(
            pageComponents,
            props.organizationConfig
          )
          
          console.log('🧭 组织后的分类:', organized.map(cat => ({
            name: cat.name,
            itemCount: cat.items.length,
            items: cat.items.map(item => ({ id: item.id, title: item.title }))
          })))
          
          categories.value = organized
          
          // 简化逻辑：如果是展开状态，总是展开所有分类
          if (organized.length > 0) {
            if (isExpanded.value) {
              // 展开状态：展开所有分类
              expandedCategories.value = organized.map(cat => cat.name)
              console.log('🚀 展开状态，展开所有分类:', expandedCategories.value)
              
              // 调整窗口大小以适应所有展开的内容
              nextTick(() => {
                const totalItems = organized.reduce((total, cat) => total + (cat.items ? cat.items.length : 0), 0)
                const headerHeight = 80
                const searchHeight = showSearch.value ? 60 : 0
                const categoriesHeaderHeight = organized.length * 70
                const itemsHeight = totalItems * 50
                const paddingHeight = 60
                
                const calculatedHeight = headerHeight + searchHeight + categoriesHeaderHeight + itemsHeight + paddingHeight
                const maxViewportHeight = window.innerHeight - 100
                const finalHeight = Math.min(Math.max(calculatedHeight, 400), maxViewportHeight)
                const calculatedWidth = 450
                
                if (windowRef.value) {
                  // 确保在右下角位置
                  const rightBottomPosition = {
                    x: window.innerWidth - calculatedWidth - 20,
                    y: window.innerHeight - finalHeight - 50
                  }
                  
                  // 更新位置
                  currentPosition.value = rightBottomPosition
                  originalPosition.value = rightBottomPosition
                  
                  // 设置窗口大小和位置
                  windowRef.value.setSize(calculatedWidth, finalHeight)
                  windowRef.value.setPosition(rightBottomPosition.x, rightBottomPosition.y)
                  console.log('🔍 调整展开窗口大小和位置:', { 
                    size: { width: calculatedWidth, height: finalHeight },
                    position: rightBottomPosition
                  })
                }
              })
            } else {
              // 非展开状态：只展开第一个分类
              expandedCategories.value = [organized[0].name]
              console.log('🔍 普通状态，展开第一个分类:', expandedCategories.value)
            }
          }
          
        } catch (error) {
          console.error('扫描组件时出错:', error)
        } finally {
          isLoading.value = false
        }
      })
    }

    const refreshComponents = () => {
      scanComponents()
    }

    const handleSearch = (term) => {
      searchTerm.value = term
    }

    const handleSearchSelect = (term) => {
      searchTerm.value = term
    }

    const handleSearchClear = () => {
      searchTerm.value = ''
    }

    const handleItemClick = (event) => {
      emit('component-click', event)
    }

    const handleItemScrollTo = (event) => {
      scrollManager.scrollToComponent(event.componentId)
      emit('component-scroll-to', event)
    }

    const handleCategoryToggle = (event) => {
      // 如果不是手动展开状态，则更新展开分类
      if (!isExpanded.value) {
        expandedCategories.value = event.expandedCategories
        storageManager.saveExpandedCategories(expandedCategories.value)
      } else {
        console.log('🔍 忽略分类切换事件，因为当前处于手动展开状态')
      }
    }

    const handlePositionChange = (position) => {
      currentPosition.value = position // 更新当前位置
      storageManager.savePosition(position)
    }

    const handleSizeChange = (size) => {
      // 可以保存窗口大小
    }

    const handleOpacityChange = (opacity) => {
      storageManager.saveOpacity(opacity)
    }

    const handleMinimize = (minimized) => {
      storageManager.saveMinimizedState(minimized)
    }

    const handleClose = () => {
      storageManager.saveVisibility(false)
      emit('close')
    }

    const toggleSettings = () => {
      showSettings.value = !showSettings.value
    }

    // 自定义双击检测
    const handleTitleClick = (event) => {
      event.preventDefault()
      event.stopPropagation()
      
      const currentTime = Date.now()
      const timeDiff = currentTime - lastClickTime.value
      
      console.log('🖱️ 标题点击，时间差:', timeDiff)
      
      if (timeDiff < doubleClickDelay && timeDiff > 50) { // 50ms 最小间隔避免误触
        console.log('🖱️ 检测到双击！')
        handleDoubleClick()
        lastClickTime.value = 0 // 重置，避免连续触发
      } else {
        lastClickTime.value = currentTime
      }
    }

    // 双击处理方法
    const handleDoubleClick = () => {
      console.log('🔄 执行双击操作，当前状态:', {
        isMinimized: isMinimized.value,
        isExpanded: isExpanded.value
      })
      
      if (isMinimized.value) {
        // 从最小化状态恢复到展开状态
        restoreFromMinimizedAndExpand()
      } else {
        // 从正常状态或展开状态直接最小化
        minimizeToCorner()
      }
    }

    const expandAllCategories = () => {
      // 检查是否有分类数据
      if (!categories.value || categories.value.length === 0) {
        console.warn('🔍 无法展开分类：没有分类数据')
        return
      }
      
      // 保存当前状态
      if (!isExpanded.value) {
        originalWindowSize.value = { ...windowSize.value }
        originalPosition.value = { ...currentPosition.value }
      }
      
      // 重置所有状态，然后设置展开状态
      isMinimized.value = false
      isExpanded.value = true
      
      // 展开所有分类
      const allCategoryNames = categories.value.map(cat => cat.name)
      
      // 计算展开后需要的窗口大小（更精确的计算）
      const categoriesCount = categories.value.length
      const totalItems = categories.value.reduce((total, cat) => total + (cat.items ? cat.items.length : 0), 0)
      
      // 更精确的高度计算（expandAllCategories版本）
      const headerHeight = 80 // 标题栏高度（增加）
      const searchHeight = showSearch.value ? 60 : 0 // 搜索框高度（增加）
      const settingsHeight = showSettings.value ? 220 : 0 // 设置面板高度（增加）
      const categoriesHeaderHeight = categoriesCount * 70 // 每个分类标题约70px（增加间距）
      const itemsHeight = totalItems * 50 // 每个项目约50px（增加间距）
      const paddingHeight = 60 // 额外的内边距和间距（增加）
      
      const calculatedHeight = headerHeight + searchHeight + settingsHeight + 
                              categoriesHeaderHeight + itemsHeight + paddingHeight
      
      // 设置最小和最大高度限制，但优先显示所有内容
      const maxViewportHeight = window.innerHeight - 100 // 保留100px给顶部和底部边距
      const finalHeight = Math.min(Math.max(calculatedHeight, 400), maxViewportHeight)
      const calculatedWidth = 450 // 进一步增加宽度确保内容不会被截断
      
      // 使用 nextTick 确保在下一个 tick 中设置展开状态和窗口大小
      nextTick(() => {
        expandedCategories.value = allCategoryNames
        
        // 调整窗口大小以适应所有内容
        if (windowRef.value) {
          setTimeout(() => {
            windowRef.value.setSize(calculatedWidth, finalHeight)
            console.log('🔍 展开所有分类完成:', {
              分类数量: categories.value.length,
              项目总数: totalItems,
              展开的分类名称: allCategoryNames,
              窗口大小: { width: calculatedWidth, height: finalHeight },
              计算详情: {
                headerHeight,
                searchHeight,
                settingsHeight,
                categoriesHeaderHeight,
                itemsHeight,
                paddingHeight,
                原始计算高度: calculatedHeight,
                最终高度: finalHeight
              }
            })
          }, 100)
        }
      })
    }

    const minimizeToCorner = () => {
      console.log('📦 开始最小化到右下角，当前状态:', {
        isExpanded: isExpanded.value,
        isMinimized: isMinimized.value,
        currentPosition: currentPosition.value
      })
      
      // 保存当前状态（用于恢复）
      if (!isMinimized.value) {
        originalWindowSize.value = { ...windowSize.value }
        // 保存当前实际位置作为恢复的参考点
        originalPosition.value = { ...currentPosition.value }
      }
      
      // 计算右下角位置
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      const miniSize = { width: 100, height: 40 }
      
      minimizedPosition.value = {
        x: viewportWidth - miniSize.width - 20,
        y: viewportHeight - miniSize.height - 50
      }
      
      // 设置最小化状态，清空展开状态
      isExpanded.value = false
      isMinimized.value = true
      expandedCategories.value = []
      
      // 移动到右下角
      if (windowRef.value) {
        windowRef.value.setPosition(minimizedPosition.value.x, minimizedPosition.value.y)
      }
      
      console.log('📦 最小化完成:', {
        miniPosition: minimizedPosition.value,
        savedOriginalPosition: originalPosition.value
      })
    }

    const restoreFromMinimized = () => {
      console.log('🔄 开始从最小化状态恢复')
      
      // 重置所有状态
      isMinimized.value = false
      isExpanded.value = false
      
      if (windowRef.value) {
        windowRef.value.setPosition(originalPosition.value.x, originalPosition.value.y)
      }
      
      console.log('🔄 恢复完成')
    }

    const restoreFromMinimizedAndExpand = () => {
      console.log('🔄 开始从最小化状态恢复并展开')
      
      // 检查是否有分类数据
      if (!categories.value || categories.value.length === 0) {
        console.warn('🔍 无法展开分类：没有分类数据，仅恢复窗口')
        restoreFromMinimized()
        return
      }
      
      // 计算展开后需要的窗口大小（更精确的计算）
      const categoriesCount = categories.value.length
      const totalItems = categories.value.reduce((total, cat) => total + (cat.items ? cat.items.length : 0), 0)
      
      // 更精确的高度计算（restoreFromMinimizedAndExpand版本）
      const headerHeight = 80 // 标题栏高度（增加）
      const searchHeight = showSearch.value ? 60 : 0 // 搜索框高度（增加）
      const settingsHeight = showSettings.value ? 220 : 0 // 设置面板高度（增加）
      const categoriesHeaderHeight = categoriesCount * 70 // 每个分类标题约70px（增加间距）
      const itemsHeight = totalItems * 50 // 每个项目约50px（增加间距）
      const paddingHeight = 60 // 额外的内边距和间距（增加）
      
      const calculatedHeight = headerHeight + searchHeight + settingsHeight + 
                              categoriesHeaderHeight + itemsHeight + paddingHeight
      
      // 设置最小和最大高度限制，但优先显示所有内容
      const maxViewportHeight = window.innerHeight - 100 // 保留100px给顶部和底部边距
      const finalHeight = Math.min(Math.max(calculatedHeight, 400), maxViewportHeight)
      const calculatedWidth = 450 // 进一步增加宽度确保内容不会被截断
      
      // 获取当前可见区域
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      
      // 计算新位置：以可见区域右下角为基准，向左上偏移窗口大小
      const newPosition = {
        x: Math.max(10, viewportWidth - calculatedWidth - 20), // 距右边缘20px，最小距左边缘10px
        y: Math.max(10, viewportHeight - calculatedHeight - 50) // 距底边50px，最小距顶边10px
      }
      
      console.log('🔄 计算的窗口参数:', {
        newPosition,
        calculatedSize: { width: calculatedWidth, height: finalHeight },
        viewport: { width: viewportWidth, height: viewportHeight },
        categoriesCount: categories.value.length,
        totalItems: categories.value.reduce((total, cat) => total + (cat.items ? cat.items.length : 0), 0),
        详细计算: {
          headerHeight,
          searchHeight,
          settingsHeight,
          categoriesHeaderHeight,
          itemsHeight,
          paddingHeight,
          原始计算高度: calculatedHeight,
          最大视口高度: maxViewportHeight,
          最终高度: finalHeight
        }
      })
      
      // 重置最小化状态，设置展开状态
      isMinimized.value = false
      isExpanded.value = true
      
      // 展开所有分类
      const allCategoryNames = categories.value.map(cat => cat.name)
      expandedCategories.value = allCategoryNames
      
      // 使用 nextTick 和延迟确保所有状态更新完成后再设置窗口大小和位置
      nextTick(() => {
        setTimeout(() => {
          if (windowRef.value) {
            // 先设置大小，再设置位置
            windowRef.value.setSize(calculatedWidth, finalHeight)
            // 再次计算位置（因为实际窗口大小可能略有不同）
            const finalPosition = {
              x: Math.max(10, viewportWidth - calculatedWidth - 20),
              y: Math.max(10, viewportHeight - finalHeight - 50)
            }
            windowRef.value.setPosition(finalPosition.x, finalPosition.y)
            
            // 更新当前位置记录
            currentPosition.value = finalPosition
            originalPosition.value = finalPosition
            
            console.log('🔄 恢复并展开完成:', {
              展开分类: allCategoryNames,
              窗口位置: finalPosition,
              窗口大小: { width: calculatedWidth, height: finalHeight }
            })
          }
        }, 100) // 100ms 延迟确保DOM更新完成
      })
    }

    const setTheme = (theme) => {
      currentTheme.value = theme
      storageManager.saveTheme(theme)
    }

    const handleSettingsChange = () => {
      // 简化：只保存基本设置，不保存状态
      const settings = {
        showSearch: showSearch.value,
        showItemDescription: showItemDescription.value,
        showItemVisibility: showItemVisibility.value,
        showItemPosition: showItemPosition.value,
        showItemActions: showItemActions.value
      }
      
      // 保存设置
      const preferences = storageManager.loadPreferences()
      Object.assign(preferences, settings)
      storageManager.savePreferences(preferences)
    }

    const resetSettings = () => {
      const defaults = storageManager.getDefaultPreferences()
      windowOpacity.value = defaults.opacity
      currentTheme.value = defaults.theme
      showSearch.value = defaults.showSearch
      showItemDescription.value = true
      showItemVisibility.value = true
      showItemPosition.value = false
      showItemActions.value = true
      
      storageManager.savePreferences(defaults)
    }

    const exportSettings = () => {
      const settings = storageManager.exportSettings()
      const dataStr = JSON.stringify(settings, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      
      const link = document.createElement('a')
      link.href = URL.createObjectURL(dataBlob)
      link.download = 'floating-navigator-settings.json'
      link.click()
    }

    const loadUserPreferences = () => {
      const preferences = storageManager.loadPreferences()
      
      windowOpacity.value = preferences.opacity || 0.95
      currentTheme.value = preferences.theme || 'light'
      showSearch.value = preferences.showSearch !== false
      showItemDescription.value = preferences.showItemDescription !== false
      showItemVisibility.value = preferences.showItemVisibility !== false
      showItemPosition.value = preferences.showItemPosition || false
      showItemActions.value = preferences.showItemActions !== false
      
      // 简化：不保存和加载expandedCategories，每次刷新都重新决定
      expandedCategories.value = []
      
      // 默认为展开状态
      isExpanded.value = true  // 简化：总是默认为展开
      isMinimized.value = false
      
      // 设置右下角位置
      const defaultPos = getDefaultExpandedPosition()
      currentPosition.value = defaultPos
      originalPosition.value = defaultPos
    }

    // 键盘快捷键
    const handleKeyDown = (e) => {
      // 注释掉 Ctrl+F 处理，让浏览器原生搜索功能正常工作
      // if (e.ctrlKey && e.key === 'f') {
      //   e.preventDefault()
      //   if (searchRef.value) {
      //     searchRef.value.focus()
      //   }
      // } else if (e.key === 'Escape') {
      if (e.key === 'Escape') {
        if (showSettings.value) {
          showSettings.value = false
        } else if (searchTerm.value) {
          searchTerm.value = ''
        } else {
          handleClose()
        }
      }
    }

    // 自动扫描
    let scanTimer = null
    const startAutoScan = () => {
      if (props.autoScan && props.scanInterval > 0) {
        scanTimer = setInterval(scanComponents, props.scanInterval)
      }
    }

    const stopAutoScan = () => {
      if (scanTimer) {
        clearInterval(scanTimer)
        scanTimer = null
      }
    }

    // 监听器 - 配置变化时重新扫描组件
    watch(() => props.organizationConfig, () => {
      console.log('🧭 组织配置发生变化，重新扫描组件')
      scanComponents()
    }, { deep: true })

    // 调试用 - 监控 expandedCategories 的变化
    watch(expandedCategories, (newVal, oldVal) => {
      console.log('🔍 expandedCategories 变化:', {
        从: oldVal,
        到: newVal,
        堆栈: new Error().stack.split('\n').slice(1, 4).join('\n')
      })
    }, { deep: true })

    // 生命周期
    onMounted(() => {
      loadUserPreferences()
      scanComponents()
      startAutoScan()
      
      // 计算位置
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      
      // 计算最小化位置（右下角）
      const miniSize = { width: 100, height: 40 }
      minimizedPosition.value = {
        x: viewportWidth - miniSize.width - 20,
        y: viewportHeight - miniSize.height - 50
      }
      
      // 如果是展开状态，设置展开位置（右下角）
      if (isExpanded.value) {
        const expandedSize = { width: 450, height: 600 } // 展开状态的预估大小
        const expandedPosition = {
          x: viewportWidth - expandedSize.width - 20,
          y: viewportHeight - expandedSize.height - 50
        }
        
        // 更新当前位置和原始位置
        currentPosition.value = expandedPosition
        originalPosition.value = expandedPosition
        
        // 设置窗口位置
        nextTick(() => {
          if (windowRef.value) {
            windowRef.value.setPosition(expandedPosition.x, expandedPosition.y)
            console.log('🚀 设置展开状态右下角位置:', expandedPosition)
          }
        })
      }
      
      document.addEventListener('keydown', handleKeyDown)
    })

    onUnmounted(() => {
      stopAutoScan()
      document.removeEventListener('keydown', handleKeyDown)
    })

    return {
      windowRef,
      searchRef,
      isLoading,
      showSettings,
      searchTerm,
      categories,
      expandedCategories,
      windowOpacity,
      currentTheme,
      showSearch,
      showItemDescription,
      showItemVisibility,
      showItemPosition,
      showItemActions,
      themes,
      minWidth,
      minHeight,
      windowSize,
      componentCount,
      windowTitle,
      initialPosition,
      filteredCategories,
      searchSuggestions,
      scanComponents,
      refreshComponents,
      handleSearch,
      handleSearchSelect,
      handleSearchClear,
      handleItemClick,
      handleItemScrollTo,
      handleCategoryToggle,
      handlePositionChange,
      handleSizeChange,
      handleOpacityChange,
      handleMinimize,
      handleClose,
      toggleSettings,
      setTheme,
      handleSettingsChange,
      resetSettings,
      exportSettings,
      handleDoubleClick,
      handleTitleClick,
      expandAllCategories,
      minimizeToCorner,
      restoreFromMinimized,
      restoreFromMinimizedAndExpand,
      isExpanded,
      isMinimized,
      currentPosition
    }
  }
}
</script>

<style lang="scss" scoped>
.navigator-title {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none; /* 防止文本选择 */
  
  &:hover {
    opacity: 0.8;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
    padding: 2px 4px;
    margin: -2px -4px;
  }
  
  &:active {
    transform: scale(0.98);
  }
}

.title-icon {
  font-size: 14px;
}

.title-text {
  font-weight: 600;
}

.title-count {
  background: #3b82f6;
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
}

.minimize-hint {
  font-size: 12px;
  color: #10b981;
  margin-left: 4px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
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
  font-size: 12px;
  color: #64748b;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #1a202c;
  }

  &.active {
    background: #3b82f6;
    color: white;
  }
}

.navigator-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.settings-panel {
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 12px;
}

.settings-section {
  margin-bottom: 16px;

  &:last-child {
    margin-bottom: 0;
  }
}

.settings-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.theme-selector {
  display: flex;
  gap: 4px;
}

.theme-button {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 6px;
  font-size: 11px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }

  &.active {
    border-color: #3b82f6;
    background: #3b82f6;
    color: white;
  }
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #374151;
  cursor: pointer;

  input[type="checkbox"] {
    margin: 0;
  }
}

.settings-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.reset-button,
.export-button {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-size: 11px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }

  &:active {
    transform: scale(0.98);
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 16px;
  color: #6b7280;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f4f6;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
}

.shortcuts-hint {
  margin-top: auto;
  padding: 8px 0;
  border-top: 1px solid #f1f5f9;
  font-size: 11px;
  color: #94a3b8;
}

.shortcuts-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.shortcut {
  kbd {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: 10px;
  }
}

// 深色主题
[data-theme="dark"] {
  .title-count {
    background: #60a5fa;
    color: #1f2937;
  }

  .settings-panel {
    border-bottom-color: #374151;
  }

  .settings-label {
    color: #f9fafb;
  }

  .theme-button {
    border-color: #4b5563;
    background: #374151;
    color: #d1d5db;

    &:hover {
      border-color: #60a5fa;
      color: #60a5fa;
    }

    &.active {
      border-color: #60a5fa;
      background: #60a5fa;
      color: #1f2937;
    }
  }

  .checkbox-item {
    color: #f9fafb;
  }

  .settings-actions {
    border-top-color: #374151;
  }

  .reset-button,
  .export-button {
    border-color: #4b5563;
    background: #374151;
    color: #d1d5db;

    &:hover {
      border-color: #60a5fa;
      color: #60a5fa;
    }
  }

  .shortcuts-hint {
    border-top-color: #374151;
    color: #9ca3af;
  }

  .shortcut kbd {
    background: #4b5563;
    border-color: #6b7280;
    color: #d1d5db;
  }
}

// 响应式适配
@media (max-width: 480px) {
  .settings-section {
    margin-bottom: 12px;
  }

  .theme-selector {
    flex-direction: column;
  }

  .theme-button {
    font-size: 10px;
    padding: 5px 6px;
  }

  .checkbox-item {
    font-size: 11px;
  }

  .settings-actions {
    flex-direction: column;
  }
}
</style>
