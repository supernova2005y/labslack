import os
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN") #tokenは環境変数から取得する
CHANNEL_ID = C051SNKKU8L

MEMBERS_1 = ["Aさん", "Bさん", "Cさん", "Dさん"]
MEMBERS_2 = ["Eさん", "Fさん", "Gさん", "Hさん"]

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
    message = f"📢 今週の当番は *{person_on_duty_1}* と *{person_on_duty_2}* です！\nよろしくお願いします✨"

    # Slack APIクライアントの初期化
    client = WebClient(token=SLACK_BOT_TOKEN)

    try:
        # メッセージの送信
        response = client.chat_postMessage(
            channel=CHANNEL_ID,
            text=message
        )
        print(f"メッセージ送信成功: {response['message']['text']}")
    except SlackApiError as e:
        print(f"エラーが発生しました: {e.response['error']}")

if __name__ == "__main__":
    main()
