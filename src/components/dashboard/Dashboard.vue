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
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router'; // 导入useRoute
import ComponentRenderer from './ComponentRenderer.vue';
import DashboardConfigEditor from './DashboardConfigEditor.vue';
import axios from 'axios';
import { getApiEndpoint, getApiUrl, getServiceInfo } from '@/config/api.js'; // 导入API配置函数

export default defineComponent({
  name: 'Dashboard',
  components: {
    ComponentRenderer,
    DashboardConfigEditor
  },  setup() {
    const route = useRoute(); // 获取当前路由
    const loading = ref(true);
    const layout = ref({
      rows: 2,
      cols: 2,
      components: []
    });
    const showConfigEditor = ref(false);
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
        
        layout.value = response.data.layout;
        
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
                sector_name: update.sector_name
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
        
        // 更新所有组件的数据源参数
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
            component.dataSource = newDataSource;
          }
        });
        
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
          
          // 启动连接监控定时器
          startConnectionMonitor();
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
          
          // 停止连接监控
          stopConnectionMonitor();
          
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
    
    // 启动连接监控定时器
    const startConnectionMonitor = () => {
      stopConnectionMonitor(); // 先停止现有定时器
      
      connectionCheckTimer = setInterval(() => {
        const currentTime = Date.now();
        const timeSinceLastHeartbeat = currentTime - lastHeartbeatTime;
        
        // 如果超过30秒没有收到心跳，认为连接异常
        if (timeSinceLastHeartbeat > 30000) {
          console.warn(`⏱️ [${new Date().toISOString()}] 检测到连接超时 (${timeSinceLastHeartbeat/1000}s)，主动重连...`);
          isConnected.value = false;
          connectToUpdateStream();
        }
      }, 10000); // 每10秒检查一次
    };
    
    // 停止连接监控定时器
    const stopConnectionMonitor = () => {
      if (connectionCheckTimer) {
        clearInterval(connectionCheckTimer);
        connectionCheckTimer = null;
      }
    };    onMounted(() => {
      console.log(`⏱️ [${new Date().toISOString()}] Dashboard组件挂载，开始初始化...`);
      
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
      
      // 停止连接监控
      stopConnectionMonitor();
      
      // 关闭SSE连接
      if (eventSource.value) {
        eventSource.value.close();
        eventSource.value = null;
      }
      
      // 重置状态
      isConnected.value = false;
      isReconnecting.value = false;
    });return {
      loading,
      layout,
      showConfigEditor,
      error,           // 错误状态
      retryCount,      // 重试计数
      maxRetries,      // 最大重试次数
      isConnected,     // 连接状态
      isReconnecting,  // 重连状态
      connectionStatusText, // 连接状态文本
      gridStyle,
      getCellStyle,
      toggleConfigEditor,      updateLayout,
      getDashboardTitle,
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
}

.grid-cell {
  display: flex;
  flex-direction: column;
  overflow: visible;
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