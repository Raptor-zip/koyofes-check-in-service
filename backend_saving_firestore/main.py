from google.cloud import firestore
import csv
from pathlib import Path
from typing import Any


# Firestoreクライアント作成
db = firestore.Client()


def _convert_value(v: Any) -> str:
    """CSVに書けるように値を文字列に変換する。
    None は空文字列に、プリミティブ型はそのまま、それ以外は str() を使う。
    """
    if v is None:
        return ""
    if isinstance(v, (str, int, float, bool)):
        return v
    try:
        return str(v)
    except Exception:
        return ""


def export_collection_to_csv(collection_name: str, output_path: str = "visitors.csv") -> None:
    """指定のコレクションの全ドキュメントを CSV に書き出す。

    - ドキュメント ID は `_id` カラムとして出力する。
    - 全ドキュメントのキーの和集合をヘッダとして使用する。
    - 値は文字列に変換して出力する。
    """
    col_ref = db.collection(collection_name)
    docs = list(col_ref.stream())

    if not docs:
        print(f"Collection '{collection_name}' has no documents.")
        return

    rows = []
    fieldnames = set()
    for doc in docs:
        data = doc.to_dict() or {}
        # ドキュメントIDを含める
        data["_id"] = doc.id
        # すべてのキーを集める
        fieldnames.update(data.keys())
        rows.append(data)

    # ヘッダ順序: _id を先頭に、それ以外はソート
    ordered_fieldnames = ["_id"] + sorted(k for k in fieldnames if k != "_id")

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with out_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
        writer.writeheader()
        for r in rows:
            # 存在しないキーは空文字列にする。値は文字列へ変換。
            row = {k: _convert_value(r.get(k)) for k in ordered_fieldnames}
            writer.writerow(row)

    print(f"Wrote {len(rows)} documents from '{collection_name}' to: {out_file.resolve()}")


if __name__ == "__main__":
    # デフォルトは 'visitor' コレクションを 'visitors.csv' に保存
    export_collection_to_csv("visitor", "visitors.csv")