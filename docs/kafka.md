# Kafka Broker

Follow these instructions to install Kafka broker.

Create Ubuntu 20.04 VM with 2vCPUs 8GB RAM 50 GB disk

The below instructions are taken from [kafka-docker readme](https://github.com/wurstmeister/kafka-docker/blob/master/README.md)

## Install

### docker-compose

Install docker-compose via: https://docs.docker.com/compose/install/

### kafka broker

Clone repository

```
cd ~
git clone https://github.com/wurstmeister/kafka-docker.git
cd kafka-docker
git checkout da5266b46d97ce6d4b780cd5f158e66a9cb2e5c8
```

Edit `docker-compose.yml` to conform the below diff example

**Note:** `KAFKA_ADVERTISED_HOST_NAME` should be set to the external ipaddress of the VM

```diff
--- a/docker-compose.yml
+++ b/docker-compose.yml
@@ -7,10 +7,10 @@ services:
   kafka:
     build: .
     ports:
-      - "9092"
+      - "9092:9092"
     environment:
       DOCKER_API_VERSION: 1.22
-      KAFKA_ADVERTISED_HOST_NAME: 192.168.99.100
+      KAFKA_ADVERTISED_HOST_NAME: 172.15.0.209
       KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
     volumes:
       - /var/run/docker.sock:/var/run/docker.sock
```

Provision kafka/zookeeper

```
docker-compose up -d
```

## Usage

Log into kafka container (replace with your container id)

```
sudo docker exec -it 4745f6478787  /bin/bash
```

### Publish message on on topic

Run the below command (taken from [kafka-quickstart](https://kafka.apache.org/quickstart))

```
/opt/kafka/bin/kafka-console-producer.sh --topic <topic name> --bootstrap-server localhost:9092
```

Terminate with `^C`

### Consume maessage from topic

Run the below command (taken from [kafka-quickstart](https://kafka.apache.org/quickstart))

```
/opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <topic name> --from-beginning
```

### Create topics

```
/opt/kafka/bin/kafka-topics.sh --create --topic <topic name> --bootstrap-server localhost:9092
```

### List topics

```
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Delete topic

```
/opt/kafka/bin/kafka-topics.sh --delete --topic <topic name> --bootstrap-server localhost:9092
```
