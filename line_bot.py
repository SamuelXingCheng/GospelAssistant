from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from db import is_name_exists, add_care_item, get_care_list,save_user_name, get_user_name
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET  # 匯入環境變數
from linebot.exceptions import InvalidSignatureError
from flex_message import get_care_list_flex  # 匯入 Flex Message 產生函式
from handlers import handle_add_care_item, handle_view_all_care_list, handle_view_user_care_list, handle_delete_care_item, handle_chat_with_ai
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def get_line_user_name(user_id):
    """透過 LINE API 取得使用者名稱"""
    try:
        profile = line_bot_api.get_profile(user_id)  # 呼叫 LINE API
        return profile.display_name  # 回傳 LINE 使用者名稱
    except Exception as e:
        print(f"❌ [ERROR] 無法獲取 LINE 使用者名稱: {e}")
        return "未知使用者"  # 如果失敗，回傳預設值

def handle_line_event(body, signature):
    """處理來自 LINE Webhook 的事件"""
    handler.handle(body, signature)

@handler.add(MessageEvent, message=TextMessage)
def handle_line_message(event):
    """處理 LINE Bot 訊息"""
    if not isinstance(event.message, TextMessage):
        return

    user_id = event.source.user_id  # 取得使用者 ID
    user_name = get_user_name(user_id)  # 先檢查 Firestore 是否有名稱
    user_message = event.message.text
    
    if not user_name:
        user_name = get_line_user_name(user_id)  # 從 LINE API 取得名稱
        save_user_name(user_id, user_name)  # 存入 Firestore

    reply_text = process_user_message(user_id, user_name, user_message)

    # 回應使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
    
def process_user_message(user_id, user_name, user_message):
    """根據使用者輸入的訊息選擇相應回應"""

    # **指令對應函數字典**
    commands = {
        "查看所有牧養名單": handle_view_all_care_list,
        "查看牧養名單": lambda: handle_view_user_care_list(user_id),
        "牧養提醒": get_care_list_flex
    }

     # **判斷是否為「新增」開頭**
    if user_message.startswith("新增"):
        return handle_add_care_item(user_id, user_name, user_message)
    
     # **判斷是否為「刪除」開頭**
    if user_message.startswith("刪除"):
        return handle_delete_care_item(user_id, user_message)

    # **檢查是否為已定義的指令**
    if user_message in commands:
        return commands[user_message]()

    # **預設為 AI 對話**
    return handle_chat_with_ai(user_id, user_message)