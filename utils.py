from datetime import datetime, timezone, timedelta

def get_moscow_time():
    # Получаем текущее время в формате UTC
    utc_now = datetime.now(timezone.utc)

    # Создаем смещение для Московского времени (+3 часа с учетом летнего/зимнего времени)
    moscow_offset = timedelta(hours=3)

    # Преобразуем время из UTC во время в Москве
    moscow_time = utc_now + moscow_offset

    return moscow_time.strftime('%H:%M')


def is_past_moscow_time(input_time):
    # Получаем текущее время в формате UTC
    utc_now = datetime.now(timezone.utc)

    # Создаем смещение для Московского времени (+3 часа с учетом летнего/зимнего времени)
    moscow_offset = timedelta(hours=3)

    # Преобразуем время из UTC во время в Москве
    moscow_time = utc_now + moscow_offset

    # Преобразуем строку с введенным временем в формат datetime
    input_hour, input_minute = map(int, input_time.split(':'))
    input_datetime = moscow_time.replace(hour=input_hour, minute=input_minute, second=0, microsecond=0)

    # Сравниваем введенное время с текущим временем в Москве
    if moscow_time > input_datetime:
        return True
    else:
        return False


def validate_time(time):
    try:
        datetime.strptime(time, '%H:%M')
        return True
    except ValueError:
        return False
