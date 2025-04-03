#зададим родительский образ
FROM python:3.9

#копируем нужные файлы
COPY main.py main.py
COPY ca.crt ca.crt
COPY target-kafka-1.crt target-kafka-1.crt
COPY target-kafka-1.key target-kafka-1.key

#установим нужные зависимости
RUN pip install fastapi uvicorn confluent-kafka hdfs

#выполним код при старте контейнера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8087"]