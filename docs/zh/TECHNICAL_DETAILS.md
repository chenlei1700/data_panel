# 🔧 技术实现详解

## 核心API工作流程：`/api/dashboard/updates`

### 🏗️ 系统架构
```
┌─────────────────┐    SSE连接    ┌──────────────────┐    数据请求    ┌─────────────────┐
│  Vue Frontend   │ ◄──────────► │  Flask Backend   │ ◄───────────► │  Data Sources   │
│  (Dashboard)    │              │  (SSE Server)    │               │  (CSV/Database) │
└─────────────────┘              └──────────────────┘               └─────────────────┘
```

### 📊 完整工作流程

#### **第一阶段：连接建立**
```
1. 【Vue Dashboard组件】在 onMounted() 时调用 connectToUpdateStream()
   └── 执行函数：connectToUpdateStream()

2. 【Vue Dashboard组件】创建 EventSource 连接到 /api/dashboard/updates
   └── 执行函数：new EventSource(sseUrl)
   └── 设置回调：eventSource.onopen, eventSource.onmessage, eventSource.onerror

3. 【Flask后端】接收SSE连接请求，创建 client_queue
   └── 执行函数：dashboard_updates()
   └── 内部函数：event_stream()
   └── 创建：queue.Queue()

4. 【Flask后端】将 client_queue 添加到 sse_clients 列表
   └── 执行操作：sse_clients.append(client_queue)

5. 【Flask后端】立即发送当前状态 latest_update 给客户端
   └── 执行函数：yield f"data: {json.dumps(latest_update)}\n\n"
   └── 调用函数：process_message_queue()

6. 【Vue Dashboard组件】接收初始状态并更新界面
   └── 触发回调：eventSource.onmessage(event)
   └── 执行函数：handleDashboardUpdate(data)
```

#### **第二阶段：用户触发更新**
```
7. 【用户】在表格中点击板块名称（如"航运概念"）
   └── 触发事件：onclick="window.updateSectorDashboard('航运概念')"

8. 【TableComponent组件】调用 updateDashboard() 函数
   └── 执行函数：updateDashboard(sector)
   └── 内部函数：fetch('http://localhost:5004/api/dashboard/update', {...})

9. 【TableComponent组件】发送POST请求到 /api/dashboard/update
   └── 请求方法：POST
   └── 请求体：JSON.stringify({componentId: 'chart2', params: {sectors: sector}})

10. 【Flask后端】update_dashboard() 接收请求并更新 latest_update
    └── 执行函数：update_dashboard()
    └── 解析数据：request.json
    └── 更新全局变量：latest_update = {...}

11. 【Flask后端】调用 send_update_to_clients() 广播消息
    └── 执行函数：send_update_to_clients(latest_update)
```

#### **第三阶段：消息传递**
```
12. 【Flask后端】遍历 sse_clients 列表中的所有客户端队列
    └── 执行函数：send_update_to_clients(data)
    └── 循环操作：for client in list(sse_clients)

13. 【Flask后端】向每个 client_queue 放入更新消息
    └── 执行操作：client.put(f"data: {json.dumps(data)}\n\n")

14. 【Flask后端】通过 yield 机制将消息推送给所有连接的客户端
    └── 执行函数：event_stream() 中的 while True 循环
    └── 阻塞获取：message = client_queue.get(block=True, timeout=30)
    └── 推送数据：yield message

15. 【Vue Dashboard组件】通过 EventSource.onmessage 接收更新
    └── 触发回调：eventSource.onmessage(event)
    └── 解析数据：JSON.parse(event.data)
```

#### **第四阶段：界面更新**
```
16. 【Vue Dashboard组件】调用 handleDashboardUpdate() 处理接收到的数据
    └── 执行函数：handleDashboardUpdate(update)
    └── 验证数据：if (!update || !update.params) return

17. 【Vue Dashboard组件】更新所有组件的 dataSource URL（添加新的板块参数）
    └── 循环处理：layout.value.components.forEach(component => {...})
    └── URL处理：component.dataSource.split('?')[0]
    └── 参数处理：new URLSearchParams()
    └── 参数合并：Object.entries(update.params).forEach(...)

18. 【Vue Dashboard组件】触发 'dashboard-update' 自定义事件
    └── 执行函数：setTimeout(() => { window.dispatchEvent(...) }, 100)
    └── 事件创建：new CustomEvent('dashboard-update', { detail: update })

19. 【各个子组件】（ChartComponent、TableComponent）监听事件并刷新数据
    └── 事件监听：window.addEventListener('dashboard-update', handleDashboardUpdate)
    └── 执行函数：handleDashboardUpdate(event)
    └── 检查条件：if (update && update.componentId === props.componentConfig.id)

20. 【各个子组件】重新请求对应的API获取新板块的数据
    └── 执行函数：refreshData()
    └── 内部调用：fetchData(props.componentConfig.dataSource)
    └── API请求：axios.get(dataSourceUrl)

21. 【用户界面】所有图表和表格同步更新为新板块的数据
    └── 数据更新：apiData.value = response.data
    └── 界面重渲染：Vue响应式系统自动更新DOM
```

### 🔄 并发处理
```
【多个浏览器窗口】如果有多个客户端连接：
- 【任意一个客户端】的操作都会触发所有客户端更新
  └── 共享函数：send_update_to_clients(data) 遍历所有 sse_clients
- 【所有客户端】同时接收相同的更新消息
  └── 并行执行：每个客户端的 eventSource.onmessage 同时触发
- 【所有客户端】界面保持同步状态
  └── 同步函数：每个客户端都执行相同的 handleDashboardUpdate(update)
```

### ⚠️ 错误处理
```
【Vue Dashboard组件】SSE连接断开时：
- 【Vue Dashboard组件】自动重连（5秒后）
  └── 错误回调：eventSource.onerror(error)
  └── 重连函数：setTimeout(connectToUpdateStream, 5000)
- 【Flask后端】清理断开的客户端队列
  └── 异常处理：try/except 块中的 sse_clients.remove(client)
- 【Vue Dashboard组件】显示连接状态指示器
  └── 状态更新：isConnected.value = false/true
  └── 计算属性：connectionStatusText.value
```

## 🎯 关键函数汇总

### Vue前端关键函数
- `connectToUpdateStream()` - 建立SSE连接
- `handleDashboardUpdate(update)` - 处理更新数据
- `updateDashboard(sector)` - 发送更新请求
- `refreshData()` - 刷新组件数据
- `fetchData(dataSource)` - 获取API数据

### Flask后端关键函数
- `dashboard_updates()` - SSE端点函数
- `event_stream()` - SSE数据流生成器
- `update_dashboard()` - 接收更新请求
- `send_update_to_clients(data)` - 广播消息
- `process_message_queue()` - 处理消息队列
- `notify_update()` - 接收通知并入队

## 💡 技术特点

1. **实时性**：Server-Sent Events 实现服务器主动推送
2. **跨组件同步**：一个组件的更新触发所有相关组件更新
3. **多客户端支持**：支持多个浏览器窗口同时连接
4. **自动重连**：连接断开时自动重新建立
5. **状态指示**：实时显示连接状态
6. **错误处理**：完善的异常处理和重试机制

## 🚀 实际效果

当用户在表格中点击"航运概念"板块名称时：
- ✅ 所有相关图表自动切换到显示航运概念的数据
- ✅ 多个浏览器窗口同步更新
- ✅ 实时数据刷新无需手动刷新页面
- ✅ 连接状态实时反馈给用户

这个完整的函数调用链实现了**实时、跨组件、多客户端**的数据同步机制！

## 🔧 调试指南

### 前端调试
```javascript
// 在浏览器控制台查看SSE连接状态
console.log('SSE连接状态:', eventSource.readyState);

// 监控接收到的数据
eventSource.onmessage = function(event) {
  console.log('接收到SSE数据:', JSON.parse(event.data));
};
```

### 后端调试
```python
# 在Flask服务器中添加日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 监控客户端连接数
print(f"当前连接的客户端数量: {len(sse_clients)}")
```

### 网络调试
- 使用浏览器开发者工具的 Network 标签查看 SSE 连接
- 检查 EventSource 连接状态和接收到的数据
- 监控 API 请求和响应

## 📊 TableComponent 功能详解

### 🎨 背景色功能系统

TableComponent 支持为表格的每一列设置动态背景色，通过指定的计算函数来为每个单元格设定不同的背景色。这个功能可以用来创建热力图、突出显示重要数据、或者根据数值范围进行可视化展示。

#### 完整函数列表

**基础函数 (4个)**
| 函数名 | 描述 | 适用场景 |
|--------|------|----------|
| `heatmap` | 热力图着色 | 数值强度对比 |
| `redGreen` | 红绿色阶（正负值） | 涨跌幅、盈亏等 |
| `percentage` | 百分比色阶 | 百分比数据 |
| `rank` | 等级色阶 | 排名数据 |

**高级自定义函数 (7个)**
| 函数名 | 描述 | 适用场景 |
|--------|------|----------|
| `stockStrength` | 股票强势度综合评分 | 股票筛选、投资决策 |
| `priceRange` | 价格区间着色 | 股价分层分析 |
| `limitUpGradient` | 涨停板梯度着色 | 连板股分析 |
| `relativePerformance` | 相对表现着色 | 相对排名分析 |
| `technicalAnalysis` ⭐ | 技术指标综合评分 | 技术面分析 |
| `marketCapSize` ⭐ | 市值规模着色 | 市值分层分析 |

#### 使用示例

**1. 基本配置**
```javascript
const tableConfig = {
  id: 'my-table',
  dataSource: 'http://api.example.com/data',
  // 或者直接传入数据
  apiData: {
    columns: [
      { 
        field: 'name', 
        header: '股票名称' 
      },
      { 
        field: 'price', 
        header: '价格',
        backgroundColor: 'heatmap' // 使用内置的热力图函数
      },
      { 
        field: 'change', 
        header: '涨跌幅',
        backgroundColor: 'redGreen' // 使用内置的红绿色阶函数
      }
    ],
    rows: [
      { name: '平安银行', price: 12.5, change: 2.3 },
      { name: '招商银行', price: 45.2, change: -1.8 }
    ]
  }
};
```

**2. 服务器端配置**
```python
# 在 Python 服务器中
@app.route('/api/table-data/stocks', methods=['GET'])
def get_stocks_table_data():
    columns = [
        {"field": "stock_name", "header": "股票名称"},
        {
            "field": "price", 
            "header": "股价",
            "backgroundColor": {
                "type": "custom",
                "function": "priceRange",
                "params": {
                    "ranges": [
                        {"min": 0, "max": 20, "color": "rgba(255, 165, 0, 0.3)"},
                        {"min": 20, "max": 50, "color": "rgba(255, 255, 0, 0.3)"},
                        {"min": 50, "max": 100, "color": "rgba(0, 255, 0, 0.3)"}
                    ]
                }
            }
        }
    ]
    
    return jsonify({
        "columns": columns,
        "rows": rows
    })
```

#### 技术指标综合评分 (technicalAnalysis)

**功能：** 基于多个技术指标的综合评分系统

**评分指标：**
- **RSI (25%权重):** 相对强弱指标
- **MACD (20%权重):** 趋势强弱判断
- **KDJ (20%权重):** 短期买卖时机
- **移动平均线 (20%权重):** 趋势方向
- **成交量 (15%权重):** 量价确认

**颜色映射：**
```javascript
评分 ≥ 8   → 深红色    (技术面极强)
评分 ≥ 6   → 红橙色    (技术面强势)
评分 ≥ 4   → 橙色      (技术面偏强)
评分 ≥ 2   → 金色      (技术面中性偏强)
评分 ≥ 0   → 浅蓝色    (技术面中性)
评分 ≥ -2  → 浅红色    (技术面偏弱)
评分 < -2  → 蓝灰色    (技术面弱势)
```

**支持的字段名：**
- RSI指标: `rsi`, `RSI`, `RSI指标`
- MACD指标: `macd`, `MACD`
- KDJ指标: `kdj_k`, `KDJ_K`, `k值`, `kdj_d`, `KDJ_D`, `d值`
- 移动平均线: `ma5`, `MA5`, `5日线`, `ma20`, `MA20`, `20日线`
- 当前价格: `price`, `close`, `现价`, `收盘价`
- 成交量比率: `volume_ratio`, `量比`, `板块量比`

#### 参数传递机制

**数据流向：**
```
API数据源 → apiData → sortedRows → 表格渲染 → getCellBackgroundColor → backgroundColorFunction
```

**函数调用示例：**
```javascript
// 当渲染"贵州茅台"行的"股价"列时
getCellBackgroundColor(row['price'], column, row)

// 实际传递的参数：
priceRange(
  1680.50,  // value - 当前单元格值
  { field: 'price', header: '股价', backgroundColor: 'priceRange' },  // column
  { stock_name: '贵州茅台', price: 1680.50, change: 2.5, rsi: 65.4 },  // row
  [ /* 完整数据集 */ ]  // allRows
)
```

### 📋 列显示控制功能

TableComponent 支持控制表格列的显示和隐藏。通过在列配置中添加 `visible` 属性，可以控制某些列是否在前端显示，同时保留数据供其他列使用。

#### 使用场景
1. **隐藏辅助数据列** - 某些列（如股票ID）需要传递给前端用于生成链接或其他逻辑，但不希望在表格中显示
2. **条件显示列** - 根据不同的业务场景，动态控制某些列的显示状态
3. **数据关联** - 隐藏的列数据仍然可以被其他列的渲染函数访问

#### 配置示例

**服务器端配置：**
```python
columns = [
    {"field": "id", "header": "股票ID", "visible": False},  # 隐藏列
    {"field": "stock_name", "header": "股票名称"},           # 显示列
    {"field": "change", "header": "涨幅(%)", "backgroundColor": "redGreen"},
]
```

**前端处理：**
```vue
<!-- 模板中只显示 visible !== false 的列 -->
<th v-for="column in apiColumns" :key="column.field">
  {{ column.header }}
</th>

<!-- 单元格渲染时可以访问所有数据，包括隐藏列 -->
<td v-for="column in apiColumns" :key="column.field">
  <!-- 股票名称可以使用隐藏的 id 列数据 -->
  <span v-if="column.field === 'stock_name'" 
        v-html="renderStockLink(row[column.field], row['id'])">
  </span>
</td>
```

## 🧩 组件架构深度解析
````
