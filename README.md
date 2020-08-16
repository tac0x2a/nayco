
# What is Nayco?

[![nayco](./doc/img/nayco.svg)](https://github.com/tac0x2a/nayco)

Nayco is a small, all-in-one data infrastructure for quickly launching a primarily on-premises data collection, storage and visualization environment.

## Key Features
+ Docker containers, launched by a single `docker-compose` command
+ Column-Oriented DWH ([ClickHouse](https://clickhouse.tech/)) for fast aggregation and high storage efficiency through data compression.
+ Schema estimation based on input data and automatically creates tables in DWH. There is no need to create tables to fit the data.
+ All the software that makes up the system is OSS.


After launching with the `docker-compose` command, you just put the files in a shared folder or send the data via MQTT, and the data is automatically stored in the DWH, and then you can use [Metabase](https://www.metabase.com/) and other common tools to use a the data.

Please see [Usage.md](/doc/Usage.md) or [Usage.ja.md](/doc/Usage.ja.md) for more details.

--------------------------------------------------------------------------------
# Quick Start
#### 1. Launch
```sh
$ docker -v
Docker version 19.03.12

$ docker-compose -v
docker-compose version 1.26.2
```

```sh
$ git clone https://github.com/tac0x2a/nayco.git
$ cd nayco
$ docker-compose up -d
```

Nayco is started by the above. You can check the status of each container by accessing the Portainer(`http://<NAYCO_HOST>:19000` )
Replace `<NAYCO_HOST>` with the host or IP address where Nayco is running.

#### 2. Sample Data Entry
Here, we send JSON via MQTT to enter data.

+ Topic: `hello/nayco`
+ Payload: `{"title": "The Perfect Insider", "pub_date": "1996/4/5", "lang": "ja"}`
+ Host: `<NAYCO_HOST>`
+ Port: `1883`


Python Example
```py
import paho.mqtt.publish as pub

topic = "hello/nayco"
payload = '{"title": "The Perfect Insider", "pub_date": "1996/4/5", "lang": "ja"}'
hostname = "<NAYCO_HOST>"
port = 1883

pub.single(topic=topic, payload=payload, hostname=hostname, port=1883)
```


#### 3. Check The Data
Once the submission is complete, check the table has been created with the following data management service.
+ Uminoco: `http://<NAYCO_HOST>:5000/table/hello_nayco_001`

  ![](/doc/img/hello_nayco_table.png)

You can see that the table is automatically created based on the data and the topic name.
The table name is generated based on the topic name, but can be changed from the `RENAME TABLE` button.
Right now the compression ratio looks bad since there is only one data, but as more data comes in, the data compression by ClickHouse will take effect.




#### 4. Data Visualization
As a service for visualizing stored data, Nayco includes [Metabase](https://www.metabase.com/)
+ Metabase: `http://<NAYCO_HOST>:3000`

In order to use Metabase, the DB of DWH (ClickHouse) must be registered as a data source the first time it is accessed.
+ Database type `ClickHouse`,
+ Database Name: Any
+ Host: `clickhouse`
+ Port: `8123`
+ Database user name: `default`
+ Database password: <Empty>

![](/doc/img/metabase_clickhouse.png)

Once you've saved the above, you're ready to visualize the data stored in Nayco in Metabse. (You may not see the actual table on Metabase until the Metabase crawl is performed.)
As a test, let's do a simple visualization: since the `hello_nayco_001` table is now visible in Metabase, do the following visualization (Question).

For more information on how to use Metabase, please refer to [Metabase Documentation](https://www.metabase.com/docs/latest/getting-started.html).

![](/doc/img/metabase_1.png)

This is a bar chart with the date of publication on the horizontal axis and the number of cases on the vertical axis. Right now, there is only one case of data registered, so it looks simple.

Now, let's run the following script to add the data.

Python Example
```py
import paho.mqtt.publish as pub

topic = "hello/nayco"
payload = """
{ "title": "Doctors in Isolated Room", "pub_date": "1996/7/5", "lang": "ja" }
{ "title": "Mathematical Goodbye",     "pub_date": "1996/9/5", "lang": "ja" }
{ "title": "Jack the Poetical Private","pub_date": "1997/1/5", "lang": "ja" }
{ "title": "Who Inside",               "pub_date": "1997/4/5", "lang": "ja" }
{ "title": "Illusion Acts Like Magic", "pub_date": "1997/10/5","lang": "ja" }
{ "title": "Replaceable Summer",       "pub_date": "1998/1/7", "lang": "ja" }
{ "title": "Switch Back",              "pub_date": "1998/4/5", "lang": "ja" }
{ "title": "Numerical Models",         "pub_date": "1998/7/5", "lang": "ja" }
{ "title": "The Perfect Outsider",     "pub_date": "1998/10/5","lang": "ja" }
"""
hostname = "<NAYCO_HOST>"
port = 1883

pub.single(topic=topic, payload=payload, hostname=hostname, port=1883)
```

You can then reload the Metabase page to see the added data.

![](/doc/img/metabase_10.png)


This way, you can easily visualize your data by simply sending it through MQTT. Otherwise, you can query the DWH directly in any SQL client or export it as a file.

----------------------------------------
# Contributing
1. Fork it ( https://github.com/tac0x2a/nayco/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request