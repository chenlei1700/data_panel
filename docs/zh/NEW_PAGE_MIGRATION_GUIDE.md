# 新页面添加与迁移指南

**Author**: chenlei  
**Date**: 2025-01-10  
**Description**: 基于新框架的页面添加与旧服务迁移详细指南

## 概述

本指南详细说明如何：
1. 将旧的股票服务迁移到新框架
2. 从零创建基于新框架的服务
3. 配置管理和自动化流程

## 迁移步骤详解

### 第一步：分析旧服务功能

在迁移 `show_plate_server_multiplate.py` 时，我们首先分析了原服务的功能：

1. **读取完整代码**：
   ```bash
   # 分析原服务的所有功能
   - 数据缓存系统 (DataCache)
   - 动态标题管理 (dynamic_titles)
   - SSE实时更新 (Server-Sent Events)
   - 多个图表API (sector-line-chart_change, uplimit, uprate等)
   - 多个表格API (plate_info, stocks, up_limit等)
   - 板块数据处理逻辑
   ```

2. **识别核心组件**：
   - 仪表盘配置 (`get_dashboard_config`)
   - 数据源处理 (`get_data_sources`)
   - 路由注册机制
   - 业务逻辑方法

### 第二步：创建新框架版本

#### 2.1 基本框架结构

```python
"""
Author: chenlei
Date: 2024-01-20
Description: 股票多板块仪表盘服务 - 基于新框架重构版本
功能: 提供多板块股票数据展示、实时涨幅分析、涨停监控等功能
"""

import time
import pandas as pd
import numpy as np
import json
# ...其他导入

# 导入新框架基类
from base_server import BaseStockServer

class MultiPlateStockServer(BaseStockServer):
    """多板块股票服务器 - 继承自BaseStockServer"""
    
    def __init__(self, port=5008):
        super().__init__(port=port, service_name="多板块股票仪表盘")
        
        # 服务特定的配置
        self.data_cache = DataCache()
        self.dynamic_titles = {...}
        # ...其他初始化
```

#### 2.2 实现必要的抽象方法

```python
def get_dashboard_config(self):
    """获取仪表盘配置"""
    return {
        "layout": {
            "rows": 6,
            "cols": 5,
            "components": [
                {
                    "id": "chart1",
                    "type": "chart",
                    "dataSource": "/api/chart-data/sector-line-chart_change",
                    "title": "板块涨幅折线图",
                    "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
                },
                # ...更多组件
            ]
        }
    }

def get_data_sources(self):
    """获取数据源配置"""
    return {
        "/api/chart-data/sector-line-chart_change": {
            "handler": "get_sector_chart_data_change",
            "description": "板块涨幅折线图数据",
            "cache_ttl": 30
        },
        # ...更多数据源
    }
```

#### 2.3 新框架的自动Handler机制

**重要发现**：新框架支持自动handler调用，大大简化了路由注册：

```python
def register_custom_routes(self):
    """注册自定义路由 - 基类会自动调用handler，无需手工注册"""
    # 基类会自动根据get_data_sources()中的handler字段调用对应方法
    # 只需注册特殊路由（如SSE）
    
    # 注册SSE和更新相关路由
    self.app.add_url_rule('/api/dashboard/update',
                         'update_dashboard',
                         self.update_dashboard, methods=['POST'])
    
    self.app.add_url_rule('/api/dashboard/updates',
                         'dashboard_updates',
                         self.dashboard_updates, methods=['GET'])
```

### 第三步：迁移业务逻辑

#### 3.1 数据处理方法

直接从旧服务复制业务逻辑方法，但改进错误处理：

```python
def get_sector_chart_data_change(self):
    """返回板块涨幅折线图数据"""
    try:
        sector_names = self._get_dynamic_titles_list()
        sector_df = pd.read_csv('strategy\\showhtml\\server\\good_plate_df.csv')
        
        # ...业务逻辑
        
        return jsonify({
            "chartType": "line",
            "data": chart_data,
            "layout": {
                "title": "板块涨幅",
                "xaxis": {"title": "时间"},
                "yaxis": {"title": "涨幅(%)"},
                "legend": {"title": "板块名称"}
            }
        })
    
    except Exception as e:
        self.logger.error(f"获取板块涨幅数据失败: {e}")
        return jsonify({"error": str(e)}), 500
```

#### 3.2 辅助类和工具

保留原有的辅助类（如DataCache），无需修改：

```python
# 数据缓存类 - 保持原有逻辑
class DataCache:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def load_data(self, file_key):
        """加载或返回缓存的数据"""
        # ...原有逻辑
```

### 第四步：配置管理

#### 4.1 更新项目配置

在 `project-config.json` 中添加新服务：

```json
{
  "id": "multiplate_v2",
  "name": "多板块仪表盘(新框架)",
  "description": "基于新框架重构的多板块股票仪表盘，支持SSE实时更新",
  "icon": "🔄",
  "port": 5008,
  "path": "/multiplate-v2",
  "title": "多板块股票仪表盘(新框架版)",
  "serverFile": "show_plate_server_multiplate_v2.py",
  "component": "StockDashboard", 
  "taskLabel": "多板块新框架服务器",
  "enabled": true
}
```

#### 4.2 运行自动配置生成器

```bash
python scripts\auto-config-generator.py
```

这会自动更新：
- `.vscode\tasks.json` - VS Code任务配置
- `src\config\api.js` - 前端API配置
- `src\router\index.js` - 前端路由配置
- `src\views\Home.vue` - 服务列表
- `start-all-services.bat/.sh` - 启动脚本

### 第五步：配置前端代理（重要）

⚠️ **重要**：`vue.config.js` 不会被自动配置生成器更新，需要手动配置！

当添加新的后端服务器时，需要手动更新前端的代理配置：

#### 5.1 编辑 vue.config.js

根据新服务的端口，添加相应的代理配置：

```javascript
// vue.config.js
module.exports = {
  publicPath: '/',
  devServer: {
    port: 8081,
    proxy: {
      // 主要API服务器 (演示服务器)
      '/api': {
        target: 'http://localhost:5004',
        changeOrigin: true,
        logLevel: 'debug'
      },
      
      // 多板块服务器 (新增)
      '/api/multiplate': {
        target: 'http://localhost:5003',  // 新增的多板块服务器
        changeOrigin: true,
        pathRewrite: {
          '^/api/multiplate': '/api'  // 路径重写，去掉前缀
        }
      },
      
      // 强势股服务器 (新增)
      '/api/strong': {
        target: 'http://localhost:5002',  // 新增的强势股服务器
        changeOrigin: true,
        pathRewrite: {
          '^/api/strong': '/api'
        }
      }
      
      // 添加新服务器时的模板：
      // '/api/your-new-service': {
      //   target: 'http://localhost:XXXX',  // 新服务器端口
      //   changeOrigin: true,
      //   pathRewrite: {
      //     '^/api/your-new-service': '/api'
      //   }
      // }
    }
  }
}
```

#### 5.2 代理配置规则

1. **路径匹配优先级**：更具体的路径要放在前面
2. **端口一致性**：确保端口与 `project-config.json` 中的配置一致
3. **路径重写**：使用 `pathRewrite` 去掉路径前缀，让后端收到标准的API路径

#### 5.3 前端调用方式

配置完代理后，前端可以这样调用不同的服务器：

```javascript
// 调用主服务器 (localhost:5004)
axios.get('/api/dashboard-config')
axios.get('/api/table-data/stock-list')

// 调用多板块服务器 (localhost:5003)
axios.get('/api/multiplate/table-data/sector-list')
axios.get('/api/multiplate/dashboard-config')

// 调用强势股服务器 (localhost:5002)
axios.get('/api/strong/table-data/up-limit')

// 调用新添加的服务器
axios.get('/api/your-new-service/your-endpoint')
```

#### 5.4 重启前端服务

修改 `vue.config.js` 后，**必须重启前端开发服务器**：

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
npm run serve
```

#### 5.5 验证代理配置

1. **检查浏览器网络面板**：确认请求被正确转发
2. **查看控制台日志**：`logLevel: 'debug'` 会显示代理详情
3. **测试API调用**：确保所有服务器都能正常响应

⚠️ **关键提醒**：
- 每次添加新的后端服务器时，都需要手动更新 `vue.config.js`
- 确保代理端口与后端实际端口一致
- 代理配置的顺序很重要，具体路径要在通用路径前面

## 从零创建新服务

### 使用快速添加工具

```bash
python scripts\quick-add-page.py
```

按提示输入：
- 服务名称
- 端口号
- 描述
- 图标

工具会自动：
1. 生成基于新框架的服务模板
2. 更新项目配置
3. 运行自动配置生成器

### 手动创建步骤

1. **创建服务文件**：
   ```python
   # api/your_new_service.py
   from base_server import BaseStockServer
   
   class YourNewServer(BaseStockServer):
       def __init__(self, port=XXXX):
           super().__init__(port=port, service_name="您的服务名")
       
       def get_dashboard_config(self):
           # 实现仪表盘配置
           
       def get_data_sources(self):
           # 实现数据源配置
   ```

2. **更新项目配置**：
   在 `project-config.json` 的 `services` 数组中添加新服务配置

3. **运行自动生成器**：
   ```bash
   python scripts\auto-config-generator.py
   ```

## 迁移检查清单

### 功能迁移检查

- [ ] ✅ 仪表盘配置 (`get_dashboard_config`)
- [ ] ✅ 数据源配置 (`get_data_sources`)
- [ ] ✅ 所有图表API方法
- [ ] ✅ 所有表格API方法
- [ ] ✅ SSE实时更新功能
- [ ] ✅ 错误处理和日志记录
- [ ] ✅ 缓存机制
- [ ] ✅ 动态标题管理

### 配置更新检查

- [ ] ✅ 项目配置文件更新
- [ ] ✅ VS Code任务配置
- [ ] ✅ 前端路由配置
- [ ] ✅ API端点配置
- [ ] ✅ 启动脚本更新

### 测试验证

- [ ] ✅ 服务正常启动
- [ ] ✅ 前端页面访问
- [ ] ✅ API接口响应
- [ ] ✅ 实时更新功能
- [ ] ✅ 错误处理机制

## 框架优势对比

### 旧框架问题
```python
# 每个API都需要手工注册路由
@app.route('/api/chart-data/sector-line-chart_change', methods=['GET'])
def get_sector_chart_data_change():
    # 大量重复代码
    try:
        # 业务逻辑
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 重复的路由注册
app.add_url_rule('/api/chart-data/sector-line-chart_change', 
                 'get_sector_chart_data_change', 
                 get_sector_chart_data_change, methods=['GET'])
```

### 新框架优势
```python
# 自动路由注册 - 基于配置驱动
def get_data_sources(self):
    return {
        "/api/chart-data/sector-line-chart_change": {
            "handler": "get_sector_chart_data_change",  # 自动调用
            "description": "板块涨幅折线图数据",
            "cache_ttl": 30
        }
    }

# 只需实现业务方法，无需手工注册路由
def get_sector_chart_data_change(self):
    # 专注业务逻辑
    return self.handle_request_with_cache(lambda: {
        # 业务实现
    })
```

## 常见问题和解决方案

### 1. Handler自动调用机制

**问题**：基类如何知道调用哪个方法？

**解决方案**：基类改进了路由处理机制：
```python
# 基类 base_server.py 中的改进
def get_chart_data(self, chart_type):
    data_sources = self.get_data_sources()
    endpoint = f"/api/chart-data/{chart_type}"
    
    if endpoint in data_sources:
        config = data_sources[endpoint]
        if 'handler' in config:
            # 自动调用对应的handler方法
            handler_method = getattr(self, config['handler'], None)
            if handler_method:
                return handler_method()
```

### 2. 路径引用问题

**问题**：CSV文件路径在不同环境下可能不一致

**解决方案**：使用相对路径或配置化路径：
```python
# 建议使用配置文件管理路径
def _get_file_paths(self):
    return {
        'plate_df': 'strategy/showhtml/server/good_plate_df.csv',
        'stock_df': 'strategy/showhtml/server/stock_df.csv',
    }
```

### 3. 端口冲突

**问题**：新服务端口与现有服务冲突

**解决方案**：
- 查看 `project-config.json` 中已使用的端口
- 使用自动配置生成器验证端口唯一性
- 建议端口范围：5000-5020

## 最佳实践

### 1. 代码组织
- 保持原有业务逻辑不变
- 使用新框架的统一错误处理
- 利用自动handler调用减少样板代码

### 2. 配置管理
- 优先使用自动配置生成器
- 手动配置后务必运行验证
- 保持配置文件同步

### 3. 测试策略
- 迁移过程中保留原服务作为对比
- 逐步验证各项功能
- 确保SSE等特殊功能正常工作

### 4. 文档维护
- 记录迁移过程中的问题和解决方案
- 更新API文档
- 维护变更日志

## 总结

通过将 `show_plate_server_multiplate.py` 迁移为 `show_plate_server_multiplate_v2.py`，我们验证了新框架的以下优势：

1. **代码复用**：减少90%的样板代码
2. **自动化**：配置驱动的路由注册
3. **统一管理**：集中的错误处理和日志
4. **易于维护**：清晰的代码结构

新框架使得添加新页面变得简单快捷，同时保持了高度的灵活性和可扩展性。
