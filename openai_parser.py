import openai
import json
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

def extract_person_info(user_message):
    """使用 OpenAI 解析姓名、身份、系級、情況"""
    system_prompt = "請從使用者輸入中擷取出：姓名、身份（如兒童、大專、青職、青少年、中壯）、系級（如果有的話）、情況。回應格式為 JSON，例如：{\"name\": \"張三\", \"identity\": \"大專\", \"department\": \"資訊工程\", \"situation\": \"考試壓力大\"}。"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    extracted_data = response.choices[0].message.content.strip()

    try:
        return json.loads(extracted_data)  # 解析為 JSON
    except json.JSONDecodeError:
        return {"error": "解析失敗，請檢查輸入格式"}
