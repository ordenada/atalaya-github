"""
Define the class to manager a Telegram bot
"""

from telebot.async_telebot import AsyncTeleBot


class TelegramBot:
    """The Telegram bot"""
    def __init__(self, token: str) -> None:
        self.bot = AsyncTeleBot(token=token)
