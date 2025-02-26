from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
#import os
from db import add_care_item, get_care_list
from openai_api import get_openai_response  # OpenAI API 處理
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET  # 匯入環境變數

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

handler = WebhookHandler(LINE_CHANNEL_SECRET)


def handle_line_event(body, signature):
    """處理來自 LINE Webhook 的事件"""
    handler.handle(body, signature)

@handler.add(MessageEvent, message=TextMessage)
def handle_line_message(event):
    """處理 LINE Bot 訊息"""
    if not isinstance(event.message, TextMessage):
        return

    user_message = event.message.text
    
    # **關懷名單操作**
    if user_message.startswith("新增關懷:"):
        try:
            _, data = user_message.split(":", 1)
            name, content = map(str.strip, data.split(","))
            add_care_item(event.source.user_id, name, content)
            reply_text = f"✅ 已新增關懷：{name} - {content}"
        except Exception:
            reply_text = "⚠️ 格式錯誤！請使用「新增關懷: 姓名, 內容」"

    elif user_message == "查看關懷名單":
        care_list = get_care_list()
        reply_text = "\n".join([f"📌 {c['name']}: {c['content']}" for c in care_list]) if care_list else "📭 目前沒有關懷名單。"

    else:
        # **使用 OpenAI 生成回應**
        try:
            reply_text = get_openai_response(user_message)
        except Exception as e:
            reply_text = "⚠️ 發生錯誤，請稍後再試！"
            print(f"OpenAI 回應錯誤: {e}")

    # 回應使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )