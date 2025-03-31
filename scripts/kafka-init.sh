#!/bin/bash

# Команда для создания топика products
kafka-topics --create --topic products --bootstrap-server kafka-0:9010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf

# Дать продюсеру права на запись в топик products
kafka-acls --bootstrap-server kafka-0:9010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:producer \
--allow-principal User:producer  \
--operation write \
--topic products 

# Дать консьюмеру права на чтение топика topic-1
kafka-acls --bootstrap-server kafka-0:9010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:consumer \
--allow-principal User:consumer  \
--operation read \
--topic topic-1 

# Дать консьюмеру доступ к группе консьюмеров
kafka-acls --bootstrap-server kafka-0:9010 \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add --allow-principal User:consumer \
--operation Read \
--group consumer-ssl-group

# Завершение скрипта
exit 0