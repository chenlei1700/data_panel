<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <h1>{{ getDashboardTitle() }}</h1>
      <div class="header-actions">
        <!-- 连接状态指示器 -->
        <div class="connection-status">
        <span class="status-dot" :class="{ 
            connected: isConnected, 
            reconnecting: isReconnecting,
            disconnected: !isConnected && !isReconnecting 
          }"></span>
          <span class="status-text">{{ connectionStatusText }}</span>
          <!-- 手动重连按钮 -->
          <button 
            v-if="!isConnected" 
            @click="forceReconnect" 
            class="reconnect-btn"
            :disabled="isReconnecting"
          >
            {{ isReconnecting ? '重连中...' : '🔄 重连' }}
          </button>
        </div>
        <button @click="toggleConfigEditor" class="config-toggle-btn">
          {{ showConfigEditor ? '隐藏配置' : '显示配置' }}
        </button>
      </div>
    </header>
    
    <!-- 加载状态 -->
    <div v-if="loading && !error" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中{{ retryCount > 0 ? ` (重试 ${retryCount}/${maxRetries})` : '' }}...</p>
    </div>
    
    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-content">
        <h3>⚠️ 加载失败</h3>
        <p class="error-message">{{ error }}</p>
        <button @click="retryLoadConfig" class="retry-btn">
          🔄 重新加载
        </button>
      </div>
    </div>
    
    <!-- 正常内容 -->
    <div v-else>
      <div class="dashboard-layout" :class="{ 'with-config': showConfigEditor }">
        <div class="dashboard-content">
          <!-- 使用 CSS Grid 替代 vue-grid-layout -->
          <div class="auto-grid" :style="gridStyle">
            <div 
              v-for="component in layout.components" 
              :key="component.id"
              class="grid-cell"
              :style="getCellStyle(component)"
              :data-component-id="component.component_id || component.id"
            >
              <div class="component-card">
                <div class="component-body" :class="`component-type-${component.type}`">
                  <component-renderer :component-config="component" />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="showConfigEditor" class="config-editor-panel">
          <dashboard-config-editor
            :config="layout"
            @update:config="updateLayout"
          />
        </div>
      </div>
      
      <!-- 悬浮导航器 -->
      <floating-navigator
        v-if="!loading && !error && navigatorConfig && navigatorConfig.enabled"
        :components="layout.components"
        :config="navigatorConfig"
        :organization-config="getNavigatorOrganization()"
        :page-key="getApiServiceName()"
        :visible="showNavigator"
        @component-click="handleNavigatorComponentClick"
        @visibility-change="handleNavigatorVisibilityChange"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router'; // 导入useRoute
import ComponentRenderer from './ComponentRenderer.vue';
import DashboardConfigEditor from './DashboardConfigEditor.vue';
import FloatingNavigator from '../floating-navigator/FloatingNavigator.vue';
import axios from 'axios';
import { getApiEndpoint, getApiUrl, getServiceInfo } from '@/config/api.js'; // 导入API配置函数

export default defineComponent({
  name: 'Dashboard',
  components: {
    ComponentRenderer,
    DashboardConfigEditor,
    FloatingNavigator
  },  setup() {
    const route = useRoute(); // 获取当前路由
    const loading = ref(true);
    const layout = ref({
      rows: 2,
      cols: 2,
      components: []
    });
    const showConfigEditor = ref(false);
    const navigatorConfig = ref(null);
    const showNavigator = ref(true);
    const error = ref(null);  // 错误状态
    const retryCount = ref(0);  // 重试计数
    const maxRetries = 5;  // 增加最大重试次数
    const isConnected = ref(false);  // SSE连接状态
    const isReconnecting = ref(false);  // 防止重复重连
    
    // 添加全局重连计数器，防止页面级重复连接
    let globalRetryCount = 0;
    const maxGlobalRetries = 10;  // 全局最大重试次数
    
    // 添加连接检查定时器
    let connectionCheckTimer = null;
    let lastHeartbeatTime = Date.now();

    // 获取当前路由对应的API服务名称
    const getApiServiceName = () => {
      return (route.meta && route.meta.apiService) || 'StockDashboard';
    };

    // 获取仪表盘标题
    const getDashboardTitle = () => {
      return (route.meta && route.meta.title) || '数据分析仪表盘';
    };    // 连接状态文本
    const connectionStatusText = computed(() => {
      if (isReconnecting.value) {
        return `重连中... (${retryCount.value}/${maxRetries})`;
      }
      return isConnected.value ? '已连接' : '未连接';
    });
    
    // 强制重连函数
    const forceReconnect = () => {
      console.log(`⏱️ [${new Date().toISOString()}] 用户手动触发重连...`);
      globalRetryCount = 0; // 重置全局计数器
      retryCount.value = 0; // 重置组件计数器
      isReconnecting.value = false; // 重置重连状态
      connectToUpdateStream();
    };

    // 计算CSS网格样式
    const gridStyle = computed(() => {
      return {
        gridTemplateColumns: `repeat(${layout.value.cols}, 1fr)`,
        gridAutoRows: 'auto',
        gap: '15px'
      };
    });      // 计算每个单元格的样式
    const getCellStyle = (component) => {
      const style = {
        gridColumn: `${component.position.col + 1} / span ${component.position.colSpan}`,
        gridRow: `${component.position.row + 1} / span ${component.position.rowSpan}`,
      };
      
      // 根据配置中的height属性设置高度，如果没有则使用默认值
      if (component.height) {
        style.height = component.height;
        style.minHeight = component.height;
      } else {
        // 默认高度：图表类型450px，表格类型150px
        style.minHeight = component.type === 'chart' ? '450px' : '150px';
      }
      
      return style;
    };

    const loadDashboardConfig = async () => {
      try {
        const startTime = performance.now();
        console.log(`⏱️ [${new Date().toISOString()}] 开始加载仪表盘配置`);
        
        error.value = null;  // 清除之前的错误
        const serviceName = getApiServiceName();
        console.log(`🔄 加载 ${serviceName} 的仪表盘配置...`);
        
        // 使用动态API配置
        const configUrl = getApiEndpoint(serviceName, 'dashboardConfig');
        console.log(`📡 请求配置URL: ${configUrl}`);
        console.log(`🛠️ 服务信息:`, getServiceInfo(serviceName));
        
        const requestStartTime = performance.now();
        console.log(`⏱️ [${new Date().toISOString()}] 开始发送HTTP请求`);
        
        const response = await axios.get(configUrl, {
          timeout: 10000  // 添加超时设置
        });
        
        const requestEndTime = performance.now();
        console.log(`⏱️ [${new Date().toISOString()}] HTTP请求完成，耗时: ${(requestEndTime - requestStartTime).toFixed(2)}ms`);
        console.log(`✅ 配置响应状态: ${response.status}`);
        console.log(`📊 配置数据:`, response.data);        
        const processingStartTime = performance.now();
        console.log(`⏱️ [${new Date().toISOString()}] 开始处理配置数据`);
        
        // 处理layout数据并去重组件
        const layoutData = response.data.layout;
        if (layoutData && layoutData.components) {
          console.log('🔍 原始组件列表:', layoutData.components.map(c => ({
            id: c.component_id || c.id,
            title: c.title,
            type: c.type
          })))
          
          // 去重组件：根据component_id去重，保留第一个
          const seenIds = new Set();
          const uniqueComponents = [];
          
          layoutData.components.forEach(component => {
            const componentId = component.component_id || component.id;
            if (!seenIds.has(componentId)) {
              seenIds.add(componentId);
              uniqueComponents.push(component);
            } else {
              console.warn(`🔍 发现重复组件配置，已忽略: ${componentId}`);
            }
          });
          
          layoutData.components = uniqueComponents;
          console.log(`🔍 组件去重完成，原始: ${response.data.layout.components.length}，去重后: ${uniqueComponents.length}`);
          console.log('🔍 去重后组件列表:', uniqueComponents.map(c => ({
            id: c.component_id || c.id,
            title: c.title,
            type: c.type
          })))
        }
        
        layout.value = layoutData;
        
        console.log('🔍 后端响应数据结构:', {
          hasFloatingNavigator: !!response.data.floating_navigator,
          hasLayoutNavigatorOrganization: !!(response.data.layout?.navigator_organization),
          floatingNavigator: response.data.floating_navigator,
          layoutNavigatorOrganization: response.data.layout?.navigator_organization
        });
        
        // 加载悬浮导航器配置
        if (response.data.floating_navigator) {
          navigatorConfig.value = {
            ...response.data.floating_navigator,
            navigator_organization: response.data.layout?.navigator_organization || {}
          };
          console.log(`🧭 导航器配置加载成功:`, navigatorConfig.value);
        } else {
          console.log(`🧭 未找到导航器配置，使用默认配置`);
          navigatorConfig.value = {
            ...getDefaultNavigatorConfig(),
            navigator_organization: response.data.layout?.navigator_organization || {}
          };
        }
        
        // 更新组件数据源URL为正确的服务地址
        layout.value.components.forEach(component => {
          if (component.dataSource && component.dataSource.startsWith('/api/')) {
            const newDataSource = getApiUrl(serviceName) + component.dataSource;
            console.log(`🔗 更新组件 ${component.id} 数据源: ${component.dataSource} → ${newDataSource}`);
            component.dataSource = newDataSource;
          }
        });
        
        const processingEndTime = performance.now();
        console.log(`⏱️ [${new Date().toISOString()}] 配置数据处理完成，耗时: ${(processingEndTime - processingStartTime).toFixed(2)}ms`);
        
        loading.value = false;
        retryCount.value = 0;  // 重置重试计数
        
        const totalTime = performance.now();
        console.log(`⏱️ [${new Date().toISOString()}] 整个配置加载完成，总耗时: ${(totalTime - startTime).toFixed(2)}ms`);
        console.log(`⏱️ [${new Date().toISOString()}]✅ ${serviceName} 配置加载成功，最终服务信息:`, getServiceInfo(serviceName));
        
      } catch (err) {
        console.error('加载仪表盘配置失败:', err);
        error.value = err.message || '加载配置失败';
        
        // 重试逻辑
        if (retryCount.value < maxRetries) {
          retryCount.value++;
          console.log(`${retryCount.value}/${maxRetries} 次重试加载配置...`);
          setTimeout(() => {
            loadDashboardConfig();
          }, 2000 * retryCount.value); // 递增延迟
          return;
        }
        
        // 超过最大重试次数，使用默认配置
        const serviceName = getApiServiceName();
        layout.value = {
          rows: 2,
          cols: 2,
          components: [
            {
              id: "chart1",
              type: "chart",
              dataSource: getApiUrl(serviceName, "/api/chart-data/stock-line-chart"),
              title: serviceName === 'StockDashboard_strong' ? "强势股票涨幅折线图" : "股票涨幅折线图",
              position: {row: 0, col: 0, rowSpan: 1, colSpan: 1}
            },
            {
              id: "table1",
              type: "table",
              dataSource: getApiUrl(serviceName, "/api/table-data/stocks"),
              title: serviceName === 'StockDashboard_strong' ? "强势股票数据表" : "股票数据表",
              position: {row: 1, col: 0, rowSpan: 1, colSpan: 2}
            }
          ]
        };
        loading.value = false;
      }
    };

    // 手动重试函数
    const retryLoadConfig = () => {
      retryCount.value = 0;
      error.value = null;
      loading.value = true;
      loadDashboardConfig();
    };
    
    const toggleConfigEditor = () => {
      showConfigEditor.value = !showConfigEditor.value;
    };
    
    const updateLayout = (newLayout) => {
      layout.value = newLayout;
    };

    // 添加SSE事件源引用
    const eventSource = ref(null);    // 处理接收到的更新
    const handleDashboardUpdate = (update) => {
      console.log(`⏱️ [${new Date().toISOString()}] 接收到更新请求:`, update);
      
      // 如果是配置更新或强制刷新，重新加载配置
      if (update.action === 'reload_config' || update.action === 'force_refresh') {
        console.log(`⏱️ [${new Date().toISOString()}] 检测到配置更新，重新加载仪表盘配置...`);
        
        loadDashboardConfig().then(() => {
          // 配置加载完成后，通知所有组件刷新数据
          console.log(`⏱️ [${new Date().toISOString()}] 配置重新加载完成，通知组件刷新数据...`);
          setTimeout(() => {
            window.dispatchEvent(new CustomEvent('dashboard-config-updated', { 
              detail: { 
                action: 'reload_config',
                timestamp: Date.now(),
                sector_name: update.sector_name,
                selected_date: update.selected_date
              }
            }));
          }, 100);
        });
        return;
      }
      
      // 处理板块更新请求
      if (update.sector_name || (update.params && update.params.sectors)) {
        const sectorName = update.sector_name || update.params.sectors;
        console.log(`⏱️ [${new Date().toISOString()}] 处理板块更新请求: ${sectorName}`);
        
        // 创建新的layout对象，而不是直接修改现有的
        const newLayout = {
          ...layout.value,
          components: layout.value.components.map(component => {
            if (component.type === 'chart' || component.type === 'table') {
              const baseUrl = component.dataSource.split('?')[0];
              const params = new URLSearchParams();
              
              // 获取当前URL的参数
              const currentUrlParts = component.dataSource.split('?');
              if (currentUrlParts.length > 1) {
                const currentParams = new URLSearchParams(currentUrlParts[1]);
                // 保留现有参数
                currentParams.forEach((value, key) => {
                  params.set(key, value);
                });
              }
              
              // 添加组件ID参数
              params.set('componentId', component.id);
              
              // 更新板块参数
              if (sectorName) {
                params.set('sectors', sectorName);
                params.set('sector_name', sectorName);
              }
              
              // 添加时间戳防止缓存
              params.set('_t', Date.now().toString());
              
              const newDataSource = `${baseUrl}?${params.toString()}`;
              console.log(`⏱️ [${new Date().toISOString()}] 更新组件 ${component.id} 数据源:`, newDataSource);
              
              return {
                ...component,
                dataSource: newDataSource
              };
            }
            return component;
          })
        };
        
        // 使用nextTick确保DOM更新完成
        layout.value = newLayout;
        
        // 通知组件刷新数据
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('dashboard-update', { 
            detail: {
              ...update,
              sector_name: sectorName,
              timestamp: Date.now()
            }
          }));
        }, 100);
        
        return;
      }
      
      // 原有的参数更新逻辑（保留兼容性）
      if (!update || !update.params) return;
      
      const serviceName = getApiServiceName();
      
      // 更新所有组件
      layout.value.components.forEach(component => {
        if (component.type === 'chart' || component.type === 'table') {
          const baseUrl = component.dataSource.split('?')[0];
          const params = new URLSearchParams();
          
          // 获取当前URL的参数
          const currentUrlParts = component.dataSource.split('?');
          if (currentUrlParts.length > 1) {
            const currentParams = new URLSearchParams(currentUrlParts[1]);
            // 保留现有参数
            currentParams.forEach((value, key) => {
              params.set(key, value);
            });
          }
          
          // 添加新的更新参数
          Object.entries(update.params).forEach(([key, value]) => {
            params.set(key, value);
          });
          
          component.dataSource = `${baseUrl}?${params.toString()}`;
        }
      });

      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('dashboard-update', { 
          detail: update
        }));
      }, 100);
    };    // 连接到SSE流 - 无间断重连机制
    const connectToUpdateStream = () => {
      const serviceName = getApiServiceName();
      console.log(`⏱️ [${new Date().toISOString()}] 尝试连接到 ${serviceName} SSE流...`);
      
      // 如果已有连接，先关闭
      if (eventSource.value) {
        console.log('关闭现有SSE连接');
        eventSource.value.close();
        eventSource.value = null;
      }
      
      // 检查全局重试限制
      if (globalRetryCount >= maxGlobalRetries) {
        console.warn(`SSE连接已达全局重试上限 (${maxGlobalRetries})，停止重连`);
        return;
      }
      
      isConnected.value = false;  // 重置连接状态
      
      try {
        // 使用动态API配置获取SSE URL
        const sseUrl = getApiEndpoint(serviceName, 'updates');
        console.log(`SSE URL: ${sseUrl}`);
        eventSource.value = new EventSource(sseUrl);
        
        // 连接成功处理
        eventSource.value.onopen = () => {
          console.log(`⏱️ [${new Date().toISOString()}] ${serviceName} SSE连接已建立`);
          isConnected.value = true;
          retryCount.value = 0;  // 重置组件级重连计数器
          globalRetryCount = 0;  // 重置全局重连计数器
          isReconnecting.value = false;
          lastHeartbeatTime = Date.now();  // 更新心跳时间
        };
        
        // 消息处理
        eventSource.value.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            // 处理心跳消息，保持连接活跃
            if (data.type === 'heartbeat') {
              lastHeartbeatTime = Date.now();
              console.log(`⏱️ [${new Date().toISOString()}] 接收到心跳消息，连接活跃`);
              return;
            }
            
            // 处理连接确认消息
            if (data.type === 'connection_established') {
              console.log(`⏱️ [${new Date().toISOString()}] 收到连接确认:`, data.client_id);
              return;
            }
            
            // 处理实际的更新消息
            handleDashboardUpdate(data);
          } catch (error) {
            console.error('处理SSE消息失败:', error);
          }
        };
        
        // 错误处理 - 实现无间断重连
        eventSource.value.onerror = (error) => {
          console.error(`⏱️ [${new Date().toISOString()}] ${serviceName} SSE连接错误:`, error);
          isConnected.value = false;
          
          // 检查是否已经在重连，避免重复重连
          if (isReconnecting.value) {
            console.log('已有重连进程在运行，跳过此次重连');
            return;
          }
          
          // 增加重连计数
          retryCount.value++;
          globalRetryCount++;
          
          // 检查重连次数限制
          if (globalRetryCount >= maxGlobalRetries) {
            console.warn(`SSE连接重试次数已达全局上限 (${maxGlobalRetries})，停止重连`);
            return;
          }
          
          isReconnecting.value = true;
          
          // 计算重连延迟 - 指数退避策略
          const baseDelay = 2000; // 基础延迟2秒
          const maxDelay = 30000; // 最大延迟30秒
          const delay = Math.min(baseDelay * Math.pow(1.5, retryCount.value - 1), maxDelay);
          
          console.log(`SSE重连尝试 ${retryCount.value}/${maxRetries} (全局: ${globalRetryCount}/${maxGlobalRetries})，${delay/1000}秒后重试...`);
          
          setTimeout(() => {
            isReconnecting.value = false;
            connectToUpdateStream();
          }, delay);
        };
        
      } catch (error) {
        console.error('创建SSE连接时出错:', error);
        isConnected.value = false;
        
        // 即使创建连接失败，也要尝试重连
        if (globalRetryCount < maxGlobalRetries) {
          setTimeout(() => {
            connectToUpdateStream();
          }, 5000);
        }
      }
    };
    
    // 连接到SSE流 - 无间断重连机制
    
    // 应用恢复的板块选择
    const applyRestoredSector = (sectorName) => {
      try {
        console.log(`🔄 开始应用恢复的板块选择: ${sectorName}`);
        let applied = false;
        
        // 方法1: 尝试设置DOM选择器的值
        const possibleSelectors = [
          'select[id*="sector"]',
          'select[id*="plate"]',
          'input[id*="sector"]', 
          'input[id*="plate"]',
          '.sector-selector select',
          '.plate-selector select',
          '[data-component="sector-selector"] select',
          '[data-component="plate-selector"] select'
        ];
        
        for (const selectorPattern of possibleSelectors) {
          const elements = document.querySelectorAll(selectorPattern);
          elements.forEach(selector => {
            // 检查选项中是否有这个板块
            if (selector.tagName.toLowerCase() === 'select') {
              const options = selector.querySelectorAll('option');
              for (const option of options) {
                if (option.value === sectorName || option.textContent.trim() === sectorName) {
                  selector.value = option.value;
                  // 触发change事件
                  selector.dispatchEvent(new Event('change', { bubbles: true }));
                  selector.dispatchEvent(new Event('input', { bubbles: true }));
                  console.log(`✅ 已通过选择器 ${selectorPattern} 恢复板块选择: ${sectorName}`);
                  applied = true;
                  break;
                }
              }
            } else if (selector.tagName.toLowerCase() === 'input') {
              selector.value = sectorName;
              selector.dispatchEvent(new Event('change', { bubbles: true }));
              selector.dispatchEvent(new Event('input', { bubbles: true }));
              console.log(`✅ 已通过输入框恢复板块选择: ${sectorName}`);
              applied = true;
            }
          });
          
          if (applied) break;
        }
        
        // 方法2: 如果DOM方式失败，尝试通过SSE发送更新消息
        if (!applied) {
          console.log(`🔄 DOM方式失败，尝试通过SSE发送板块更新消息`);
          
          // 模拟服务器端的板块更新消息
          const updateMessage = {
            action: 'restore_sector',
            sector_name: sectorName,
            timestamp: Date.now()
          };
          
          // 直接调用handleDashboardUpdate处理
          handleDashboardUpdate(updateMessage);
          applied = true;
        }
        
        if (!applied) {
          console.warn(`⚠️ 无法应用恢复的板块选择: ${sectorName}`);
        }
        
      } catch (error) {
        console.warn('应用恢复的板块选择时出错:', error);
      }
    };
    
    // 应用恢复的日期选择
    const applyRestoredDate = (dateValue) => {
      try {
        console.log(`📅 开始应用恢复的日期选择: ${dateValue}`);
        let applied = false;
        
        // 尝试设置各种可能的日期选择器
        const possibleSelectors = [
          'input[type="date"]',
          'input[id*="date"]',
          '.date-selector input',
          '[data-component="date-selector"] input'
        ];
        
        for (const selectorPattern of possibleSelectors) {
          const elements = document.querySelectorAll(selectorPattern);
          elements.forEach(selector => {
            selector.value = dateValue;
            // 触发change事件
            selector.dispatchEvent(new Event('change', { bubbles: true }));
            selector.dispatchEvent(new Event('input', { bubbles: true }));
            console.log(`✅ 已通过选择器 ${selectorPattern} 恢复日期选择: ${dateValue}`);
            applied = true;
          });
          
          if (applied) break;
        }
        
        if (!applied) {
          console.warn(`⚠️ 无法应用恢复的日期选择: ${dateValue}`);
        }
        
      } catch (error) {
        console.warn('应用恢复的日期选择时出错:', error);
      }
    };
    
    // ===== SSE连接管理功能 =====
    
    onMounted(() => {
      console.log(`⏱️ [${new Date().toISOString()}] Dashboard组件挂载，开始初始化...`);
      
      // � 在开发环境中加载调试工具
      if (process.env.NODE_ENV === 'development') {
        try {
          // 直接在控制台添加调试功能，避免动态导入问题
          console.log('🔧 会话状态管理调试工具已加载');
          
          // 添加调试函数到window对象
          window.SessionDebugger = {
            inspectSelectorElements() {
              console.log('🔍 检查板块选择器...');
              const possibleSelectors = [
                'select[id*="sector"]', 'select[id*="plate"]', 
                'input[id*="sector"]', 'input[id*="plate"]',
                '.sector-selector select', '.plate-selector select'
              ];
              
              let found = false;
              possibleSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                  console.log(`✅ 找到选择器: ${selector}`);
                  elements.forEach((el, index) => {
                    console.log(`  - 元素 ${index + 1}:`, {
                      tagName: el.tagName, id: el.id, className: el.className, value: el.value,
                      options: el.tagName === 'SELECT' ? Array.from(el.options).map(opt => opt.value) : null
                    });
                  });
                  found = true;
                }
              });
              
              if (!found) console.log('❌ 未找到任何板块选择器');
              return found;
            },
            
            async testSaveState() {
              console.log('💾 测试保存状态...');
              if (window.sessionStateManager) {
                try {
                  const testState = {
                    selected_sector: "航运概念",
                    selected_date: new Date().toISOString().split('T')[0],
                    component_states: { test: { component_type: 'test', last_interaction: Date.now() } },
                    page_url: window.location.href, timestamp: Date.now()
                  };
                  
                  console.log('发送状态:', testState);
                  const result = await window.sessionStateManager.saveUserState(testState);
                  console.log('保存结果:', result);
                  return result;
                } catch (error) {
                  console.error('保存失败:', error);
                  return false;
                }
              } else {
                console.error('❌ sessionStateManager 未找到');
                return false;
              }
            },
            
            async testRestoreState() {
              console.log('🔄 测试恢复状态...');
              if (window.sessionStateManager) {
                try {
                  const state = await window.sessionStateManager.getUserState();
                  console.log('恢复的状态:', state);
                  return state;
                } catch (error) {
                  console.error('恢复失败:', error);
                  return null;
                }
              } else {
                console.error('❌ sessionStateManager 未找到');
                return null;
              }
            }
          };
          
          console.log('🔧 调试工具: SessionDebugger.inspectSelectorElements(), SessionDebugger.testSaveState(), SessionDebugger.testRestoreState()');
          
        } catch (error) {
          console.warn('调试工具初始化失败:', error);
        }
      }
      
      // �🔄 会话状态恢复功能 - 在配置加载前先尝试恢复状态
      console.log(`🔄 [${new Date().toISOString()}] 检查是否需要恢复用户状态...`);
      
      // 立即加载配置，不等待 SSE 连接
      loadDashboardConfig();
      
      // 延迟启动SSE连接，确保主要界面先加载
      setTimeout(() => {
        console.log(`⏱️ [${new Date().toISOString()}] 开始建立SSE连接...`);
        connectToUpdateStream();
      }, 1000);
      
      // 添加页面可见性检测
      const handleVisibilityChange = () => {
        if (document.visibilityState === 'visible') {
          console.log(`⏱️ [${new Date().toISOString()}] 页面重新获得焦点，检查SSE连接状态...`);
          
          // 页面重新可见时，检查连接状态
          if (!isConnected.value && !isReconnecting.value) {
            console.log('页面重新可见，恢复SSE连接...');
            globalRetryCount = 0; // 重置全局重试计数
            connectToUpdateStream();
          }
        } else {
          console.log(`⏱️ [${new Date().toISOString()}] 页面失去焦点`);
        }
      };
      
      // 添加网络状态检测
      const handleOnline = () => {
        console.log(`⏱️ [${new Date().toISOString()}] 网络重新连接，恢复SSE连接...`);
        if (!isConnected.value && !isReconnecting.value) {
          globalRetryCount = 0;
          connectToUpdateStream();
        }
      };
      
      const handleOffline = () => {
        console.log(`⏱️ [${new Date().toISOString()}] 网络断开连接`);
        isConnected.value = false;
      };
      
      // 绑定事件监听器
      document.addEventListener('visibilitychange', handleVisibilityChange);
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);
      
      // 在组件卸载时清理事件监听器
      onBeforeUnmount(() => {
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      });
    });
    
    onBeforeUnmount(() => {
      console.log(`⏱️ [${new Date().toISOString()}] Dashboard组件卸载，清理SSE连接...`);
      
      // 关闭SSE连接
      if (eventSource.value) {
        eventSource.value.close();
        eventSource.value = null;
      }
      
      // 重置状态
      isConnected.value = false;
      isReconnecting.value = false;
    });
    
    // 获取默认导航器配置
    const getDefaultNavigatorConfig = () => {
      return {
        enabled: true,
        default_position: { x: 20, y: 100 },
        default_opacity: 0.9,
        default_size: { width: 320, height: 450 },
        organization_structure: {},
        uncategorized_section: {
          title: '其他组件',
          icon: '📦',
          order: 99,
          collapsible: true,
          description: '未分类的组件'
        },
        settings: {
          enable_search: true,
          enable_tooltips: true,
          enable_keyboard_shortcuts: true,
          auto_collapse_categories: false,
          remember_user_preferences: true
        }
      };
    };
    
    // 处理导航器组件点击
    const handleNavigatorComponentClick = (component) => {
      console.log(`🧭 导航器组件点击:`, component);
      // 可以在这里添加额外的处理逻辑，比如高亮组件等
    };
    
    // 处理导航器可见性变化
    const handleNavigatorVisibilityChange = (visible) => {
      showNavigator.value = visible;
      console.log(`🧭 导航器可见性变化:`, visible);
    };
    
    // 切换导航器显示/隐藏
    const toggleNavigator = () => {
      showNavigator.value = !showNavigator.value;
    };
    
    // 获取导航器组织结构配置
    const getNavigatorOrganization = () => {
      const serviceName = getApiServiceName();
      const fullConfig = navigatorConfig.value || {};
      
      console.log('🗂️ 获取导航组织配置:', {
        serviceName,
        hasNavigatorConfig: !!navigatorConfig.value,
        hasNavigatorOrganization: !!(fullConfig.navigator_organization),
        navigatorOrganization: fullConfig.navigator_organization,
        navigatorOrganizationKeys: Object.keys(fullConfig.navigator_organization || {}),
        fullConfig: fullConfig
      });
      
      // 查找页面特定的组织结构
      if (fullConfig.navigator_organization) {
        const result = {
          categories: Object.keys(fullConfig.navigator_organization).map(categoryName => {
            const categoryConfig = fullConfig.navigator_organization[categoryName];
            return {
              name: categoryName,
              icon: categoryConfig.icon || '📂',
              order: categoryConfig.order || 0,
              components: categoryConfig.components || [],
              collapsible: categoryConfig.collapsible !== false,
              description: categoryConfig.description || '',
              color: categoryConfig.color
            };
          }).sort((a, b) => a.order - b.order)
        };
        
        console.log('🗂️ 生成的导航分类配置:', result);
        return result;
      }
      
      return { categories: [] };
    };
    
    return {
      loading,
      layout,
      showConfigEditor,
      error,           // 错误状态
      retryCount,      // 重试计数
      maxRetries,      // 最大重试次数
      isConnected,     // 连接状态
      isReconnecting,  // 重连状态
      connectionStatusText, // 连接状态文本
      
      // 导航器相关
      navigatorConfig,
      showNavigator,
      handleNavigatorComponentClick,
      handleNavigatorVisibilityChange,
      toggleNavigator,
      getNavigatorOrganization,  // 新增导航器组织结构配置
      
      gridStyle,
      getCellStyle,
      toggleConfigEditor,
      updateLayout,
      getDashboardTitle,
      getApiServiceName,   // 添加缺失的函数
      retryLoadConfig,  // 重试函数
      forceReconnect    // 强制重连函数
    };
  }
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 98%; /* 从1600px改为百分比 */
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #f44336;
  transition: background-color 0.3s;
}

.status-dot.connected {
  background-color: #4caf50;
}

.status-dot.reconnecting {
  background-color: #ff9800;
  animation: pulse 1s infinite;
}

.status-dot.disconnected {
  background-color: #f44336;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.status-text {
  white-space: nowrap;
}

.reconnect-btn {
  margin-left: 8px;
  padding: 4px 8px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  transition: background-color 0.3s;
}

.reconnect-btn:hover:not(:disabled) {
  background-color: #f57c00;
}

.reconnect-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.config-toggle-btn {
  padding: 8px 16px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.config-toggle-btn:hover {
  background-color: #1976D2;
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196F3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 50px;
}

.error-content {
  text-align: center;
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #f44336;
  max-width: 500px;
}

.error-content h3 {
  color: #f44336;
  margin: 0 0 15px 0;
  font-size: 20px;
}

.error-message {
  color: #666;
  margin: 15px 0;
  line-height: 1.6;
}

.retry-btn {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.retry-btn:hover {
  background-color: #1976D2;
}

.dashboard-layout {
  display: flex;
  gap: 20px;
}

.dashboard-layout.with-config .dashboard-content {
  width: 70%;
}

.dashboard-content {
  width: 100%;
  transition: width 0.3s;
  overflow: visible;
}

.config-editor-panel {
  width: 30%;
  height: calc(100vh - 140px);
  overflow-y: auto;
}

/* CSS Grid 样式 */
.auto-grid {
  display: grid;
  width: 100%;
  /* 启用硬件加速 */
  transform: translateZ(0);
  /* 优化滚动性能 */
  contain: layout style paint;
}

.grid-cell {
  display: flex;
  flex-direction: column;
  overflow: visible;
  /* 启用硬件加速 */
  transform: translateZ(0);
  /* 优化渲染性能 */
  contain: layout style paint;
  /* 减少重排重绘 */
  will-change: transform;
}

.component-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.component-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.component-header {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  background-color: #f9f9f9;
}

.component-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.component-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 根据组件类型设置不同样式 */
.component-type-chart {
  padding: 10px;
  min-height: 450px;
}

.component-type-table {
  padding: 0;
  height: auto;
  min-height: 150px; /* 设置一个最小高度，避免初始加载时太小 */
  flex: 1; /* 确保表格在容器中能够伸展 */
  display: flex;
  flex-direction: column;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .dashboard-layout {
    flex-direction: column;
  }
  
  .dashboard-layout.with-config .dashboard-content {
    width: 100%;
  }
  
  .config-editor-panel {
    width: 100%;
    height: auto;
    max-height: 500px;
  }
  
  .auto-grid {
    grid-template-columns: 1fr !important; /* 在小屏幕上强制单列 */
  }
  
  .grid-cell {
    grid-column: 1 !important;
  }
}
</style>

<!-- 导入悬浮导航器样式 -->
<style src="@/assets/styles/floating-navigator/floating-navigator.scss" lang="scss"></style>