# 📋 統一設定管理システム使用ガイド

**作成者**: chenlei

## 🌟 概要

新しいページ追加の煩雑な手順を簡素化するため、統一設定管理システムを設計しました：

- **📄 project-config.json** - 統一設定ファイル、すべてのページとサービスの設定情報を含む
- **🤖 auto-config-generator.py** - 自動生成器、設定ファイルに基づいて必要なコードファイルをすべて生成
- **➕ quick-add-page.py** - ページ高速追加ツール、対話式で新ページを作成

## 🚀 クイックスタート

### 1. プロジェクト設定初期化

```bash
# 現在の設定を確認
cat project-config.json

# すべての設定ファイルを生成
python scripts/auto-config-generator.py
```

### 2. 新ページ追加（推奨方法）

```bash
# 対話式で新ページを追加
python quick-add-page.py

# サンプルページを一括追加
python quick-add-page.py batch
```

### 3. 手動設定（上級者向け）

```bash
# project-config.json を直接編集
# 新サービスを services 配列に追加
# 自動生成器を実行
python scripts/auto-config-generator.py
```

## 📋 設定ファイル構造

### project-config.json 詳細

```json
{
  "projectInfo": {
    "name": "プロジェクト名",
    "description": "プロジェクト説明", 
    "version": "バージョン番号",
    "basePort": 5001,              // 開始ポート番号
    "frontendPort": 8080,          // フロントエンドポート
    "pythonExecutable": "python"   // Python 実行ファイル
  },
  "services": [
    {
      "id": "StockDashboard_example",           // サービス一意識別子
      "name": "サンプル分析",                   // 表示名
      "description": "機能説明",                // 機能説明
      "icon": "📊",                            // アイコン
      "port": 5004,                            // ポート番号
      "path": "/stock-dashboard-example",       // URL パス
      "title": "サンプル分析ダッシュボード",     // ページタイトル
      "serverFile": "show_plate_server_example.py",  // サーバーファイル
      "component": "StockDashboard",            // Vue コンポーネント
      "taskLabel": "サンプル分析サーバー",      // VS Code タスクラベル
      "enabled": true                           // 有効かどうか
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
    "pythonPath": "Python インタープリター パス",
    "apiBasePath": "./api",                // API ファイル相対パス（相対パス推奨）
    "autoOpenBrowser": true,
    "enableHotReload": true
  }
}
```

## 🔧 ツール説明

### auto-config-generator.py

自動設定ジェネレーター、`project-config.json` に基づいて必要な設定ファイルをすべて生成：

```bash
# すべての設定ファイルを生成
python scripts/auto-config-generator.py

# ヘルプ情報を表示
python scripts/auto-config-generator.py --help
```

**生成されるファイル:**
- `src/config/api.js` - API 設定
- `src/router/index.js` - ルーティング設定
- `src/views/Home.vue` - ホームページコンポーネント
- `.vscode/tasks.json` - VS Code タスク設定
- `start-all-services.bat/sh` - 起動スクリプト

### quick-add-page.py

ページ高速追加ツール、インタラクティブインターフェースを提供：

```bash
# インタラクティブに新しいページを追加
python quick-add-page.py

# サンプルページを一括追加
python quick-add-page.py batch

# ヘルプ情報を表示
python quick-add-page.py --help
```

**追加フロー:**
1. ページ基本情報を入力
2. ポート番号を自動割り当て
3. サーバーファイルテンプレートを生成
4. すべての設定ファイルを更新
5. オプションでサービスを即座に起動

## 📝 使用例

### 例1：AI分析ページを追加

```bash
python quick-add-page.py
```

入力情報：
- サービス ID: `StockDashboard_ai`
- サービス名: `AI インテリジェント分析`
- 機能説明: `機械学習ベースの株式トレンド予測`
- アイコン: `🤖` を選択

自動生成：
- ポート: `5004`
- パス: `/stock-dashboard-ai`
- サーバーファイル: `api/show_plate_server_stockdashboard_ai.py`

### 例2：手動設定による複数ページ

`project-config.json` を編集：

```json
{
  "services": [
    // 既存のサービス...
    {
      "id": "StockDashboard_news",
      "name": "ニュース分析",
      "description": "リアルタイムニュース感情分析",
      "icon": "📰",
      "port": 5005,
      "path": "/stock-dashboard-news",
      "title": "ニュース分析ダッシュボード",
      "serverFile": "show_plate_server_news.py",
      "component": "StockDashboard",
      "taskLabel": "ニュース分析サーバー",
      "enabled": true
    }
  ]
}
```

その後実行：
```bash
python scripts/auto-config-generator.py
```

## 🔄 ワークフロー

### 従来の方法（煩雑）
1. Python サーバーファイルを作成
2. `src/config/api.js` を修正
3. `src/router/index.js` を修正
4. `src/views/Home.vue` を修正
5. `.vscode/tasks.json` を修正
6. 起動スクリプトを更新
7. テストとデバッグ

### 新しい方法（簡素化）
1. `python quick-add-page.py` を実行
2. ページ情報を入力
3. すべてのファイルを自動生成
4. ビジネスロジックを編集（オプション）
5. サービスを起動

## 🎯 ベストプラクティス

### 1. 命名規約
- **サービス ID**: `StockDashboard_` プレフィックスを使用、例：`StockDashboard_ai`
- **ファイル名**: 小文字とアンダースコアを使用、例：`show_plate_server_ai.py`
- **パス**: ハイフンを使用、例：`/stock-dashboard-ai`

### 2. ポート管理
- システムが自動的にポートを割り当て、競合を回避
- 推奨範囲：5001-5099
- フロントエンドは固定で 8080 を使用

### 3. 開発フロー
1. 最初にツールを使用して基本フレームワークを生成
2. 生成されたサーバーファイルでビジネスロジックを実装
3. API エンドポイントをテスト
4. フロントエンド表示を最適化

### 4. 設定管理
- 定期的に `project-config.json` をバックアップ
- バージョン管理に設定ファイルを含める
- チーム開発時は設定を同期

## 🛠️ カスタム設定

### デフォルトテンプレートの修正

`quick-add-page.py` の `create_server_template` メソッドを編集してサーバーファイルテンプレートをカスタマイズ。

### API エンドポイントの修正

`project-config.json` の `apiEndpoints` 部分で修正：

```json
{
  "apiEndpoints": {
    "dashboardConfig": "/api/dashboard-config",
    "chartData": "/api/chart-data",
    "tableData": "/api/table-data",
    "updates": "/api/dashboard/updates",
    "health": "/health",
    "customEndpoint": "/api/custom"  // カスタムエンドポイントを追加
  }
}
```

### 環境設定

`developmentConfig` 部分で開発環境を設定：

```json
{
  "developmentConfig": {
    "pythonPath": "C:/Python39/python.exe",
    "apiBasePath": "D:/project/api",
    "autoOpenBrowser": true,
    "enableHotReload": true
  }
}
```

## 🔍 トラブルシューティング

### よくある問題

1. **ポート競合**
   - ポートが使用中かどうかをチェック
   - 設定ファイルのポート番号を修正

2. **Python パスエラー**
   - `developmentConfig.pythonPath` を更新
   - Python 環境が正しいかチェック

3. **設定ファイルフォーマットエラー**
   - JSON 検証ツールを使用して構文をチェック
   - すべてのフィールドが正しく記入されているか確認

4. **サービス起動失敗**
   - 依存パッケージがインストールされているかチェック
   - エラーログを確認

### デバッグコマンド

```bash
# 設定ファイル構文をチェック
python -m json.tool project-config.json

# 環境を検証
python check-environment.py

# サービス状態を確認
curl http://localhost:5001/health
```

## 📈 高度な使用方法

### バッチ操作

バッチ設定ファイル `batch-config.json` を作成：

```json
[
  {
    "id": "StockDashboard_ml",
    "name": "機械学習分析",
    "description": "深層学習ベースの株価予測",
    "icon": "🧠"
  },
  {
    "id": "StockDashboard_sentiment",
    "name": "感情分析",
    "description": "ソーシャルメディア感情分析",
    "icon": "😊"
  }
]
```

その後バッチで追加：

```bash
python -c "
import json
from quick_add_page import QuickPageAdder

with open('batch-config.json', 'r') as f:
    services = json.load(f)

adder = QuickPageAdder()
adder.batch_add(services)
"
```

### カスタムコンポーネント

デフォルトの `StockDashboard` ではなくカスタム Vue コンポーネントを使用する場合：

1. 新しい Vue コンポーネントを作成
2. 設定で `component` フィールドを指定
3. 設定ファイルを再生成

## 🎉 まとめ

この統一設定管理システムにより、新しいページの追加が従来の7ステップから以下に簡素化されました：

1. ⚡ `python quick-add-page.py` を実行
2. ✏️ ページ情報を入力
3. 🚀 サービスを起動してテスト

開発効率が大幅に向上し、エラーの可能性が減少し、開発者が設定管理ではなくビジネスロジックに集中できるようになりました。

## 🎯 システムの利点

1. **統一管理** - すべての設定を一箇所で管理
2. **自動化** - 手動ファイル編集の削減
3. **エラー防止** - 自動生成によるミス削減
4. **高速開発** - 新ページ追加時間の大幅短縮
5. **保守性向上** - 明確な設定構造

## 📚 詳細ドキュメント

- [設定ガイド](CONFIG_GUIDE.md) - 詳細な設定項目説明
- [ページマイグレーションガイド](NEW_PAGE_MIGRATION_GUIDE.md) - 既存サービスの移行方法
- [データソース設定ガイド](DATA_SOURCE_CONFIGURATION_GUIDE.md) - APIとデータソース設定

## 🔧 トラブルシューティング

### よくある問題
1. **設定が反映されない** → 自動生成器を再実行
2. **ポート競合** → project-config.json でポート番号を変更
3. **VS Code タスクが表示されない** → VS Code を再起動

---

このシステムにより、新ページ追加が従来の複数ファイル編集から単一設定変更に簡素化されます。
