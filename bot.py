import telebot
from telebot import types
import re
from config import bot_token, lin_id, group_id
import time
import schedule
from datetime import datetime, date
import xlwt
from xlwt import Workbook
from threading import Thread
from date_formating import st_to_date
import io
import sql_lib
import sys

token = bot_token
bot = telebot.TeleBot(token)

# Города и объекты перенести в базу данных, сделать запросы
towns_and_objects = {
    "Алакуртти": ["Алакуртти"],
    "Абакан": ["Плоскостные спортивные сооружения", "Учебное поле для подразделений связи", "УСТК Старт",
               "КПП (ЖДБР)", "Комплексное здание штабов с помещениями для личного состава",
               "Казарма для размещения личного состава", "ПТОР на 8 постов", "Здание командного пункта", "Склад"],
    "Алыгджер": ["Школа сад на 60-20 чел"],
    "Нижнеудинск": ["Школа на 520 чел", "Дет сад на 140 чел", "ФОК с бассейном 2 этажа", "Водозабор", "Теплотрасса"],
    "Евдокимова": ["КДЦ", "Школа сад на 128 человек"],
    "Тулун": ["ИЖС"],
    "Иркутск": ["СВУ", "Патриот", "Школа на 500 мест", "Онкоцентр"],
    "Москва": ["Хамовники"],
    "Дивногорск": ["В/ч"],
    "Новосибирск": ["Стужа", "Госпиталь"],
    "Североморск": ["Госпиталь"],
    "Кызыл": ["Жилая зона", "Госпиталь этап 2", "55 бригада", "Зеленые крыши"],
    "Мурманск": ["Школа на 800 мест"],
    "Ужур": ["УСТК старт", "Ледовая площадка", "КДЦ"]}
towns = towns_and_objects.keys()

pattern1 = '^[а-я]{1}[0-9]{3}[а-я]{2}[0-9]{2,3}$'
pattern2 = '/^[а-я]{2}[0-9]{4} [0-9]{2}$/'
pattern3 = '^[а-я]{2}[0-9]{5}'
carNumRegex1 = re.compile(r'^[а-я]{1}[0-9]{3}[а-я]{2}[0-9]{2,3}$')
carNumRegex2 = re.compile(r'/^[а-я]{2} [0-9]{4} [0-9]{2}$/')
carNumRegex3 = re.compile(r'^[а-я]{2}[0-9]{5}')
NumRegex = re.compile(r'^[0-9]+$')


def journal_log(text_):
    print(text_)
    sys.stdout.flush()


# команда /start
@bot.message_handler(commands=['start'])
def start(message):
    # откатываем назад прогресс
    sql_lib.sql_update_user_status(message.from_user.id, "idle")
    # создаем клавиатуру
    keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_car = types.InlineKeyboardButton(text="Пришла машина", callback_data='arrival')
    keyboard1.add(key_car)
    bot.send_message(message.chat.id, 'Привет! \nЯ могу фиксировать '
                                      'приходящие на объект машины. И на этом пока все.\n Если Вы хотите задать вопрос'
                                      ' или предложить функцию для моей работы, введите /help \n Если вы хотите учесть '
                                      'машину, которая пришла на объект, введите (или нажмите в тексте) /arrival, либо '
                                      'нажмите кнопку "Пришла машина"',
                     reply_markup=keyboard1, parse_mode="Markdown")


# команда /help
@bot.message_handler(commands=['help'])
def start(message):
    keyboard0 = telebot.types.InlineKeyboardMarkup()
    key_connection = telebot.types.InlineKeyboardButton(text='Связаться с создательницей', url='telegram.me/Veir_Rocky')
    keyboard0.add(key_connection)

    bot.send_message(message.chat.id, "Если у вас есть вопросы, жалобы, предложения касательно моей работы, "
                                      "то нажмите на кнопку ниже.", reply_markup=keyboard0, parse_mode="Markdown")


# команла arrival
@bot.message_handler(commands=['arrival'])
def arrival(message):
    # откатываем назад прогресс
    sql_lib.sql_update_user_status(message.from_user.id, "idle")
    # создаем клавиатуру
    keyboard12 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_car = types.InlineKeyboardButton(text="Пришла машина", callback_data='arrival')
    keyboard12.add(key_car)
    bot.send_message(message.chat.id, "Нажмите 'Пришла машина'", reply_markup=keyboard12, parse_mode="Markdown")


# Команда download_all
@bot.message_handler(commands=['download_all'])
def download_all(message):
    data = sql_lib.sql_select_cars()
    new_name = 'all_cars' + '.xls'
    wb = Workbook()
    sheet1 = wb.add_sheet('Весь транспорт')
    sheet1.write(0, 0, "Город")
    sheet1.write(0, 1, "Объект")
    sheet1.write(0, 2, "Номер машины")
    sheet1.write(0, 3, "Грузоподъемность")
    sheet1.write(0, 4, "Дата")
    for i in range(len(data)):
        sheet1.write(i + 1, 0, data[i][0])
        sheet1.write(i + 1, 1, data[i][1])
        sheet1.write(i + 1, 2, data[i][2])
        sheet1.write(i + 1, 3, data[i][3])
        sheet1.write(i + 1, 4, datetime.fromtimestamp(int(data[i][4])).isoformat(sep=" "))


    wb.save(new_name)
    with open(new_name, "rb") as misc:
        f = misc.read()
        file_obj = io.BytesIO(f)
        file_obj.name = new_name
    bot.send_message(message.chat.id, "Вы хотите получить все данные. Я Вас понял!", parse_mode="Markdown")
    bot.send_document(message.chat.id, file_obj)


# выгрузка файла с сегодняшними машинами
@bot.message_handler(commands=['download_today'])
def download_today(message):
    if message.chat.type == 'private' and can_chat(message.chat.id) is True:
        today = date.today()
        bot.send_message(message.chat.id,
                         f"Отсылаю файл с машинами, которые были {today.strftime('%d.%m.%Y')} (20:00 по Красноярскому времени)",
                         parse_mode="Markdown")
        new_name = str(today) + '_pers' + '.xls'
        data_to_write = sql_lib.select_everyday_summary(today)

        wb = Workbook()
        sheet1 = wb.add_sheet('Весь транспорт')
        sheet1.write(0, 0, "Город")
        sheet1.write(0, 1, "Объект")
        sheet1.write(0, 2, "Номер машины")
        sheet1.write(0, 3, "Дата")
        sheet1.write(0, 4, "Грузоподъемность")

        for i in range(len(data_to_write)):
            sheet1.write(i + 1, 0, data_to_write[i][0])
            sheet1.write(i + 1, 1, data_to_write[i][1])
            sheet1.write(i + 1, 2, data_to_write[i][2])
            sheet1.write(i + 1, 3, datetime.fromtimestamp(int(data_to_write[i][3])).isoformat(sep=" "))
            sheet1.write(i + 1, 4, data_to_write[i][4])

        wb.save(new_name)
        with open(new_name, "rb") as misc:
            f = misc.read()
            file_obj = io.BytesIO(f)
            file_obj.name = new_name
        bot.send_document(message.chat.id, file_obj)


# получить список всех объектов без привязки к городу
def get_all_objects(towns_and_objects):
    all_objects = []
    list = towns_and_objects.values()
    for element in list:
        for object in element:
            all_objects.append(object)
    return all_objects


# получить список объектов для заданного города
def get_objects(town):
    objects = towns_and_objects[town]
    return objects


# получить данные из сообщения, подготовить клавиатуру и ответ, вызвать функцию для логгирования
def parse_message(message):
    statuses = {
        'idle': parse_message_idle,
        'waiting_town': parse_message_asked_town,
        'waiting_obj': parse_message_asked_obj,
        'waiting_car_num': parse_message_asked_car_num,
        'waiting_car_weight': parse_message_asked_weight,
        # 'waiting_car_photo': parse_message_car_photo,
        'waiting_confirmation': parse_message_finish
    }

    user_id = message.from_user.id
    username = message.from_user.username
    message_id = message.message_id
    text = message.text
    datetime = message.date
    photo = message.photo

    user = sql_lib.sql_get_user_data(user_id)
    if not user:
        id = sql_lib.add_user(user_id, username)
        user = [id, user_id, username, "idle"]
    user_status = user[3]

    message_data = {'user_id': user_id,
                    'username': username,
                    'message_id': message_id,
                    'datetime': datetime,
                    'text': text,
                    'photo': photo,
                    'town': None,
                    'object': None,
                    'car_num': None,
                    'car_weight': None,
                    'state': user_status}

    sql_lib.sql_log_message(message_data)

    output = []
    if user_status in statuses:
        output = statuses.get(user_status)(message, user)
    if output:
        return output
    else:
        assert "Debugging problem, check logs"


def parse_message_idle(message, user):
    if message.text == 'Пришла машина':
        print("Пришло сообщение пришла машина")
        # обновим статус пользователя, чтобы начиналась новая запись, при получении этого сообщения
        sql_lib.sql_update_user_status(message.from_user.id, "idle")
        # удалим предыдущие данные от этого пользователя если они не готовы
        sql_lib.remove_unready_car(message)
        # создаем новую запись в cars
        sql_lib.sql_car_start(message)
        keyboard = types.ReplyKeyboardMarkup()
        for town in towns:
            key = types.InlineKeyboardButton(text=town, callback_data="town")
            keyboard.add(key)

        # меняем статус в users
        sql_lib.sql_update_user_status(message.from_user.id, "waiting_town")
        sql_lib.sql_update_user_row_id(message.from_user.id)
        return ["Выберите город:", keyboard]
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key = types.InlineKeyboardButton(text="Пришла машина")
        keyboard.add(key)
        msg = 'Я Вас не понимаю. Нажмите "Пришла машина", чтобы учесть транспорт. \nЕсли что-то пошло не так, ' \
              'нажмите /start, чтобы начать сначала.\n\nЕсли бот работает некорректно, ' \
              'нажмите /help, чтобы сообщить об ошибке'
        return [msg, keyboard]


def parse_message_asked_town(message, user):
    if message.text in towns:
        keyboard = types.ReplyKeyboardMarkup()
        objects = get_objects(message.text)
        for object in objects:
            key = types.InlineKeyboardButton(text=object, callback_data="object")
            keyboard.add(key)
        # меняем статус в users
        sql_lib.sql_update_user_status(message.from_user.id, "waiting_obj")
        # меняем город в cars
        sql_lib.sql_update_car_town(message)
        return ["Выберите объект:", keyboard]
    else:
        keyboard = types.ReplyKeyboardMarkup()
        for town in towns:
            key = types.InlineKeyboardButton(text=town, callback_data="town")
            keyboard.add(key)
        msg = 'Я Вас не понимаю. Выберите город из списка. \nЕсли что-то пошло не так, нажмите /start, ' \
              'чтобы начать сначала.\n\nЕсли бот работает некорректно, нажмите /help, чтобы сообщить об ошибке'
        return [msg, keyboard]


# Получили объект от пользователя
def parse_message_asked_obj(message, user):
    if message.text in get_all_objects(towns_and_objects):
        # Обновляем объект в cars
        sql_lib.sql_update_car_object(message)
        sql_lib.sql_update_user_status(message.from_user.id, "waiting_car_num")

        return ["Введите номер машины в формате а000аа00", []]
    else:
        keyboard = types.ReplyKeyboardMarkup()
        town = sql_lib.sql_get_town(message.chat.id)
        town = town[0]
        objects = get_objects(town)
        for object in objects:
            key = types.InlineKeyboardButton(text=object, callback_data="object")
            keyboard.add(key)
        msg = 'Я Вас не понимаю. Выберите объект из списка. \nЕсли что-то пошло не так, нажмите /start, ' \
              'чтобы начать сначала.\n\nЕсли бот работает некорректно, нажмите /help, чтобы сообщить об ошибке'
        return [msg, keyboard]


# Получили номер машшины от пользователя
def parse_message_asked_car_num(message, user):
    if (re.fullmatch(carNumRegex1, message.text.lower())) \
            or (re.fullmatch(carNumRegex2, message.text.lower())) \
            or (re.fullmatch(carNumRegex3, message.text.lower())):
        sql_lib.sql_update_user_status(message.from_user.id, "waiting_car_weight")
        # Обновление car_num в cars
        sql_lib.sql_update_car_num(message)

        # вот это перенести в другую функцию
        answer = "Укажите грузоподъемность машины"
        keyboard = types.ReplyKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(text="1")
        key_3 = types.InlineKeyboardButton(text="3")
        key_5 = types.InlineKeyboardButton(text="5")
        key_8 = types.InlineKeyboardButton(text="8")
        key_10 = types.InlineKeyboardButton(text="10")
        key_20 = types.InlineKeyboardButton(text="20")
        key_35 = types.InlineKeyboardButton(text="35")
        key_tral = types.InlineKeyboardButton(text="Трал")


        keyboard.add(key_1)
        keyboard.add(key_3)
        keyboard.add(key_5)
        keyboard.add(key_8)
        keyboard.add(key_10)
        keyboard.add(key_20)
        keyboard.add(key_35)
        keyboard.add(key_tral)


        return ['Номер введен корректно!\n\n' + answer, keyboard]
    else:
        msg = 'Номер введёт некорректно. Введите корркетный номер в формате а000аа00.\nЕсли что-то пошло не так, ' \
              'нажмите /start, чтобы начать сначала.\n\nЕсли бот работает некорректно, нажмите /help, ' \
              'чтобы сообщить об ошибке'
        return [msg, []]


# Получили грузоподъемность машины от пользователя
def parse_message_asked_weight(message, user):
    if re.fullmatch(NumRegex, message.text) or message.text =='Трал':
        # замена статуса в cars
        sql_lib.sql_update_car_weight(message, message.text)
        sql_lib.sql_update_user_status(message.from_user.id, "waiting_confirmation")
        # генерация ответа
        question = '\nДавайте сверим данные. \n'
        current_car = sql_lib.sql_select_car(message)
        car_data = 'Пришла машина в город *' + str(current_car[0]) + '*, \nна объект *' + str(current_car[1]) + \
                   '* \nс номером *' + str(current_car[2]) + '*,\nгрузоподъемностью *' + str(current_car[3]) + \
                   'т.*\n\nВсе верно?\n'
        answer = question + car_data
        # генерация клавиатуры
        keyboard = types.ReplyKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text="Да")
        key_no = types.InlineKeyboardButton(text='Нет')
        keyboard.add(key_yes)
        keyboard.add(key_no)

    else:
        answer = 'Я Вас не понимаю. Выберите ответ из списка, \nЕсли что-то пошло не так, нажмите /start, ' \
                 'чтобы начать сначала.\n\nЕсли бот работает некорректно, нажмите /help, чтобы сообщить об ошибке'
        keyboard = types.ReplyKeyboardMarkup()
        key_1 = types.InlineKeyboardButton(text="1")
        key_3 = types.InlineKeyboardButton(text="3")
        key_5 = types.InlineKeyboardButton(text="5")
        key_8 = types.InlineKeyboardButton(text="8")
        key_10 = types.InlineKeyboardButton(text="10")
        key_20 = types.InlineKeyboardButton(text="20")
        key_35 = types.InlineKeyboardButton(text="35")
        key_tral = types.InlineKeyboardButton(text="Трал")


        keyboard.add(key_1)
        keyboard.add(key_3)
        keyboard.add(key_5)
        keyboard.add(key_8)
        keyboard.add(key_10)
        keyboard.add(key_20)
        keyboard.add(key_tral)

    return [answer, keyboard]


def parse_message_finish(message, user):
    if message.text == 'Да':
        # обновление статуса в cars
        sql_lib.sql_update_car_confirmed(message)
        sql_lib.sql_update_user_status(message.from_user.id, "idle")
        # генерация клавиатуры
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key = types.InlineKeyboardButton(text="Пришла машина")
        keyboard.add(key)
        # генерация ответа
        msg = 'Все записал!'
    elif message.text == 'Нет':
        sql_lib.sql_update_user_status(message.from_user.id, "idle")
        # удалить строчку с машиной
        sql_lib.remove_car(message)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key = types.InlineKeyboardButton(text="Пришла машина")
        keyboard.add(key)
        msg = 'Давайте повторим запрос. Нажмите "Пришла машина"'
    else:
        msg = 'Я Вас не понимаю. Выберите ответ из списка, чтобы подтвердить введенные данные. ' \
              '\nЕсли что-то пошло не так, нажмите /start, ' \
              'чтобы начать сначала.\n\nЕсли бот работает некорректно, нажмите /help, чтобы сообщить об ошибке. ' \
              '\n\nДавайте проверим введенные данные. \nВсе верно?'
        keyboard = types.ReplyKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text="Да")
        key_no = types.InlineKeyboardButton(text='Нет')
        keyboard.add(key_yes)
        keyboard.add(key_no)

    return [msg, keyboard]


def can_chat(user):
    status = ['creator', 'administrator', 'member']
    for i in status:
        if i == bot.get_chat_member(chat_id=group_id, user_id=user).status:
            result = True
            break
    else:
        bot.send_message(user, text="У вас нет доступа общаться с ботом. Если Вы считаете, что произошла ошибка, "
                                    "нажмите /help, чтобы сообщить о ней. ")
        journal_log("Не одобрил доступ кожаному мешку. День прошел не зря")
        result = False

    return result


@bot.message_handler(content_types=["text"])
def text(message):
    if message.chat.type == 'private' and can_chat(message.chat.id) is True:
        journal_log("Написал кожаный мешок с одобренным доступом")
        answer = parse_message(message)
        if answer[1]:
            bot.send_message(message.chat.id, answer[0], reply_markup=answer[1], parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, answer[0], reply_markup=types.ReplyKeyboardRemove(),
                             parse_mode="Markdown")


# сохранение фотографий
@bot.message_handler(content_types=["photo"])
def photo(message):
    journal_log("прилетела фотка")
    file_info = bot.get_file(message.photo[2].file_id)
    file_id = message.photo[2].file_id
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f"photos/{file_id}.png", "wb") as new_file:
        new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "Фотография сохранена!")


# Ежедневная генерация и отправка файла со всеми машинами с вчера 16:00 по сегодня 16:00 по московскому времени
# добавить загрузку в большоооой файл
def send_everyday_summary():
    try:
        today = date.today()
        bot.send_message(group_id, f"Отсылаю файл с машинами, которые были {today.strftime('%d.%m.%Y')}",
                         parse_mode="Markdown")
        new_name = str(today) + '.xls'
        data_to_write = sql_lib.select_everyday_summary(today)
        journal_log(data_to_write)
        wb = Workbook()
        sheet1 = wb.add_sheet('Весь транспорт')
        sheet1.write(0, 0, "Город")
        sheet1.write(0, 1, "Объект")
        sheet1.write(0, 2, "Номер машины")
        sheet1.write(0, 3, "Дата")
        sheet1.write(0, 4, "Грузоподъемность")

        for i in range(len(data_to_write)):
            sheet1.write(i + 1, 0, data_to_write[i][0])
            sheet1.write(i + 1, 1, data_to_write[i][1])
            sheet1.write(i + 1, 2, data_to_write[i][2])
            sheet1.write(i + 1, 3, datetime.fromtimestamp(int(data_to_write[i][3])).isoformat(sep=" "))
            sheet1.write(i + 1, 4, data_to_write[i][4])

        wb.save(new_name)

        with open(new_name, "rb") as misc:
            f = misc.read()
            file_obj = io.BytesIO(f)
            file_obj.name = f"{today.strftime('%d-%m-%Y')}.xls"
        bot.send_document(group_id, file_obj)
    except Exception as e:
        journal_log(e)


def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(30)


# По московскому времени отсылает отчет в 16:00
schedule.every().day.at("13:00").do(send_everyday_summary)

# schedule.every(10).seconds.do(send_everyday_summary, curr_date)


Thread(target=schedule_checker).start()
try:
    bot.polling()
except ConnectionError as e:
    journal_log("ConnectionError - restarting after 5 seconds!!!")
    time.sleep(5)
    bot.polling()
