import sqlite3
from date_formating import date_to_st
import time
from datetime import datetime, timedelta


# запросные функции
def sql_put_and_get_row_id(sql_command):
    con = sqlite3.connect('VSK_transport.db')
    cur = con.cursor()
    cur.execute(sql_command)
    output = cur.lastrowid
    con.commit()
    con.close()
    return output


def sql_set(sql_command):
    sql_put(sql_command)  # To avoid some errors


def sql_put(sql_command):
    con = sqlite3.connect('VSK_transport.db')
    cur = con.cursor()
    cur.execute(sql_command)
    con.commit()
    con.close()


def sql_get(sql_command):
    con = sqlite3.connect('VSK_transport.db')
    cur = con.cursor()
    cur.execute(sql_command)
    output = cur.fetchone()
    con.close()
    return output


def sql_get_all(sql_command):
    con = sqlite3.connect('VSK_transport.db')
    cur = con.cursor()
    cur.execute(sql_command)
    output = cur.fetchall()
    con.close()
    return output


# Функции для бота
# вывод всех данных о машине
def sql_select_car(message):
    query = f'SELECT town as "Город", object as "Объект", car_num as "Номер машины", weight as "Грузоподъемность" ' \
            f'FROM `cars` WHERE id = (SELECT last_row_id FROM `users` WHERE user_id = "{message.from_user.id}")'
    return sql_get(query)


# Создание машины в cars
def sql_car_start(message):
    query = f'INSERT INTO `cars` (user_id, datetime_start, confirmed) VALUES ("{message.from_user.id}",' \
            f' "{message.date}", "False");'

    sql_put_and_get_row_id(query)


def sql_update_user_row_id(user_id):
    query = f'UPDATE `users` SET last_row_id = (SELECT MAX(id) FROM `cars`) WHERE user_id = "{user_id}"'
    sql_set(query)


# Обновление города в cars ВРОДЕ РАБОТАЕТ
def sql_update_car_town(message):
    query = f'UPDATE `cars` SET town = "{message.text}" WHERE id = (SELECT last_row_id FROM `users`' \
            f' WHERE user_id = "{message.from_user.id}")'
    sql_set(query)


# Обновление объекта в cars ВРОДЕ РАБОТАЕТ
def sql_update_car_object(message):
    query = f'UPDATE `cars` SET object = "{message.text}" WHERE id = (SELECT last_row_id FROM `users`' \
            f' WHERE user_id = "{message.from_user.id}")'
    sql_set(query)


# Обновление номера машины в cars ВРОДЕ РАБОТАЕТ
def sql_update_car_num(message):
    query = f'UPDATE `cars` SET car_num = "{message.text}" WHERE id = (SELECT last_row_id FROM `users`' \
            f' WHERE user_id = "{message.from_user.id}")'
    sql_set(query)


# Обновить статус на ready, добавить datetime_end и статус на confirmed ВРОДЕ РАБОТАЕТ
def sql_update_car_confirmed(message):
    query1 = f'UPDATE `cars` SET confirmed = "True" WHERE id = (SELECT last_row_id FROM `users` ' \
             f'WHERE user_id = "{message.from_user.id}")'
    query2 = f'UPDATE `cars` SET is_ready = "READY" WHERE id = (SELECT last_row_id FROM `users` ' \
             f'WHERE user_id = "{message.from_user.id}")'
    query3 = f'UPDATE `cars` SET datetime_end = "{message.date}" WHERE ' \
             f'id = (SELECT last_row_id FROM `users` WHERE user_id = "{message.from_user.id}")'

    sql_set(query1)
    sql_set(query2)
    sql_set(query3)


def remove_car(message):
    query = f'DELETE FROM `cars` WHERE id = (SELECT last_row_id FROM `users` WHERE user_id = "{message.from_user.id}")'
    sql_set(query)


def remove_unready_car(message):
    query = f'DELETE FROM `cars` WHERE id = (SELECT last_row_id FROM `users` WHERE user_id = "{message.from_user.id}") ' \
            f'AND is_ready = "not_ready"'
    sql_set(query)


# запись в messages каждого сообщения НЕ РАБОТАЕТ СЛОМАЛОСЬ
def sql_log_message(message):
    msg = f'INSERT INTO `messages` (user_id, username, message_id, message_text, datetime, pic_id,'\
            f' user_state, full_message, town, object, car_num) VALUES ("{message["user_id"]}", ' \
          f'"{message["username"]}", "{message["message_id"]}", '\
            f'"{message["text"]}", "{message["datetime"]}", "{message["photo"]}", "{message["state"]}", ' \
          f'"{message["text"]}", "{message["town"]}","{message["object"]}", '\
            f'"{message["car_num"]}") ;'
    sql_set(msg)


# добавление пользователя в таблицу users
def add_user(user_id, username):
    msg = f'INSERT INTO `users` (user_id, username, state) VALUES ("{user_id}", "{username}", "idle")'
    return sql_put_and_get_row_id(msg)


# Получить информацию о пользователе по айди
def sql_get_user_data(user_id):
    return sql_get(f"SELECT * FROM `users` WHERE user_id = {user_id}")


# Изменение статуса пользователя в зависимости от ответа
def sql_update_user_status(user_id, status):
    query = f'UPDATE `users` SET state = "{status}" WHERE user_id = "{user_id}"'
    sql_set(query)


# загрузить все машины
def sql_select_cars():
    query = f'SELECT town as "Город", object as "Объект", car_num as "Номер машины", weight as "Грузоподъемность", datetime_start as "Дата" FROM `cars` WHERE is_ready = "READY"'
    return sql_get_all(query)


# загрузить все машины в определенную дату
def select_everyday_summary(date):
    query = f'SELECT town as "Город", object as "Объект", car_num as "Номер машины", ' \
            f'datetime_start as "Дата", weight as "Грузоподъемность" FROM `cars` ' \
            f'WHERE datetime_start > "{int((datetime.now() - timedelta(days=1)).timestamp())}" ' \
            f'AND datetime_end < "{int((datetime.now()).timestamp())}" AND is_ready = "READY"'
    print(query)
    return sql_get_all(query)


def sql_update_car_weight(message, weight):
    query = f'UPDATE `cars` SET weight = "{weight}" WHERE id = (SELECT last_row_id FROM `users` ' \
            f'WHERE user_id = "{message.from_user.id}")'
    sql_set(query)


def sql_get_town(user):
    query = f'SELECT town as "Город" FROM `cars` WHERE user_id = "{user}" and id = (SELECT  last_row_id FROM `users` ' \
            f'WHERE user_id = "{user}")'
    return list(sql_get_all(query)[0])
