# KRAFT6
## Финальный проект (Разработать аналитическую платформу для маркетплейса)

## Архитектура решения представлена следующими сервисами:
### 1. kafka-ui
Сервис для визуализации кафка и не только.

### 2. schema-registrar
Сервис для работы со схемами данных.

### 3. schema-registry
Сервис для регистрации схемы данных.

### 4. zookeeper
Сервис для координации брокеров.

### 5. kafka-0
Сервис брокер.

### 6. kafka-1
Сервис брокер.

### 7. kafka-2
Сервис брокер.

### 8. kafka-init
Сервис для создания топиков и настройки ACL.

### 9. target-zookeeper
Сервис для координации брокеров.

### 10. target-kafka-0
Сервис брокер.

### 11. target-kafka-1
Сервис брокер.

### 12. target-kafka-2
Сервис брокер.

### 13. target-kafka-init
Сервис для создания топиков и настройки ACL.

### 14. mirror-maker
Сервис для дублирования данных на второстепенный кластер.

### 15. shopapi
Веб-сервис который отправляет данные о товарах в кафку.
Swagger - http://localhost:8085/docs

### 16. clientapi
Веб-сервис который моделирует запросы от клиентов.
Swagger - http://localhost:8086/docs

### 17. elasticsearch
Сервис для хранения и анализа данных.

### 18. kibana
Сервис, который предоставляет интерфейс для визуализации и анализа данных.

### 19. hadoop-namenode
Сервис - главный узел в кластере Hadoop, который управляет файловой системой и метаданными.

### 20. hadoop-datanode-1
Сервис - один из рабочих узлов в кластере Hadoop, который отвечает за хранение фактических данных.

### 21. hadoop-datanode-2
Сервис - один из рабочих узлов в кластере Hadoop, который отвечает за хранение фактических данных.

### 22. hadoop-datanode-3
Сервис - один из рабочих узлов в кластере Hadoop, который отвечает за хранение фактических данных.

### 23. hadoopapi
Веб-сервис который моделирует перенос данных в HDFS, а так же отправление рекомендаций в топик Kafka.
Swagger - http://localhost:8087/docs

### 24. streamprocessing
Сервис потоковой обработки данных.

### 25. kafka-connect
Сервис для сохранения данных из топика в файл.

### 26. kafka-connect-init
Сервис для регистрации коннектора.

### 27. prometheus
Сервис для сбора метрик.

### 28. grafana
Сервис для визуализации собранных метрик.

### 29. alertmanager
Сервис для отправки уведомлений.

## Пример использования

### 1. Поднять контейнеры

```bash
docker compose up -d
```

### 2. Перейти в UI Kafka

```bash
http://localhost:8080/
```

Убедиться что поднято 2 кластера:

![alt text](resources/image.png)

Проверить более детально поднятый основной кластер:

Брокеры,

![alt text](resources/image-3.png)

Топики,

![alt text](resources/image-2.png)

Консьюмеры,

![alt text](resources/image-1.png)

Схемы,

![alt text](resources/image-4.png)

ACL,

![alt text](resources/image-5.png)

Так же, проверить дублирующий кластер:

Брокеры,

![alt text](resources/image-6.png)

Топики (пока нет копий из основного кластера),

![alt text](resources/image-7.png)

Консьюмеры (так же пока ничего нет),

![alt text](resources/image-8.png)

Схемы,

![alt text](resources/image-9.png)

ACL,

![alt text](resources/image-10.png)

### 3. Смоделировать отправку данных о товарах

Перейти в сервис shopapi

```bash
http://localhost:8085/docs
```

![alt text](resources/image-11.png)

и выполнить запрос set_products

В результате на основном кластере в топике products появиться 5 продуктов:

![alt text](resources/image-12.png)

Так же данный топик будет создан на дублирующем кластере (данные будут загружены и туда при помощи сервиса mirror-maker).

### 4. Смоделировать поиск информации о товаре

Перейти в сервис clientapi

```bash
http://localhost:8086/docs
```

![alt text](resources/image-13.png)

и выполнить запрос get_product_info, указав например, клавиатура

![alt text](resources/image-14.png)

В результате данный запрос попадет в топик search-products на основном:

![alt text](resources/image-15.png)

и дублирующем кластере:

![alt text](resources/image-16.png)

Так же, данный запрос попадет еще и в сервис elasticsearch.
Перейти в сервис kibana

```bash
http://localhost:5601/app/management/kibana/
```

Создать index pattern

![alt text](resources/image-17.png)

![alt text](resources/image-18.png)

Далее перейти в Discover, где можно увидеть поисковой запрос:

![alt text](resources/image-19.png)

### 5. Смоделировать отправку данных в HDFS

Перейти в сервис hadoopapi

![alt text](resources/image-20.png)

и выполнить запросы get_data (данные попадут в HDFS)

![alt text](resources/image-23.png)

и get_recommendations,

![alt text](resources/image-21.png)

рекомендации попадут в топик recommendations на дублирующем кластере:

![alt text](resources/image-24.png)

### 6. Смоделировать потоковую обработку данных

Перейти в сервис streamprocessing (провалиться в логи контейнера)

![alt text](resources/image-25.png)

Видим что прогрузилось 5 товаров.
Далее смоделировать блокировку товаров.

Перейти в сервис shopapi, 

```bash
http://localhost:8085/docs
```

и выполнить запрос set_ban_products (указав например, 1, 2, 3, 4 - последовательно)

В результате данные попадут в топик ban-products на основном кластере:

![alt text](resources/image-26.png)

Выполнить повторную загрузку товаров (в этом же сервисе, set_products)

В результате, в сервисе streamprocessing можно увидеть, во первых обработку заблокированных товаров, 
во вторых что был обработан только товар с идентфикатором 5 (который не был заблокирован)

![alt text](resources/image-27.png)

### 7. Смоделировать запись в файл

Если выполнить запрос (подставив идентификатор сервиса kafka-connect)

```bash
docker exec 17fa932644ef750ec49246504e65d1ddae28eebb2c1ce3f61387f3aa5174e564 cat /home/appuser/products.out
```

можно увидеть следующее:

![alt text](resources/image-28.png)

Это говорит о том что сервис kafka-connect пишет данные из топика products в файл.

### 8. Мониторинг

Перейти в сервис prometheus:

```bash
http://localhost:9060/targets
```

Видим что сервис собирает метрики с двух кластеров:

![alt text](resources/image-29.png)

Перейти в сервис grafana:

```bash
http://localhost:3000/dashboards
```

Выбрать дашборд Kafka Broker Metrics:

![alt text](resources/image-30.png)

Так же был поднять сервис alertmanager (настроено оповещение)
Для корректной работы сервиса необходимо указать почту отправителя и пароль, а так же почту получателя.

![alt text](resources/image-31.png)

Смоделировать падение брокера, остановить например kafka-0:

![alt text](resources/image-32.png)
