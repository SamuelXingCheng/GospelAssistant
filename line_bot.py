from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from db import add_care_item, get_care_list, get_conversation, save_conversation
from openai_api import get_openai_response  # OpenAI API 處理
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET  # 匯入環境變數
from openai_parser import extract_person_info  # 新增資料萃取功能

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

    user_id = event.source.user_id  # 取得使用者 ID
    user_message = event.message.text
    
    # **關懷名單操作**
    if user_message.startswith("新增"):
        try:
            extracted_info = extract_person_info(user_message)
            name = extracted_info.get("name", "未知")
            identity = extracted_info.get("identity", "未知")
            department = extracted_info.get("department", "")
            situation = extracted_info.get("situation", "無")
            add_care_item(user_id, name, situation)  # 存入資料庫
            reply_text = f"✅ 已新增名單：{name} - {situation}"
        except Exception:
            reply_text = "⚠️ 格式錯誤！請使用「新增關懷: 姓名, 內容」"

    elif user_message == "查看牧養名單":
        care_list = get_care_list()
        reply_text = "\n".join([f"📌 {c['name']}: {c['content']}" for c in care_list]) if care_list else "📭 目前沒有牧養名單。"

    else:
        # **取得過去的對話歷史**
        conversation_history = get_conversation(user_id)

        if not conversation_history:
            conversation_history = [{"role": "system", "content": "你是一個智慧 AI 助手，請幫助使用者解答問題。"}]

        # **加入使用者新訊息**
        conversation_history.append({"role": "user", "content": user_message})
        
        # **發送完整對話給 OpenAI**
        try:
            print("📌 [DEBUG] conversation_history:", conversation_history)  # 檢查格式
            reply_text = get_openai_response(user_message=conversation_history)
            # **儲存最新對話**
            conversation_history.append({"role": "assistant", "content": reply_text})
            save_conversation(user_id, conversation_history)
        except Exception as e:
            reply_text = "⚠️ 發生錯誤，請稍後再試！"
            print(f"OpenAI 回應錯誤: {e}")

    # 回應使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )