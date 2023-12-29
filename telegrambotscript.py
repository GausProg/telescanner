import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telebot import types
import zipfile
from datetime import datetime, timedelta


sub = datetime.now().replace(microsecond=0)  #дата время окончания подписки
sublen = 0  #длительность подписки в секундах(потом поправить в дни)
payflag = False  #флаг того, что надо считывать время пополнения подписки

# инициализация логгера
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# функция для обработки команды start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я - бот, который поможет тебе распознать текст на твоем документе!")

# функция для обработки команды account
def account(update, context):
    if sub > datetime.now():
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ваша подписка закончится {sub} до этого момента осталось: {sub - datetime.now().replace(microsecond=0)}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"К сожалению, на данный момент, мы не обнаружили у вас подписку на наш сервис, нажмите /pay чтобы совершить покупку подписки.")


# функция для обработки сообщений с текстом
def text_handler(update, context):
    global balance, sublen, payflag
    text = update.message.text
    if text == 'Привет':
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"привет, я бот, который может распознать текст, нажмите /help, чтобы узнать подробнее, что я умею!")
    elif payflag and text.isdigit():
        sublen = int(text)
        payflag = True
        context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, нажмите /pay еще раз, для подтверждения или введите любую другую команду для отмены.")
    elif payflag and not text.isdigit():
        payflag = False
        context.bot.send_message(chat_id=update.effective_chat.id, text="Вы ввели не число, пожалуйста повторите алгоритм оплаты")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Неверная команда")


# функция для обработки сообщений с фотографиями
def photo_handler(update, context):
    if sub <= datetime.now():
        context.bot.send_message(chat_id=update.effective_chat.id, text="На данный момент у вас нет активных подписок для работы с нашем сервисом, введите /pay чтобы узнать доступные тарифы!")
        return
    # обработка фотки
    photo = update.message.photo[-1].get_file()
    ourphoto = photo.download('image.jpeg')
    from opsv import imagination
    ourphoto = imagination(ourphoto)

    handler = zipfile.ZipFile("PhotoZip.zip", "w")
    handler.write(ourphoto)
    handler.close()

    context.bot.send_document(chat_id=update.effective_chat.id, document=open('PhotoZip.zip', 'rb'))

# функция для обработки команды help
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Список команд:\n/start - Начать\n/account - Узнать сколько осталось до конца подписки\n/pay - Купить подписку")

#обработка оплаты
def pay(update, context):
    global sub, sublen, payflag
    #если подписка уже есть
    if sub > datetime.now():
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"У вас уже есть подписка длительностью {sublen} секунд, она заканчивается {sub}, после этого вам будет необходимо произвести оплату для использования нашего сервиса. А пока, наслаждайтесь возможностями распознавания текста!!!")
    else:
        if payflag:#если подписка продляется и уже получено количество секунд, на которое оно должно быть продлено
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ваша подписка продлена на {sublen} секунд")
            substart = datetime.now().replace(microsecond=0)
            sub = substart + timedelta(seconds=sublen)
            payflag = False
        else:#если подписка продляется, но количество секунд пока не получено
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Введите цифрами количество секунд на которую вы бы хотели продлить вашу подписку")
            payflag = True

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
#doc_handler = MessageHandler(Filters.document,  doc_handler)
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

