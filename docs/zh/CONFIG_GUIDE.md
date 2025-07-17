# 📋 配置管理指南

**作者**: chenlei

## 🎯 统一配置系统

项目采用 `project-config.json` 作为唯一的配置文件，所有的前后端配置都从这个文件自动生成。

### 📄 配置文件结构

```json
{
  "projectInfo": {
    "name": "股票仪表盘系统",
    "description": "实时股票数据分析与可视化平台",
    "version": "1.0.0",
    "basePort": 5004,
    "frontendPort": 8081,
    "pythonExecutable": "python"
  },
  "services": [
    {
      "id": "demo_1",
      "name": "演示仪表盘",
      "description": "使用模拟数据的完整功能演示",
      "icon": "🎯",
      "port": 5004,
      "path": "/demo_1",
      "title": "股票仪表盘演示",
      "serverFile": "show_plate_server_demo.py",
      "component": "StockDashboard",
      "taskLabel": "演示服务器",
      "enabled": true
    }
  ],
  "apiEndpoints": {
    "dashboardConfig": "/api/dashboard-config",
    "chartData": "/api/chart-data",
    "tableData": "/api/table-data",
    "updates": "/api/dashboard/updates",
    "health": "/health"
  },
  "developmentConfig": {
    "pythonPath": "python",
    "apiBasePath": "./api",
    "autoOpenBrowser": true,
    "enableHotReload": true
  }
}
```

## 🔧 配置字段详解

### projectInfo 部分
- `name`: 项目名称，显示在页面标题和文档中
- `description`: 项目描述
- `version`: 项目版本号
- `basePort`: 后端服务的基础端口
- `frontendPort`: 前端开发服务器端口
- `pythonExecutable`: Python 解释器路径

### services 部分
每个服务包含以下字段：
- `id`: 唯一标识符，用于生成路由和API配置
- `name`: 服务显示名称
- `description`: 服务描述
- `icon`: 图标（支持 emoji 或图标类名）
- `port`: 服务端口（通常与 basePort 相同）
- `path`: 前端路由路径
- `title`: 页面标题
- `serverFile`: 后端服务文件名
- `component`: Vue 组件名
- `taskLabel`: VS Code 任务标签
- `enabled`: 是否启用该服务

## 🚀 自动生成的文件

运行 `python scripts/auto-config-generator.py` 后，系统会自动生成：

### 前端配置文件

**1. src/config/api.js**
```javascript
export const API_CONFIG = {
  demo_1: {
    baseUrl: 'http://localhost:5004',
    name: '演示仪表盘'
  }
};

export default API_CONFIG;
```

**2. src/router/index.js**
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import StockDashboard from '@/views/StockDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/demo_1',
    name: 'demo_1',
    component: StockDashboard,
    meta: {
      apiService: 'demo_1',
      title: '股票仪表盘演示'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

**3. src/views/Home.vue**
```vue
<template>
  <div class="home-container">
    <h1>🎯 股票仪表盘系统</h1>
    <div class="services-grid">
      <div class="service-card" v-for="service in services" :key="service.id">
        <div class="service-icon">{{ service.icon }}</div>
        <h3>{{ service.name }}</h3>
        <p>{{ service.description }}</p>
        <router-link :to="service.path" class="service-link">
          打开仪表盘
        </router-link>
      </div>
    </div>
  </div>
</template>
```

### VS Code 配置

**4. .vscode/tasks.json**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "type": "shell",
      "label": "🚀 启动所有服务",
      "dependsOn": [
        "启动前端开发服务器",
        "演示服务器"
      ],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    },
    {
      "label": "启动前端开发服务器",
      "type": "shell",
      "command": "npm run serve",
      "isBackground": true
    },
    {
      "label": "演示服务器",
      "type": "shell",
      "command": "python",
      "args": ["api/show_plate_server_demo.py"],
      "isBackground": true
    }
  ]
}
```

### 启动脚本

**5. start-all-services.bat (Windows)**
```batch
@echo off
echo 🚀 启动股票仪表盘系统..
echo.

start "前端开发服务器" cmd /k "npm run serve"
timeout /t 2 /nobreak >nul

start "演示服务器" cmd /k "python api/show_plate_server_demo.py"

echo ✅ 所有服务已启动！
echo 📱 前端地址: http://localhost:8081
echo 🔧 后端地址: http://localhost:5004
```

**6. start-all-services.sh (Linux/Mac)**
```bash
#!/bin/bash
echo "🚀 启动股票仪表盘系统.."

# 启动前端服务
npm run serve &
FRONTEND_PID=$!

# 等待一会儿
sleep 2

# 启动后端服务
python api/show_plate_server_demo.py &
BACKEND_PID=$!

echo "✅ 所有服务已启动！"
echo "📱 前端地址: http://localhost:8081"
echo "🔧 后端地址: http://localhost:5004"
echo "前端PID: $FRONTEND_PID"
echo "后端PID: $BACKEND_PID"
```

## 🛠️ 自定义配置

### 添加新服务

1. **编辑配置文件**
   ```json
   {
     "services": [
       {
         "id": "new_service",
         "name": "新服务",
         "description": "新的仪表盘服务",
         "icon": "📊",
         "port": 5005,
         "path": "/new_service",
         "title": "新仪表盘",
         "serverFile": "new_server.py",
         "component": "StockDashboard",
         "taskLabel": "新服务器",
         "enabled": true
       }
     ]
   }
   ```

2. **重新生成配置**
   ```bash
   python scripts/auto-config-generator.py
   ```

3. **创建服务器文件**
   ```bash
   cp api/show_plate_server_demo.py api/new_server.py
   # 然后编辑 new_server.py 文件
   ```

### 修改端口配置

1. **更新配置文件**
   ```json
   {
     "projectInfo": {
       "basePort": 6000,
       "frontendPort": 8090
     }
   }
   ```

2. **重新生成配置**
   ```bash
   python scripts/auto-config-generator.py
   ```

3. **手动更新代理配置**
   ⚠️ **重要**：`vue.config.js` 不会被自动更新，需要手动配置新服务器的代理规则。
   
   添加新服务器时，编辑 `vue.config.js`：
   ```javascript
   proxy: {
     '/api': {
       target: 'http://localhost:5004', // 主服务器
       changeOrigin: true
     },
     '/api/new-service': {
       target: 'http://localhost:XXXX', // 新服务器端口
       changeOrigin: true,
       pathRewrite: {
         '^/api/new-service': '/api'
       }
     }
   }
   ```

## 🔍 配置验证

### 检查配置文件
```bash
python -c "import json; print(json.load(open('project-config.json')))"
```

### 验证生成的文件
```bash
# 检查API配置
cat src/config/api.js

# 检查路由配置
cat src/router/index.js

# 检查VS Code任务
cat .vscode/tasks.json
```

## 📋 配置管理最佳实践

1. **版本控制**
   - 将 `project-config.json` 纳入版本控制
   - 不要直接修改生成的文件
   - 使用 `.gitignore` 忽略自动生成的文件（可选）

2. **环境管理**
   - 为不同环境创建不同的配置文件
   - 使用环境变量覆盖配置
   - 保持开发和生产配置的同步

3. **配置备份**
   - 自动生成器会自动备份被覆盖的文件
   - 备份文件位于 `backup/` 目录
   - 定期清理旧的备份文件

4. **团队协作**
   - 统一使用相同的配置文件格式
   - 文档化自定义配置的修改过程
   - 使用代码审查确保配置变更的正确性
