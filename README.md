## Проект «Telegram-bot» 
***
### Описание:
Telegram-bot для проверки статуса домашней работы на Яндекс.Практикум. Присылает сообщения о принятии на ревью, принятии ревьювером, отправки на доработку. Проверяет статус каждые 10 минут. У API Практикум.Домашка есть лишь один эндпоинт: https://practicum.yandex.ru/api/user_api/homework_statuses/ и доступ к нему возможен только по токену. Получить токен можно по адресу: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a.
***
### Системные требования:
Python 3.11.5.
***
### Установка:

1. Склонируйте репозиторий по ссылке:
```
git clone git@github.com:Freelancerroma/homework_bot.git
```
2. Установите и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
3. Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
4. Добавьте в корень директории файл .env с актуальными данными:
- PRACTICUM_TOKEN #Токен сайта практикума
- TELEGRAM_TOKEN  #Токен телеграм-бота
- TELEGRAM_CHAT_ID #Токен id юзера
5. Выполните команду для запуска бота:
```
python homework.py
```
***
### Инструменты и стек:
- Python
- Telegram
