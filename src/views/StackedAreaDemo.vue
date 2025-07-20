<!-- 堆叠面积图演示组件 -->
<!-- 基于项目配置驱动的仪表盘系统 -->
<template>
  <div class="stacked-area-demo-wrapper">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>📊 堆叠面积图组件演示</h1>
      <p class="description">
        展示堆叠面积图组件的各种功能和配置选项，完全基于项目配置驱动
      </p>
      <div class="service-info">
        <span class="service-badge">📊 堆叠面积图演示</span>
        <span class="port-badge">端口: 5005</span>
      </div>
    </div>

    <!-- 仪表盘容器 -->
    <div v-if="dashboardConfig" class="dashboard-container">
      <Dashboard :config="dashboardConfig" />
    </div>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在从端口 5005 加载演示配置...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <p class="error-message">{{ error }}</p>
      <button @click="loadDashboardConfig" class="retry-button">重新加载</button>
    </div>

    <!-- 组件使用说明 -->
    <div class="usage-guide">
      <h2>🛠️ 基于配置驱动的开发模式</h2>
      
      <div class="guide-section">
        <h3>📋 配置文件驱动</h3>
        <p>该演示页面完全由 <code>project-config.json</code> 配置文件驱动：</p>
        <div class="config-example">
          <pre><code>{
  "services": [
    {
      "id": "stacked_area_demo",
      "name": "堆叠面积图演示",
      "port": 5005,
      "serverFile": "stacked_area_demo_server.py",
      "component": "StackedAreaDemo"
    }
  ]
}</code></pre>
        </div>
      </div>

      <div class="guide-section">
        <h3>🌐 API 端点</h3>
        <div class="endpoint-grid">
          <div class="endpoint-item">
            <strong>GET /api/dashboard-config</strong>
            <span>获取仪表盘配置</span>
          </div>
          <div class="endpoint-item">
            <strong>GET /api/chart-data/stacked-area-basic</strong>
            <span>基础堆叠面积图数据</span>
          </div>
          <div class="endpoint-item">
            <strong>GET /api/chart-data/stacked-area-with-table</strong>
            <span>带表格的堆叠面积图数据</span>
          </div>
          <div class="endpoint-item">
            <strong>GET /api/chart-data/stacked-area-trend</strong>
            <span>趋势对比数据</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';
import Dashboard from '@/components/dashboard/Dashboard.vue';
import { getApiEndpoint } from '@/config/api';

export default defineComponent({
  name: 'StackedAreaDemo',
  components: {
    Dashboard
  },
  setup() {
    const dashboardConfig = ref(null);
    const loading = ref(true);
    const error = ref(null);

    const loadDashboardConfig = async () => {
      loading.value = true;
      error.value = null;

      try {
        console.log('从堆叠面积图演示服务加载仪表盘配置...');
        
        // 使用API配置系统获取正确的端点URL (端口5005)
        const apiUrl = getApiEndpoint('stacked_area_demo', 'dashboardConfig');
        console.log('API端点URL:', apiUrl);
        
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        dashboardConfig.value = data;
        
        console.log('仪表盘配置加载成功:', data);
        loading.value = false;
      } catch (err) {
        console.error('加载仪表盘配置失败:', err);
        error.value = `加载配置失败: ${err.message}. 请确保堆叠面积图演示服务器(端口5005)正在运行。`;
        loading.value = false;
      }
    };

    onMounted(() => {
      console.log('StackedAreaDemo 组件挂载（配置驱动版本）');
      loadDashboardConfig();
    });

    return {
      dashboardConfig,
      loading,
      error,
      loadDashboardConfig
    };
  }
});
</script>

<style scoped>
.stacked-area-demo-wrapper {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.page-header h1 {
  margin: 0 0 15px 0;
  font-size: 2.5em;
  font-weight: 700;
}

.description {
  font-size: 1.1em;
  margin: 0 0 20px 0;
  opacity: 0.9;
  line-height: 1.6;
}

.service-info {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.service-badge, .port-badge {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.dashboard-container {
  margin-bottom: 40px;
}

.loading-container, .error-container {
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 15px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3em;
  margin-bottom: 15px;
}

.error-message {
  color: #f44336;
  font-size: 1.1em;
  margin-bottom: 25px;
  line-height: 1.6;
}

.retry-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background-color: #45a049;
}

.usage-guide {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 15px rgba(0,0,0,0.1);
}

.usage-guide h2 {
  color: #333;
  margin-bottom: 25px;
  font-size: 2em;
  text-align: center;
}

.guide-section {
  margin-bottom: 35px;
  padding-bottom: 25px;
  border-bottom: 1px solid #e0e0e0;
}

.guide-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.guide-section h3 {
  color: #4CAF50;
  margin-bottom: 15px;
  font-size: 1.4em;
}

.guide-section p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.config-example {
  background-color: #f8f9fa;
  border-left: 4px solid #4CAF50;
  padding: 20px;
  border-radius: 6px;
  overflow-x: auto;
}

.config-example pre {
  margin: 0;
  font-size: 0.9em;
  line-height: 1.4;
}

.config-example code {
  color: #2c3e50;
}

.endpoint-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 15px;
}

.endpoint-item {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #2196F3;
}

.endpoint-item strong {
  display: block;
  color: #2196F3;
  font-family: 'Courier New', monospace;
  margin-bottom: 5px;
}

.endpoint-item span {
  color: #666;
  font-size: 0.9em;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stacked-area-demo-wrapper {
    padding: 15px;
  }
  
  .page-header {
    padding: 20px;
  }
  
  .page-header h1 {
    font-size: 2em;
  }
  
  .service-info {
    flex-direction: column;
    align-items: center;
  }
  
  .endpoint-grid {
    grid-template-columns: 1fr;
  }
  
  .usage-guide {
    padding: 20px;
  }
}
</style>
