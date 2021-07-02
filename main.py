import telebot
from telebot import types
import mysql.connector


bot = telebot.TeleBot("1878599177:AAFrV-J58nUKCEj6KCEIRnGWl6wu-RujrJ8")


# db = mysql.connector.connect(
# 	host='localhost',
# 	user='nuradil',
# 	passwd='iwannakms',
# 	port='3306'
# )

# cursor = db.cursor()
#


# print(db)

print("Started...")



user_date = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "бот TezBus приветствует вас!")
	bot.send_message(message.chat.id, "Нажмите на /kettik для того, чтобы начать.")


@bot.message_handler(commands=['kettik'])
def get_user_direction(message):
	markup_inline = types.InlineKeyboardMarkup()
	item_driver = types.InlineKeyboardButton(text = 'Водитель', callback_data = 'driver')
	item_passenger = types.InlineKeyboardButton(text = 'Пассажир', callback_data = 'passenger')

	markup_inline.add(item_driver, item_passenger)

	bot.send_message(message.chat.id, "Кто вы?", reply_markup = markup_inline)

	# if not bot.message_handler(commands=[""]):
	# 	bot.send_message(message.chat.id, "")
	# else:
	# 	bot.send_message(message.chat.id,"Да заебал нажимать!")
	# # bot.reply_to(message, "Отлично! ")

if __name__ == 'main':
	bot.polling(none_stop=True)

# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	bot.reply_to(message, message.text)
#
bot.polling()