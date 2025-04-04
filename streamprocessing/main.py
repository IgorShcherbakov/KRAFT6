import os
import faust
import logging
import ssl
from confluent_kafka import serialization
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

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
        ssl_context=ssl_context
    )
)

# таблица для хранения заблокированных товароы
ban_products_table = app.Table(
    "ban_products",
    partitions=3,    # Количество партиций
    default=dict,     # Функция или тип для пропущенных ключей
)

# Настройка клиента Schema Registry
schema_registry_conf = {'url': 'http://schema-registry:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Получение схемы из Schema Registry
subject_name = "products-value"
schema_response = schema_registry_client.get_latest_version(subject_name)
json_schema_str = schema_response.schema.schema_str

# Настройка десериализатора
def from_dict(data, ctx):
    return data

json_deserializer = JSONDeserializer(
    schema_str=json_schema_str, 
    schema_registry_client=schema_registry_client, 
    from_dict=from_dict
)
string_deserializer = serialization.StringDeserializer()

# топик заблокированных товаров для входных данных
ban_products_topic = app.topic("ban-products", key_type=str, value_type=str)

# топик заблокированных товаров для входных данных
products_topic = app.topic("products", key_type=str, value_type=bytes)

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

def is_product_not_banned(product):
    """Проверяет, не находится ли продукт в таблице заблокированных товаров."""
    msg = json_deserializer(product, SerializationContext(products_topic.get_topic_name(), MessageField.VALUE))
    product_id = msg.get('product_id')
    return product_id not in ban_products_table[product_id]

# Функция, реализующая потоковую обработку сообщений
@app.agent(products_topic)
async def process_messages(products):
    async for product in products.filter(lambda product: is_product_not_banned(product)):
        try:
            msg = json_deserializer(product, SerializationContext(products_topic.get_topic_name(), MessageField.VALUE))
            logger.info(f"Получен товар: {msg}")
            yield msg
        except Exception as e:
            logger.exception(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    os.system("faust -A streamprocessing.main worker -l INFO")