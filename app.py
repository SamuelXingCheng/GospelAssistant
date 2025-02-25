from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境變數（從 Render 讀取）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/")
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # 呼叫 OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 或 "gpt-4"（需確認你的 API Key 是否有權限）
        messages=[{"role": "user", "content": user_message}]
    )

    chatgpt_reply = response["choices"][0]["message"]["content"].strip()

    # 回應使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=chatgpt_reply)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)