"""Кастомные исключения."""


class TelegramError(Exception):
    """Ошибка работы Telegram."""

    pass


class ResponseCodeError(Exception):
    """Ошибка кода ответа."""

    pass


class EmptyDictError(Exception):
    """Пустой словарь."""

    pass
