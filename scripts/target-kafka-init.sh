#!/bin/bash

# Команда для создания топика recommendations
kafka-topics --create --topic recommendations --bootstrap-server target-kafka-0:10010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf

# Дать продюсеру права на запись в топик products и search-products
kafka-acls --bootstrap-server target-kafka-0:10010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:producer \
--allow-principal User:producer  \
--operation write \
--topic recommendations

# Дать консьюмеру права на чтение топика topic-1
kafka-acls --bootstrap-server target-kafka-0:10010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:consumer \
--allow-principal User:consumer  \
--operation read \
--topic recommendations 

# Дать консьюмеру доступ к группе консьюмеров
kafka-acls --bootstrap-server target-kafka-0:10010 \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add --allow-principal User:consumer \
--operation Read \
--group consumer-ssl-group

# Завершение скрипта
exit 0