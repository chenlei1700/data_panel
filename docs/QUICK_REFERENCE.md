# 📋 クイックリファレンス

**作成者**: chenlei

## 🚀 1分間で起動

```bash
# 1. 初期化（初回のみ）
python scripts/init-config.py

# 2. 依存関係インストール（初回のみ）
npm install

# 3. サービス開始
start-all-services.bat    # Windows
./start-all-services.sh   # Linux/Mac
```

**アクセス先**: http://localhost:8081

## 🎯 VS Code ワンクリック起動

1. `Ctrl+Shift+P` (Windows/Linux) または `Cmd+Shift+P` (Mac) を押下
2. "Tasks: Run Task" を入力
3. "🚀 启动所有服务" を選択

## 📁 コアファイル

| ファイル | 説明 | タイプ |
|------|------|------|
| `project-config.json` | 🎯 統一設定ファイル（コア） | 手動編集 |
| `auto-config-generator.py` | 🔧 自動設定生成 | ツールスクリプト |
| `init-config.py` | 🚀 プロジェクト初期化 | ツールスクリプト |
| `quick-add-page.py` | ➕ ページ高速追加 | ツールスクリプト |
| `api/show_plate_server_demo.py` | 🎯 デモサーバー | バックエンドサービス |

## 🌐 デフォルトポート

| サービス | ポート | アドレス |
|------|------|------|
| フロントエンド Vue | 8081 | http://localhost:8081 |
| バックエンド Flask | 5004 | http://localhost:5004 |
| デモページ | - | http://localhost:8081/demo_1 |

## 🛠️ よく使用するコマンド

### 設定再生成
```bash
python scripts/auto-config-generator.py
```

### 新しいページ追加
```bash
python quick-add-page.py
```

### 再初期化
```bash
python scripts/init-config.py
```

### 本番ビルド
```bash
npm run build
```

## 🔧 トラブルシューティング

### ポート競合
1. `project-config.json` を編集
2. `frontendPort` と `basePort` を修正
3. `python scripts/auto-config-generator.py` を実行

### Python環境問題
```bash
# Python バージョン確認
python --version

# 依存関係インストール
pip install flask flask-cors
```

### npm 依存関係問題
```bash
# クリーンアップと再インストール
rm -rf node_modules package-lock.json
npm install
```

### SSE 接続問題
- ブラウザコンソールエラーを確認
- バックエンドサービスが実行中であることを確認
- ネットワークタブでEventSource接続を確認

## 📖 詳細ドキュメント

- 📖 [技術実装詳解](docs/TECHNICAL_DETAILS.md)
- 🛠️ [設定管理ガイド](docs/CONFIG_GUIDE.md)
- 🎯 [ベストプラクティス](docs/BEST_PRACTICES.md)
- 🤝 [コントリビューションガイド](docs/CONTRIBUTING.md)

## 🆘 ヘルプ

1. 🔍 [技術実装詳解](docs/TECHNICAL_DETAILS.md) を確認
2. 💬 [GitHub Issue](https://github.com/your-repo/issues) を提出
3. 📖 プロジェクト [Wiki](https://github.com/your-repo/wiki) を確認
