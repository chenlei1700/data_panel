# 🔧 技術実装詳解

## コアAPI作業フロー：`/api/dashboard/updates`

### 🏗️ システムアーキテクチャ
```
┌─────────────────┐    SSE接続    ┌──────────────────┐    データ要求    ┌─────────────────┐
│  Vue Frontend   │ ◄──────────► │  Flask Backend   │ ◄───────────► │  Data Sources   │
│  (Dashboard)    │              │  (SSE Server)    │               │  (CSV/Database) │
└─────────────────┘              └──────────────────┘               └─────────────────┘
```

### 📊 完全作業フロー

#### **第一段階：接続確立**
```
1. 【Vue Dashboardコンポーネント】onMounted() 時に connectToUpdateStream() を呼び出し
   └── 実行関数：connectToUpdateStream()

2. 【Vue Dashboardコンポーネント】EventSource を /api/dashboard/updates に接続作成
   └── 実行関数：new EventSource(sseUrl)
   └── コールバック設定：eventSource.onopen, eventSource.onmessage, eventSource.onerror

3. 【Flaskバックエンド】SSE接続リクエストを受信、client_queue を作成
   └── 実行関数：dashboard_updates()
   └── 内部関数：event_stream()
   └── 作成：queue.Queue()

4. 【Flaskバックエンド】client_queue を sse_clients リストに追加
   └── 実行操作：sse_clients.append(client_queue)

5. 【Flaskバックエンド】現在の状態 latest_update をクライアントに即座に送信
   └── 実行関数：yield f"data: {json.dumps(latest_update)}\n\n"
   └── 呼び出し関数：process_message_queue()

6. 【Vue Dashboardコンポーネント】初期状態を受信してUIを更新
   └── コールバック発火：eventSource.onmessage(event)
   └── 実行関数：handleDashboardUpdate(data)
```

#### **第二段階：ユーザートリガー更新**
```
7. 【ユーザー】テーブル内のセクター名（例：「海運概念」）をクリック
   └── イベント発火：onclick="window.updateSectorDashboard('海運概念')"

8. 【TableComponentコンポーネント】updateDashboard() 関数を呼び出し
   └── 実行関数：updateDashboard(sector)
   └── 内部関数：fetch('http://localhost:5004/api/dashboard/update', {...})

9. 【TableComponentコンポーネント】/api/dashboard/update にPOSTリクエストを送信
   └── リクエスト方法：POST
   └── リクエストボディ：JSON.stringify({componentId: 'chart2', params: {sectors: sector}})

10. 【Flaskバックエンド】update_dashboard() がリクエストを受信して latest_update を更新
    └── 実行関数：update_dashboard()
    └── データ解析：request.json
    └── グローバル変数更新：latest_update = {...}

11. 【Flaskバックエンド】send_update_to_clients() を呼び出してメッセージをブロードキャスト
    └── 実行関数：send_update_to_clients(latest_update)
```

#### **第三段階：メッセージ伝達**
```
12. 【Flaskバックエンド】sse_clients リスト内のすべてのクライアントキューを走査
    └── 実行関数：send_update_to_clients(data)
    └── ループ操作：for client in list(sse_clients)

13. 【Flaskバックエンド】各 client_queue に更新メッセージを投入
    └── 実行操作：client.put(f"data: {json.dumps(data)}\n\n")

14. 【Flaskバックエンド】yield メカニズムを通じて接続されたすべてのクライアントにメッセージをプッシュ
    └── 実行関数：event_stream() 内の while True ループ
    └── ブロッキング取得：message = client_queue.get(block=True, timeout=30)
    └── データプッシュ：yield message

15. 【Vue Dashboardコンポーネント】EventSource.onmessage を通じて更新を受信
    └── コールバック発火：eventSource.onmessage(event)
    └── データ解析：JSON.parse(event.data)
```

#### **第四段階：UI更新**
```
16. 【Vue Dashboardコンポーネント】handleDashboardUpdate() を呼び出して受信データを処理
    └── 実行関数：handleDashboardUpdate(update)
    └── データ検証：if (!update || !update.params) return

17. 【Vue Dashboardコンポーネント】すべてのコンポーネントの dataSource URL を更新（新しいセクターパラメータを追加）
    └── ループ処理：layout.value.components.forEach(component => {...})
    └── URL処理：component.dataSource.split('?')[0]
    └── パラメータ処理：new URLSearchParams()
    └── パラメータ結合：Object.entries(update.params).forEach(...)

18. 【Vue Dashboardコンポーネント】'dashboard-update' カスタムイベントを発火
    └── 実行関数：setTimeout(() => { window.dispatchEvent(...) }, 100)
    └── イベント作成：new CustomEvent('dashboard-update', { detail: update })

19. 【各子コンポーネント】（ChartComponent、TableComponent）イベントを監視してデータを更新
    └── イベント監視：window.addEventListener('dashboard-update', handleDashboardUpdate)
    └── 実行関数：handleDashboardUpdate(event)
    └── 条件チェック：if (update && update.componentId === props.componentConfig.id)

20. 【各子コンポーネント】対応するAPIを再リクエストして新しいセクターのデータを取得
    └── 実行関数：refreshData()
    └── 内部呼び出し：fetchData(props.componentConfig.dataSource)
    └── APIリクエスト：axios.get(dataSourceUrl)

21. 【ユーザーUI】すべてのチャートとテーブルが新しいセクターのデータに同期更新
    └── データ更新：apiData.value = response.data
    └── UI再レンダリング：Vue響応システムが自動的にDOMを更新
```

### 🔄 並行処理
```
【複数のブラウザウィンドウ】複数のクライアントが接続されている場合：
- 【任意のクライアント】の操作がすべてのクライアントの更新をトリガー
  └── 共有関数：send_update_to_clients(data) がすべての sse_clients を走査
- 【すべてのクライアント】同じ更新メッセージを同時に受信
  └── 並列実行：各クライアントの eventSource.onmessage が同時に発火
- 【すべてのクライアント】UIが同期状態を維持
  └── 同期関数：各クライアントが同じ handleDashboardUpdate(update) を実行
```

### ⚠️ エラー処理
```
【Vue Dashboardコンポーネント】SSE接続が切断された場合：
- 【Vue Dashboardコンポーネント】自動再接続（5秒後）
  └── エラーコールバック：eventSource.onerror(error)
  └── 再接続関数：setTimeout(connectToUpdateStream, 5000)
- 【Flaskバックエンド】切断されたクライアントキューをクリーンアップ
  └── 例外処理：try/except ブロック内の sse_clients.remove(client)
- 【Vue Dashboardコンポーネント】接続状態インジケータを表示
  └── 状態更新：isConnected.value = false/true
  └── 計算プロパティ：connectionStatusText.value
```

## 🎯 主要関数まとめ

### Vueフロントエンド主要関数
- `connectToUpdateStream()` - SSE接続を確立
- `handleDashboardUpdate(update)` - 更新データを処理
- `updateDashboard(sector)` - 更新リクエストを送信
- `refreshData()` - コンポーネントデータを更新
- `fetchData(dataSource)` - APIデータを取得

### Flaskバックエンド主要関数
- `dashboard_updates()` - SSEエンドポイント関数
- `event_stream()` - SSEデータストリームジェネレーター
- `update_dashboard()` - 更新リクエストを受信
- `send_update_to_clients(data)` - メッセージをブロードキャスト
- `process_message_queue()` - メッセージキューを処理
- `notify_update()` - 通知を受信してエンキュー

## 💡 技術特徴

1. **リアルタイム性**：Server-Sent Events でサーバーからのプッシュ通知を実装
2. **コンポーネント間同期**：一つのコンポーネントの更新がすべての関連コンポーネントをトリガー
3. **マルチクライアントサポート**：複数のブラウザウィンドウの同時接続をサポート
4. **自動再接続**：接続が切断された際に自動的に再確立
5. **状態表示**：接続状態をリアルタイムで表示
6. **エラー処理**：完全な例外処理と再試行メカニズム

## 🚀 実際の効果

ユーザーがテーブル内の「海運概念」セクター名をクリックした場合：
- ✅ すべての関連チャートが海運概念のデータ表示に自動切り替え
- ✅ 複数のブラウザウィンドウが同期更新
- ✅ リアルタイムデータ更新、手動ページ更新不要
- ✅ 接続状態をユーザーにリアルタイムフィードバック

この完全な関数呼び出しチェーンで**リアルタイム、コンポーネント間、マルチクライアント**のデータ同期メカニズムを実現！

## 🔧 デバッグガイド

### フロントエンドデバッグ
```javascript
// ブラウザコンソールでSSE接続状態を確認
console.log('SSE接続状態:', eventSource.readyState);

// 受信データを監視
eventSource.onmessage = function(event) {
  console.log('SSEデータを受信:', JSON.parse(event.data));
};
```

### バックエンドデバッグ
```python
# Flaskサーバーにログを追加
import logging
logging.basicConfig(level=logging.DEBUG)

# クライアント接続数を監視
print(f"現在接続中のクライアント数: {len(sse_clients)}")
```

### ネットワークデバッグ
- ブラウザ開発者ツールの Network タブでSSE接続を確認
- EventSource 接続状態と受信データをチェック
- APIリクエストとレスポンスを監視

## 📊 TableComponent 機能詳解

### 🎨 背景色機能システム

TableComponent はテーブルの各列に動的背景色を設定することをサポートし、指定された計算関数を通じて各セルに異なる背景色を設定できます。この機能はヒートマップの作成、重要データのハイライト、数値範囲に基づく視覚化表示に使用できます。

#### 完全関数リスト

**基本関数 (4個)**
| 関数名 | 説明 | 適用シーン |
|--------|------|----------|
| `heatmap` | ヒートマップ着色 | 数値強度対比 |
| `redGreen` | 赤緑色階（正負値） | 騰落率、収益等 |
| `percentage` | パーセンテージ色階 | パーセンテージデータ |
| `rank` | ランク色階 | ランキングデータ |

**高度カスタム関数 (7個)**
| 関数名 | 説明 | 適用シーン |
|--------|------|----------|
| `stockStrength` | 株式強度総合評価 | 株式スクリーニング、投資判断 |
| `priceRange` | 価格区間着色 | 株価階層分析 |
| `limitUpGradient` | ストップ高グラデーション着色 | 連続ストップ高株分析 |
| `relativePerformance` | 相対パフォーマンス着色 | 相対ランキング分析 |
| `technicalAnalysis` ⭐ | 技術指標総合評価 | テクニカル分析 |
| `marketCapSize` ⭐ | 時価総額規模着色 | 時価総額階層分析 |

#### 使用例

**1. 基本設定**
```javascript
const tableConfig = {
  id: 'my-table',
  dataSource: 'http://api.example.com/data',
  // または直接データを渡す
  apiData: {
    columns: [
      { 
        field: 'name', 
        header: '株式名' 
      },
      { 
        field: 'price', 
        header: '価格',
        backgroundColor: 'heatmap' // 内蔵ヒートマップ関数を使用
      },
      { 
        field: 'change', 
        header: '騰落率',
        backgroundColor: 'redGreen' // 内蔵赤緑色階関数を使用
      }
    ],
    rows: [
      { name: '平安銀行', price: 12.5, change: 2.3 },
      { name: '招商銀行', price: 45.2, change: -1.8 }
    ]
  }
};
```

**2. サーバーサイド設定**
```python
# Python サーバー内で
@app.route('/api/table-data/stocks', methods=['GET'])
def get_stocks_table_data():
    columns = [
        {"field": "stock_name", "header": "株式名"},
        {
            "field": "price", 
            "header": "株価",
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

#### 技術指標総合評価 (technicalAnalysis)

**機能：** 複数の技術指標に基づく総合評価システム

**評価指標：**
- **RSI (25%重み):** 相対強弱指標
- **MACD (20%重み):** トレンド強弱判断
- **KDJ (20%重み):** 短期売買タイミング
- **移動平均線 (20%重み):** トレンド方向
- **出来高 (15%重み):** 価格と出来高の確認

**カラーマッピング：**
```javascript
スコア ≥ 8   → 深紅色    (テクニカル極強)
スコア ≥ 6   → 赤オレンジ色 (テクニカル強勢)
スコア ≥ 4   → オレンジ色  (テクニカル強め)
スコア ≥ 2   → 金色      (テクニカル中性強め)
スコア ≥ 0   → 薄青色    (テクニカル中性)
スコア ≥ -2  → 薄赤色    (テクニカル弱め)
スコア < -2  → 青グレー色 (テクニカル弱勢)
```

**サポート対象フィールド名：**
- RSI指標: `rsi`, `RSI`, `RSI指標`
- MACD指標: `macd`, `MACD`
- KDJ指標: `kdj_k`, `KDJ_K`, `k値`, `kdj_d`, `KDJ_D`, `d値`
- 移動平均線: `ma5`, `MA5`, `5日線`, `ma20`, `MA20`, `20日線`
- 現在価格: `price`, `close`, `現価`, `終値`
- 出来高比率: `volume_ratio`, `量比`, `セクター量比`

#### パラメータ渡しメカニズム

**データフロー：**
```
APIデータソース → apiData → sortedRows → テーブルレンダリング → getCellBackgroundColor → backgroundColorFunction
```

**関数呼び出し例：**
```javascript
// 「貴州茅台」行の「株価」列をレンダリングする際
getCellBackgroundColor(row['price'], column, row)

// 実際に渡されるパラメータ：
priceRange(
  1680.50,  // value - 現在セルの値
  { field: 'price', header: '株価', backgroundColor: 'priceRange' },  // column
  { stock_name: '貴州茅台', price: 1680.50, change: 2.5, rsi: 65.4 },  // row
  [ /* 完全データセット */ ]  // allRows
)
```

### 📋 列表示制御機能

TableComponent はテーブル列の表示・非表示制御をサポートします。列設定に `visible` 属性を追加することで、特定の列をフロントエンドで表示するかどうかを制御し、データを保持して他の列で使用できます。

#### 使用シーン
1. **補助データ列の非表示** - 特定の列（株式IDなど）はフロントエンドにリンク生成や他のロジックのために渡す必要があるが、テーブルには表示したくない場合
2. **条件付き列表示** - 異なるビジネスシーンに応じて、特定の列の表示状態を動的に制御
3. **データ関連付け** - 非表示の列データは他の列のレンダリング関数からアクセス可能

#### 設定例

**サーバーサイド設定：**
```python
columns = [
    {"field": "id", "header": "株式ID", "visible": False},  # 非表示列
    {"field": "stock_name", "header": "株式名"},           # 表示列
    {"field": "change", "header": "騰落率(%)", "backgroundColor": "redGreen"},
]
```

**フロントエンド処理：**
```vue
<!-- テンプレート内で visible !== false の列のみ表示 -->
<th v-for="column in apiColumns" :key="column.field">
  {{ column.header }}
</th>

<!-- セルレンダリング時に非表示列も含む全データにアクセス可能 -->
<td v-for="column in apiColumns" :key="column.field">
  <!-- 株式名は非表示の id 列データを使用可能 -->
  <span v-if="column.field === 'stock_name'" 
        v-html="renderStockLink(row[column.field], row['id'])">
  </span>
</td>
```

## 🧩 コンポーネントアーキテクチャ詳細解析
````
