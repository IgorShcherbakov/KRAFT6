#!/bin/bash

# Ждем, пока Kafka Connect не станет доступен
echo "Waiting for Kafka Connect to start..."
while ! nc -z localhost 8083; do
  sleep 1
done

echo "Creating or updating Kafka Connect connector..."
curl -X PUT \
    -H "Content-Type: application/json" \
    --data '{
    "name": "file-stream-sink",
    "connector.class": "org.apache.kafka.connect.file.FileStreamSinkConnector",
    "tasks.max": "1",
    "topics": "products",
    "file": "products.out",
    "value.converter": "org.apache.kafka.connect.storage.StringConverter"
    }' \
    http://localhost:8083/connectors/file-stream-sink/config
    #http://kafka-connect:8083/connectors/file-stream-sink/config

    #docker exec 3b05df941dad4b09633ccf1d1e0d4b8959b57619fe7a2a0a7ace9e774203e885 cat /home/appuser/products.out