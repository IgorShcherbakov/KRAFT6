import uvicorn
import logging
import json
import time
from fastapi import FastAPI, HTTPException
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient


logger = logging.getLogger(__name__)

app = FastAPI()

# Конфигурация для подключения к Schema Registry
schema_registry_conf = {
    'url': 'http://schema-registry:8081',  # URL вашего Schema Registry
}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Получаем последнюю версию схемы по имени
subject_name = "products-value"  # Имя subject в Schema Registry
schema_response = schema_registry_client.get_latest_version(subject_name)
json_schema_str = schema_response.schema.schema_str

json_serializer = JSONSerializer(json_schema_str, schema_registry_client)

producer_conf = {
    "bootstrap.servers": "kafka-1:9011",

    "security.protocol": "SASL_SSL",
    "ssl.ca.location": "ca.crt",  # Сертификат центра сертификации
    "ssl.certificate.location": "kafka-1.crt",  # Сертификат клиента Kafka
    "ssl.key.location": "kafka-1.key",  # Приватный ключ для клиента Kafka

    "sasl.mechanism": "PLAIN",  # Используемый механизм SASL (PLAIN)
    "sasl.username": "producer",  # Имя пользователя для аутентификации
    "sasl.password": "producer",  # Пароль пользователя для аутентификации
}

def delivery_report(err, msg):
    """
    Проверить статус доставки сообщения
    """
    if err is not None:
        logger.info(f"Ошибка доставки сообщения в топик {msg.topic()}: {err}")
    else:
        logger.info(f"Сообщение «{msg.__str__()}» доставлено в {msg.topic()} [{msg.partition()}]")

@app.get("/")
async def root():
    return "Перейдите по адресу http://localhost:8085/docs для взаимодействия со Swagger"

@app.get("/products")
async def get_products():
    # создание продюсера
    producer = Producer(producer_conf)
    try:
        # Открываем файл и читаем данные
        with open('products.json', 'r', encoding='utf-8') as file:
            products = json.load(file)

        # Отправляем каждый продукт в Kafka
        for product in products:
            producer.produce(
                topic="products",  # Укажите ваш топик
                key="product",  # Используйте уникальный идентификатор продукта в качестве ключа
                value=json_serializer(product, SerializationContext("products", MessageField.VALUE)),
                callback=delivery_report
            )
            time.sleep(30)
        producer.flush()
        return {"status": "Сообщение отправлено успешно"}
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при отправке сообщения")
    

if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   uvicorn.run(app, host="0.0.0.0", port=8085) 