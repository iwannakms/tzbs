import telebot
import collections
from telebot import types
import mysql.connector
from socket import error as SocketError
import errno
import re
import datetime


try:
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="tezbus_db"
    )
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
    sys.exit()
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
    sys.exit()
  else:
    print(err)
    sys.exit()

mycursor = mydb.cursor()


bot = telebot.TeleBot("1878599177:AAFrV-J58nUKCEj6KCEIRnGWl6wu-RujrJ8")


print("Started...")


user_data = collections.defaultdict(dict)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/kettik')
    user_data[message.chat.id]['id'] = message.chat.id
    bot.send_message(message.chat.id, "бот TezBus приветствует вас!")
    bot.send_message(message.chat.id, "Нажмите на /kettik для того, чтобы начать.", reply_markup=markup)
    print(message.chat.id)


#ОБРАБОТКА РОЛИ ПОЛЬЗОВАТЕЛЯ
@bot.message_handler(commands=['kettik'])
def get_user_role(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Водитель', 'Пассажир')
    bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)

    bot.register_next_step_handler(message, post_user_role)


@bot.message_handler(content_types=['text'])
def post_user_role(message):
    if message.text.lower() == 'водитель' or message.text.lower() == 'пассажир':
        user_data[message.chat.id]['role'] = message.text
        return get_start_point(message) #ПЕРЕХОДИМ В ВВОДУ МЕСТА НАЧАЛА ПОЕЗДКИ
    else:
        bot.send_message(message.chat.id, 'ОШИБКА! Введите заново.')
        return get_user_role(message) #ЗАНОВО ПЕРЕХОДИМ К ВВОДУ РОЛИ ПОЛЬЗОВАТЕЛЯ


def reinput_user_role(message):
    if message.text.lower() == 'ввести заново роль':
        return get_user_role(message)

    return post_start_point(message)


#ОБРАБОТКА МЕСТА НАЧАЛА ПОЕЗДКИ
def get_start_point(message):
    start_point_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_point_markup.add('Ввести заново роль')
    bot.send_message(message.chat.id, 'Введите место начала поезки.', reply_markup=start_point_markup)
    bot.register_next_step_handler(message, reinput_user_role)


def post_start_point(message):
    user_data[message.chat.id]['start_point'] = re.sub(r"\d+", "", message.text, flags=re.UNICODE)
    return get_end_point(message)


def reinput_start_point(message):
    if message.text.lower() == 'ввести заново место начала поездки':
        return get_start_point(message)

    return post_end_point(message)


#ОБРАБОТКА МЕСТА КОНЦА ПОЕЗДКИ
def get_end_point(message):
    end_pont_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    end_pont_markup.add('Ввести заново место начала поездки')
    bot.send_message(message.chat.id, 'Введите место конца поездки', reply_markup=end_pont_markup)
    bot.register_next_step_handler(message, reinput_start_point)


def post_end_point(message):
    if user_data[message.chat.id]['start_point'].lower() != message.text.lower():
        user_data[message.chat.id]['end_point'] = re.sub(r"\d+", "", message.text, flags=re.UNICODE)
    else:
        bot.send_message(message.chat.id, 'ОШИБКА! Место конца поездки не может быть таким же, что и место начала поездки. Введите заново')
        return get_end_point(message)

    return get_date_of_travel(message)


def reinput_end_point(message):
    if message.text.lower() == 'ввести заново место конца поездки':
        return get_end_point(message)

    return post_date_of_travel(message)


#ОБРАБОТКА ДАТЫ ПОЕЗДКИ
def get_date_of_travel(message):
    date_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    date_markup.add('Сегодня', 'Завтра', 'Ввести заново место конца поездки')
    bot.send_message(message.chat.id, 'Введите дату поездки в формате год-месяц-день \nНапример: 1999-12-31 ', reply_markup=date_markup)
    bot.register_next_step_handler(message, reinput_end_point)


def post_date_of_travel(message):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    if message.text.lower() == 'сегодня':
        user_data[message.chat.id]['date_of_travel'] = today.strftime('%Y-%m-%d')
    elif message.text.lower() == 'завтра':
        user_data[message.chat.id]['date_of_travel'] = tomorrow.strftime('%Y-%m-%d')
    else:
        user_data[message.chat.id]['date_of_travel'] = message.text
    return get_time_of_travel(message)


def reinput_date_of_travel(message):
    if message.text.lower() == 'ввести заново дату поездки':
        return get_date_of_travel(message)

    return post_time_of_travel(message)


#ОБРАБОТКА ВРЕМЕНИ ПОЕЗДКИ
def get_time_of_travel(message):
    time_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    time_markup.add('Ввести заново дату поездки')
    bot.send_message(message.chat.id, 'Введите время поездки', reply_markup=time_markup)
    bot.register_next_step_handler(message, reinput_date_of_travel)


def post_time_of_travel(message):
    user_data[message.chat.id]['time_of_travel'] = message.text
    return get_type_of_transport(message)


def reinput_time_of_travel(message):
    if message.text.lower() == 'ввести заново время поездки':
        return get_date_of_travel(message)

    return post_type_of_transport(message)


#ОБРАБОТКА ТИПА ТРАНСПОРТА ПОЛЬЗОВАТЕЛЯ
def get_type_of_transport(message):
    type_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_data[message.chat.id]['role'].lower() == 'водитель':
        type_markup.add('машина', 'автобус', 'ввести заново время поездки')
    else:
        type_markup.add('машина', 'автобус', 'поезд', 'ввести заново время поездки')

    bot.send_message(message.chat.id, 'Введите тип транспорта.', reply_markup=type_markup)
    bot.register_next_step_handler(message, reinput_time_of_travel)


def post_type_of_transport(message):
    if user_data[message.chat.id]['role'].lower == 'водитель':
        if message.text.lower() == 'машина' or message.text.lower() == 'автобус':
            user_data[message.chat.id]['type_of_transport'] = message.text
            return get_number_of_seats(message)
        else:
            bot.send_message(message.chat.id, 'ОШИБКА! Введите заново')
            return get_type_of_transport(message)
    else:
        if message.text.lower() == 'машина' or message.text.lower() == 'автобус' or message.text.lower() == 'поезд':
            user_data[message.chat.id]['type_of_transport'] = message.text
            return get_number_of_seats(message)
        else:
            bot.send_message(message.chat.id, 'ОШИБКА! Введите заново')
            return get_type_of_transport(message)


def reinput_type_of_transport(message):
    if message.text.lower() == 'ввести заново тип транспорта':
        return get_type_of_transport(message)

    return post_number_of_seats(message)


#ОБРАБОТКА КОЛИЧЕСТВ МЕСТ
def get_number_of_seats(message):
    seats_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    seats_markup.add('1', '2', '3', '4', '5', '6', 'ввести заново тип транспорта')
    bot.send_message(message.chat.id, 'Введите количество мест.', reply_markup=seats_markup)
    bot.register_next_step_handler(message, reinput_type_of_transport)


def post_number_of_seats(message):
    if message.text.isdigit():
        user_data[message.chat.id]['number_of_seats'] = int(message.text)
        return get_price_of_travel(message)
    else:
        bot.send_message(message.chat.id, 'ОШИБКА! Введите заново')
        return get_number_of_seats(message)


def reinput_number_of_seats(message):
    if message.text.lower() == 'ввести заново количество мест':
        return get_number_of_seats(message)

    return post_price_of_travel(message)


#ОБРАБОТКА ЦЕНЫ ПОЕЗДКИ
def get_price_of_travel(message):
    price_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    price_markup.add('ввести заново количество мест')
    bot.send_message(message.chat.id, 'Введите цену поездки (сом).', reply_markup=price_markup)
    bot.register_next_step_handler(message, reinput_number_of_seats)


def post_price_of_travel(message):
    if message.text.isdigit():
        user_data[message.chat.id]['price_of_travel'] = message.text
        return get_telephone(message)
    else:
        bot.send_message(message.chat.id, 'ОШИБКА. Введите заново')
        return get_price_of_travel(message)


def reinput_price_of_travel(message):
    if message.text.lower() == 'ввести заново цену поездки':
        return get_price_of_travel(message)

    return post_telephone(message)


#ОБРАБОТКА НОМЕРА ТЕЛЕФОНА
def get_telephone(message):
    telephone_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    telephone_markup.add('ввести заново цену поездки')
    bot.send_message(message.chat.id, 'Введите ваш номер телефона.', reply_markup=telephone_markup)
    bot.register_next_step_handler(message, reinput_price_of_travel)


def post_telephone(message):
    user_data[message.chat.id]['telephone'] = message.text
    return final(message)


def reinput_telephone(message):
    if message.text.lower() == 'ввести заново номер телефона':
        return get_telephone(message)

    return get_result(message)


#РЕЗУЛЬТАТ
def final(message):
    final_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    final_markup.add('завершить регистрацию', 'ввести заново номер телефона')
    bot.send_message(message.chat.id, 'Хотите завершить регистрацию?', reply_markup=final_markup)
    bot.register_next_step_handler(message, reinput_telephone)


#РЕКОМЕНДАЦИИ
def get_result(message):
    result_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    result_markup.add('получить рекомендации', 'нет')
    bot.send_message(message.chat.id, 'Регистрация прошла успешно!')
    bot.send_message(message.chat.id, f"Человек: {user_data[message.chat.id]['role']}\nМесто начала поездки: {user_data[message.chat.id]['start_point']}\nМесто конца поездки: {user_data[message.chat.id]['end_point']}\nДата поездки: {user_data[message.chat.id]['date_of_travel']}\nВремя поездки: {user_data[message.chat.id]['time_of_travel']}\nТип транспорта: {user_data[message.chat.id]['type_of_transport']}\nКоличество мест: {user_data[message.chat.id]['number_of_seats']}\nЦана поездки: {user_data[message.chat.id]['price_of_travel']}\nНомер телефона: {user_data[message.chat.id]['telephone']}")
    bot.send_message(message.chat.id, 'Хотите получить рекомендации?', reply_markup=result_markup)
    bot.register_next_step_handler(message, send_recommendations)


def send_recommendations(message):
    if message.text.lower() == 'получить рекомендации':
        if user_data[message.chat.id]['role'] == "Пассажир":
            sql = "SELECT * FROM drivers WHERE start_point = %s AND end_point = %s AND date_of_travel = %s "
            val = (user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'],)
            mycursor.execute(sql, val)
            myresult_1 = mycursor.fetchall()
            myresult = list(myresult_1)
            for i in myresult:
                bot.send_message(message.chat.id, '===========\nОткуда: '+str(i[2])+'\nКуда: '+str(i[3])+'\nКогда: '+str(i[4])+'\nВремя: '+str(i[5])+'\nТип траспорта: '+str(i[6])+'\nКоличество пассажиров: '+str(i[7])+'\nЦена: '+str(i[8])+'\nНомер: '+i[9]+'\n============'+'\n')
        else:
            sql = "SELECT * FROM passengers WHERE start_point = %s AND end_point = %s AND date_of_travel = %s "
            val = (user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'],)
            mycursor.execute(sql, val)
            myresult_1 = mycursor.fetchall()
            myresult = list(myresult_1)
            for i in myresult:
                bot.send_message(message.chat.id, '===========\nОткуда: '+str(i[2])+'\nКуда: '+str(i[3])+'\nКогда: '+str(i[4])+'\nВремя: '+str(i[5])+'\nТип траспорта: '+str(i[6])+'\nКоличество пассажиров: '+str(i[7])+'\nЦена: '+str(i[8])+'\nНомер: '+i[9]+'\n============'+'\n')

    return send_result(message)


#ФИНАЛ
def send_result(message):
    post_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    post_markup.add('отправить','нет')
    if user_data[message.chat.id]['type_of_transport'] =='поезд':
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Нажмите на /kettik для того, чтобы начать.', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Хотите отправить этот пост в группу?', reply_markup=post_markup)
        bot.register_next_step_handler(message, post_message)

    if user_data[message.chat.id]['role'] =='Водитель':
        sql = "INSERT INTO drivers(user_id, start_point, end_point, date_of_travel, time_of_travel, type_of_transport, number_of_seats, price_of_travel, telephone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (user_data[message.chat.id]['id'], user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'], user_data[message.chat.id]['time_of_travel'], user_data[message.chat.id]['type_of_transport'], user_data[message.chat.id]['number_of_seats'], user_data[message.chat.id]['price_of_travel'], user_data[message.chat.id]['telephone'])
        mycursor.execute(sql, val)
        mydb.commit()
    else:
        sql = "INSERT INTO passengers(user_id, start_point, end_point, date_of_travel, time_of_travel, type_of_transport, number_of_seats, price_of_travel, telephone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (user_data[message.chat.id]['id'], user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'], user_data[message.chat.id]['time_of_travel'], user_data[message.chat.id]['type_of_transport'], user_data[message.chat.id]['number_of_seats'], user_data[message.chat.id]['price_of_travel'], user_data[message.chat.id]['telephone'])
        mycursor.execute(sql, val)
        mydb.commit()


bot.enable_save_next_step_handlers(delay=2)


def post_message(message):
    if message.text.lower() == 'отправить':
        bot.send_message(-1001561468463, f"Кто: {user_data[message.chat.id]['role']}\nОткуда: {user_data[message.chat.id]['start_point']}\nКуда: {user_data[message.chat.id]['end_point']}\nКогда: {user_data[message.chat.id]['date_of_travel']}\nВремя: {user_data[message.chat.id]['time_of_travel']}\nТип транспорта: {user_data[message.chat.id]['type_of_transport']}\nКоличество мест: {user_data[message.chat.id]['number_of_seats']}\nЦана: {user_data[message.chat.id]['price_of_travel']}\nНомер телефона: {user_data[message.chat.id]['telephone']}" )
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Ваш пост отправлен!', reply_markup=markup)
        bot.send_message(message.chat.id, 'Нажмите на /kettik для того, чтобы начать.', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Нажмите на /kettik для того, чтобы начать.', reply_markup=markup)


bot.load_next_step_handlers()

bot.infinity_polling()

