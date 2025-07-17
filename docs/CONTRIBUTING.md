# 🤝 コントリビューションガイド

**プロジェクト作成者**: chenlei

## 👋 コントリビューション歓迎

データ可視化システムプロジェクトへのご関心をありがとうございます！以下を含む様々な形のコントリビューションを歓迎します：

- 🐛 バグ報告
- 💡 新機能提案
- 📝 ドキュメント改善
- 🔧 コード修正提出
- 🎯 新機能開発
- 🎨 UI/UX 改善

## 🚀 クイックスタート

### 開発環境セットアップ

1. **プロジェクトをFork**
   ```bash
   # GitHub からプロジェクトをあなたのアカウントにFork
   git clone https://github.com/your-username/vue-project.git
   cd vue-project
   ```

2. **開発環境設定**
   ```bash
   # プロジェクト設定
   python scripts/init-config.py
   
   # 依存関係インストール
   npm install
   
   # 開発サーバー起動
   python scripts/auto-config-generator.py
   start-all-services.bat  # Windows
   ./start-all-services.sh # Linux/Mac
   ```

3. **環境確認**
   - http://localhost:8081 でフロントエンドが正常であることを確認
   - http://localhost:5004/health でバックエンドが正常であることを確認

## 📋 コントリビューションタイプ

### 🐛 バグ報告

**GitHub Issues を使用してバグを報告する際は、以下を含めてください：**

1. **バグの説明** - 問題を明確かつ簡潔に記述
2. **再現手順** - 詳細な手順説明
3. **期待される動作** - 正しい動作の説明
4. **実際の動作** - 実際に発生した状況の説明
5. **環境情報**：
   - OS：Windows/macOS/Linux
   - Node.js バージョン：`node --version`
   - Python バージョン：`python --version`
   - ブラウザ：Chrome/Firefox/Safari とバージョン
6. **スクリーンショットまたは録画**（該当する場合）
7. **エラーログ**（ブラウザコンソールまたはサーバーログ）

### 💡 機能提案

**新機能を提案する際は、以下を説明してください：**

1. **機能概要** - 提案機能の簡潔な説明
2. **使用シーン** - いつどこでこの機能を使用するかの説明
3. **期待される解決策** - 希望する実装方法の記述
4. **代替案** - 検討した他の解決策
5. **影響評価** - 既存機能への潜在的影響

### 📝 ドキュメント改善

- 誤字脱字の修正
- 説明の明確化
- 新機能のドキュメント追加
- 翻訳の改善

## 🔧 コード貢献

### 開発フロー

1. **イシューを作成**（まだない場合）
2. **ブランチを作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **コードを作成**
   - コードスタイルガイドラインに従う
   - 適切なコメントを追加
   - テストを書く（該当する場合）

4. **テストを実行**
   ```bash
   # 品質チェック
   python scripts/quality-check.py
   
   # テスト実行
   python -m pytest tests/
   ```

5. **コミットとプッシュ**
   ```bash
   git add .
   git commit -m "feat: 新機能の説明"
   git push origin feature/your-feature-name
   ```

6. **プルリクエストを作成**

### コードスタイル

- **Python**: PEP 8 スタイルガイドに従う
- **JavaScript/Vue**: ESLint 設定に従う
- **コミットメッセージ**: Conventional Commits 形式を使用

## 🎯 コミュニティガイドライン

1. **尊重** - すべての参加者を尊重する
2. **建設的** - 建設的なフィードバックを提供する
3. **協力的** - 他の人の学習を支援する
4. **包括的** - すべての人を歓迎する

## 📞 サポート

質問がある場合は：
- GitHub Issues で質問を作成
- GitHub Discussions で議論に参加

---

**コントリビューションに感謝します！** 🎉
