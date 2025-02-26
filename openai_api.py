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