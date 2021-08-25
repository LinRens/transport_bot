import time
from datetime import date, timedelta
from datetime import datetime


# выдает две даты в системном формате, между которыми происходит поиск записей.
def date_to_st(date_to_use):
    pattern = "%d.%m.%Y %H:%M:%S"
    yesterday_date = date_to_use - timedelta(days=1)

    # Вчера 16:00 по МСК (20:00 по Красноярску)
    time_string_1 = str(yesterday_date.day) + '.' + str(yesterday_date.month) + '.' + \
                    str(yesterday_date.year) + ' ' + str('13:00:00')
    print("с " + time_string_1 + " по системному времени")

    # Сегодня 16:00 по МСК (20:00 по Красноярску)
    time_string_2 = str(date_to_use.day) + '.' + str(date_to_use.month) + '.' + \
                    str(date_to_use.year) + ' ' + str('13:59:59')

    print("по " + time_string_2)

    obj_1 = datetime.strptime(time_string_1, pattern)
    obj_2 = datetime.strptime(time_string_2, pattern)

    ts_1 = time.mktime(obj_1.timetuple())
    ts_2 = time.mktime(obj_2.timetuple())
    print(ts_1)
    print(ts_2)
    return [ts_1, ts_2]


# НАПИСАТЬ
def st_to_date(date_to_use):
    pattern = "%d.%m.%Y %H:%M:%S"

    time_string_1 = str(date_to_use.day) + '.' + str(date_to_use.month) + '.' + \
                    str(date_to_use.year) + ' ' + str('00:00:00')

    time_string_2 = str(date_to_use.day) + '.' + str(date_to_use.month) + '.' + \
                    str(date.year) + ' ' + str('23:59:59')

    obj_1 = datetime.strptime(time_string_1, pattern)
    obj_2 = datetime.strptime(time_string_2, pattern)

    ts_1 = time.mktime(obj_1.timetuple())
    ts_2 = time.mktime(obj_2.timetuple())

    return [ts_1, ts_2]
# сохраняет и отправляет файл в формате csv.
