#зададим родительский образ
FROM python:3.11

#установим нужные зависимости
RUN pip install confluent-kafka[json] faust-streaming==0.11.3

#копируем нужные файлы
COPY main.py main.py
COPY ca.crt ca.crt
COPY kafka-1.crt kafka-1.crt
COPY kafka-1.key kafka-1.key
COPY wait-for-services.sh wait-for-services.sh

# обновим список пакетов и установим netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

# установим права на выполнение скрипта
RUN chmod +x wait-for-services.sh

#выполним код при старте контейнера
CMD ["./wait-for-services.sh", "faust", "-A", "main", "worker", "-l", "info"]