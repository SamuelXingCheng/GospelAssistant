from db import is_name_exists, add_care_item, get_care_list, get_user_care_list, save_conversation, get_conversation, delete_care_item, get_shepherding_logs
from openai_parser import extract_person_info
from openai_api import get_openai_response, get_openai_shepherding_advice
from text_parser import parse_text

def handle_add_care_item(user_id, user_name, user_message, use_ai=False):
    """處理新增關懷名單的邏輯"""
    try:
        # **選擇解析方式**
        if use_ai:
            extracted_info = extract_person_info(user_message)  # AI 解析
        else:
            extracted_info = parse_text(user_message)  # 非 AI 解析
        
        # **擷取關鍵資訊**
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
            reply_text = f"✅ 恭喜 {user_name} 已新增名單：{name} - {situation} - {date}"
        return reply_text
    except Exception:
        reply_text = "⚠️ 格式錯誤！請使用「新增關懷: 姓名, 內容」"

def handle_view_all_care_list():
    """處理查看所有牧養名單"""
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
    return reply_text

def handle_view_user_care_list(user_id, user_name):
    """處理查看使用者的牧養名單"""
    care_items = get_user_care_list(user_id)  # 只取該使用者的名單

    reply_text = f"{user_name} 的牧養名單：\n\n" + "\n\n".join([
        f"{i+1}. {c.get('name', '未知')}：{c.get('situation', '無內容')}：📅 {c.get('date', '無日期')}"
        for i, c in enumerate(care_items)
    ]) if care_items else "📭 目前沒有您的牧養名單。"
    print("📌 [DEBUG] 查看牧養名單:")  # 檢查格式
    return reply_text

def handle_chat_with_ai(user_id, user_message):
    """處理與 AI 的對話"""
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

    return reply_text

def handle_seek_shepherding_advice(user_id, target_name):
    """
    根據牧養對象的情況與記錄，向 OpenAI 尋求關心方向建議。

    :param target_name: 牧養對象姓名
    :return: AI 生成的建議
    """
    if not is_name_exists(target_name) :
        return f"⚠️ 找不到 {target_name}，請確認名字是否正確"

    # 🔎 查詢該人的牧養記錄
    logs = get_shepherding_logs(user_id, target_name)

    # 🧠 生成 AI 輔導建議
    advice = get_openai_shepherding_advice(
        name=target_name,
        logs=logs
    )

    return f"📝 **關心建議**：\n{advice}"


def handle_delete_care_item(user_id, user_message):
    """處理刪除牧養名單項目"""
    name_to_delete = user_message.replace("刪除", "").strip()  # 取得使用者輸入的名稱
    print("📌 [DEBUG] 查看刪除名單:", name_to_delete)  # 檢查格式
    if not name_to_delete:
        return "❌ 請提供要刪除的名字，例如：刪除 小明"

    success = delete_care_item(user_id, name_to_delete)  # 嘗試刪除
    if success:
        return f"✅ 已將 {name_to_delete} 從您的牧養名單刪除"
    else:
        return f"⚠️ 找不到 {name_to_delete}，請確認名字是否正確"

def handle_help_command():
    """
    回應使用者目前可用的功能語法
    """
    help_text = """✨【📖 牧養助手功能說明】✨

📌 牧養對象名單管理
1. 新增
✅範例：新增 曾愛主，財經一，大專生，最近壓力很大，需要關心

2. 刪除
✅範例：刪除 曾愛主

3. 查看
✅範例：查看牧養名單
-------------------------------------
📖 牧養記錄
1. 新增
✅範例：牧養 曾愛主，今天讀了約翰福音，很受感動！

2. 查詢
✅範例：牧養 曾愛主
-------------------------------------
🤖 AI 建議
1. 尋求 AI 關心建議
✅範例：尋求 曾愛主

2. 查看使用說明
✅範例：使用說明

💡 請依照上述語法輸入指令，讓 AI 牧養助手幫助你關心弟兄姊妹！
"""
    return help_text
