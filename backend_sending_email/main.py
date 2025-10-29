import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import time
from datetime import datetime
import requests
from urllib.parse import quote
import sys
import argparse


def send_emails(csv_file, dry_run=False):
    # Gmail設定
    GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS', 'your-email@gmail.com')
    GMAIL_APP_PASSWORD = os.environ.get(
        'GMAIL_APP_PASSWORD', 'your-app-password')

    # 送信遅延時間(秒)
    DELAY_SECONDS = 2

    # 送信リストを格納する配列
    email_list = []

    print(f"\n{'='*60}")
    print(f"モード: {'【テスト実行】' if dry_run else '【本番実行】'}")
    print(f"対象ファイル: {csv_file}")
    print(f"{'='*60}\n")

    if not dry_run:
        print("⚠️  本番モードで実行します。メールが実際に送信されます。")
        confirmation = input("続行しますか? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("実行を中止しました。")
            return

    # CSVファイルを読み込む
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            sent_email = row['SENT_EMAIL'].strip()
            email_address = row['メールアドレスをご記入ください'].strip()
            name = row['氏名をご記入ください'].strip()

            # SENT_EMAILが"TRUE"でも"skipped"でもない場合
            if sent_email != 'TRUE' and sent_email != 'skipped' and email_address:
                # 送信状態とエラー内容を初期化
                row['送信状態'] = ''
                row['エラー内容'] = ''

                try:
                    # QRコード生成
                    uuid = row['UUID'].strip()
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?qzone=5&ecc=H&size=400x400&data={quote(uuid)}"
                    qr_response = requests.get(qr_url)

                    if qr_response.status_code != 200:
                        raise Exception(
                            f"QRコード生成失敗: {qr_response.status_code}")

                    qr_image_data = qr_response.content

                    # メール作成
                    msg = MIMEMultipart('related')
                    msg['From'] = f'こうよう祭2025'
                    msg['To'] = email_address
                    msg['Subject'] = '【こうよう祭2025】来場登録が完了しました'

                    # HTML本文を添付
                    msg_alternative = MIMEMultipart('alternative')
                    msg.attach(msg_alternative)

                    # プレーンテキスト版
                    text_body = "本文はHTML対応メールでご確認ください"
                    msg_alternative.attach(MIMEText(text_body, 'plain'))

                    # HTML版
                    html_body = create_email_content(row)
                    msg_alternative.attach(MIMEText(html_body, 'html'))

                    # QRコード画像をインライン添付
                    qr_image = MIMEImage(qr_image_data, name='qrcode.png')
                    qr_image.add_header('Content-ID', '<qr>')
                    qr_image.add_header(
                        'Content-Disposition', 'inline', filename='qrcode.png')
                    msg.attach(qr_image)

                    # Gmail SMTPサーバーに接続して送信
                    if not dry_run:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                            server.sendmail(
                                GMAIL_ADDRESS, email_address, msg.as_string())
                        print(
                            f'✓ メール送信成功: {email_address} (name: {name}, UUID: {uuid})')
                    else:
                        print(
                            f'[テスト] メール送信予定: {email_address} (name: {name}, UUID: {uuid})')

                    row['送信状態'] = '成功'
                    row['エラー内容'] = ''

                except Exception as e:
                    error_msg = str(e)
                    print(
                        f'✗ メール送信失敗: {email_address} (name: {name}, UUID: {uuid}) - エラー: {error_msg}')
                    row['送信状態'] = '失敗'
                    row['エラー内容'] = error_msg

                # リストに追加
                email_list.append(row)

                # 送信遅延（テストモードでは短縮）
                time.sleep(0.5 if dry_run else DELAY_SECONDS)

    # 送信リストをCSVファイルに保存
    if email_list:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = 'test_' if dry_run else ''
        output_filename = f'{prefix}sent_email_list_{timestamp}.csv'

        # 新しいフィールド名を追加
        new_fieldnames = list(fieldnames) + ['送信状態', 'エラー内容']

        with open(output_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=new_fieldnames)
            writer.writeheader()
            writer.writerows(email_list)

        print(f'\n送信結果を {output_filename} に保存しました。')
        print(f'総送信試行数: {len(email_list)}件')
        success_count = sum(1 for row in email_list if row['送信状態'] == '成功')
        failure_count = sum(1 for row in email_list if row['送信状態'] == '失敗')
        print(f'成功: {success_count}件, 失敗: {failure_count}件')
    else:
        print('送信対象のメールはありませんでした。')


def create_email_content(data):
    name = data['氏名をご記入ください'].strip()
    type = data['区分を選択してください'].strip()
    phone_number = data['電話番号をご記入ください'].strip()
    visit_date = data['来場される日付を選択してください'].strip()
    uuid = data['UUID'].strip()

    html_body = f"""
    <div style="font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; background-color:#f4f6f8; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:white; border-radius:16px; box-shadow:0 6px 18px rgba(0,0,0,0.08); padding:40px;">

        <h2 style="color:#2c3e50; text-align:center; margin-bottom:20px;">来場登録が完了しました</h2>
        <p style="font-size:16px; color:#444; line-height:1.6; text-align:center;">
            {name} 様、ご登録いただきありがとうございます。<br>
            以下のQRコードを <b style="color:#e74c3c;">こうよう祭当日の受付</b> でご提示ください。<br>
            欠席の連絡は不要です。
        </p>

        <div style="text-align:center; margin:30px 0;">
            <img src="cid:qr" style="width:180px; height:180px; border:8px solid #f4f6f8; border-radius:12px;"/>
        </div>

        <table style="width:100%; border-collapse:collapse; font-size:15px; margin-top:20px;">
            <tr>
            <td style="padding:10px; border-bottom:1px solid #aaa; font-weight:bold; color:#555; width:30%;">お名前</td>
            <td style="padding:10px; border-bottom:1px solid #aaa; color:#333;">{name}</td>
            </tr>
            <tr>
            <td style="padding:10px; border-bottom:1px solid #aaa; font-weight:bold; color:#555;">区分</td>
            <td style="padding:10px; border-bottom:1px solid #aaa; color:#333;">{type}</td>
            </tr>
            <tr>
            <td style="padding:10px; border-bottom:1px solid #aaa; font-weight:bold; color:#555;">電話番号</td>
            <td style="padding:10px; border-bottom:1px solid #aaa; color:#333;">{phone_number}</td>
            </tr>
            <tr>
            <td style="padding:10px; font-weight:bold; color:#555;">来場日</td>
            <td style="padding:10px; color:#333;">{visit_date}</td>
            </tr>
        </table>

        <p style="font-size:14px; color:#444; margin-top:60px; margin-bottom:10px; text-align:center;">
        独立行政法人国立高等専門学校機構豊田工業高等専門学校<br>
        こうよう祭実行委員会<br>
        住所: 〒471-8525 愛知県豊田市栄生町2-1<br>
        サイト: <a href="https://koyosai.com/">https://koyosai.com/</a><br>
        メールアドレス: kouyousai.system@gmail.com
        </p>

        <hr>

        <p style="font-size:14px; color:#444; margin-top:10px; text-align:center;">
            このメールは自動送信です。ご不明な点がございましたら koyofes.system@gmail.com までお問い合わせください。
        </p>

        <p style="font-size:11px; color:#666; margin-top:20px; text-align:center;">
            UUID: {uuid}
        </p>
        </div>
    </div>
    """
    return html_body


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='こうよう祭2025 メール一括送信スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # テストモード（実際にメールは送信されません）
  python main.py --csv list.csv --dry-run

  # 本番実行（実際にメールが送信されます）
  python main.py --csv list.csv --production

  # テストモード（短縮形）
  python main.py -c test.csv -d

  # 本番実行（短縮形）
  python main.py -c list.csv -p
        """
    )

    parser.add_argument(
        '-c', '--csv',
        type=str,
        required=True,
        help='送信対象のCSVファイルパス（必須）'
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='テストモード（メールは送信されません）'
    )
    mode_group.add_argument(
        '-p', '--production',
        action='store_true',
        help='本番モード（実際にメールが送信されます）'
    )

    args = parser.parse_args()

    # CSVファイルの存在確認
    if not os.path.exists(args.csv):
        print(f"エラー: ファイル '{args.csv}' が見つかりません。")
        sys.exit(1)

    # 実行
    send_emails(args.csv, dry_run=args.dry_run)
