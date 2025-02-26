# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from linebot.models import MessageEvent, TextMessage, SourceUser
from line_bot import handle_line_message

class MockEvent:
    """模擬 LINE Bot 事件"""
    def __init__(self, user_id, text):
        self.reply_token = "mock_reply_token"
        self.source = SourceUser(user_id=user_id)
        self.message = TextMessage(text=text)

class TestLineBot(unittest.TestCase):
    @patch("line_bot.line_bot_api.reply_message")  # 模擬 LINE API，避免實際發送訊息
    def test_add_care_item(self, mock_reply):
        event = MockEvent("U123456", "新增關懷: 小明, 需要代禱考試")
        handle_line_message(event)
        mock_reply.assert_called_once()

    @patch("line_bot.line_bot_api.reply_message")
    def test_view_care_list(self, mock_reply):
        event = MockEvent("U123456", "查看關懷名單")
        handle_line_message(event)
        mock_reply.assert_called_once()

    @patch("line_bot.line_bot_api.reply_message")
    def test_chatgpt_response(self, mock_reply):
        event = MockEvent("U123456", "你好！")
        handle_line_message(event)
        mock_reply.assert_called_once()

if __name__ == "__main__":
    unittest.main()
