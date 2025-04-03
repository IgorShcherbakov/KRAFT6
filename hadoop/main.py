import uuid
import uvicorn
import logging
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from confluent_kafka import Consumer, Producer
from hdfs import InsecureClient

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="HadoopAPI")

consumer_conf = {
    "bootstrap.servers": "target-kafka-1:10011",
    "group.id": "consumer-ssl-group-hadoop",
    "auto.offset.reset": "earliest",

    "security.protocol": "SASL_SSL", 
    "ssl.ca.location": "ca.crt",  # Сертификат центра сертификации
    "ssl.certificate.location": "target-kafka-1.crt",  # Сертификат клиента Kafka
    "ssl.key.location": "target-kafka-1.key",  # Приватный ключ для клиента Kafka

    "sasl.mechanism": "PLAIN",  # Используемый механизм SASL (PLAIN)
    "sasl.username": "consumer",  # Имя пользователя для аутентификации
    "sasl.password": "consumer",  # Пароль пользователя для аутентификации
}

producer_conf = {
    "bootstrap.servers": "target-kafka-1:10011",

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

@app.get("/data")
async def get_data():
    # Инициализация HDFS Hadoop клиента
    hdfs_client = InsecureClient("http://hadoop-namenode:9870", user="root")

    consumer = Consumer(consumer_conf)
    consumer.subscribe(["products"])

    try:
        while True:
            message = consumer.poll(10.0)

            if message is None:
                logger.info(f"В топике нет сообщений!")
                break
            if message.error():
                logger.error(f"Ошибка топика {message.topic()}: {message.error()}")
                continue

            key = message.key().decode("utf-8")
            value = message.value().decode("utf-8")
            logger.info(f"Получено сообщение из топика {message.topic()}: {key=}, {value=}, offset={message.offset()}")

            # Запись сообщения, как файл, в HDFS
            hdfs_file = f"data/message_{uuid.uuid4()}"
            with hdfs_client.write(hdfs_file, encoding="utf-8") as writer:
                writer.write(value + "\n")
            logger.info(f"Сообщение '{value=}' записано в HDFS по пути '{hdfs_file}'")

            # Чтение файла из HDFS для проверки
            with hdfs_client.read(hdfs_file, encoding="utf-8") as reader:
                content = reader.read()
            logger.info(f"Чтение файла '{hdfs_file}' из HDFS. Содержимое файла: '{content.strip()}'")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content="Сообщение отправлено успешно."
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f"Ошибка при отправке сообщения: {e}."
    )
    finally:
        consumer.close()
    
@app.get("/recommendations")
async def get_recommendations(recommendation_name: str):
    producer = Producer(producer_conf)
    try:
        # Отправка сообщения в Kafka
        producer.produce(
            topic="recommendations",
            key="rec",
            value=recommendation_name,
            callback=delivery_report
        )
        producer.flush()

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
   uvicorn.run(app, host="0.0.0.0", port=8087) 