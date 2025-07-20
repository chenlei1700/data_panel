<!-- 基于项目配置的堆叠面积图演示页面 -->
<template>
  <div class="stacked-area-demo-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>{{ pageTitle || '📊 堆叠面积图组件演示' }}</h1>
      <p class="description">
        {{ pageDescription || '展示新增的堆叠面积图组件，支持三维数据可视化：X轴、Y轴累积值、以及每个X点的字典数据分解' }}
      </p>
    </div>

    <!-- 使用配置驱动的仪表盘 -->
    <div v-if="dashboardConfig" class="dashboard-container">
      <Dashboard :config="dashboardConfig" />
    </div>

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载演示配置...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="loadDashboardConfig" class="retry-button">重试</button>
    </div>

    <!-- 功能说明区域 -->
    <div class="features-section">
      <h2>✨ 组件特性详解</h2>
      
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">📈</div>
          <h3>三维数据可视化</h3>
          <p>将三维数据（X轴：时间/类别，Y轴：累积值，Z轴：数据系列）转换为直观的堆叠面积图</p>
          <div class="feature-details">
            <span class="detail-badge">自动累积计算</span>
            <span class="detail-badge">平滑过渡动画</span>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">📋</div>
          <h3>可选表格显示</h3>
          <p>在图表上方可显示表格，展示每个X轴点对应的汇总数据，支持颜色映射</p>
          <div class="feature-details">
            <span class="detail-badge">动态颜色</span>
            <span class="detail-badge">数据汇总</span>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🎨</div>
          <h3>自定义配置</h3>
          <p>支持自定义颜色方案、图表标题、表格样式等多种个性化配置选项</p>
          <div class="feature-details">
            <span class="detail-badge">颜色主题</span>
            <span class="detail-badge">样式定制</span>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">🖱️</div>
          <h3>丰富交互功能</h3>
          <p>支持鼠标悬停详情显示、图表缩放、平移等交互操作，提升用户体验</p>
          <div class="feature-details">
            <span class="detail-badge">悬停提示</span>
            <span class="detail-badge">缩放平移</span>
          </div>
        </div>
      </div>
    </div>

    <!-- API 使用示例 -->
    <div class="api-section">
      <h2>🔧 API 使用示例</h2>
      
      <div class="api-examples">
        <div class="api-example">
          <h3>基础用法</h3>
          <pre><code>// 组件配置
{
  "id": "myStackedChart",
  "type": "stackedAreaChart",
  "dataSource": "/api/chart-data/stacked-area-basic",
  "title": "我的堆叠面积图"
}

// API 响应格式
{
  "stackedAreaData": {
    "data": {
      "09:30": {"系列1": 10, "系列2": 20},
      "10:00": {"系列1": 15, "系列2": 25}
    },
    "keyOrder": ["系列1", "系列2"],
    "colors": ["#FF6B6B", "#4ECDC4"]
  },
  "xAxisValues": ["09:30", "10:00"],
  "tableData": {
    "09:30": "30亿",
    "10:00": "40亿" 
  }
}</code></pre>
        </div>

        <div class="api-example">
          <h3>可用端点</h3>
          <ul class="endpoint-list">
            <li><code>GET /api/chart-data/stacked-area-basic</code> - 基础堆叠面积图数据</li>
            <li><code>GET /api/chart-data/stacked-area-with-table</code> - 带表格的堆叠面积图数据</li>
            <li><code>GET /api/chart-data/stacked-area-trend</code> - 趋势对比数据</li>
            <li><code>GET /api/dashboard-config</code> - 获取仪表盘配置</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';
import Dashboard from '@/components/dashboard/Dashboard.vue';

export default defineComponent({
  name: 'StackedAreaDemoPage',
  components: {
    Dashboard
  },
  setup() {
    const dashboardConfig = ref(null);
    const pageTitle = ref('');
    const pageDescription = ref('');
    const loading = ref(true);
    const error = ref(null);

    const loadDashboardConfig = async () => {
      loading.value = true;
      error.value = null;

      try {
        // 从项目配置获取服务信息
        const configResponse = await axios.get('/project-config.json');
        const projectConfig = configResponse.data;
        
        // 找到堆叠面积图演示服务
        const stackedAreaService = projectConfig.services.find(
          service => service.id === 'stacked_area_demo'
        );

        if (stackedAreaService) {
          pageTitle.value = stackedAreaService.title;
          pageDescription.value = stackedAreaService.description;
          
          // 从堆叠面积图演示服务获取仪表盘配置
          const dashboardResponse = await axios.get('/api/dashboard-config');
          dashboardConfig.value = dashboardResponse.data;
          
          console.log('加载的仪表盘配置:', dashboardConfig.value);
        } else {
          throw new Error('在项目配置中未找到堆叠面积图演示服务');
        }

        loading.value = false;
      } catch (err) {
        console.error('加载仪表盘配置失败:', err);
        error.value = `加载配置失败: ${err.message}`;
        loading.value = false;
      }
    };

    onMounted(() => {
      console.log('堆叠面积图演示页面挂载完成');
      loadDashboardConfig();
    });

    return {
      dashboardConfig,
      pageTitle,
      pageDescription,
      loading,
      error,
      loadDashboardConfig
    };
  }
});
</script>

<style scoped>
.stacked-area-demo-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5em;
  font-weight: 700;
}

.description {
  font-size: 1.1em;
  margin: 0;
  opacity: 0.9;
  line-height: 1.6;
}

.dashboard-container {
  margin-bottom: 40px;
}

.loading-container, .error-container {
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #f44336;
  font-size: 1.1em;
  margin-bottom: 20px;
}

.retry-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
}

.retry-button:hover {
  background-color: #45a049;
}

.features-section {
  background-color: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.features-section h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 2em;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.feature-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 25px;
  border-radius: 10px;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.feature-icon {
  font-size: 3em;
  margin-bottom: 15px;
}

.feature-card h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.3em;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.feature-details {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-badge {
  background-color: #4CAF50;
  color: white;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.8em;
  font-weight: 500;
}

.api-section {
  background-color: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.api-section h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 2em;
}

.api-examples {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.api-example {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #4CAF50;
}

.api-example h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.2em;
}

.api-example pre {
  background-color: #272822;
  color: #f8f8f2;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  font-size: 0.9em;
  line-height: 1.4;
}

.endpoint-list {
  list-style: none;
  padding: 0;
}

.endpoint-list li {
  background-color: #e8f5e8;
  margin-bottom: 8px;
  padding: 12px;
  border-radius: 5px;
  border-left: 3px solid #4CAF50;
}

.endpoint-list code {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #2c5282;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stacked-area-demo-page {
    padding: 10px;
  }
  
  .page-header h1 {
    font-size: 2em;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .api-examples {
    grid-template-columns: 1fr;
  }
}
</style>
