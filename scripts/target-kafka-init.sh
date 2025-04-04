#!/bin/bash

echo "Waiting for Kafka to start..."
while ! nc -z target-kafka-0 10010; do
  echo "Kafka is not available yet. Retrying in 5 seconds..."
  sleep 5
done

echo "Kafka is up. Proceeding with topic creation and ACL setup."

# Команда для создания топика recommendations
kafka-topics --create --topic recommendations --bootstrap-server target-kafka-0:10010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf

# Дать продюсеру права на запись в топик products и search-products
kafka-acls --bootstrap-server target-kafka-0:10010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:producer \
--allow-principal User:producer  \
--operation write \
--topic recommendations

# Дать консьюмеру права на чтение топика products
kafka-acls --bootstrap-server target-kafka-0:10010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:consumer \
--allow-principal User:consumer  \
--operation read \
--topic products 

# Дать консьюмеру доступ к группе консьюмеров
kafka-acls --bootstrap-server target-kafka-0:10010 \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add --allow-principal User:consumer \
--operation Read \
--group consumer-ssl-group-hadoop

# Завершение скрипта
exit 0