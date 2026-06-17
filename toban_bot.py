import os
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = "C051SNKKU8L" 

# GitHubのSecretsからメンバーリストを取得して分解
# 鍵から文字列を取り出す
members1_raw = os.environ.get("TOBAN_MEMBERS1", "")
members2_raw = os.environ.get("TOBAN_MEMBERS2", "")
# Pythonのリストに変換
MEMBERS_1 = [m.strip() for m in members1_raw.split(",") if m.strip()]
MEMBERS_2 = [m.strip() for m in members2_raw.split(",") if m.strip()]
# ==========================================

def get_duty_person():
    # 現在の「週番号」（今年に入ってから何週目か）を取得
    # ※ISOカレンダーでは月曜日に週番号が切り替わります
    week_number = datetime.now().isocalendar()[1]
    
    # 週番号をメンバー数で割った「余り」を使ってインデックスを決定
    duty_index1 = week_number % len(MEMBERS_1)
    duty_index2 = week_number % len(MEMBERS_2)
    return MEMBERS_1[duty_index1], MEMBERS_2[duty_index2]


def main():
    person_on_duty_1, person_on_duty_2 = get_duty_person()
    
    # 1. チャンネルに送る親メッセージ
    main_message = f"📢 今週の当番は {person_on_duty_1}さんと {person_on_duty_2}さんです！\nよろしくお願いします⭐"
    
    # 2. スレッドに追記する仕事内容のメッセージ
    task_message = (
        "当番のお仕事は\n"
        "• 届いた物品の検収\n"
        "• 共用スペースの整理整頓\n"
        "• 毎週金曜日13時から30分ほど行う掃除の責任者\n"
        "です！"
    )

    # Slack APIクライアントの初期化
    client = WebClient(token=SLACK_BOT_TOKEN)

    try:
        # 親メッセージをチャンネルに送信
        response = client.chat_postMessage(
            channel=CHANNEL_ID,
            text=main_message
        )
        print("親メッセージ送信成功")

        # 送信したメッセージの「タイムスタンプ(ts)」を取得
        thread_ts = response["ts"]

        # 取得したタイムスタンプ(thread_ts)を指定して、スレッドに返信
        client.chat_postMessage(
            channel=CHANNEL_ID,
            text=task_message,
            thread_ts=thread_ts
        )
        print("スレッドへの仕事内容の追記成功")

    except SlackApiError as e:
        print(f"エラーが発生しました: {e.response['error']}")

if __name__ == "__main__":
    main()
