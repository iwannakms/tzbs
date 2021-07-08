import telebot
from telebot import types
import mysql.connector


bot = telebot.TeleBot("1878599177:AAFrV-J58nUKCEj6KCEIRnGWl6wu-RujrJ8")


print("Started...")

user_data = {}


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
	if message.text or message.text == 'Ввести заново тип транспорта':
		transport_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

		if message.text == 'Водитель':
			transport_markup.add('Машина', 'Автобус')
			bot.send_message(message.chat.id, 'Какой у вас вид транпорта?', reply_markup=transport_markup)
			user_data['id'] = message.chat.id
			user_data['role'] = message.text
		elif message.text == 'Пассажир':
			transport_markup.add('Машина', 'Автобус', 'Поезд')
			bot.send_message(message.chat.id, 'Какой у вас вид транпорта?', reply_markup=transport_markup)
			user_data['id'] = message.chat.id
			user_data['role'] = message.text

	bot.register_next_step_handler(message, get_number_of_seats)


def get_number_of_seats(message):
	seats_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	seats_markup.add('1', '2', '3', '4', '5', '6', 'Ввести заново тип транспорта')

	if user_data['role'] == 'Водитель':
		if message.text == 'Машина' or message.text == 'Автобус' or message.text == 'Ввести заново количество мест':
			bot.send_message(message.chat.id, 'Выберите количество ваших мест, либо введите с клавиатуры.', reply_markup=seats_markup)
			if message.text == 'Машина' or message.text == 'Автобус':
				user_data['type_of_transport'] = message.text
		else:
			bot.send_message(message.chat.id, 'Ошибка.')
	elif user_data['role'] == 'Пассажир':
		if message.text == 'Машина' or message.text == 'Автобус' or message.text == 'Поезд' or message.text == 'Ввести заново количество мест':
			bot.send_message(message.chat.id, 'Выберите количество ваших мест, либо введите с клавиатуры.', reply_markup=seats_markup)
			if message.text == 'Машина' or message.text == 'Автобус' or message.text == 'Поезд':
				user_data['type_of_transport'] = message.text
		else:
			bot.send_message(message.chat.id, 'Ошибка.')

	bot.register_next_step_handler(message, get_start_point)


def get_start_point(message):
	if message.text == 'Ввести заново тип транспорта':
		message.text = user_data['role']
		get_type_of_transport(message)
	elif message.text.isdigit() or message.text == 'Ввести заново место начала поездки':
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново количество мест')
		bot.send_message(message.chat.id, 'Введите место начала поездки.', reply_markup=markup)
		if message.text.isdigit():
			user_data['number_of_seats'] = message.text
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
		if message.text != 'Ввести заново место конца поездки':
			user_data['start_point'] = message.text
		bot.register_next_step_handler(message, get_time_of_travel)


def get_time_of_travel(message):
	if message.text == 'Ввести заново место начала поездки':
		get_start_point(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново место конца поездки')
		bot.send_message(message.chat.id, 'Введите время начала поездки', reply_markup=markup)
		if message.text != 'Ввести заново время поездки':
			user_data['end_point'] = message.text
		bot.register_next_step_handler(message, get_price_of_travel)


def get_price_of_travel(message):
	if message.text == 'Ввести заново место конца поездки':
		get_end_point(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново время поездки')
		bot.send_message(message.chat.id, 'Введите цену поездки (с человека)', reply_markup=markup)
		if message.text != 'Ввести заново цену поездки':
			user_data['time_of_travel'] = message.text
		bot.register_next_step_handler(message, get_telephone)


def get_telephone(message):
	if message.text == 'Ввести заново время поездки':
		get_time_of_travel(message)
	else:
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('Ввести заново цену поездки')
		bot.send_message(message.chat.id, 'Введите свой номер телефона.', reply_markup=markup)
		if message.text != 'да':
			user_data['price_of_travel'] = message.text
		bot.register_next_step_handler(message, reinput_telephone)


def reinput_telephone(message):
	if message.text == 'Ввести заново цену поездки':
		get_price_of_travel(message)
	else:
		user_data['telephone'] = message.text
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
		markup.add('да', 'нет')
		bot.send_message(message.chat.id, 'Хотите ввести заново номер телефона?', reply_markup=markup)
		bot.register_next_step_handler(message, final)


def final(message):
	if message.text == 'да':
		get_telephone(message)
	else:
		markup = types.ReplyKeyboardRemove(selective=False)
		bot.send_message(message.chat.id, 'Регистрация прошла успешно', reply_markup=markup)
		bot.send_message(message.chat.id, f"Человек: {user_data['role']}\nТип транспорта: {user_data['type_of_transport']}\nКоличество мест: {user_data['number_of_seats']}\nМесто начала поездки: {user_data['start_point']}\nМесто конца поездки: {user_data['end_point']}\nВремя поездки: {user_data['time_of_travel']}\nЦена поездки: {user_data['price_of_travel']}\nНомер телефона: {user_data['telephone']}")


bot.polling(none_stop=True)

