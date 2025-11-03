# Firestore を CSV にダウンロードするスクリプト

このディレクトリには、Google Firestore の `visitor` コレクションを読み取り、CSV ファイルとして保存するPython スクリプトが含まれています。
来場者数を集計するために、Firestore からデータをエクスポートする目的で作成されました。エクスポートされたcsvと、当日用Google フォームからの集計データを組み合わせて、来場者数の最終的な確認を行うのを目的としています。

主なファイル
- `main.py` - Firestore の全ドキュメントを読み取り、`visitors.csv`（デフォルト）へ書き出します。

概要
- Firestore コレクション内の全ドキュメントを取得し、ドキュメント ID を `_id` カラムとして含む CSV を出力します。
- 各ドキュメントのキーフィールドの和集合をヘッダとして使います。

インストール

1. 仮想環境を作る（任意）

```bash
python -m venv .venv
source .venv/bin/activate
```

2. 必要パッケージをインストール

```bash
pip install google-cloud-firestore
```

設定（認証）

Google Cloud のサービスアカウント JSON キーをダウンロードし、環境変数を設定します:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
```

実行方法

- デフォルト（`visitor` コレクションを `visitors.csv` に出力）:

```bash
python ./download_firestore/main.py
```

- 別のコレクション名や出力ファイル名で実行したい場合は、`main.py` の最下部の呼び出しを編集するか、Python の一行呼び出しで関数を実行できます（リポジトリルートから実行することを想定）:

```bash
python -c "from download_firestore.main import export_collection_to_csv; export_collection_to_csv('your_collection_name','out.csv')"
```

出力
- デフォルトで `visitors.csv` が作成されます。ファイルは UTF-8 エンコードです。
- CSV のカラム順は `_id`（ドキュメント ID）が先頭、その後に残りのフィールド名をソートした順で並びます。