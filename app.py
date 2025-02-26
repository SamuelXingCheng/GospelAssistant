from flask import Flask, request, abort
from config import OPENAI_API_KEY, LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from line_bot import handle_line_event  # 匯入處理訊息的方法
from linebot.exceptions import InvalidSignatureError


app = Flask(__name__)

@app.route("/")
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        # 把請求內容傳給 line_bot.py 處理
        handle_line_event(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)