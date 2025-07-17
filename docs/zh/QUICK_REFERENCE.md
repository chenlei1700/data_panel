# 📋 快速参�?

**作�?*: chenlei

## 🚀 一分钟启动

```bash
# 1. 初始化（仅首次）
python scripts/init-config.py

# 2. 安装依赖（仅首次�?
npm install

# 3. 启动服务
start-all-services.bat    # Windows
./start-all-services.sh   # Linux/Mac
```

**访问地址**: http://localhost:8081

## 🎯 VS Code 一键启�?

1. �?`Ctrl+Shift+P` (Windows/Linux) �?`Cmd+Shift+P` (Mac)
2. 输入 "Tasks: Run Task"
3. 选择 "🚀 启动所有服�?

## 📁 核心文件

| 文件 | 说明 | 类型 |
|------|------|------|
| `project-config.json` | 🎯 统一配置文件（核心） | 手动编辑 |
| `auto-config-generator.py` | 🔧 自动生成配置 | 工具脚本 |
| `init-config.py` | 🚀 项目初始�?| 工具脚本 |
| `quick-add-page.py` | �?快速添加页�?| 工具脚本 |
| `api/show_plate_server_demo.py` | 🎯 演示服务�?| 后端服务 |

## 🌐 默认端口

| 服务 | 端口 | 地址 |
|------|------|------|
| 前端 Vue | 8081 | http://localhost:8081 |
| 后端 Flask | 5004 | http://localhost:5004 |
| 演示页面 | - | http://localhost:8081/demo_1 |

## 🛠�?常用命令

### 重新生成配置
```bash
python scripts/auto-config-generator.py
```

### 添加新页�?
```bash
python quick-add-page.py
```

### 重新初始�?
```bash
python scripts/init-config.py
```

### 构建生产版本
```bash
npm run build
```

## 🔧 故障排除

### 端口冲突
1. 编辑 `project-config.json`
2. 修改 `frontendPort` �?`basePort`
3. 运行 `python scripts/auto-config-generator.py`

### Python 环境问题
```bash
# 检�?Python 版本
python --version

# 安装依赖
pip install flask flask-cors
```

### npm 依赖问题
```bash
# 清理并重新安�?
rm -rf node_modules package-lock.json
npm install
```

### SSE 连接问题
- 检查浏览器控制台错�?
- 确认后端服务正在运行
- 查看网络标签中的 EventSource 连接

## 📖 更多文档

- 📖 [技术实现详解](docs/TECHNICAL_DETAILS.md)
- 🛠�?[配置管理指南](docs/CONFIG_GUIDE.md)
- 🎯 [最佳实践](docs/BEST_PRACTICES.md)
- 🤝 [贡献指南](docs/CONTRIBUTING.md)

## 🆘 获取帮助

1. 🔍 查看 [技术实现详解](docs/TECHNICAL_DETAILS.md)
2. 💬 提交 [GitHub Issue](https://github.com/your-repo/issues)
3. 📖 查看项目 [Wiki](https://github.com/your-repo/wiki)
