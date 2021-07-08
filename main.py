import telebot
from telebot import types
import mysql.connector


bot = telebot.TeleBot("1878599177:AAFrV-J58nUKCEj6KCEIRnGWl6wu-RujrJ8")


print("Started...")


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
	print(message.chat.id)


@bot.message_handler(commands=['kettik'])
def get_user_direction(message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	markup.add('Водитель', 'Пассажир')
	bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_type_of_transport(message):
	if message.text == 'Водитель' or message.text == 'Ввести заново тип транспорта':
		transport_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		transport_markup.add('Машина', 'Автобус')
		bot.send_message(message.chat.id, 'Какой у вас вид транпорта?', reply_markup=transport_markup)
		bot.register_next_step_handler(message, get_number_of_seats)


def get_number_of_seats(message):
	if message.text == 'Машина' or message.text == 'Автобус' or message.text == 'Ввести заново количество мест':
		seats_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		seats_markup.add('1', '2', '3', '4', '5', '6', 'Ввести заново тип транспорта')
		bot.send_message(message.chat.id, 'Выберите количество ваших мест, либо введите с клавиатуры.', reply_markup=seats_markup)
		bot.register_next_step_handler(message, get_start_point)
	else:
		bot.send_message(message.chat.id, 'Ошибка.')


def get_start_point(message):
	if message.text == 'Ввести заново тип транспорта':
		get_type_of_transport(message)
	elif message.text.isdigit() or message.text == 'Ввести заново место начала поездки':
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново количество мест')
		bot.send_message(message.chat.id, 'Введите место начала поездки.', reply_markup=markup)
		bot.register_next_step_handler(message, get_end_point)
	else:
		bot.send_message(message.chat.id, 'Ошибка')


def get_end_point(message):
	if message.text == 'Ввести заново количество мест':
		get_number_of_seats(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново место начала поездки')
		bot.send_message(message.chat.id, 'Введите место конца поездки.', reply_markup=markup)
		bot.register_next_step_handler(message, get_time_of_travel)


def get_time_of_travel(message):
	if message.text == 'Ввести заново место начала поездки':
		get_start_point(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново место конца поездки')
		bot.send_message(message.chat.id, 'Введите время начала поездки', reply_markup=markup)
		bot.register_next_step_handler(message, get_price_of_travel)


def get_price_of_travel(message):
	if message.text == 'Ввести заново место конца поездки':
		get_end_point(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново время поездки')
		bot.send_message(message.chat.id, 'Введите цену поездки', reply_markup=markup)
		bot.register_next_step_handler(message, reinput_time_of_travel)


def reinput_time_of_travel(message):
	if message.text == 'Ввести заново время поездки':
		get_time_of_travel(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('да', 'нет')
		bot.send_message(message.chat.id, 'Хотите ввести заново цену поездки?', reply_markup=markup)
		bot.register_next_step_handler(message, reinput_price_of_travel)


def reinput_price_of_travel(message):
	if message.text == 'да':
		get_price_of_travel(message)
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, 'Регистрация прошла успешно', reply_markup=markup)


bot.polling(none_stop=True)

