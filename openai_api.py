import openai
import os
from config import OPENAI_API_KEY  # 匯入環境變數

# 設定 OpenAI API Key
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()  # 創建 OpenAI 客戶端

def get_openai_response(user_message):
    """使用 OpenAI API 產生回應"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = user_message
    )
    return response.choices[0].message.content.strip()

def get_openai_shepherding_advice(name, logs):
    """
    呼叫 OpenAI 生成牧養關心建議。

    :param name: 牧養對象姓名
    :param logs: 牧養記錄(含第一次情況)
    :return: AI 生成的建議
    """
    openai_prompt = f"""
    這是一位名叫 {name} 的弟兄姊妹，這是我目前和他相處的情況和對他過往牧養記錄：
    {logs}

    請根據這些資訊，提供適合的關心建議，並以溫暖的語氣回應。
    """
    print("📌 [DEBUG] get_openai_shepherding_advice:", name)  # 檢查格式
    print("📌 [DEBUG] get_openai_shepherding_advice:", logs)  # 檢查格式
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "你是一位有有趣的聊天員，擅長關心開啟話題。"},
                  {"role": "user", "content": openai_prompt}]
    )

    return response.choices[0].message.content.strip()
