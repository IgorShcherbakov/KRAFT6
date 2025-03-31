import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import Producer


logger = logging.getLogger(__name__)

app = FastAPI()

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

# создание продюсера
producer = Producer(producer_conf)

def delivery_report(err, msg):
    """
    Проверить статус доставки сообщения
    """
    if err is not None:
        logger.info(f"Ошибка доставки сообщения в топик {msg.topic()}: {err}")
    else:
        logger.info(f"Сообщение «{msg.__str__()}» доставлено в {msg.topic()} [{msg.partition()}]")

class Message(BaseModel):
    topic: str
    key: str
    value: str

@app.get("/")
async def root():
    return "Перейдите по адресу http://localhost:8085/docs для взаимодействия со Swagger"

@app.post("/send-message/")
async def send_message(message: Message):
    try:
        producer.produce(
            message.topic,
            key=message.key,
            value=message.value,
            callback=delivery_report
        )
        producer.flush()
        return {"status": "Сообщение отправлено успешно"}
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при отправке сообщения")
    

if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   uvicorn.run(app, host="0.0.0.0", port=8085) 