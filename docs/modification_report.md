# Отчёт о модификации системы
## Запрос заказчика
> Добавить возможность временно отключать валюты (поле is_active)
## Изменения
### 1. База данных
- Добавлено поле `is_active` в таблицу `currencies` (INTEGER, DEFAULT 1)
- Создан скрипт миграции: `scripts/migrate_add_is_active.py`
### 2. Модель данных
```python
is_active = Column(Integer, default=1, nullable=False)

3. CRUD-операции

4. API-эндпоинты

5. Тестирование

6. Документация

Демонстрация работы
get_all_currencies() : добавлен параметр include_inactive
get_currency_by_code() : добавлен параметр include_inactive
Новые функции: deactivate_currency() , activate_currency()

PATCH /currency/{code}/deactivate — скрыть валюту
PATCH /currency/{code}/activate — показать валюту

Добавлены тесты: test_deactivate_currency()
Все существующие тесты проходят ✅

Обновлено docs/user_guide.md
Добавлены примеры использования новых эндпоинтов

# 1. Проверяем список валют (USD видна)
curl http://localhost:8000/currencies
# 2. Деактивируем USD
curl -X PATCH http://localhost:8000/currency/USD/deactivate \
-H "Authorization: Basic $(echo -n 'admin:secret' | base64)"
# 3. Проверяем список (USD исчезла)
curl http://localhost:8000/currencies
# 4. Пытаемся конвертировать из USD (ошибка 404)
curl "http://localhost:8000/exchange?from=USD&to=EUR&amount=100"
# 5. Активируем обратно

Тестирование после изменений

Вывод
Изменение успешно внедрено, код протестирован, документация обновлена.
Система готова к работе с новым требованием.

Раздел 13. Документация (ПМ.03)
💡 Почему документация важна для ПМ.03?
Пункт «Эксплуатационная и пользовательская документация» — руководство
пользователя для каждой роли и руководство администратора.
13.1. Создаём docs/user_guide.md — руководство пользователя
curl -X PATCH http://localhost:8000/currency/USD/activate \
-H "Authorization: Basic $(echo -n 'admin:secret' | base64)"

# Запуск всех тестов
pytest tests/ -v
# Результат: 42 passed (добавилось 3 новых теста)

### 12.8. Фиксация в Git
```bash
git add app/ scripts/ tests/ docs/modification_report.md
git commit -m "feat: добавлена возможность деактивации валют (запрос
заказчика)"