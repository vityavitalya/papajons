# Руководство пользователя Currency Exchange API
## Для кого это руководство
- Разработчики, интегрирующие API в свои приложения
- Администраторы, управляющие курсами валют
- Тестировщики, проверяющие работу системы
## Быстрый старт
### 1. Проверка работы сервера
```bash
curl http://api.example.com/

curl http://api.example.com/currencies

curl "http://api.example.com/exchange?from=USD&to=EUR&amount=100"

[
{
"id": 1,
"code": "USD",
"full_name": "US Dollar",

GET /currency/{code} — получить одну валюту
Пример: GET /currency/USD
POST /currencies — создать валюту
Тело запроса:

Курсы обмена (Exchange Rates)
GET /exchangeRates — список всех курсов
Ответ содержит вложенные объекты валют:

GET /exchangeRate/{pair} — курс по паре
"sign": "$"
}
]

{
"code": "GBP",
"full_name": "British Pound",
"sign": "£"
}

[
{
"id": 1,
"rate": 0.92,
"base_currency": {"code": "USD", "full_name": "US Dollar", "sign":
"$"},
"target_currency": {"code": "EUR", "full_name": "Euro", "sign":
"€"}
}
]

Пример: GET /exchangeRate/USDEUR
POST /exchangeRates — создать курс
Тело запроса:

PATCH /exchangeRate/{pair} — обновить курс
Пример: PATCH /exchangeRate/USDEUR с телом {"rate": 0.95}
Конвертация (Exchange)
GET /exchange — главный эндпоинт
Параметры:

Пример: GET /exchange?from=USD&to=EUR&amount=100
Ответ:
{
"base_currency_code": "USD",
"target_currency_code": "EUR",
"rate": 0.92
}

from — код исходной валюты (обязательный)
to — код целевой валюты (обязательный)
amount — сумма для конвертации (обязательный, >0)

{
"base_currency": {"code": "USD", "full_name": "US Dollar", "sign":
"$"},
"target_currency": {"code": "EUR", "full_name": "Euro", "sign": "€"},
"rate": 0.92,
"amount": 100,
"converted_amount": 92.00
}

Административные эндпоинты (требуют аутентификации)
PATCH /currency/{code}/deactivate — скрыть валюту

GET /admin/stats — статистика системы

Коды ответов

Код Значение
200 OK — запрос выполнен успешно
201 Created — объект создан
400 Bad Request — неверные параметры запроса
404 Not Found — объект не найден
409 Conflict — дубликат (валюта или курс уже существует)
422 Unprocessable Entity — ошибка валидации
500 Internal Server Error — ошибка на сервере

Примеры в разных языках
Python (requests)
curl -X PATCH http://api.example.com/currency/USD/deactivate \
-u admin:your_password

curl http://api.example.com/admin/stats -u admin:your_password

import requests
response = requests.get(
"http://api.example.com/exchange",
params={"from": "USD", "to": "EUR", "amount": 100}

JavaScript (fetch)

cURL

Часто задаваемые вопросы (FAQ)
Вопрос: Почему курс USD→EUR = 0.92, а не 1.086?
Ответ: Курсы всегда указываются как количество целевой валюты за 1 единицу базовой.
Вопрос: Как добавить кросс-курс?
Ответ: Не нужно. Система сама вычисляет кросс-курсы через USD.
Вопрос: Почему конвертация EUR→USD даёт 108.70, а не 100/0.92?
Ответ: Обратный курс вычисляется как 1/0.92 = 1.086956, затем 100 * 1.086956 =
108.6956 → округление до 108.70.