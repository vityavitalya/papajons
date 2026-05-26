# Use-Case диаграмма системы «Обмен валют»

## Диаграмма вариантов использования

```plantuml
@startuml

left to right direction
skinparam packageStyle rectangle

actor "Клиент API" as Client
actor "Администратор" as Admin

rectangle "Система обмена валют" {

    usecase "UC-01\nПолучить список валют" as UC1
    usecase "UC-02\nПолучить валюту по коду" as UC2
    usecase "UC-03\nПолучить список курсов" as UC3
    usecase "UC-04\nПолучить курс валют" as UC4
    usecase "UC-05\nКонвертировать валюту" as UC5

    usecase "UC-06\nДобавить валюту" as UC6
    usecase "UC-07\nДобавить курс" as UC7
    usecase "UC-08\nОбновить курс" as UC8
}

Client --> UC1
Client --> UC2
Client --> UC3
Client --> UC4
Client --> UC5

Admin --> UC6
Admin --> UC7
Admin --> UC8

Admin --|> Client

@enduml
```

---

## Бизнес-правила

1. Код валюты состоит из 3 заглавных букв (USD, EUR, RUB)
2. Курс обмена является положительным числом
3. Каждая пара валют уникальна
4. Конвертация выполняется:
   - по прямому курсу
   - по обратному курсу
   - через кросс-курс USD

---

## Назначение диаграммы

Use-Case диаграмма показывает:
- кто взаимодействует с системой
- какие функции доступны
- какие операции реализует API

Документ используется для проектирования REST API системы обмена валют.