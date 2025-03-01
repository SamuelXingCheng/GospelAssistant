import os
from dotenv import load_dotenv

# 如果是在本地環境（非 Render），則載入 .env 檔案
if not os.getenv("RENDER"):
    env_path = "/Users/xinchenglin/檔案/GospelAssistant/.env"
    
    if os.path.exists(env_path):  # 確保 .env 存在
        print("📌 找到 .env 檔案，開始載入...")
        load_dotenv(env_path)

        LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")  # Firebase 金鑰檔案路徑
        GOOGLESHEET_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLESHEET_SERVICE_ACCOUNT_FILE")
    else:
        print("⚠️ 無法找到 .env 檔案，請確認路徑是否正確！")
else:
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FIREBASE_CREDENTIALS_PATH = "/etc/secrets/gospelassistant-firebase-adminsdk-fbsvc-69aeff154b.json"
    SERVICE_ACCOUNT_FILE = "/etc/secrets/gospelassistant-452215-3aa41b17c041.json"
    #FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")  # Firebase 金鑰檔案路徑

# 檢查是否成功載入（可在本地測試時開啟）
if __name__ == "__main__":
    print("LINE_CHANNEL_ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
    print("LINE_CHANNEL_SECRET:", LINE_CHANNEL_SECRET)
    print("OPENAI_API_KEY:", OPENAI_API_KEY)
    #print("FIREBASE_CREDENTIALS_PATH:", FIREBASE_CREDENTIALS_PATH)