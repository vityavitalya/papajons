# Диаграмма последовательности: конвертация валюты

## Бизнес-процесс

Пользователь выполняет конвертацию суммы из одной валюты в другую через REST API.

---

# Сценарий 1: прямой курс

Курс USD → EUR существует в базе данных.

```plantuml
@startuml

actor "Клиент API" as Client
participant "API" as API
database "База данных" as DB
participant "Калькулятор" as Calc

Client -> API : GET /exchange\n?from=USD&to=EUR&amount=100

API -> DB : Поиск курса USD→EUR
DB --> API : rate = 0.92

API -> Calc : 100 * 0.92
Calc --> API : 92.00

API --> Client : Response { convertedAmount: 92.00 }

@enduml
```

---

# Сценарий 2: обратный курс

Курс USD → EUR отсутствует, но существует EUR → USD.

```plantuml
@startuml

actor "Клиент API" as Client
participant "API" as API
database "База данных" as DB
participant "Калькулятор" as Calc

Client -> API : GET /exchange\n?from=USD&to=EUR&amount=100

API -> DB : Поиск USD→EUR
DB --> API : Курс не найден

API -> DB : Поиск EUR→USD
DB --> API : rate = 1.086956

API -> Calc : 1 / 1.086956
Calc --> API : reverseRate = 0.92

API -> Calc : 100 * 0.92
Calc --> API : 92.00

API --> Client : Response { convertedAmount: 92.00 }

@enduml
```

---

# Сценарий 3: кросс-курс через USD

Прямой курс EUR → RUB отсутствует.
Используются курсы EUR → USD и USD → RUB.

```plantuml
@startuml

actor "Клиент API" as Client
participant "API" as API
database "База данных" as DB
participant "Калькулятор" as Calc

Client -> API : GET /exchange\n?from=EUR&to=RUB&amount=100

API -> DB : Поиск EUR→RUB
DB --> API : Курс не найден

API -> DB : Поиск EUR→USD
DB --> API : rate1 = 1.08

API -> DB : Поиск USD→RUB
DB --> API : rate2 = 92.50

API -> Calc : 1.08 * 92.50
Calc --> API : crossRate = 99.90

API -> Calc : 100 * 99.90
Calc --> API : 9990.00

API --> Client : Response { convertedAmount: 9990.00 }

@enduml
```

---

# Почему используется DECIMAL

Для хранения денежных значений используется тип DECIMAL(10,6), так как тип FLOAT может давать ошибки округления.

Пример ошибки FLOAT:

```python
0.1 + 0.2
# 0.30000000000000004
```

Тип DECIMAL обеспечивает точность финансовых вычислений.

---

# Назначение диаграммы последовательности

Диаграмма последовательности используется для:
- описания бизнес-процессов
- отображения взаимодействия компонентов системы
- проектирования логики REST API
- документирования процесса конвертации валют