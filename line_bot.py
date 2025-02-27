from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from db import is_name_exists, add_care_item, get_care_list,save_user_name, get_user_name, get_user_care_list, get_conversation, save_conversation
from openai_api import get_openai_response  # OpenAI API 處理
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET  # 匯入環境變數
from openai_parser import extract_person_info  # 新增資料萃取功能
from linebot.exceptions import InvalidSignatureError
from flex_message import get_care_list_flex  # 匯入 Flex Message 產生函式

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

    # **關懷名單操作**
    if user_message.startswith("新增"):
        try:
            extracted_info = extract_person_info(user_message)
            name = extracted_info.get("name", "未知")
            if is_name_exists(name):
                reply_text = f"⚠️ 名單中已經有 {name}，請勿重複新增！"
            else:
                identity = extracted_info.get("identity", "未知")
                department = extracted_info.get("department", "")
                situation = extracted_info.get("situation", "無")
                print("📌 [DEBUG] situation:", situation)  # 檢查格式
                date = extracted_info.get("date", "未知")
                print("📌 [DEBUG] date:", date)  # 檢查格式
                time = extracted_info.get("time", "未知")
                print("📌 [DEBUG] time:", time)  # 檢查格式
                add_care_item(user_id, name, situation, date, time)  # 存入資料庫
                print("📌 [DEBUG] name:", name)  # 檢查格式
                reply_text = f"✅ 恭喜{user_name}已新增名單：{name} - {situation} - {date}"
        except Exception:
            reply_text = "⚠️ 格式錯誤！請使用「新增關懷: 姓名, 內容」"

    elif user_message == "查看所有牧養名單":
        care_list = get_care_list()
        care_items = [item for care in care_list for item in care.get("care_items", [])]
        
        previous_date = None  # 記錄上一筆的日期
        previous_user = None  # 記錄上一筆的 LINE 名稱
        formatted_list = []
        for i, c in enumerate(care_list):
            current_date = c.get('date', '無日期')  # 取得目前的日期
            user_name = c.get('user_name', '未知使用者')  # 取得 LINE 名稱

            # 如果當前日期與前一個不同，則印出日期
            date_display = f"📅 {current_date}\n" if current_date != previous_date else ""
            
            # 判斷是否顯示使用者名稱
            user_display = f"\n👤 {user_name}\n" if user_name != previous_user else ""

            # 建立每一行的文字
            formatted_list.append(
                f"{date_display}{user_display}{i+1}. {c.get('name', '未知')}：{c.get('situation', '無內容')}"
            )
            
            # 更新 previous_date
            previous_date = current_date
            previous_user = user_name
        
        formatted_list.append("\n")
        reply_text = "\n".join(formatted_list) if formatted_list else "📭 目前沒有牧養名單。"

        print("📌 [DEBUG] 查看所有牧養名單:", care_list)  # 檢查格式

    elif user_message == "查看牧養名單":
        user_id = event.source.user_id  # 取得使用者的 LINE ID
        care_items = get_user_care_list(user_id)  # 只取該使用者的名單

        reply_text = "\n\n".join([
            f"{i+1}. {c.get('name', '未知')}：{c.get('situation', '無內容')}：📅 {c.get('date', '無日期')}"
            for i, c in enumerate(care_items)
        ]) if care_items else "📭 目前沒有您的牧養名單。"
        print("📌 [DEBUG] 查看牧養名單:")  # 檢查格式

    elif user_message == "牧養提醒":# 📌 **當使用者輸入「提醒牧養名單」時，回應 Flex Message**
        flex_message = get_care_list_flex()
        line_bot_api.reply_message(event.reply_token, flex_message)
        return
        
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

