import uvicorn
import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from confluent_kafka import Producer
from elasticsearch import Elasticsearch
from elasticsearch.connection import Urllib3HttpConnection

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ClientAPI")

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

es = Elasticsearch(
    ["http://elasticsearch:9200"],
    connection_class=Urllib3HttpConnection,
    http_auth=('elastic', 'elastic'),  # Укажите ваши учетные данные
    headers={"Content-Type": "application/json"}
)

def delivery_report(err, msg):
    """
    Проверить статус доставки сообщения
    """
    if err is not None:
        logger.info(f"Ошибка доставки сообщения в топик {msg.topic()}: {err}")
    else:
        logger.info(f"Сообщение «{msg.__str__()}» доставлено в {msg.topic()} [{msg.partition()}]")

@app.get("/product_info")
async def get_product_info(product_name: str):
    producer = Producer(producer_conf)
    try:
        # Отправка сообщения в Kafka
        producer.produce(
            topic="search-products",
            key="sp",
            value=product_name,
            callback=delivery_report
        )
        producer.flush()

        # Отправка сообщения в Elasticsearch
        es.index(index="products", body={"product_name": product_name})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Сообщение отправлено успешно."
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f"Ошибка при отправке сообщения: {e}."
        )
    

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8086) 