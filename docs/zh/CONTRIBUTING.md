# 🤝 贡献指南

**项目作者**: chenlei

## 👋 欢迎贡献

感谢您对股票仪表盘系统项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🎯 开发新功能
- 🎨 UI/UX 改进

## 🚀 快速开始

### 开发环境设置

1. **Fork 项目**
   ```bash
   # 从 GitHub 上 Fork 项目到你的账号
   git clone https://github.com/your-username/vue-project.git
   cd vue-project
   ```

2. **设置开发环境**
   ```bash
   # 配置项目
   python scripts/init-config.py
   
   # 安装依赖
   npm install
   
   # 启动开发服务
   python scripts/auto-config-generator.py
   start-all-services.bat  # Windows
   ./start-all-services.sh # Linux/Mac
   ```

3. **验证环境**
   - 访问 http://localhost:8081 确认前端正常
   - 访问 http://localhost:5004/health 确认后端正常

## 📋 贡献类型

### 🐛 Bug 报告

**使用 GitHub Issues 报告 Bug，请包含：**

1. **Bug 描述** - 清楚简洁地描述问题
2. **复现步骤** - 详细的步骤说明
3. **预期行为** - 说明您期望的正确行为
4. **实际行为** - 说明实际发生的情况
5. **环境信息**：
   - 操作系统：Windows/macOS/Linux
   - Node.js 版本：`node --version`
   - Python 版本：`python --version`
   - 浏览器：Chrome/Firefox/Safari 及版本
6. **截图或录制**（如果适用）
7. **错误日志**（浏览器控制台或服务器日志）

**Bug 报告模板：**
```markdown
**Bug 描述**
简洁清楚地描述这个 bug

**复现步骤**
1. 打开 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

**预期行为**
清楚简洁地描述您期望发生的事情

**截图**
如果适用，添加截图来帮助解释您的问题

**环境信息：**
 - 操作系统: [e.g. Windows 10]
 - Node.js: [e.g. 16.14.0]
 - Python: [e.g. 3.9.7]
 - 浏览器: [e.g. Chrome 96.0.4664.110]

**附加信息**
在此处添加有关问题的任何其他信息
```

### 💡 功能建议

**提出新功能建议时，请说明：**

1. **功能概述** - 简要描述建议的功能
2. **使用场景** - 解释何时何地会用到这个功能
3. **期望的解决方案** - 描述您希望的实现方式
4. **替代方案** - 考虑过的其他解决方案
5. **影响评估** - 对现有功能的潜在影响

### 📝 文档改进

文档贡献同样重要！您可以：

- 修正拼写或语法错误
- 添加使用示例
- 改进 API 文档
- 增加最佳实践说明
- 翻译文档到其他语言

## 🔧 开发指南

### 代码规范

#### JavaScript/Vue.js 规范

```javascript
// 使用 2 个空格缩进
// 使用 ES6+ 语法
// 变量命名使用 camelCase
const userName = 'example'

// 函数命名要有描述性
function calculateStockPrice(basePrice, changePercent) {
  return basePrice * (1 + changePercent / 100)
}

// Vue 组件使用 PascalCase
export default {
  name: 'StockDashboard',
  props: {
    // 定义 prop 类型
    config: {
      type: Object,
      required: true
    }
  }
}
```

#### Python 规范

```python
# 遵循 PEP 8 规范
# 使用 4 个空格缩进
# 函数名使用 snake_case
def calculate_stock_score(price, volume, change):
    """计算股票评分
    
    Args:
        price (float): 股票价格
        volume (int): 成交量
        change (float): 涨跌幅
    
    Returns:
        float: 综合评分
    """
    return (price * 0.4 + volume * 0.3 + change * 0.3)

# 类名使用 PascalCase
class StockAnalyzer:
    def __init__(self, data):
        self.data = data
```

### 提交规范

#### Git 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响代码运行）
- `refactor`: 重构代码
- `test`: 添加测试
- `chore`: 构建过程或辅助工具的变动

**范围 (scope)：**
- `frontend`: 前端相关
- `backend`: 后端相关
- `config`: 配置相关
- `docs`: 文档相关

**示例：**
```bash
feat(frontend): 添加股票技术分析背景色函数

- 新增 technicalAnalysis 函数
- 支持 RSI、MACD、KDJ 指标综合评分
- 提供 7 种颜色梯度显示技术面强弱

Closes #123
```

### 分支管理

```bash
# 创建功能分支
git checkout -b feature/add-technical-analysis

# 创建修复分支
git checkout -b fix/dashboard-loading-issue

# 创建文档分支
git checkout -b docs/update-api-guide
```

### Pull Request 流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发和测试**
   - 编写代码
   - 添加必要的测试
   - 更新相关文档

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   git push origin feature/your-feature-name
   ```

4. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 填写 PR 模板
   - 等待代码审查

#### PR 模板

```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 重构
- [ ] 文档更新
- [ ] 样式改进

## 变更描述
简要描述这个 PR 的目的和实现方式

## 测试
- [ ] 添加了新的测试用例
- [ ] 现有测试通过
- [ ] 手动测试通过

## 截图（如果适用）

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 自测通过
- [ ] 更新了相关文档
- [ ] 没有引入新的警告
```

## 🔍 测试指南

### 前端测试

```bash
# 运行前端测试
npm test

# 运行测试覆盖率
npm run test:coverage
```

### 后端测试

```bash
# 运行后端测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_api.py
```

### 手动测试

1. **功能测试**
   - 验证新功能按预期工作
   - 确认不影响现有功能

2. **兼容性测试**
   - 测试不同浏览器
   - 测试不同屏幕尺寸

3. **性能测试**
   - 检查加载时间
   - 监控内存使用

## 📚 代码审查

### 审查要点

**功能性：**
- 代码是否实现了预期功能？
- 是否有逻辑错误？
- 边界条件是否处理正确？

**可读性：**
- 代码是否易于理解？
- 命名是否清晰有意义？
- 注释是否充分？

**性能：**
- 是否有性能问题？
- 算法是否高效？
- 是否有内存泄漏？

**安全性：**
- 是否存在安全漏洞？
- 输入验证是否充分？
- 敏感信息是否正确处理？

### 审查礼仪

- 保持建设性和友善的语调
- 专注于代码，而不是个人
- 提供具体的改进建议
- 承认好的代码和想法

## 🏆 贡献者认可

我们会在以下地方认可贡献者：

- README 中的贡献者列表
- 发布说明中的感谢
- 项目网站（如果有）

### 贡献者级别

- **💎 核心贡献者** - 长期活跃，多次重要贡献
- **🌟 活跃贡献者** - 定期贡献代码或文档
- **👍 贡献者** - 至少有一次合并的 PR
- **🐛 Bug 报告者** - 报告有效 Bug
- **💡 想法贡献者** - 提出有价值的建议

## 📞 获取帮助

遇到问题时，可以通过以下方式寻求帮助：

1. **查看文档**
   - [快速参考](../QUICK_REFERENCE.md)
   - [技术详解](TECHNICAL_DETAILS.md)
   - [配置指南](CONFIG_GUIDE.md)

2. **GitHub Discussions**
   - 提出问题和讨论
   - 分享想法和经验

3. **GitHub Issues**
   - 报告 Bug
   - 请求新功能

## 📄 许可证

通过贡献代码，您同意您的贡献将在与项目相同的 [MIT 许可证](../LICENSE) 下进行许可。

---

再次感谢您的贡献！让我们一起打造更好的股票仪表盘系统！ 🚀
