#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动配置生成器 - 根据 project-config.json 自动生成所有配置文件
Auto Configuration Generator - Automatically generate all config files based on project-config.json

Author: chenlei
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import shutil
from datetime import datetime

class ConfigGenerator:
    def __init__(self, config_file: str = "project-config.json"):
        """初始化配置生成器"""
        self.config_file = config_file
        self.config = self.load_config()
        self.project_root = Path.cwd()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件 {self.config_file} 不存在")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            sys.exit(1)
    
    def backup_existing_files(self):
        """备份现有文件"""
        backup_dir = self.project_root / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        files_to_backup = [
            "src/config/api.js",
            "src/router/index.js", 
            "src/views/Home.vue",
            ".vscode/tasks.json"
        ]
        
        for file_path in files_to_backup:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(full_path, backup_path)
                print(f"📋 备份文件: {file_path}")
        
        print(f"✅ 文件已备份到: {backup_dir}")
    
    def generate_api_config(self):
        """生成 API 配置文件"""
        config_content = """// API配置文件 - 管理不同仪表盘的后端服务配置
// 此文件由 auto-config-generator.py 自动生成，请勿手动编辑

export const API_CONFIG = {
"""
        
        # 生成每个服务的配置
        for service in self.config['services']:
            if service['enabled']:
                config_content += f"""  // {service['name']} - 使用端口{service['port']}
  '{service['id']}': {{
    baseURL: 'http://localhost:{service['port']}',
    name: '{service['name']}数据服务',
    endpoints: {{
"""
                # 添加端点配置
                for endpoint_name, endpoint_path in self.config['apiEndpoints'].items():
                    config_content += f"      {endpoint_name}: '{endpoint_path}',\n"
                
                config_content += "    }\n  },\n\n"
        
        # 获取第一个启用的服务作为默认配置
        enabled_services = [s for s in self.config['services'] if s['enabled']]
        default_service_id = enabled_services[0]['id'] if enabled_services else 'StockDashboard_demo'
        
        config_content += f"""}}

/**
 * 根据路由名称获取对应的API配置
 * @param {{string}} routeName - 路由名称
 * @returns {{Object}} API配置对象
 */
export const getApiConfig = (routeName) => {{
  console.log(`🔍 查找路由 ${{routeName}} 的API配置...`);
  const config = API_CONFIG[routeName]
  if (!config) {{
    console.warn(`❌ 未找到路由 ${{routeName}} 对应的API配置，使用默认配置`)
    return API_CONFIG['{default_service_id}'] // 返回默认配置
  }}
  console.log(`✅ 找到配置: ${{config.name}} (${{config.baseURL}})`)
  return config
}}

/**
 * 获取所有可用的API服务列表
 * @returns {{Array}} 服务列表
 */
export const getAllServices = () => {{
  return Object.keys(API_CONFIG).map(key => ({{
    id: key,
    ...API_CONFIG[key]
  }}))
}}

/**
 * 检查服务健康状态
 * @param {{string}} serviceId - 服务ID
 * @returns {{Promise<boolean>}} 服务是否健康
 */
export const checkServiceHealth = async (serviceId) => {{
  const config = API_CONFIG[serviceId]
  if (!config) return false
  
  try {{
    const response = await fetch(`${{config.baseURL}}${{config.endpoints.health}}`, {{
      method: 'GET',
      timeout: 3000
    }})
    return response.ok
  }} catch (error) {{
    console.warn(`❌ 服务 ${{serviceId}} 健康检查失败:`, error)
    return false
  }}
}}

/**
 * 获取特定API端点的完整URL
 * @param {{string}} serviceName - 服务名称
 * @param {{string}} endpointName - 端点名称
 * @returns {{string}} 完整的API URL
 */
export const getApiEndpoint = (serviceName, endpointName) => {{
  console.log(`🔍 获取 ${{serviceName}} 服务的 ${{endpointName}} 端点...`);
  const config = API_CONFIG[serviceName]
  if (!config) {{
    console.warn(`❌ 未找到服务 ${{serviceName}} 的配置，使用默认配置`)
    const defaultConfig = API_CONFIG['{default_service_id}']
    return `${{defaultConfig.baseURL}}${{defaultConfig.endpoints[endpointName] || ''}}`
  }}
  const url = `${{config.baseURL}}${{config.endpoints[endpointName] || ''}}`
  console.log(`✅ 获取端点: ${{url}}`)
  return url
}}

/**
 * 获取服务的基础URL
 * @param {{string}} serviceName - 服务名称
 * @returns {{string}} 基础URL
 */
export const getApiUrl = (serviceName) => {{
  console.log(`🔍 获取 ${{serviceName}} 服务的基础URL...`);
  const config = API_CONFIG[serviceName]
  if (!config) {{
    console.warn(`❌ 未找到服务 ${{serviceName}} 的配置，使用默认配置`)
    return API_CONFIG['{default_service_id}'].baseURL
  }}
  console.log(`✅ 基础URL: ${{config.baseURL}}`)
  return config.baseURL
}}

/**
 * 获取服务信息
 * @param {{string}} serviceName - 服务名称
 * @returns {{Object}} 服务信息对象
 */
export const getServiceInfo = (serviceName) => {{
  console.log(`🔍 获取 ${{serviceName}} 服务信息...`);
  const config = API_CONFIG[serviceName]
  if (!config) {{
    console.warn(`❌ 未找到服务 ${{serviceName}} 的配置，返回默认服务信息`)
    const defaultConfig = API_CONFIG['{default_service_id}']
    return {{
      name: defaultConfig.name,
      baseURL: defaultConfig.baseURL,
      endpoints: defaultConfig.endpoints
    }}
  }}
  console.log(`✅ 服务信息: ${{config.name}}`)
  return {{
    name: config.name,
    baseURL: config.baseURL,
    endpoints: config.endpoints
  }}
}}
"""
        
        # 写入文件
        api_config_path = self.project_root / "src" / "config" / "api.js"
        api_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(api_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("✅ 生成 API 配置文件: src/config/api.js")
    
    def generate_router_config(self):
        """生成路由配置文件"""
        router_content = """// src/router/index.js
// 此文件由 auto-config-generator.py 自动生成，请勿手动编辑

import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import StockDashboard from '../views/StockDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
"""
        
        # 生成每个服务的路由
        for service in self.config['services']:
            if service['enabled']:
                router_content += f"""  {{
    path: '{service['path']}',
    name: '{service['id']}',
    component: {service['component']},
    meta: {{
      title: '{service['title']}',
      apiService: '{service['id']}'  // 对应API配置中的键名，使用端口{service['port']}
    }}
  }},
"""
        
        router_content += """]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
"""
        
        # 写入文件
        router_config_path = self.project_root / "src" / "router" / "index.js"
        router_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(router_config_path, 'w', encoding='utf-8') as f:
            f.write(router_content)
        
        print("✅ 生成路由配置文件: src/router/index.js")
    
    def generate_home_vue(self):
        """生成主页组件"""
        home_content = f"""<template>
  <div class="home-container">
    <!-- 系统标题和介绍 -->
    <header class="hero-section">
      <h1 class="main-title">📈 {self.config['projectInfo']['name']}</h1>
      <p class="subtitle">{self.config['projectInfo']['description']}</p>
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
            <code>python auto-config-generator.py</code>
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
"""
        
        # 生成服务卡片
        for service in self.config['services']:
            if service['enabled']:
                home_content += f"""        <router-link to="{service['path']}" class="dashboard-card">
          <div class="card-icon">{service['icon']}</div>
          <h3>{service['name']}</h3>
          <p>{service['description']}</p>
          <div class="card-status">
            <span class="status-dot" :class="{{ active: serviceStatus.{service['id'].lower().replace('_', '')} }}"></span>
            {{{{ serviceStatus.{service['id'].lower().replace('_', '')} ? '服务正常' : '服务未启动' }}}}
          </div>
        </router-link>

"""
        
        home_content += """      </div>
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
            {{ connectedServices }}/""" + str(len([s for s in self.config['services'] if s['enabled']])) + """ 服务在线
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
"""
        
        # 生成服务状态响应式数据
        for service in self.config['services']:
            if service['enabled']:
                key = service['id'].lower().replace('_', '')
                home_content += f"      {key}: false,\n"
        
        home_content += """    })
    
    const lastUpdateTime = ref('检查中...')

    // 检查服务状态
    const checkServiceStatus = async () => {
      const services = [
"""
        
        # 生成服务检查列表
        for service in self.config['services']:
            if service['enabled']:
                key = service['id'].lower().replace('_', '')
                home_content += f"        {{ key: '{key}', url: 'http://localhost:{service['port']}{self.config['apiEndpoints']['health']}' }},\n"
        
        home_content += """      ]

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
"""
        
        # 写入文件
        home_vue_path = self.project_root / "src" / "views" / "Home.vue"
        
        with open(home_vue_path, 'w', encoding='utf-8') as f:
            f.write(home_content)
        
        print("✅ 生成主页组件: src/views/Home.vue")
    
    def generate_vscode_tasks(self):
        """生成 VS Code 任务配置"""
        tasks_content = {
            "version": "2.0.0",
            "tasks": []
        }
        
        # 获取API基础路径，如果是相对路径则转换为绝对路径
        api_base_path = self.config['developmentConfig']['apiBasePath']
        if not os.path.isabs(api_base_path):
            api_base_path = os.path.abspath(api_base_path)
        
        # 1. 一键启动所有服务的主任务
        backend_tasks = []
        for service in self.config['services']:
            if service['enabled']:
                backend_tasks.append(service['taskLabel'])
        
        main_task = {
            "type": "shell",
            "label": "🚀 启动所有服务",
            "dependsOn": ["启动前端开发服务器"] + backend_tasks,
            "group": {
                "kind": "build",
                "isDefault": True
            },
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "shared",
                "group": "main",
                "clear": True,
                "showReuseMessage": False
            }
        }
        tasks_content["tasks"].append(main_task)
        
        # 2. 前端相关任务
        frontend_tasks = [
            {
                "label": "启动前端开发服务器",
                "type": "shell",
                "command": "npm run serve",
                "isBackground": True,
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "dedicated",
                    "group": "frontend",
                    "clear": True,
                    "showReuseMessage": False
                },
                "options": {
                    "cwd": "${workspaceFolder}"
                }
            },
            {
                "label": "构建前端项目",
                "type": "shell",
                "command": "npm run build",
                "isBackground": False,
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "dedicated",
                    "group": "frontend",
                    "clear": True,
                    "showReuseMessage": False
                },
                "options": {
                    "cwd": "${workspaceFolder}"
                }
            },
            {
                "label": "安装前端依赖",
                "type": "shell",
                "command": "npm install",
                "isBackground": False,
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "dedicated",
                    "group": "frontend",
                    "clear": True,
                    "showReuseMessage": False
                },
                "options": {
                    "cwd": "${workspaceFolder}"
                }
            }
        ]
        tasks_content["tasks"].extend(frontend_tasks)
        
        # 3. 后端服务组合任务
        if backend_tasks:
            backend_group_task = {
                "label": "启动所有后端服务",
                "type": "shell",
                "dependsOn": backend_tasks,
                "group": "build",
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "shared",
                    "group": "backend",
                    "clear": True,
                    "showReuseMessage": False
                }
            }
            tasks_content["tasks"].append(backend_group_task)
        
        # 4. 为每个后端服务创建单独任务
        for service in self.config['services']:
            if service['enabled']:
                task = {
                    "label": service['taskLabel'],
                    "type": "shell",
                    "command": f"& {self.config['developmentConfig']['pythonPath']} {api_base_path}/{service['serverFile']}",
                    "isBackground": True,
                    "problemMatcher": [],
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated",
                        "group": "backend",
                        "clear": False,
                        "showReuseMessage": False
                    }
                }
                tasks_content["tasks"].append(task)
        
        # 5. 工具任务
        utility_tasks = [
            {
                "label": "检查Python环境",
                "type": "shell",
                "command": "python --version && pip list | findstr flask",
                "isBackground": False,
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "dedicated",
                    "group": "utils",
                    "clear": True,
                    "showReuseMessage": False
                }
            },
            {
                "label": "项目初始化",
                "type": "shell",
                "command": "python init-config.py",
                "isBackground": False,
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "dedicated",
                    "group": "utils",
                    "clear": True,
                    "showReuseMessage": False
                },
                "options": {
                    "cwd": "${workspaceFolder}"
                }
            },
            {
                "label": "重新生成配置",
                "type": "shell",
                "command": "python auto-config-generator.py",
                "isBackground": False,
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "dedicated",
                    "group": "utils",
                    "clear": True,
                    "showReuseMessage": False
                },
                "options": {
                    "cwd": "${workspaceFolder}"
                }
            },
            {
                "label": "添加新页面",
                "type": "shell",
                "command": "python quick-add-page.py",
                "isBackground": False,
                "problemMatcher": [],
                "presentation": {
                    "reveal": "always",
                    "panel": "dedicated",
                    "group": "utils",
                    "clear": True,
                    "showReuseMessage": False
                },
                "options": {
                    "cwd": "${workspaceFolder}"
                }
            }
        ]
        tasks_content["tasks"].extend(utility_tasks)
        
        # 确保 .vscode 目录存在
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        # 写入文件
        tasks_json_path = vscode_dir / "tasks.json"
        
        with open(tasks_json_path, 'w', encoding='utf-8') as f:
            json.dump(tasks_content, f, indent=2, ensure_ascii=False)
        
        print("✅ 生成 VS Code 任务配置: .vscode/tasks.json")
    
    def generate_startup_scripts(self):
        """生成启动脚本"""
        # Windows 批处理脚本
        bat_content = f"""@echo off
echo ========================================
echo {self.config['projectInfo']['name']} - 一键启动脚本
echo ========================================
echo.

:: 检查 Python 环境
echo [1/4] 检查 Python 环境...
{self.config['projectInfo']['pythonExecutable']} --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python 环境
    echo 请确保已安装 Python 并添加到系统 PATH
    pause
    exit /b 1
)
echo ✅ Python 环境检查通过

:: 检查依赖包
echo [2/4] 检查 Python 依赖包...
{self.config['projectInfo']['pythonExecutable']} -c "import flask, pandas, plotly" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告: 缺少必要的 Python 包
    echo 正在安装依赖包...
    pip install flask flask-cors pandas plotly numpy
)
echo ✅ 依赖包检查完成

:: 启动后端服务
echo [3/4] 启动后端API服务...

"""
        
        # 为每个服务添加启动命令
        for service in self.config['services']:
            if service['enabled']:
                # 使用相对路径
                bat_content += f"""start "{service['name']} (端口{service['port']})" cmd /k "echo 启动{service['name']}服务... && {self.config['projectInfo']['pythonExecutable']} api/{service['serverFile']}"
timeout /t 2 >nul

"""
        
        bat_content += f"""echo ✅ 后端服务启动完成

:: 启动前端服务
echo [4/4] 启动前端服务...
echo.
echo 🚀 正在启动前端开发服务器...
echo 📱 浏览器将自动打开 http://localhost:{self.config['projectInfo']['frontendPort']}
echo.
echo ⚠️  注意: 请等待几秒钟让所有服务完全启动
echo 💡 如需停止服务，请关闭所有终端窗口
echo.

:: 启动前端 (在当前窗口)
npm run serve

pause"""
        
        # 写入 Windows 脚本
        with open(self.project_root / "start-all-services.bat", 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        # Linux/Mac 脚本
        sh_content = f"""#!/bin/bash

echo "========================================"
echo "{self.config['projectInfo']['name']} - 一键启动脚本 (Linux/Mac)"
echo "========================================"
echo

# 检查 Python 环境
echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 环境"
    echo "请确保已安装 Python 3"
    exit 1
fi
echo "✅ Python 环境检查通过"

# 检查依赖包
echo "[2/4] 检查 Python 依赖包..."
python3 -c "import flask, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  警告: 缺少必要的 Python 包"
    echo "正在安装依赖包..."
    pip3 install flask flask-cors pandas plotly numpy
fi
echo "✅ 依赖包检查完成"

# 启动后端服务
echo "[3/4] 启动后端API服务..."

"""
        
        # 为每个服务添加启动命令
        for service in self.config['services']:
            if service['enabled']:
                # 使用相对路径
                sh_content += f"""# 启动{service['name']}服务
gnome-terminal --title="{service['name']} (端口{service['port']})" -- bash -c "echo '启动{service['name']}服务...'; python3 api/{service['serverFile']}; exec bash" &
sleep 2

"""
        
        sh_content += f"""echo "✅ 后端服务启动完成"

# 启动前端服务
echo "[4/4] 启动前端服务..."
echo
echo "🚀 正在启动前端开发服务器..."
echo "📱 浏览器将自动打开 http://localhost:{self.config['projectInfo']['frontendPort']}"
echo
echo "⚠️  注意: 请等待几秒钟让所有服务完全启动"
echo "💡 如需停止服务，请关闭所有终端窗口"
echo

# 启动前端
npm run serve"""
        
        # 写入 Linux/Mac 脚本
        with open(self.project_root / "start-all-services.sh", 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        print("✅ 生成启动脚本: start-all-services.bat, start-all-services.sh")
    
    def generate_all(self):
        """生成所有配置文件"""
        print("🚀 开始自动生成配置文件...")
        print(f"📋 项目: {self.config['projectInfo']['name']}")
        print(f"🔧 服务数量: {len([s for s in self.config['services'] if s['enabled']])}")
        print()
        
        # 备份现有文件
        self.backup_existing_files()
        print()
        
        # 生成各种配置文件
        self.generate_api_config()
        self.generate_router_config()
        self.generate_home_vue()
        self.generate_vscode_tasks()
        self.generate_startup_scripts()
        
        print()
        print("🎉 所有配置文件生成完成!")
        print()
        print("📝 生成的文件:")
        print("   - src/config/api.js")
        print("   - src/router/index.js")
        print("   - src/views/Home.vue")
        print("   - .vscode/tasks.json")
        print("   - start-all-services.bat")
        print("   - start-all-services.sh")
        print()
        print("🚀 下一步:")
        print("   1. 检查生成的配置文件")
        print("   2. 运行 start-all-services.bat (Windows) 或 ./start-all-services.sh (Linux/Mac)")
        print(f"   3. 访问 http://localhost:{self.config['projectInfo']['frontendPort']}")

def add_new_service():
    """交互式添加新服务"""
    config_file = "project-config.json"
    
    # 加载现有配置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ 配置文件不存在，请先创建 project-config.json")
        return
    
    print("📝 添加新服务配置")
    print("=" * 40)
    
    # 获取用户输入
    service_id = input("服务ID (如: StockDashboard_new): ").strip()
    if not service_id:
        print("❌ 服务ID不能为空")
        return
    
    name = input("服务名称 (如: 新功能分析): ").strip()
    description = input("服务描述: ").strip()
    icon = input("图标 (如: 📊): ").strip() or "📊"
    
    # 自动分配端口
    used_ports = [s['port'] for s in config['services']]
    new_port = max(used_ports) + 1 if used_ports else config['projectInfo']['basePort']
    
    path = input(f"路径 (默认: /{service_id.lower().replace('_', '-')}): ").strip()
    if not path:
        path = f"/{service_id.lower().replace('_', '-')}"
    
    title = input(f"页面标题 (默认: {name}仪表盘): ").strip()
    if not title:
        title = f"{name}仪表盘"
    
    server_file = input(f"服务器文件名 (默认: show_plate_server_{service_id.lower()}.py): ").strip()
    if not server_file:
        server_file = f"show_plate_server_{service_id.lower()}.py"
    
    task_label = input(f"任务标签 (默认: {name}服务器): ").strip()
    if not task_label:
        task_label = f"{name}服务器"
    
    # 创建新服务配置
    new_service = {
        "id": service_id,
        "name": name,
        "description": description,
        "icon": icon,
        "port": new_port,
        "path": path,
        "title": title,
        "serverFile": server_file,
        "component": "StockDashboard",
        "taskLabel": task_label,
        "enabled": True
    }
    
    # 添加到配置
    config['services'].append(new_service)
    
    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print()
    print("✅ 新服务已添加到配置文件")
    print(f"🔌 分配端口: {new_port}")
    print(f"📁 需要创建: api/{server_file}")
    print()
    print("🚀 运行以下命令生成所有配置:")
    print("   python auto-config-generator.py")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "add":
            add_new_service()
            return
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("""
自动配置生成器使用说明

用法:
  python auto-config-generator.py          # 生成所有配置文件
  python auto-config-generator.py add      # 交互式添加新服务
  python auto-config-generator.py --help   # 显示帮助信息

功能:
  - 根据 project-config.json 自动生成所有配置文件
  - 支持添加新服务配置
  - 自动备份现有文件
  - 生成启动脚本和VS Code任务配置
            """)
            return
    
    generator = ConfigGenerator()
    generator.generate_all()

if __name__ == "__main__":
    main()
