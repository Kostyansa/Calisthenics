import time
import uuid
import threading
import os
import logging
import sys
import json
from datetime import datetime
from pytz import timezone

from apscheduler.schedulers.blocking import BlockingScheduler

from telegram.error import NetworkError, Unauthorized, TelegramError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext

from controller import Controller
from config.engine import InternalDatabaseConfiguration
from repository.user import UserRepository
from entity import Response


class AdapterTelegram:

    def __init__(self, APIKey, controller: Controller):
        self.controller = controller
        self.updater = Updater(token=APIKey, use_context=True)
        self.bot = self.updater.bot
        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.on_message))
        self.updater.dispatcher.add_error_handler(self.error_handler)

    def start(self, update, context: CallbackContext) -> None:
        logging.info(f'Start command from {update.message.chat.id}')
        response = self.controller.on_start(update.message.chat.id)
        self.send_response(update.message.chat.id, response)

    def error_handler(self, update, context) -> None:
        logging.warning(f'Error while sendind message', exc_info=context.error)
        if update is not None:
            if update.message is not None:
                if update.message.chat is not None:
                    self.bot.send_message(update.message.chat.id,
                                          "Во время обработки вашего сообщения произошла ошибка, пожалуйста, попробуйте позже.")

    def send_response(self, chat_id, response: Response):
        if response.replyMarkup:
            self.bot.send_message(chat_id, response.message, reply_markup=response.replyMarkup)
        else:
            self.bot.send_message(chat_id, response.message)
        if response.photo:
            self.bot.send_photo(chat_id, response.photo)

    def on_message(self, update, context) -> None:
        logging.info(f'Got message from {update.message.chat.id}')
        logging.debug(f'Message: {update.message.text}')
        response = self.controller.on_message(update.message.chat.id, update.message.text)
        self.send_response(update.message.chat.id, response)
        logging.info(f'Sent response to {update.message.chat.id}')

    def on_callback(self, update, context) -> None:
        query = update.callback_query
        logging.info(f'Got callback message from {query.message.chat.id}')
        logging.debug(f'Got message: {query.data}')
        query.answer()
        response = self.controller.on_message(query.message.chat.id, query.data)
        self.send_response(query.message.chat.id, response)
        logging.info(f'Send response to {query.message.chat.id}')

    def scheduled(self):
        users, response = self.controller.reminder()
        for user in users:
            self.send_response(user.chat_id, response)

    def schedule_job(self):
        logging.debug("Preparing scheduling job")
        scheduler = BlockingScheduler()
        logging.debug("Starting schedule")
        scheduler.scheduled_job(
            'cron',
            day_of_week='mon-fri',
            hour=10,
            timezone=timezone("Europe/Moscow"),
            next_run_time=datetime.now()
        )(self.scheduled)
        scheduler.start()

    def telegram_start(self):
        self.updater.start_polling()


def main():
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', encoding='utf-8', level=logging.DEBUG)
    api_key = os.environ.get('API_KEY')
    engine = InternalDatabaseConfiguration.get_engine()
    user_repository = UserRepository(engine)
    controller = Controller(user_repository)
    telegram = AdapterTelegram(api_key, controller)
    telegram.telegram_start()
    scheduler_thread = threading.Thread(target=telegram.schedule_job, daemon=True)
    telegram_thread = threading.Thread(target=telegram.telegram_start, daemon=True)
    scheduler_thread.start()
    telegram_thread.start()
    scheduler_thread.join()
    telegram_thread.join()


if __name__ == "__main__":
    main()
