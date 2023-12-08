import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telebot import types
import zipfile

balance = 20

# инициализация логгера
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# функция для обработки команды start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Привет! Ваш баланс: {balance}")

# функция для обработки команды account
def account(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ваш баланс: {balance}")


# функция для обработки сообщений с текстом
def text_handler(update, context):
    global balance
    text = update.message.text
    if text == 'Узнать баланс':
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ваш баланс: {balance}")
    elif text == 'Пополнить баланс':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Баланс пополнен на 10 единиц")
        balance = balance + 10
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Неверная команда")


# функция для обработки сообщений с фотографиями
def photo_handler(update, context):
    global balance
    if balance <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш баланс равен нулю, пополните баланс")
        return

    photo = update.message.photo[-1].get_file()
    ourphoto = photo.download('image.jpeg')
    from opsv import imagination
    ourphoto = imagination(ourphoto)

    handler = zipfile.ZipFile("PhotoZip.zip", "w")
    handler.write(ourphoto)
    handler.close()

    context.bot.send_document(chat_id=update.effective_chat.id, document=open('PhotoZip.zip', 'rb'))

    balance = balance - 10

def doc_handler(update, context):
    return 

# функция для обработки команды help
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Список команд:\n/start - Начать\n/account - Узнать баланс\n/pay - Пополнить баланс")

def pay(update, context):
    global balance
    context.bot.send_message(chat_id=update.effective_chat.id, text="Баланс пополнен на 10 единиц")
    balance = balance + 10


# функция для обработки неизвестных команд
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Неверная команда")


# создание экземпляра Updater и добавление обработчиков
updater = Updater(token='6422490098:AAE2-XMqDV3CHUnF68lNDJAR7atZEk3dX58', use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
account_handler = CommandHandler('account', account)
text_handler = MessageHandler(Filters.text & (~Filters.command), text_handler)
photo_handler = MessageHandler(Filters.photo, photo_handler)
doc_handler = MessageHandler(Filters.document,  doc_handler)
help_handler = CommandHandler('help', help)
pay_handler = CommandHandler('pay', pay)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(account_handler)
dispatcher.add_handler(text_handler)
dispatcher.add_handler(photo_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(pay_handler)
dispatcher.add_handler(unknown_handler)

# запуск бота
updater.start_polling()

