# Nayco

[![nayco](./doc/img/nayco.svg)](https://github.com/tac0x2a/nayco)

Nayco(内湖) is an all in one micro Data Lake for IoT data.

# How to deploy
## Deploy
```sh
$ docker-compose up -d
```

## Shutdown
```sh
$ docker-compose down
```

# Services
## [RabbitMQ](https://www.rabbitmq.com/)
Message broker service. The MQTT port listen json format messages. Its general entry point of data stream to Nayco.

### Ports
+ 15672: Web management console. Default account is `guest`:`guest`.
+ 1883: MQTT port.

## [Grebe](https://github.com/tac0x2a/grebe)
Grebe is forwarder JSON message from RabbitMQ to Clickhouse.

## [ClickHouse](https://clickhouse.tech/)
ClickHouse is a free analytics DBMS for big data. Central data storage of Nayco.
Default database is `default`, and user name and password is `default`.

### Ports
+ 8123: HTTP client port.

## [Portainer](https://www.portainer.io/)
Portainer is a lightweight management UI. After login, please select `Local` and press `Connect` button.

### Ports
+ 19000: Web interface.

## [Metabase](https://www.metabase.com/)
Metabase visualize data on ClickHouse. It works with [metabase-clickhouse-driver](https://github.com/enqueue/metabase-clickhouse-driver).

In first access, you need to register ClickHouse table as data source.
+ Database type `ClickHouse`,
+ Database Name: any
+ Host: `clickhouse`
+ Port: `8123`
+ Database user name: `default`
+ Database password: empty

### Ports
+ 3000: Web interface.

## [Tabix](https://tabix.io/)
Open source simple business intelligence application and sql editor tool for Clickhouse.

+ Name: any
+ `http://host:port` : `http://<host-of-nayco-running>:8123`
+ Login: `default`
+ Password: empty
+ (Experimental) HTTP Base auth: True

### Ports
+ 8080: Web interface.


## [Node-RED](https://nodered.org/)
Node-RED is a programming tool for wiring together hardware devices, APIs and online services in new and interesting ways.

### Ports
+ 1880: Web interface.


## [Filebrowser](https://filebrowser.org/)
> File Browser is a create-your-own-cloud-kind of software where you can install it on a server, direct it to a path and then access your files through a nice web interface.

+ Host: `filebrowser`
+ Port: `8082`
+ User: `admin`
+ Pass: `admin`

### Ports
+ 8082: Web interface.

## [Samba](https://github.com/dperson/samba)
> Samba docker container
Pleaase see https://github.com/dperson/samba
