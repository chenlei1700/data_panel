# 📚 BaseStockServer データソース設定詳解

## 🎯 コア概念説明

`BaseStockServer` フレームワークにおいて、`get_dashboard_config()` と `get_data_sources()` の二つのメソッドは異なる責任を担っており、フレームワークを正しく使用するためには、それらの違いを理解することが重要です。

## 📊 get_dashboard_config() - フロントエンドレイアウト設定

### 役割
`get_dashboard_config()` は**フロントエンドUIのレイアウトとコンポーネント設定**を定義し、フロントエンドに以下を指示します：
- ページに表示すべきコンポーネント
- コンポーネントの位置とサイズ
- 各コンポーネントがデータを取得すべきAPIエンドポイント

### dataSource の役割
`get_dashboard_config()` 内の `dataSource` は**APIエンドポイントパス**で、フロントエンドコンポーネントがデータ取得のために呼び出すべきURLを指定します。

```python
def get_dashboard_config(self) -> Dict[str, Any]:
    return {
        "layout": {
            "components": [
                {
                    "id": "chart1",
                    "type": "chart", 
                    "dataSource": "/api/chart-data/stock-trend",  # ← これはAPIエンドポイントURL
                    "title": "株式トレンドチャート",
                    "position": {"row": 0, "col": 0, "rowSpan": 1, "colSpan": 1}
                }
            ]
        }
    }
```

## 🔧 get_data_sources() - バックエンドデータ処理設定

### 役割
`get_data_sources()` は**APIエンドポイントとバックエンド処理関数の対応関係**を定義し、フレームワークに以下を指示します：
- 各APIパスがどの処理関数を呼び出すべきか
- キャッシュ設定
- その他のAPIメタ情報

```python
def get_data_sources(self) -> Dict[str, Any]:
    return {
        "/api/chart-data/stock-trend": {
            "handler": "get_stock_trend_data",  # ← これは処理関数名
            "description": "株式トレンドデータ",
            "cache_ttl": 30
        }
    }
```

## 🔄 データフロー

```
フロントエンド → APIリクエスト → フレームワーク → データ処理関数 → レスポンス
    ↑              ↑              ↑              ↑
dashboard_config  dataSource     data_sources   handler
```

## 📝 設定例

### 完全な例

```python
class MyStockServer(BaseStockServer):
    def get_dashboard_config(self):
        return {
            "layout": {
                "components": [
                    {
                        "id": "price_chart",
                        "type": "chart",
                        "dataSource": "/api/chart-data/price-trend",
                        "title": "価格トレンド"
                    },
                    {
                        "id": "stock_table", 
                        "type": "table",
                        "dataSource": "/api/table-data/stock-list",
                        "title": "株式一覧"
                    }
                ]
            }
        }
    
    def get_data_sources(self):
        return {
            "/api/chart-data/price-trend": {
                "handler": "get_price_trend_data",
                "description": "価格トレンドチャートデータ",
                "cache_ttl": 60
            },
            "/api/table-data/stock-list": {
                "handler": "get_stock_list_data", 
                "description": "株式一覧テーブルデータ",
                "cache_ttl": 30
            }
        }
    
    def get_price_trend_data(self):
        # 価格トレンドデータを返す
        return {"data": [...]}
    
    def get_stock_list_data(self):
        # 株式一覧データを返す
        return {"columns": [...], "rows": [...]}
```

## 🎯 ベストプラクティス

### 1. 命名規則
- APIパス: `/api/{type}-data/{specific-name}`
- ハンドラー: `get_{specific_name}_data`

### 2. データ形式
- チャートデータ: `{"data": [...], "labels": [...]}`
- テーブルデータ: `{"columns": [...], "rows": [...]}`

### 3. キャッシュ設定
- リアルタイムデータ: `cache_ttl: 10-30`
- 静的データ: `cache_ttl: 300-3600`

### 4. エラー処理
```python
def get_data_handler(self):
    try:
        # データ処理ロジック
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## 🔍 トラブルシューティング

### 一般的な問題

1. **404 エラー** - `data_sources` にAPIパスが定義されていない
2. **500 エラー** - ハンドラー関数が存在しないか例外が発生
3. **データが表示されない** - データ形式が期待される形式と一致しない

### デバッグ方法

```python
# ログを追加してデバッグ
def get_debug_data(self):
    print(f"データリクエスト受信: {datetime.now()}")
    result = self.process_data()
    print(f"データレスポンス: {len(result)} 件")
    return result
```

---

**重要**: `dataSource` はパスを指定し、`handler` は関数名を指定します。この区別を理解することがフレームワークの正しい使用の鍵です。
