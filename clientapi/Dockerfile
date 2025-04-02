#зададим родительский образ
FROM python:3.9

#копируем нужные файлы
COPY main.py main.py
COPY ca.crt ca.crt
COPY kafka-1.crt kafka-1.crt
COPY kafka-1.key kafka-1.key

#установим нужные зависимости
RUN pip install fastapi uvicorn confluent-kafka elasticsearch==7.10.0

#выполним код при старте контейнера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8086"]