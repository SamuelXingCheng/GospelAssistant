import re
from datetime import datetime

def parse_text(text):
    """非 AI 解析：從使用者輸入擷取姓名、身份、系級、情況"""
    result = {
        "name": None,
        "identity": None,
        "department": None,
        "situation": None,
        "date": None,
        "time": None
    }

    # **身份類別**
    identities = ["兒童", "大專", "青職", "青少年", "中壯"]

    # **擴展學系與年級的正則**
    department_pattern = re.compile(
        r"^(?:[\u4e00-\u9fa5]+系(?:碩士|博士)?[一二三四五六]年級?|[\u4e00-\u9fa5]+(?:碩士|博士)?[一二三四五六])$"
    )

    # **分割輸入（支援「，」與空白）**
    parts = re.split(r"[，\s]+", text.strip())
    if not parts or parts == [""]:
        return {"error": "⚠️ 無法解析，請輸入有效內容"}
    print("📌 [DEBUG] parse_text: parts", parts)  # 檢查格式
    # **解析姓名**
    parts.pop(0)  # 先移除「新增」、「牧養」、「尋求」
    if parts:
        result["name"] = parts.pop(0)  # 取出正確的姓名

    # **解析身份、系級、情況**
    remaining_text = []
    for part in parts:
        # if part in identities:
        #     result["identity"] = part
        #     print("📌 [DEBUG] parse_text: result[identity]",{result["identity"]})  # 檢查格式
        # elif department_pattern.fullmatch(part):  # 確保完整匹配系級
        #     result["department"] = part
        #     print("📌 [DEBUG] parse_text: result[department]",{result["department"]})  # 檢查格式
        # else:
        #     remaining_text.append(part)
        remaining_text.append(part)
    print("📌 [DEBUG] parse_text: remaining_text",remaining_text)  # 檢查格式

    result["date"] = datetime.now().strftime("%Y-%m-%d")
    result["time"] = datetime.now().strftime("%H")

    # **合併情況**
    result["situation"] = "，".join(remaining_text) if remaining_text else None

    return result
