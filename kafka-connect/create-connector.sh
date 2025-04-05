#!/bin/bash

echo "Waiting for Kafka Connect to start..."
while ! nc -z kafka-connect 8083; do
  echo "Kafka Connect is not available yet. Retrying in 5 seconds..."
  sleep 5
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
    http://kafka-connect:8083/connectors/file-stream-sink/config