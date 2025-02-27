from linebot.models import FlexSendMessage

def get_care_list_flex():
    """產生 Flex Message 讓使用者點擊按鈕查詢關懷名單"""
    flex_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🔔 牧養提醒",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": "點擊下方按鈕查看牧養名單",
                    "size": "md",
                    "color": "#666666"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": "📜 查看名單",
                        "text": "查看牧養名單"  # 這裡是關鍵，當用戶點擊，會送出這個訊息
                    },
                    "style": "primary",
                    "color": "#007AFF"
                }
            ]
        }
    }
    return FlexSendMessage(alt_text="點擊查看牧養名單", contents=flex_message)

def handle_text_message(event):
    user_message = event.message.text.strip()
    if user_message == "牧養提醒":
        return get_care_list_flex()
    return None