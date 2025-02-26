import os
from dotenv import load_dotenv

# 如果是在本地環境（非 Render），則載入 .env 檔案
if not os.getenv("RENDER"):
    load_dotenv('/Users/xinchenglin/檔案/GospelAssistant/.env')

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")  # Firebase 金鑰檔案路徑

# 檢查是否成功載入（可在本地測試時開啟）
if __name__ == "__main__":
    print("LINE_CHANNEL_ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
    print("LINE_CHANNEL_SECRET:", LINE_CHANNEL_SECRET)
    print("OPENAI_API_KEY:", OPENAI_API_KEY)
    print("FIREBASE_CREDENTIALS_PATH:", FIREBASE_CREDENTIALS_PATH)