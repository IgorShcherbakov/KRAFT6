#!/bin/bash

echo "Waiting for Kafka to start..."
while ! nc -z kafka-1 9011; do
  echo "Kafka is not available yet. Retrying in 5 seconds..."
  sleep 5
done

echo "Kafka is up. Waiting for Schema Registry to start..."
while ! nc -z schema-registry 8081; do
  echo "Schema Registry is not available yet. Retrying in 5 seconds..."
  sleep 5
done

echo "Schema Registry is up. Starting the application."
exec "$@"