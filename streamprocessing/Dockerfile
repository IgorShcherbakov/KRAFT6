#зададим родительский образ
FROM python:3.11

#установим нужные зависимости
RUN pip install confluent-kafka[json] faust-streaming==0.11.3

#копируем нужные файлы
COPY main.py main.py
COPY ca.crt ca.crt
COPY kafka-1.crt kafka-1.crt
COPY kafka-1.key kafka-1.key

#выполним код при старте контейнера
CMD ["faust", "-A", "main", "worker", "-l", "info"]