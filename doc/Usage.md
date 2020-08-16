
I think this document contains a strange English, because this is transrated based on machine translation.
So, if you find poind to fix, I wish you raise issue or PR. It's very helpful. Thanks.

-------------------------------------------------
# Usage of Nayco
## OverView
![overview](/doc/img/overview.drawio.svg)

Nayco consists of a suite of software for data entry, transformation, storage and visualization.
The basic input is MQTT, which accepts data in JSON, JSONL, or CSV format with headers. CSV format without headers is not supported.
Data can be entered in the same way by placing a file of the above format in a given folder or by adding a file to it.

The entered data is stored in the DWH via an internal broker. At this point, a table is automatically created based on the type estimated from the data.

The data stored in the DWH can be analyzed and dashboards created using Nayco's built-in visualization services, or the data can be accessed directly from an external SQL client.

Other tools are included to manage containers and DWH tables.


## The services that make up Nayco
### **[RabbitMQ](https://www.rabbitmq.com/)**
  ![](/doc/img/rabbit_mq_sample.png)
  Message Broker Service, an endpoint for MQTT data entry into Nayco.
  **Ports:**
  + 1883: Port for connecting via MQTT.
  + 15672: The RabbitMQ administration console. The default account is `guest`:`guest`.

### **[Grebe](https://github.com/tac0x2a/grebe)**
This service retrieves messages from RabbitMQ and stores them in the DWH.
  It parses the payload of the message, estimates the JSON/JSONL/headered CSV format and the type of each data, creates a table in the DWH and inserts it.

### **[Samba](https://github.com/dperson/samba)**
  It provides a network shared folder that can be accessed by users and Nayco.
  It is assumed to be used for file input by o-namazu and file output of data taken out by Node-red.

  Open the following SMB shared folder by explorer, and access it. The share name is `nayco`.
  + Windows: `\\<NAYCO_HOST>\nayco`
  + Mac: `smb://<NAYCO_HOST>/nayco`

  **Initial Setting**
  + UserName: `nayco`
  + Password: `nayco`


### **[o-namazu](https://github.com/tac0x2a/o-namazu)**
  This is a service that monitors a shared folder and sends differential data to message brokers when files are added/changed.
  The marker file (`onamazu.conf`) is placed in the folder to be monitored, and the data to be submitted to Nayco is placed/added to the folder as JSON/JSONL/CSV file with headers.

### **[ClickHouse](https://clickhouse.tech/)**
  A DWH where Nayco's data is aggregated, ClickHouse is a column-oriented database suitable for OLAP, with column-by-column data compression for efficient storage utilization and fast aggregation, making it a key on-premise data foundation service.
  **Ports**.
  + 8123: The HTTP client port
  + 9000: This is a Native client port of ClickHouse
  + 9004: Port for the MySQL interface (wire protocol). You can connect to this port using the general MySQL client.


### **[Portainer](https://www.portainer.io/)**
  ![](/doc/img/portainer_sample.png)
  You can check the status of a container and restart/stop it.
  **Ports**.
  + 19000: The access port to the web service. After logging in, select `Local` and press the `Connect` button to make it available.

### **[Metabase](https://www.metabase.com/)**
  ![](/doc/img/metabase_sample.png)

  The service is designed to visualize, analyze and build dashboards of DWH data. to connect with ClickHouse, [metabase-clickhouse-driver](https://github.com/enqueue/metabase-clickhouse-driver).
  **Initial Settings**
  The first time you access ClickHouse, you will need to set up a connection with ClickHouse as follows
  + Database type `ClickHouse`,
  + Database Name: any
  + Host: `clickhouse`
  + Port: `8123`
  + Database user name: `default`
  + Database password: empty

  **Ports**
  + 3000: Web access port

### **[Tabix](https://tabix.io/)**
  ![](/doc/img/tabix_sample.png)
  This is ClickHouse's SQL client available in a web browser. It comes with a simple visualization tool for query results.

  **Initial Setting**
  + Name: any
  + `http://host:port` : `http://<host-of-nayco-running>:8123`
  + Login: `default`
  + Password: empty
  + (Experimental) HTTP Base auth: True

  **Ports**
  + 8080: Web access port

### **[Uminoco](/uminoco/)**
  ![](/doc/img/uminoco_sample.png)
  You can see the size of the stored data and the compression ratio against the original data in each table/column. You can also rename tables, as Nayco automatically creates tables for storing data, the table names are automatically determined. This service allows you to change the table names later to suit your operation.

  ![](/doc/img/uminoco_sample02.png)
  When Nayco receives data from a new schema (number of columns, column names, data types, etc.), it creates a new table.
  Therefore, when the input data changes, such as increasing the number of collected data, the old and new data is stored in a different table.
  With this service, you can migrate data from the old table to the newly created table.

  **Ports**
  + 5000: Web access port


### **[Node-RED](https://nodered.org/)**
  ![](/doc/img/nodered_sample.png)
  It can be used as an ETL service for folders shared by Nayco in Samba and data in the DWH. It can also be used as a data entry service by sending MQTT to RabbitMQ with data acquired from outside.

  **Ports**
  + 1880: Web access port


### **[Filebrowser](https://filebrowser.org/)**
  This service provides browser-based access to folders shared by Nayco in Samba.
  ![](/doc/img/filebrowser_sample.png)

  **Initial Setting**
  + Host: `filebrowser`
  + Port: `8082`
  + User: `admin`
  + Pass: `admin`

  **Ports**
  + 8082: Web access port


## Directory Structure
  ```
  ├── LICENSE
  ├── README.md
  ├── backup.sh
  ├── doc
  ├── docker-compose.yml
  ├── metabase
  ├── rabbitmq
  ├── uminoco
  │   ├── Dockerfile
  │   ├── README.md
  │   ├── backend
  │   ├── docker-compose.yml
  │   └── frontend
  │
  └── volume
      ├── clickhouse
      ├── grebe
      ├── metabase
      ├── nodered
      ├── onamazu
      ├── portainer
      └── storage_volume
  ```

+ After launching, `$NAYCO_HOME/volume` will be created. This directory contains the volumes that each container mounts, such as settings and stored data. In particular, `$NAYCO_HOME/volume/storage_volume` is the directory shared by Samba. The other directories are of no concern: `$NAYCO_HOME/volume/storage_volume` is the directory shared by Samba.

+ The `uminoco/docker-compose.yml` is the docker-compose file for the Uminoco development environment.


## Setup
The main requirements for Nayco are
+ Docker: version 19.03.12 or later
+ docker-compose: version 1.26.2 or later


```sh
$ docker -v
Docker version 19.03.12

$ docker-compose -v
docker-compose version 1.26.2
```

Clone the repository.
```sh
$ git clone https://github.com/tac0x2a/nayco.git
$ cd nayco
```

### Launch

```sh
$ docker-compose up -d
```

In order to download the images needed to operate, the
The first time you start the system, you must have an internet connection.

### Shutdown
```sh
$ docker-compose down
```

### Backup
```sh
$ ./backup.sh
```

Stop the service to mount the `volume` directory and copy and compress it.
Restore by extracting the backup file and replacing the `volume`.


-------------------------------------------------
# Data Entry
There are two main ways to enter data into Nayco.

+ MQTT interface: publish a message to Nayco's RabbitMQ in any MQTT client
+ File interface: Put/add files in the SMB shared folder monitored by o-namazu

In both cases, the data is sent to RabbitMQ, Nayco's internal message broker. The data sent is data type estimated by Grebe and stored in the DWH.


## MQTT Interface
MQTT data entry sets the payload to JSON, JSONL, or text data in header CSV format and sends it to the Nayco host's internal broker. The topic name is used as the initial value for the name of the table in which the data is stored.

## File Interface
Data entry through the file interface is done by placing a text file in JSON, JSONL, or CSV format with headers in the SMB shared folder on Nayco.
Placed files are sent to the internal broker by [o-namazu](https://github.com/tac0x2a/o-namazu) via MQTT.

The following preparations are required to input a file by o-namazu:

1. Place a marker file (`onamazu.conf`) in a folder to be monitored
2. Restart the o-namazu container (from a service such as Portainer).


#### About Marker Files
The marker file (`onamazu.conf`) specifies the pattern of files to be monitored, and the amount of time between last file modification and archiving or deletion.

+ Example : `onamazu.config`
  ```yaml
  pattern: "*.csv"

  callback_delay: 10

  ttl: 300

  mqtt:
    host: rabbitmq
    port: 1883
    topic: nayco/sample
    format: csv

  archive:
    type: zip
    name: archive.zip
  ```

+ `mqtt.host` and `mqtt.por` should always use the above values. These are special values for Nayco, so don't change them.
+ `csv` if the file is in CSV format, or `txt` if the file is in JSON/JSONL format.

+ The file will be read a `callback_delay` second after the file was last written. This is to prevent the file from being read before the file is finished being written. The `callback_delay` should be set longer if you have large files in a folder or a lot of data to be written at once.

+ The `topic` is the name of the MQTT topic to send to the broker, and is used as the initial value for the name of the table where the data is to be stored.

+ The file that has been modified more than `tll` seconds since it was last modified will be evacuated or deleted in the manner specified by the `archive`.
  The above configuration compresses files that have been written more than five minutes since they were last written into archive.zip and archives them.

Please refer to [README.md of o-namazu](https://github.com/tac0x2a/o-namazu/README.md) for details of the parameters.


#### About Read Data
+ If a file matching the `pattern` is placed in the folder where `onamazu.config` is located, all files are read and sent to the internal broker by MQTT.
+ When data is appended to a file that has already been read, only the appended data will be sent to the new file.
  If the `mqtt.format` is `csv`, the header line (the first line of the file) and the appended data are concatenated and sent. That is, if nine lines are added to the file, ten lines of data including the header are sent.



-------------------------------------------------
# Accumulation of data

## Grebe for data type estimation and table creation
The data submitted to the message broker is stored in the [Grebe](https://github.com/tac0x2a/grebe)(and [Lake Weed](https://github.com/tac0x2a/lake_weed), which is used internally, so that the data type is It estimates and determines the schema of the DWH (ClickHouse) and the tables are automatically created and stored.

Grebe determines the tables to be stored as follows.
1. parse each column data in the payload and estimate the data type of each column.
   If the payload contains multiple rows of data, it selects a type that can store all data in the same column. For example, if a date/time format string and a real number are contained in the same column, this column is estimated to be a string type (capable of storing both).
   See [Lake Weed] (https://github.com/tac0x2a/lake_weed/blob/master/tests/test_clickhouse.py) for data type estimation and conversion rules.
   We denote here the set of pairs of column names and presumed data types as the schema. 2.
Replace '/' in the topic with '_' to make it a data source name. 3.
If a table has already been created with the same data source name and the same schema, insert data into it. 4.
If the above table does not exist yet, create a new table corresponding to this schema and insert the data into it. The name of the table should be `data source name_%03d`.

The data source name and the schema are stored in a special table `schema_table` on the DWH and Grebe refers to this table to determine the table where the data will be stored.
When Grebe creates a new table, it inserts the name of the data source, the schema and the destination table in the `schema_table`.

When Uminoco (see below) renames a table, the target table name on the `schema_table` will be changed as well.
Since Grebe uses the `schema_table` to determine the target table based on the data source name and schema, Grebe will be able to store data in the renamed table even after the table is renamed.


## Data stored in ClickHouse
[ClickHouse](https://clickhouse.tech/) is an open source column-oriented DWH that stores data in a tabular format, like an RDB.
The columnar nature of data compression makes it very well suited for fast aggregation and efficient storage utilization in on-premises environments without ample resources such as the cloud.
For more information about ClickHouse, see the documentation [What is ClickHouse?] (https://clickhouse.tech/docs/ja/).

The data is stored in the `default` database. (at least for now).
The `default` database contains the data tables created by Grebe and the aforementioned `schema_table`.

The data tables and the `schema_table` are usually referred to as read-only tables, since they are managed by Grebe and Uminoco.
As these tables are maintained by Grebe and Uminoco, any manual changes to them may cause inconsistencies.

If you want to rename a table, delete a table or copy data from one table to another, you can do so from Uminoco.


#### Checking stored data with Tabix
Tabix is a SQL client for DWH (ClickHouse) and is shipped with Nayco.
This service allows you to query DWH data in SQL.

+ Tabix: `http://<NAYCO_HOST>:8080`

  ![](/doc/img/tabix.png)

  + Name: Any
  + `http://host:port` : `http://<host-of-nayco-running>:8123`
  + Login: `default`
  + Password: empty
  + (Experimental) HTTP Base auth: True

After signing in, open the table you want to review from the list of tables in the left pane.

  ![](/doc/img/tabix_schema.png)

You can double-click to view the record.

  ![](/doc/img/tabix_table.png)

You can query in SQL as well as RDB, as shown below.

  ![](/doc/img/tabix_query.png)

See ClickHouse's [SQL Reference](https://clickhouse.tech/docs/ja/sql-reference/) for more information about SQL.


-------------------------------------------------
# Data Visualization and Analysis
Data stored in the DWH can be referenced, visualized and analyzed by tools with DB interfaces.

### Visualization with Metabase.
Nayco has a built-in BI service [Metabase](https://www.metabase.com/) that can be connected to ClickHouse and is available without any additional services or tools.
By registering ClickHouse as a DB at first startup, you can refer to the data stored in ClickHouse thereafter.

For more information on how to use Metabase, see [Metabase documentation](https://www.metabase.com/docs/latest/getting-started.html).

### Connection from External Services.
ClickHouse supports MySQL-compatible I/F (wire protocol) and can be queried by connecting to port `9004` with a common MySQL client.


-------------------------------------------------
# Management/Monitoring

## Checking the Broker
Visit RabbitMQ's Web Management Console (`http://<NAYCO_HOST>:15672`) to see how many messages are coming in and how they are being processed by Grebe. The default credentials are `guest`:`guest`.

## Table management
Tables created at DWH can be checked/managed at Uminoco(`http://<NAYCO_HOST>:5000`)
+ Table check: schema of the table, data size, data compression
+ Change table name
+ delete table
+ Copying table data to another table


#### Copy table
When Nayco receives data from a new schema (number of columns, column names, data types, etc.), it creates a new table.
So, if the input data changes, such as increasing the number of collected data, the old and new data will be stored in a different table.
In this case, you can copy the data from the old table to the newly created table from Uminoco.


![](/doc/img/uminoco_sample02.png)
1. Go to `http://<NAYCO_HOST>:5000/table_migration` and use `Select Tables` to specify the source and target tables.

2. Then, use `Select Columns` to select the values to be stored in the columns of the destination table from the columns of the source table. If the source column is not selected, null or an empty array `[]` is copied.

3. If some data may fail to be copied, such as a data type mismatch, the center icon will display a warning.
4. When the column selection is completed, press the `MIGRATE!` button to copy the data.


## container management
All the services of Nayco are executed in the container, and the execution status of the container can be confirmed by Portainer(`http://<NAYCO_HOST>:19000` ).
Portainer(`<NAYCO_HOST>:19000` ) is used to check the status of the container.

Please refer to [Portainer documentation](https://www.portainer.io/documentation/) to know how to use Portainer.

-------------------------------------------------
# Nayco Usage Example

Example: The temperature and humidity in my room. Even though I'm on vacation, I know I'm at home almost every day.
![](/doc/img/metabase_example.png)
The temperature/humidity/illumination obtained from [Nature Remo] (https://nature.global/) in Node-Red is fed into RabbitMQ and visualized in Metabase.
I only set up the Node-Red data acquisition pipeline and the Metabase screen. There is no need to convert the data or define tables on the way.
