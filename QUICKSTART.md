# 🚀 クイックスタートガイド - 5分でデータ可視化システムをマスター

## 📋 環境チェックリスト

開始前に、環境が以下の要件を満たしていることを確認してください：

### 必須環境
- ✅ **Python 3.7+** - バックエンドサービス実行環境
- ✅ **Node.js 16+** - フロントエンドビルド環境  
- ✅ **npm または yarn** - パッケージ管理ツール
- ✅ **Git** - バージョン管理ツール

### オプションツール
- 🔧 **VS Code** - 推奨開発環境
- 🐳 **Docker** - コンテナ化デプロイ
- 📊 **Chrome/Firefox** - モダンブラウザ

## 🎯 30秒クイック検証

```bash
# 1. プロジェクトをクローン
git clone [your-repo-url]
cd vue-project

# 2. ワンクリック環境チェック
python scripts/check-environment.py

# 3. チェックが通った場合、直接起動
python scripts/init-config.py  # 初回実行
```

## ⚡ 5分完全起動

> **🆕 新フレームワークの利点**: 本プロジェクトは現在、最適化されたBaseStockServerフレームワークを使用し、自動ルート登録、インテリジェントキャッシュ、標準化APIなどの機能を提供して、開発をより簡単で効率的にします！

### ステップ1: 環境初期化 (1分)
```bash
# プロジェクト設定を初期化
python scripts/init-config.py

# Python 依存関係をインストール
pip install -r requirements.txt

# Node.js 依存関係をインストール
npm install
```

### ステップ2: サービス起動 (1分)

#### 方法A: VS Code ユーザー (推奨)
1. VS Code を開く
2. `Ctrl+Shift+P` を押す
3. "Tasks: Run Task" を入力
4. "🚀 すべてのサービスを起動" を選択

#### 方法B: コマンドラインユーザー
```bash
# Windows
.\start-all-services.bat

# Linux/Mac
./start-all-services.sh

# 手動起動
python api/show_plate_server_v2.py 5004 &
npm run serve &
```

### ステップ3: デプロイ検証 (1分)
```bash
# バックエンドサービスをチェック
curl http://localhost:5004/health

# ブラウザでフロントエンドにアクセス
# http://localhost:8080
```

### ステップ4: 機能探索 (2分)
1. **フロントエンド画面** - `http://localhost:8080` にアクセス
2. **APIテスト** - `http://localhost:5004/api/chart-data/stock-trend` にアクセス
3. **ヘルス監視** - プロジェクトルートディレクトリの `public/api-detector.html` にアクセス
4. **新フレームワークの利点**：
   - 🚀 **自動ルート登録** - 手動でAPIルートを設定する必要なし
   - 🔄 **インテリジェントキャッシュ** - 自動データキャッシュと更新
   - 📊 **標準化API** - 統一されたデータソース設定フォーマット
   - ⚡ **高速開発** - BaseStockServerを継承するだけで新しいサービスを迅速に作成

## 🛠️ 開発者ワークフロー

### 日常開発サイクル
```bash
# 1. コード品質チェック
python scripts/quality-check.py

# 2. テスト実行
python -m pytest tests/ --cov=api

# 3. 開発サービス起動
# VS Code: Ctrl+Shift+P → "🚀 すべてのサービスを起動"

# 4. 開発とデバッグ
# コードを修正し、ブラウザが自動リフレッシュ

# 5. コミット前チェック
python scripts/quality-check.py
python tests/backend/test_api_integration.py
```

### 新しいページの追加
```bash
# 高速追加ツールを使用
python scripts/quick-add-page.py

# プロンプトに従ってページ情報を入力
# システムが必要なファイルをすべて自動生成
```

### 複数バックエンドサービスの設定 (重要)

⚠️ **重要ステップ**：新しいバックエンドサービスを追加する場合、フロントエンドプロキシ設定を手動で更新する必要があります！

#### 1. プロキシ設定が必要な理由
- フロントエンド (ポート8081) は複数のバックエンドサーバー (ポート5004, 5003, 5002など) にアクセスする必要
- ブラウザの同一オリジンポリシーがクロスドメインリクエストをブロック
- Vue.js 開発サーバーがプロキシ機能でこの問題を解決

#### 2. vue.config.js を手動更新
```javascript
// vue.config.js - 手動編集が必要
module.exports = {
  publicPath: '/',
  devServer: {
    port: 8081,
    proxy: {
      // メインサーバー (デフォルト)
      '/api': {
        target: 'http://localhost:5004',
        changeOrigin: true,
        logLevel: 'debug'
      },
      
      // 新しいサーバー - 類似の設定を追加
      '/api/new-service': {
        target: 'http://localhost:XXXX',  // 新しいサーバーポート
        changeOrigin: true,
        pathRewrite: {
          '^/api/new-service': '/api'  // パスプレフィックスを削除
        }
      }
    }
  }
}
```

#### 3. フロントエンド呼び出し方法
```javascript
// メインサーバーを呼び出し
axios.get('/api/dashboard-config')

// 新しいサーバーを呼び出し  
axios.get('/api/new-service/table-data/your-data')
```

#### 4. 重要な注意事項
- ⚠️ `vue.config.js` は自動設定ジェネレーターによって更新されません
- 🔄 変更後はフロントエンドサービスを再起動する必要があります: `npm run serve`
- 📋 ポート設定は `project-config.json` と一致する必要があります
- 📖 詳細については `docs/NEW_PAGE_MIGRATION_GUIDE.md` を参照してください

## 🔧 よくある問題の解決

### 問題1: ポートが使用中
```bash
# ポート使用状況をチェック
netstat -ano | findstr :5004  # Windows
lsof -i :5004                 # Linux/Mac

# ポート設定を修正
# project-config.json を編集
python scripts/auto-config-generator.py
```

### 問題2: 依存関係インストール失敗
```bash
# Python 依存関係の問題
pip install --upgrade pip
pip install -r requirements.txt

# Node.js 依存関係の問題
npm cache clean --force
npm install
```

### 問題3: サービス起動失敗
```bash
# エラーログをチェック
python scripts/check-environment.py

# 設定を再生成
python scripts/init-config.py

# サービスを個別に起動してデバッグ
python api/show_plate_server_v2.py 5004
```

### 問題4: フロントエンドがバックエンドAPIにアクセスできない (よくある問題)
```bash
# 症状：フロントエンドページに「ネットワークエラー」または「データを取得できません」が表示

# 解決手順：
# 1. バックエンドサービスが実行中かチェック
curl http://localhost:5004/health

# 2. フロントエンドプロキシ設定をチェック
# vue.config.js を編集し、プロキシ設定が正しいことを確認

# 3. フロントエンドサービスを再起動
# Ctrl+C で停止、その後再実行：
npm run serve

# 4. プロキシが有効かどうか検証
# ブラウザ開発者ツール → Network パネルでリクエストを確認
```

### 問題5: 新しいサーバーを追加後にアクセスできない
```bash
# 症状：新しく追加したバックエンドサービスが正常に起動しているが、フロントエンドからアクセスできない

# 解決手順：
# 1. project-config.json の設定が正しいことを確認
# 2. 自動設定ジェネレーターを実行
python scripts/auto-config-generator.py

# 3. vue.config.js を手動更新（重要ステップ）
# 新しいサーバーのプロキシ設定を追加、上記の「複数バックエンドサービスの設定」部分を参照

# 4. フロントエンドサービスを再起動
npm run serve
```

## 📚 クイックリファレンス

### 重要ファイルの場所
```
vue-project/
├── api/                     # バックエンドサービス
│   ├── base_server.py      # 🆕 新フレームワーク基底クラス (自動ルート+キャッシュ)
│   ├── show_plate_server_v2.py  # 🆕 新フレームワークベースのデモサービス
│   └── show_plate_*.py     # その他のサービス実装
├── src/                     # フロントエンドソースコード
│   ├── components/         # Vue コンポーネント
│   ├── views/             # ページビュー
│   └── config/api.js      # API 設定 (自動生成)
├── vue.config.js           # ⚠️ フロントエンドプロキシ設定 (手動メンテナンス必要)
├── scripts/                # ツールスクリプト
│   ├── quick-add-page.py  # 🆕 ページ高速追加 (新フレームワーク対応)
│   └── auto-config-generator.py # 🆕 自動設定ジェネレーター
├── docs/                   # プロジェクトドキュメント
│   ├── MIGRATION_GUIDE.md # 🆕 ページ移行ガイド
│   ├── vue.config.js.template # 🆕 プロキシ設定テンプレート
│   └── BACKEND_FRAMEWORK_OPTIMIZATION.md # 🆕 フレームワーク最適化ドキュメント
└── tests/                  # テストファイル
```

### よく使うコマンド
```bash
# 環境チェック
python scripts/check-environment.py

# 品質チェック
python scripts/quality-check.py

# パフォーマンス監視
python scripts/performance-monitor.py

# テスト実行
python -m pytest tests/ -v

# 新しいページを追加
python scripts/quick-add-page.py

# 設定生成
python scripts/auto-config-generator.py
```

### VS Code タスクショートカット
- `Ctrl+Shift+P` → "Tasks: Run Task"
- 🚀 すべてのサービスを起動
- 🔍 コード品質チェック  
- 📊 パフォーマンス監視
- 🧪 テスト実行
- 🎨 コードフォーマット

## 🎯 次のステップガイド

### 初心者ユーザー
1. **インターフェースに慣れる** - フロントエンドページを閲覧し、機能レイアウトを理解
2. **データを確認** - リアルタイムデータ更新とチャート表示を観察
3. **API探索** - `public/api-detector.html` を使用してAPIをテスト
4. **ドキュメントを読む** - `docs/` ディレクトリ下の詳細ドキュメントを確認

### 開発者ユーザー
1. **コード構造** - `api/base_server.py` フレームワーク設計を理解
2. **機能追加** - `quick-add-page.py` を使用して新しいページを作成
3. **テスト検証** - 完全なテストスイートを実行
4. **品質チェック** - コード品質チェック習慣を確立

### 運用ユーザー
1. **監視設定** - パフォーマンス監視とアラート設定
2. **デプロイ検証** - Docker コンテナ化デプロイを使用
3. **CI/CD** - GitHub Actions ワークフローを理解
4. **バックアップ戦略** - データと設定のバックアップ計画を策定

## 📞 ヘルプの取得

### ドキュメントリソース
- 📖 **完全ドキュメント** - `docs/README.md`
- 🔧 **技術詳細** - `docs/TECHNICAL_DETAILS.md`
- 🏗️ **バックエンドフレームワーク** - `docs/BACKEND_FRAMEWORK_OPTIMIZATION.md`
- 📈 **プロジェクト改善** - `docs/PROJECT_IMPROVEMENT_ASSESSMENT.md`

### サポートチャネル
- 🐛 **問題報告** - GitHub Issues
- 💡 **機能提案** - GitHub Discussions  
- 📧 **技術サポート** - プロジェクトメンテナーに連絡
- 🤝 **貢献ガイド** - `CONTRIBUTING.md`

---

**🎉 おめでとうございます！データ可視化システムのマスターに成功しました！**

これで各種機能の探索を開始したり、自分のニーズに応じてカスタム開発を行うことができます。プロジェクトは完全なツールチェーンサポートを提供し、開発プロセスをより効率的で楽しいものにすることを忘れないでください！

---
**Author**: chenlei  
**Date**: 2025-01-10
