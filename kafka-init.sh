#!/bin/bash

# Команда для создания топика topic-1
kafka-topics --create --topic topic-1 --bootstrap-server kafka-0:9010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf

# Команда для создания топика topic-2
kafka-topics --create --topic topic-2 --bootstrap-server kafka-0:9010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf

# Команда для создания топика topic-3
kafka-topics --create --topic topic-3 --bootstrap-server kafka-0:9010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf

# Дать продюсеру права на запись в топик topic-1
kafka-acls --bootstrap-server kafka-0:9010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:producer \
--allow-principal User:producer  \
--operation write \
--topic topic-1 

# Дать продюсеру права на запись в топик topic-2
kafka-acls --bootstrap-server kafka-0:9010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:producer \
--allow-principal User:producer  \
--operation write \
--topic topic-2 

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