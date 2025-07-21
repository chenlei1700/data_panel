# 股票仪表盘服务器自动更新配置系统

## 概述

这是一个为股票仪表盘服务器添加的自动更新配置系统，允许用户通过多种方式管理服务器的自动更新行为。

## 功能特性

- 🔧 **灵活的配置管理**: 支持配置文件、命令行参数和Web界面三种配置方式
- 🎛️ **实时控制开关**: 可以在运行时启用/禁用自动更新，无需重启服务器
- 📊 **Web配置界面**: 提供直观的Web界面来管理所有服务器配置
- 🚀 **预定义配置模板**: 提供多种预设配置，适应不同使用场景
- 📡 **SSE客户端管理**: 智能管理SSE连接，防止资源过度占用
- 💾 **配置持久化**: 配置更改会自动保存到文件，重启后保持

## 使用方法

### 1. 命令行启动

#### 基本启动
```bash
# 使用默认配置启动多板块服务器
python server_launcher.py start --server multiplate

# 指定端口启动
python server_launcher.py start --server multiplate --port 5008
```

#### 自动更新配置
```bash
# 启用自动更新，30秒间隔
python server_launcher.py start --server multiplate --auto-update --interval 30

# 禁用自动更新
python server_launcher.py start --server multiplate --no-auto-update

# 设置最大客户端数
python server_launcher.py start --server multiplate --max-clients 50
```

#### 使用预定义配置模板
```bash
# 高频更新模式 (10秒间隔)
python server_launcher.py start --server multiplate --config-template high_frequency

# 正常模式 (30秒间隔)
python server_launcher.py start --server multiplate --config-template normal

# 低频更新模式 (60秒间隔)
python server_launcher.py start --server multiplate --config-template low_frequency

# 禁用自动更新
python server_launcher.py start --server multiplate --config-template disabled

# 演示模式 (15秒间隔)
python server_launcher.py start --server multiplate --config-template demo
```

#### 管理工具命令
```bash
# 查看所有服务器状态
python server_launcher.py status

# 列出可用配置模板
python server_launcher.py list-configs

# 交互式配置
python server_launcher.py config --interactive
```

### 2. Web配置界面

启动服务器后，访问配置管理界面：
- 地址: `http://localhost:<port>/config`
- 例如: `http://localhost:5008/config`

Web界面提供的功能：
- 📊 **实时状态监控**: 显示所有服务器的运行状态
- ⚙️ **配置管理**: 修改自动更新配置
- 🔄 **即时切换**: 启用/禁用自动更新
- 🗑️ **缓存管理**: 清理服务器缓存
- 📝 **操作日志**: 显示配置变更日志

### 3. API接口

#### 获取自动更新状态
```http
GET /api/auto-update/status
```

响应示例：
```json
{
  "status": "success",
  "auto_update": {
    "enabled": true,
    "thread_running": true,
    "interval": 30,
    "components": ["chart1", "chart2", "table1", "table2"],
    "sse_clients": 2,
    "max_clients": 50
  }
}
```

#### 获取配置
```http
GET /api/auto-update/config
```

#### 更新配置
```http
PUT /api/auto-update/config
Content-Type: application/json

{
  "enabled": true,
  "interval": 25,
  "max_clients": 30
}
```

#### 切换自动更新开关
```http
POST /api/auto-update/toggle
```

#### 清理缓存
```http
POST /api/cache/clear
```

#### 获取缓存状态
```http
GET /api/cache/status
```

## 配置文件说明

配置文件位置: `server_config.json`

### 配置文件结构

```json
{
  "auto_update": {
    "enabled": true,
    "interval": 30,
    "components": ["chart1", "chart2", "table1", "table2"],
    "random_selection": true,
    "max_clients": 50,
    "heartbeat_interval": 30
  },
  "servers": {
    "multiplate": {
      "port": 5008,
      "name": "多板块股票仪表盘",
      "auto_update": {
        "enabled": true,
        "interval": 25,
        "components": ["chart1", "chart2", "table1", "table2", "table12"],
        "max_clients": 30
      }
    }
  },
  "global": {
    "debug": true,
    "host": "0.0.0.0",
    "max_cache_size": 100
  }
}
```

### 配置参数说明

#### auto_update 配置
- `enabled`: 是否启用自动更新 (boolean)
- `interval`: 更新间隔，单位秒 (integer, 5-300)
- `components`: 参与自动更新的组件列表 (array)
- `random_selection`: 是否随机选择组件更新 (boolean)
- `max_clients`: 最大SSE客户端数 (integer)
- `heartbeat_interval`: 心跳间隔，单位秒 (integer)

## 预定义配置模板

| 模板名称 | 描述 | 更新间隔 | 适用场景 |
|---------|------|---------|---------|
| `high_frequency` | 高频更新模式 | 10秒 | 需要实时性很高的场景 |
| `normal` | 正常模式 | 30秒 | 普通使用场景 |
| `low_frequency` | 低频更新模式 | 60秒 | 资源有限或低频更新需求 |
| `disabled` | 禁用模式 | - | 完全禁用自动更新 |
| `demo` | 演示模式 | 15秒 | 演示和测试用途 |

## 程序化使用

### Python代码示例

```python
from server_config import get_server_config, create_auto_update_config
from show_plate_server_multiplate_v2 import MultiPlateStockServer

# 创建自定义配置
custom_config = create_auto_update_config("multiplate", 
                                         enabled=True, 
                                         interval=15, 
                                         max_clients=25)

# 启动服务器
server = MultiPlateStockServer(port=5008, auto_update_config=custom_config)
server.run()
```

### 动态配置修改

```python
# 获取配置管理器
from server_config import config_manager

# 更新服务器配置
config_manager.update_server_config("multiplate", {
    "auto_update": {
        "enabled": False,
        "interval": 45
    }
})

# 切换自动更新状态
new_status = config_manager.toggle_server_auto_update("multiplate")
print(f"自动更新状态: {'启用' if new_status else '禁用'}")
```

## 监控和日志

### 服务器日志
服务器会记录以下自动更新相关日志：
- 自动更新线程启动/停止
- 自动更新推送成功/失败
- SSE客户端连接/断开
- 配置变更记录

### Web界面日志
配置管理Web界面提供实时操作日志，包括：
- 配置保存成功/失败
- 自动更新状态切换
- 缓存清理结果
- 服务器连接状态

## 故障排除

### 常见问题

1. **服务器无法启动**
   - 检查端口是否被占用
   - 确认配置文件格式正确
   - 查看错误日志

2. **自动更新不工作**
   - 确认 `enabled` 设置为 `true`
   - 检查是否有SSE客户端连接
   - 查看后台线程状态

3. **Web配置界面无法访问**
   - 确认服务器已启动
   - 检查端口配置
   - 尝试 `http://localhost:<port>/config`

4. **配置更改不生效**
   - 确认配置已保存到文件
   - 某些配置可能需要重启线程
   - 查看API响应错误信息

### 调试方法

启用调试模式获取更详细日志：
```bash
python server_launcher.py start --server multiplate --debug
```

检查配置文件：
```bash
python -c "from server_config import config_manager; print(config_manager.config)"
```

## 更新历史

- v1.0.0: 初始版本，基本自动更新功能
- v1.1.0: 添加配置文件支持
- v1.2.0: 添加Web配置界面
- v1.3.0: 添加预定义配置模板
- v1.4.0: 添加启动器和命令行工具

## 贡献指南

欢迎提交Issue和Pull Request来改进这个配置系统。

## 许可证

本项目使用MIT许可证。
