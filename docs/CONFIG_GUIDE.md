# 📋 設定管理ガイド

**作成者**: chenlei

## 🎯 統一設定システム

プロジェクトでは `project-config.json` を唯一の設定ファイルとして採用し、すべてのフロントエンド・バックエンド設定がこのファイルから自動生成されます。

### 📄 設定ファイル構造

```json
{
  "projectInfo": {
    "name": "データ可視化システム",
    "description": "リアルタイム株式データ分析・可視化プラットフォーム",
    "version": "1.0.0",
    "basePort": 5004,
    "frontendPort": 8081,
    "pythonExecutable": "python"
  },
  "services": [
    {
      "id": "demo_1",
      "name": "デモダッシュボード",
      "description": "モックデータを使用した完全機能デモ",
      "icon": "🎯",
      "port": 5004,
      "path": "/demo_1",
      "title": "データ可視化デモ",
      "serverFile": "show_plate_server_demo.py",
      "component": "StockDashboard",
      "taskLabel": "デモサーバー",
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

## 🔧 設定管理ワークフロー

### 1. 設定変更
- `project-config.json` を編集
- 新しいサービス、ポート、ルートを追加

### 2. 自動生成実行
```bash
python scripts/auto-config-generator.py
```

### 3. 生成されるファイル
- `src/config/api.js` - フロントエンド API 設定
- `src/router/index.js` - Vue ルーター設定
- `.vscode/tasks.json` - VS Code タスク設定
- `vue.config.js` - Vue 開発サーバー設定

## 📝 設定項目説明

### プロジェクト基本情報
- `name`: プロジェクト名
- `description`: プロジェクト説明
- `version`: バージョン番号
- `basePort`: バックエンドベースポート
- `frontendPort`: フロントエンドポート

### サービス設定
- `id`: サービス一意識別子
- `name`: サービス表示名
- `port`: サービスポート
- `serverFile`: バックエンドファイル名
- `component`: フロントエンドコンポーネント名
- `enabled`: サービス有効化フラグ

### API エンドポイント
- 標準化された API パス設定
- 各サービスで統一されたエンドポイント

### 開発設定
- Python 実行パス
- API ファイルパス
- 開発支援機能の設定

## 🎯 ベストプラクティス

1. **統一設定原則** - すべての設定を `project-config.json` に集約
2. **自動生成** - 手動設定ファイル編集を避ける
3. **バージョン管理** - 設定ファイルのみをバージョン管理対象に
4. **環境設定** - 異なる環境ごとに異なる設定ファイルを使用

## 🔍 トラブルシューティング

### 設定が反映されない
```bash
# 設定を再生成
python scripts/auto-config-generator.py

# サービスを再起動
start-all-services.bat
```

### ポート競合
- `project-config.json` でポート番号を変更
- 自動生成スクリプトを再実行

### VS Code タスクが表示されない
- VS Code を再起動
- 設定ファイルが正しく生成されているか確認

---

**注意**: 自動生成されたファイルは直接編集しないでください。すべての変更は `project-config.json` を通じて行ってください。
