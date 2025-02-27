import logging
from flask import Flask, request, abort
from config import OPENAI_API_KEY, LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from line_bot import handle_line_event  # 匯入處理訊息的方法
from linebot.exceptions import InvalidSignatureError
from google_sheets import update_google_sheet

app = Flask(__name__)

# 設定 Logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    """健康檢查，確保服務正常運行"""
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    """處理 LINE Webhook 請求"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    logging.info("📌 收到 LINE Webhook 請求")
    if not signature:
        logging.error("❌ 缺少 X-Line-Signature 標頭")
        abort(400)

    try:
        # 把請求內容傳給 line_bot.py 處理
        handle_line_event(body, signature)
    except InvalidSignatureError:
        logging.error("❌ 無效的簽名")
        abort(400)

    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)