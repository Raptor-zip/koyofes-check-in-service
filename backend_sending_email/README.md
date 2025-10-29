# こうよう祭2025 メール一括送信スクリプト

このスクリプトは、GASの一日あたりの送信数制限でGASからメールを送信できなくなったときに、ローカルからメールを一括送信するためのツールです。

## 機能

- CSVファイルから来場者情報を読み込み
- UUIDベースのQRコードを自動生成
- HTML形式のメール送信（インライン画像対応）
- テストモード/本番モードの切り替え
- 送信結果をCSVファイルに保存
- 送信遅延による負荷対策
- 誤送信防止機能

## セットアップ

### 1. ライブラリのインストール

```bash
pip install requests
```

### 2. 環境変数の設定

Gmailのアプリパスワードを環境変数に設定します。

```bash
export GMAIL_ADDRESS="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
```

#### Gmailアプリパスワードの取得方法

1. Googleアカウントで2段階認証を有効化
2. [アプリパスワード](https://myaccount.google.com/apppasswords)にアクセス
3. 「メール」アプリ用のパスワードを生成
4. 生成された16桁のパスワードを環境変数に設定

### 3. CSVファイルの準備

以下の列を含むCSVファイルを準備してください:

- `タイムスタンプ`
- `氏名をご記入ください`
- `区分を選択してください`
- `メールアドレスをご記入ください`
- `電話番号をご記入ください`
- `来場される日付を選択してください`
- `LINEはご登録済みですか?`
- `UUID`
- `SENT_EMAIL`
- `REGISTERED_FIRESTORE`

## 使用方法

### テストモード（推奨）

実際にメールは送信されず、送信予定のログのみ表示されます。

```bash
python main.py --csv list.csv --dry-run
```

または短縮形:

```bash
python main.py -c list.csv -d
```

### 本番実行

実際にメールが送信されます。実行前に確認プロンプトが表示されます。

```bash
python main.py --csv list.csv --production
```

または短縮形:

```bash
python main.py -c list.csv -p
```

### ヘルプの表示

```bash
python main.py --help
```

## 送信対象

以下の条件を満たす行のみが送信対象となります:

- `SENT_EMAIL`列が`TRUE`でも`skipped`でもない（空文字列）
- `メールアドレスをご記入ください`列にメールアドレスが入力されている

## 出力ファイル

送信結果は以下の形式でCSVファイルとして保存されます:

- **テストモード**: `test_sent_email_list_YYYYMMDD_HHMMSS.csv`
- **本番モード**: `sent_email_list_YYYYMMDD_HHMMSS.csv`

### 追加される列

- `送信状態`: "成功" または "失敗"
- `エラー内容`: エラーが発生した場合の詳細メッセージ

## 設定のカスタマイズ

### 送信遅延時間の変更

`main.py`内の`DELAY_SECONDS`を変更してください（デフォルト: 2秒）

```python
# 送信遅延時間(秒)
DELAY_SECONDS = 2
```

### メール本文のカスタマイズ

`create_email_content()`関数内のHTMLテンプレートを編集してください。

## 安全機能

1. **必須引数**: モード（`--dry-run`または`--production`）とCSVファイルの指定が必須
2. **本番確認**: 本番モードでは実行前に`yes`の入力が必要
3. **ファイル存在確認**: 指定されたCSVファイルが存在しない場合はエラー
4. **テストモード**: dry-runモードでは実際にメールは送信されない