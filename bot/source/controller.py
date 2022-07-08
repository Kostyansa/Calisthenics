from datetime import datetime, timezone
import os
import time
import logging
import uuid
import base64

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update

from entity import Response, User
from repository.user import UserRepository


class Controller:
    __slots__ = "user_repository"

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def on_message(self, userid, text):
        response = Response("К сожалению я пока не умею отвечать на сообщения")
        return response

    def on_start(self, userid):
        user = User()
        user.chat_id = userid
        self.user_repository.save(user)
        response = Response("Добро пожаловать, список упражений:")
        keyboard = [
            [InlineKeyboardButton("Отжимания", url="https://www.hybridcalisthenics.com/pushups")],
            [InlineKeyboardButton("Поднятия ног", url="https://www.hybridcalisthenics.com/legraises")],
            [InlineKeyboardButton("Приседания", url="https://www.hybridcalisthenics.com/squats")],
            [InlineKeyboardButton("Подтягивания", url="https://www.hybridcalisthenics.com/pullups")],
            [InlineKeyboardButton("Мостик", url="https://www.hybridcalisthenics.com/bridges")],
            [InlineKeyboardButton("Скручивания", url="https://www.hybridcalisthenics.com/twists")]
        ]
        response.replyMarkup = InlineKeyboardMarkup(keyboard)
        return response

    def reminder(self):
        response = Response("Упражнения сегодня:")
        weekday = datetime.now().weekday()
        match weekday:
            case 0 | 3:
                keyboard = [
                    [InlineKeyboardButton("Отжимания", url="https://www.hybridcalisthenics.com/pushups")],
                    [InlineKeyboardButton("Поднятия ног", url="https://www.hybridcalisthenics.com/legraises")]
                ]
                response.replyMarkup = InlineKeyboardMarkup(keyboard)
            case 1 | 4:
                keyboard = [
                    [InlineKeyboardButton("Подтягивания", url="https://www.hybridcalisthenics.com/pullups")],
                    [InlineKeyboardButton("Приседания", url="https://www.hybridcalisthenics.com/squats")],
                ]
                response.replyMarkup = InlineKeyboardMarkup(keyboard)
            case 2 | 5:
                keyboard = [
                    [InlineKeyboardButton("Мостик", url="https://www.hybridcalisthenics.com/bridges")],
                    [InlineKeyboardButton("Скручивания", url="https://www.hybridcalisthenics.com/twists")]
                ]
                response.replyMarkup = InlineKeyboardMarkup(keyboard)
            case 6:
                response.message = "Сегодня выходной, отдыхайте"
        users = self.user_repository.get_all()
        return users, response
