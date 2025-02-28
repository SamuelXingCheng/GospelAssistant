from db import is_name_exists, add_shepherding_log, get_shepherding_logs

def handle_shepherding_log(user_id, target_name, log_content=None):
    """
    新增或查詢牧養記錄。
    
    :param target_name: 需要牧養的對象姓名
    :param log_content: 牧養內容（若為 None，則查詢現有記錄）
    :return: 牧養記錄或確認訊息
    """

    # 🔹 查詢該人是否存在於資料庫
    person_info = is_name_exists(target_name)
    if not person_info:
        return f"❌ 找不到「{target_name}」的資料，請確認姓名是否正確。"

    if log_content:
        # 🔹 新增牧養記錄
        return add_shepherding_log(user_id, target_name, log_content)

    else:
        # 🔹 查詢牧養記錄
        logs = get_shepherding_logs(user_id, target_name)
        if not logs:
            return f"📭「{target_name}」目前沒有牧養記錄，請輸入「我牧養 {target_name}，內容」來新增。"
        
        log_text = "\n".join([f" {log}" for log in logs])
        return f"📖 牧養記錄（{target_name}）：\n{log_text}"
