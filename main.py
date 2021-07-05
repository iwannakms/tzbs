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

user_data = []

"""
class Driver:

	def __init__(self, type_of_transport, number_of_seats, start_point, end_point, travel_time):
		self.type_of_transport = type_of_transport
		self.number_of_seats = number_of_seats
		self.start_point = start_point
		self.end_point = end_point
		self.travel_time = travel_time"""


@bot.message_handler(commands=['start'])
def send_welcome(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	markup.add('/kettik')
	bot.send_message(message.chat.id, "бот TezBus приветствует вас!")
	bot.send_message(message.chat.id, "Нажмите на /kettik для того, чтобы начать.", reply_markup=markup)


"""@bot.message_handler(commands=['help'])
def get_help(message):
	commands = bot.get_my_commands()
	bot.send_message(message.chat.id, commands)"""


@bot.message_handler(commands=['kettik'])
def get_user_direction(message):
	markup_inline = types.InlineKeyboardMarkup()
	item_driver = types.InlineKeyboardButton(text='Водитель', callback_data='driver')
	item_passenger = types.InlineKeyboardButton(text='Пассажир', callback_data='passenger')

	markup_inline.add(item_driver, item_passenger)

	bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup_inline)

	# if not bot.message_handler(commands=[""]):
	# 	bot.send_message(message.chat.id, "")
	# else:
	# 	bot.send_message(message.chat.id,"Да заебал нажимать!")
	# # bot.reply_to(message, "Отлично! ")


@bot.callback_query_handler(func=lambda call: True)
def get_type_of_transport(call):
	if call.data == 'driver':
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Принято', reply_markup=None)
		transport_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		transport_markup.add('машина', 'автобус', 'поезд')
		bot.send_message(call.message.chat.id, 'Какой у вас вид транпорта?', reply_markup=transport_markup)
	else:
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Принято', reply_markup=None)


@bot.message_handler(content_types=['text'])
def get_number_of_seats(message):
	if message.text == 'машина' or message.text == 'автобус' or message.text == 'поезд':
		seats_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		seats_markup.add('1', '2', '3', '4', '5', '6')
		bot.send_message(message.chat.id, 'Выберите количество ваших мест, либо введите с клавиатуры.', reply_markup=seats_markup)
		bot.register_next_step_handler(message, get_start_point)
	else:
		bot.send_message(message.chat.id, 'Ошибка.')


@bot.message_handler(content_types=['text'])
def get_start_point(message):
	if message.text.isdigit():
		bot.send_message(message.chat.id, 'Введите место начала поездки.')
		bot.register_next_step_handler(message, get_end_point)
	else:
		bot.send_message(message.chat.id, 'Ошибка')


@bot.message_handler(content_types=['text'])
def get_end_point(message):
	bot.send_message(message.chat.id, 'Введите место конца поездки.')
	bot.register_next_step_handler(message, get_time_of_travel)


@bot.message_handler(content_types=['text'])
def get_time_of_travel(message):
	bot.send_message(message.chat.id, 'Введите время начала поездки')


if __name__ == 'main':
	bot.polling(none_stop=True)

# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
# 	bot.reply_to(message, message.text)
#
bot.polling()
