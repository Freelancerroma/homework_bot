import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def check_tokens():
    """Проверка наличия переменных из окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    logging.info('Начало отправки сообщения')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Не удалось отправить сообщение: {error}')
        raise exceptions.TelegramError(f'Сообщение не отправлено: {error}')
    else:
        logging.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Запрос к эндпоинту API-сервиса."""
    logging.info('Начало отправки запроса к API')
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise exceptions.ResponseCodeError(
                'Ответ от API не получен, '
                f'ошибка: {response.status_code}'
                f'причина: {response.reason}'
                f'текст ошибки: {response.text}'
            )
    except Exception as error:
        raise exceptions.ResponseCodeError(f'Неверный код ответа: {error}')
    return response.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    logging.info('Начало проверки соответствия')
    if not isinstance(response, dict):
        logging.error('Ответ от запроса не является словарем')
        raise TypeError('Ответ от запроса не является словарем')
    if 'homeworks' not in response or 'current_date' not in response:
        logging.error('Ответ от запроса пуст')
        raise exceptions.EmptyDictError('Ответ от запроса пуст')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        logging.error('Ответ от запроса не является списком')
        raise TypeError('Ответ от запроса не является списком')
    return homeworks


def parse_status(homework):
    """Извлечение информации о конкретной домашней работе."""
    logging.info('Начало парсинга')
    if 'homework_name' not in homework:
        logging.error('Нет названия работы в запросе')
        raise KeyError('Нет названия работы в запросе')
    if 'status' not in homework:
        logging.error('Нет статуса работы в запросе')
        raise KeyError('Нет статуса работы в запросе')
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    if homework_status not in HOMEWORK_VERDICTS:
        logging.error('Неверный статус')
        raise ValueError('Нет такого статуса')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Нет всех переменных для работы')
        sys.exit('Нет всех переменных для работы (Выход)')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_report = ''
    last_error = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            new_homeworks = check_response(response)
            message = parse_status(new_homeworks[0])
            if last_report != message:
                last_report = message
                send_message(bot, last_report)
            else:
                logging.debug('Статус работ не изменился')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if last_error != error:
                try:
                    send_message(bot, message)
                    last_error = error
                except telegram.error.TelegramError as error:
                    logging.error(f'Сбой работы Telegram: {error}')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main()
