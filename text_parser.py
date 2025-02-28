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
        r"[\u4e00-\u9fa5]+(?:系)?(?:碩士|博士)?[一二三四五六]?"
    )

    # **分割輸入（支援「，」與空白）**
    parts = re.split(r"[，\s]+", text.strip())

    # **解析姓名**
    if parts:
        result["name"] = parts.pop(0)

    # **解析身份、系級、情況**
    remaining_text = []
    for part in parts:
        if part in identities:
            result["identity"] = part
        elif department_pattern.fullmatch(part):  # 確保完整匹配系級
            result["department"] = part
        elif re.match(r"\d{4}-\d{2}-\d{2}", part):  # YYYY-MM-DD 日期
            try:
                result["date"] = datetime.strptime(part, "%Y-%m-%d").date().isoformat()
            except ValueError:
                pass  # 忽略無效日期
        elif re.match(r"\d{1,2}:\d{2}", part):  # HH:MM 時間
            try:
                result["time"] = datetime.strptime(part, "%H:%M").time().isoformat()
            except ValueError:
                pass  # 忽略無效時間
        else:
            remaining_text.append(part)

    # **合併情況**
    result["situation"] = "，".join(remaining_text) if remaining_text else None

    return result
