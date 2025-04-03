import os
import faust
import logging
import ssl
from confluent_kafka import serialization

# Установите переменные окружения для SSL
os.environ['KAFKA_SSL_CA_LOCATION'] = 'ca.crt'
os.environ['KAFKA_SSL_CERTIFICATE_LOCATION'] = 'kafka-1.crt'
os.environ['KAFKA_SSL_KEY_LOCATION'] = 'kafka-1.key'
os.environ['KAFKA_SECURITY_PROTOCOL'] = 'SASL_SSL'
os.environ['KAFKA_SASL_MECHANISM'] = 'PLAIN'
os.environ['KAFKA_SASL_USERNAME'] = 'consumer'
os.environ['KAFKA_SASL_PASSWORD'] = 'consumer'

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


# Создание SSL контекста
ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
ssl_context.load_cert_chain(certfile='kafka-1.crt', keyfile='kafka-1.key')
ssl_context.load_verify_locations(cafile='ca.crt')

# Конфигурация Faust-приложения
app = faust.App(
    "sfa",
    broker="kafka://kafka-1:9011",
    value_serializer="raw", # Работа с байтами (default: "json")
    store="memory://",
#    #store="rocksdb://",
    broker_credentials=faust.SASLCredentials(
        username='admin',
        password='admin-secret',
        #mechanism='PLAIN',
        #security_protocol='SASL_SSL',
        ssl_context=ssl_context
    )
)

# таблица для хранения заблокированных товароы
ban_products_table = app.Table(
    "ban_products",
    partitions=3,    # Количество партиций
    default=dict,     # Функция или тип для пропущенных ключей
)

string_deserializer = serialization.StringDeserializer()

# топик заблокированных товаров для входных данных
ban_products_topic = app.topic("ban-products", key_type=str, value_type=str)

# Функция, реализующая потоковую обработку заблокированных товаров       
@app.agent(ban_products_topic)
async def process_ban_products(ban_products):
    async for bp in ban_products:
        try:
            msg = bp
        except Exception as e:
            logger.exception(f"Ошибка десериализации: {str(e)}")

        logger.info(f"Текущий список заблокированных товаров:")
        for key, value in ban_products_table.items():
            logger.info(f"Ключ: {key}, Значение: {value}")

        # сохраняем новое значение
        ban_products_table[msg] = msg
        logger.info(f"Новый список заблокированных товаров:")
        for key, value in ban_products_table.items():
            logger.info(f"Ключ: {key}, Значение: {value}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    os.system("faust -A streamprocessing.main worker -l INFO")