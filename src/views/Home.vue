<template>
  <div class="home-container">
    <!-- 系统标题和介绍 -->
    <header class="hero-section">
      <h1 class="main-title">📈 股票仪表盘系统</h1>
      <p class="subtitle">实时股票数据分析与可视化平台</p>
      <div class="features">
        <span class="feature-tag">🔄 实时数据</span>
        <span class="feature-tag">📊 多维分析</span>
        <span class="feature-tag">🎨 可视化</span>
        <span class="feature-tag">📱 响应式</span>
      </div>
    </header>

    <!-- 快速开始指南 -->
    <section class="quick-start">
      <h2>🚀 快速开始</h2>
      <div class="start-steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>运行配置生成器</h3>
            <p>自动生成所有配置文件</p>
            <code>python scripts/auto-config-generator.py</code>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>一键启动服务</h3>
            <p>启动所有后端和前端服务</p>
            <code>start-all-services.bat</code>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>开始分析</h3>
            <p>选择分析模式，实时查看数据</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 功能模块导航 -->
    <section class="dashboard-navigation">
      <h2>📊 功能模块</h2>
      <div class="dashboard-grid">
        <router-link to="/demo_1" class="dashboard-card">
          <div class="card-icon">🎯</div>
          <h3>演示仪表盘</h3>
          <p>使用模拟数据的完整功能演示</p>
          <div class="card-status">
            <span class="status-dot" :class="{ active: serviceStatus.demo1 }"></span>
            {{ serviceStatus.demo1 ? '服务正常' : '服务未启动' }}
          </div>
        </router-link>

      </div>
    </section>

    <!-- 系统状态监控 -->
    <section class="system-status">
      <h2>🔧 系统状态</h2>
      <div class="status-grid">
        <div class="status-item">
          <div class="status-header">
            <span class="status-icon">🌐</span>
            <span>前端服务</span>
          </div>
          <div class="status-value good">运行正常</div>
        </div>
        <div class="status-item">
          <div class="status-header">
            <span class="status-icon">🔌</span>
            <span>API连接</span>
          </div>
          <div class="status-value" :class="{ good: connectedServices > 0, warning: connectedServices === 0 }">
            {{ connectedServices }}/1 服务在线
          </div>
        </div>
        <div class="status-item">
          <div class="status-header">
            <span class="status-icon">📊</span>
            <span>数据更新</span>
          </div>
          <div class="status-value">{{ lastUpdateTime }}</div>
        </div>
      </div>
    </section>

    <!-- 帮助链接 -->
    <section class="help-section">
      <h2>📚 帮助文档</h2>
      <div class="help-links">
        <a href="/api-diagnostic.html" class="help-link" target="_blank">
          🔍 API 诊断工具
        </a>
        <a href="./project-config.json" class="help-link" target="_blank">
          ⚙️ 项目配置文件
        </a>
        <a href="./CONTRIBUTING.md" class="help-link" target="_blank">
          🤝 贡献指南
        </a>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'Home',
  setup() {
    const serviceStatus = ref({
      demo1: false,
    })
    
    const lastUpdateTime = ref('检查中...')

    // 检查服务状态
    const checkServiceStatus = async () => {
      const services = [
        { key: 'demo1', url: 'http://localhost:5004/health' },
      ]

      for (const service of services) {
        try {
          const response = await fetch(service.url, { 
            method: 'GET',
            timeout: 3000 
          })
          serviceStatus.value[service.key] = response.ok
        } catch (error) {
          serviceStatus.value[service.key] = false
        }
      }
      
      lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN')
    }

    const connectedServices = computed(() => {
      return Object.values(serviceStatus.value).filter(status => status).length
    })

    onMounted(() => {
      checkServiceStatus()
      // 每30秒检查一次服务状态
      setInterval(checkServiceStatus, 30000)
    })

    return {
      serviceStatus,
      connectedServices,
      lastUpdateTime
    }
  }
}
</script>

<style scoped>
/* 样式代码保持不变，这里省略以节省空间 */
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.hero-section {
  text-align: center;
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.main-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.subtitle {
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  opacity: 0.9;
}

.features {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.feature-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
}

.quick-start {
  margin-bottom: 3rem;
}

.start-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #2196F3;
}

.step-number {
  background: #2196F3;
  color: white;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.dashboard-navigation {
  margin-bottom: 3rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.dashboard-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 2rem;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  border-color: #2196F3;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.dashboard-card h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.3rem;
}

.dashboard-card p {
  color: #666;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.card-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #dc3545;
}

.status-dot.active {
  background: #28a745;
}

/* 其他样式... */
h2 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
}
</style>
