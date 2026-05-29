# Руководство по развёртыванию Currency Exchange API
## Требования к серверу
- ОС: Ubuntu 20.04+ / Debian 11+ (или Windows Server 2019+)
- Python 3.9+
- 1 GB RAM (минимум), 2 GB RAM (рекомендуется)
- 10 GB свободного дискового пространства
## Вариант 1: Локальный запуск (разработка)
1. **Клонирование репозитория**
```bash
git clone https://github.com/yourusername/currency-exchange.git
cd currency-exchange

2. Создание виртуального окружения

python -m venv venv
source venv/bin/activate # Linux/Mac

Вариант 2: Production-запуск (Ubuntu)
Шаг 1: Установка Python 3.11

Шаг 2: Клонирование и настройка

Шаг 3: Настройка .env файла
# venv\Scripts\activate # Windows

3. Установка зависимостей

pip install -r requirements.txt

4. Запуск приложения

uvicorn app.main:app --reload

5. Проверка
Откройте браузер: http://127.0.0.1:8000/docs

sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y

git clone https://github.com/yourusername/currency-exchange.git
cd currency-exchange
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Шаг 4: Настройка systemd-сервиса

Шаг 5: Настройка Nginx (reverse proxy + статика)

Шаг 6: Настройка HTTPS (Let's Encrypt)

Настройка резервного копирования (cron)
cat > .env << EOF
DEBUG=False
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./currencies.db
EOF

sudo cp systemd/currency-exchange.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable currency-exchange
sudo systemctl start currency-exchange

sudo apt install nginx -y

sudo cp docs/nginx_currency_exchange.conf /etc/nginx/sites-
available/currency-exchange

sudo ln -s /etc/nginx/sites-available/currency-exchange /etc/nginx/sites-
enabled/

sudo nginx -t
sudo systemctl restart nginx

sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com

Проверка работоспособности

Устранение неполадок

Проблема Решение
Порт 8000 уже занят sudo lsof -i :8000 → kill PID
Ошибка подключения к
БД

Проверьте права на папку: chmod 755 ./

502 Bad Gateway
(Nginx)

Проверьте, запущен ли uvicorn: systemctl status
currency-exchange

Медленные запросы Увеличьте количество воркеров: --workers 8
# Добавляем задачу в crontab для ежедневного бэкапа в 2:00
crontab -e
# Добавляем строку:
0 2 * * * /path/to/currency-exchange/scripts/backup.sh

# Базовая проверка
curl http://localhost:8000/
# Просмотр логов
journalctl -u currency-exchange -f
# Мониторинг ресурсов
htop

### 10.5. Создание конфигурации Nginx
**Создаём `docs/nginx_currency_exchange.conf`:**
```nginx
# Конфигурация Nginx для Currency Exchange API

# Разместить в /etc/nginx/sites-available/currency-exchange
server {
listen 80;
server_name api.yourdomain.com;
# Максимальный размер загружаемых данных
client_max_body_size 10M;
# Логи
access_log /var/log/nginx/currency-exchange-access.log;
error_log /var/log/nginx/currency-exchange-error.log;
# Основное расположение — прокси на FastAPI
location / {
proxy_pass http://127.0.0.1:8000;
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
# Таймауты
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
}
# Статические файлы (если будут добавляться позже)
location /static/ {
alias /var/www/currency-exchange/static/;
expires 30d;
}
# Здоровье приложения (healthcheck)
location /health {
proxy_pass http://127.0.0.1:8000/;
access_log off;
}
}

