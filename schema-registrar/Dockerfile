FROM python:3.11

# Установим curl, если он необходим
RUN apt-get update && apt-get install -y curl && apt-get clean

# Копируем скрипт в контейнер
COPY register-schema.sh /usr/local/bin/register-schema.sh

# Делаем скрипт исполняемым
RUN chmod +x /usr/local/bin/register-schema.sh

# Указываем команду для выполнения при запуске контейнера
CMD ["register-schema.sh"]