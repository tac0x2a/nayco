# Nayco とは
[![nayco](/doc/img/nayco.svg)](https://github.com/tac0x2a/nayco)

Nayco(内湖) は、主にオンプレミスでデータの収集・蓄積・可視化環境を素早く立ち上げるための、オールインワンの小さなデータ基盤です。


## 主な特徴
+ Dockerコンテナ群で構成され、`docker-compose` コマンド一発で起動
+ 列指向DWH([ClickHouse](https://clickhouse.tech/))による、高速な集計とデータ圧縮による高いストレージ効率
+ 入力データを元にスキーマを推定し、自動でDWHにテーブルを作成。データに合わせてテーブルを作成する必要はありません。
+ 構成するソフトウェアは全てOSS

`docker-compose` コマンドで立ち上げたあとは、共有フォルダにファイルを置いたりMQTTでデータを送信するだけで、DWHへ自動でデータが蓄積され、[Metabase](https://www.metabase.com/)や一般的なツールによってデータを利用することができます。


## クイックスタート

#### 1. 起動
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
上記でNaycoが起動します。各コンテナの状態は Portainer(`http://<NAYCO_HOST>:19000` )にアクセスして確認することができます。

なお、`<NAYCO_HOST>` は Naycoが実行されているホストまたはIPアドレスに読み替えてください。

#### 2. サンプルデータの入力
ここでは、MQTTでJSONを送信してデータを入力します。

+ Topic: `hello/nayco`
+ Payload: `{"title": "The Perfect Insider", "pub_date": "1996/4/5", "lang": "ja"}`
+ Host: `<NAYCO_HOST>`
+ Port: `1883`


Pythonの例
```py
import paho.mqtt.publish as pub

topic = "hello/nayco"
payload = '{"title": "The Perfect Insider", "pub_date": "1996/4/5", "lang": "ja"}'
hostname = "<NAYCO_HOST>"
port = 1883

pub.single(topic=topic, payload=payload, hostname=hostname, port=1883)
```



#### 3. データの確認

送信が完了したら、以下のデータ管理サービスでテーブルが作成されたことを確認します。
+ Uminoco: `http://<NAYCO_HOST>:5000/table/hello_nayco_001`
  ![](/doc/img/hello_nayco_table.png)

データとtopic名を元にテーブルが自動作成されていることを確認できます。
テーブル名はtopic名を元に生成されますが、`RENAME TABLE` ボタンから変更することができます。
今はデータが1件だけなので圧縮率が悪く見えますが、データが増えるにつれて、ClickHouseによるデータ圧縮が効果を発揮します。


#### 4. データの可視化
蓄積したデータを可視化するサービスとして、Naycoには[Metabase](https://www.metabase.com/) が含まれています。
+ Metabase: `http://<NAYCO_HOST>:3000`

Metabaseを利用するためにあ、初回アクセス時に、DWH(ClickHouse)のDBをデータソースとして登録する必要があります。
+ Database type `ClickHouse`,
+ Database Name: 任意
+ Host: `clickhouse`
+ Port: `8123`
+ Database user name: `default`
+ Database password: <空>

![](/doc/img/metabase_clickhouse.png)

上記をSaveすれば、Naycoに蓄積されたデータをMetabseで可視化する準備が整いました。(Metabaseのクロールが実行されるまでの間、実際のテーブルがMetabase上に表示されない場合があります)
試しに、簡単な可視化をしてみましょう。Metabase上で `hello_nayco_001` テーブルが見えるようになったので、以下のような可視化(Question)を行います。
Metabaseの使い方については、[Metabaseのドキュメント](https://www.metabase.com/docs/latest/getting-started.html)を参照してください。

![](/doc/img/metabase_1.png)

横軸を公開日、縦軸を件数とするバーチャートです。今は1件しかデータが登録されていないので、シンプルな見た目です。

以下のようなスクリプトを実行し、データを追加してみます。

Pythonの例
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

その後、Metabaseのページをリロードすると追加されたデータが表示されます。

![](/doc/img/metabase_10.png)


このように、MQTTでデータを送信するだけで、簡単に可視化が可能です。その他、任意のSQLクライアントでDWHを直接クエリしたり、ファイルとしてエクスポートすることが可能です。

-------------------------------------------------
# 基本

## 概要
![overview](/doc/img/overview.drawio.svg)


Naycoは、データの入力、変換、蓄積、可視化のためのソフトウェア群によって構成されています。
基本の入力はMQTTで、JSON, JSONL, またはヘッダ付きCSV形式のデータを受け付けます。ヘッダなしのCSVフォーマットはサポートされません。
ファイルによる入力も可能で、所定のフォルダに上記形式のファイルを置くか追記することで、同様にデータを入力できます。

入力されたデータは内部のブローカーを経由し、DWHへ保存されます。このとき、データから推定された型を元に、自動的にテーブルが作成されます。

DWHへ格納されたデータは、Naycoが内蔵する可視化サービスを用いて分析やダッシュボードを作ったり、外部のSQLクライアントから直接データを利用することができます。

その他、コンテナの管理ツールや、DWHのテーブルを管理するツールが含まれています。

## Naycoを構成するサービス一覧
### **[RabbitMQ](https://www.rabbitmq.com/)**
  ![](/doc/img/rabbit_mq_sample.png)
  メッセージブローカーサービスです。NaycoにMQTTでデータ入力する際のエンドポイントです。
  **ポート:**
  + 1883: MQTTで接続するためのポートです。
  + 15672: RabbitMQの管理コンソールです。デフォルトのアカウントは `guest`:`guest` です。

### **[Grebe](https://github.com/tac0x2a/grebe)**
  RabbitMQからメッセージを取り出し、DWHへ格納するサービスです。
  メッセージのペイロードを解析し、JSON/JSONL/ヘッダ付きCSVフォーマットと、各データの型を推定して、DWHにテーブルを作成し、Insertします。

### **[Samba](https://github.com/dperson/samba)**
  ユーザとNaycoがアクセス可能なネットワーク共有フォルダを提供します。
  o-namazuでのファイル入力や、Node-redで取り出したデータのファイル出力先としての使用を想定しています。

  エクスプローラ等で以下のSMB共有フォルダを開いてアクセスします。共有名は `nayco` です。
  + Windows: `\\<NAYCO_HOST>\nayco`
  + Mac: `smb://<NAYCO_HOST>/nayco`

  **初期設定**
  + ユーザ名: `nayco`
  + パスワード: `nayco`


### **[o-namazu](https://github.com/tac0x2a/o-namazu)**
  共有フォルダを監視し、ファイルの追加/変更があると、差分データをメッセージブローカーへ送信するサービスです。
  監視対象とするフォルダにマーカファイル(`onamazu.conf`)を置いて、Naycoへ投入するデータをJSON/JSONL/ヘッダ付きCSVファイルとして同フォルダへ配置/追記します。

### **[ClickHouse](https://clickhouse.tech/)**
  Naycoのデータが集約されるDWHです。ClickHouseはOLAPに適した列指向のデータベースで、列単位のデータ圧縮により効率的なストレージ利用と高速な集計が可能であり、オンプレミスのデータ基盤としてのキーとなるサービスです。
  **ポート**
  + 8123: HTTP クライアントのポートです
  + 9000: ClickHouseのNative クライアントのポートです
  + 9004: MySQL インタフェース(wire protocol)のポートです。一般的なMySQLのクライアントを用いて接続することができます。

### **[Portainer](https://www.portainer.io/)**
  ![](/doc/img/portainer_sample.png)
  コンテナの状態を一覧し、動作状況の確認やコンテナの再起動/停止が可能です。
  **ポート**
  + 19000: Webサービスへのアクセスポートです。ログイン後、`Local` を選択して`Connect` ボタンを押して利用できるようになります。

### **[Metabase](https://www.metabase.com/)**
  ![](/doc/img/metabase_sample.png)

  DWHのデータを可視化し、分析やダッシュボード構築を行うためのサービスです。ClickHouseとの接続には、[metabase-clickhouse-driver](https://github.com/enqueue/metabase-clickhouse-driver) を使っています。
  **初期設定**
  初回アクセス時は、以下のClickHouseとの接続設定を行う必要があります。
  + Database type `ClickHouse`,
  + Database Name: any
  + Host: `clickhouse`
  + Port: `8123`
  + Database user name: `default`
  + Database password: empty

  **ポート**
  + 3000: Webアクセス用ポート

### **[Tabix](https://tabix.io/)**
  ![](/doc/img/tabix_sample.png)
  Webブラウザで利用可能な、ClickHouseのSQLクライアントです。クエリ結果の簡単な可視化ツールが付属しています。

  **初期設定**
  + Name: any
  + `http://host:port` : `http://<host-of-nayco-running>:8123`
  + Login: `default`
  + Password: empty
  + (Experimental) HTTP Base auth: True

  **Ports**
  + 8080: Webアクセス用ポート

### **[Uminoco](/uminoco/)**
  ![](/doc/img/uminoco_sample.png)
  蓄積されたデータのサイズや元データに対する圧縮率などをテーブル/カラムごとに確認することができます。また、テーブル名を変更することができます。Naycoは蓄積先のテーブルを自動で作成するため、テーブル名も自動的に決定されてしまいます。本サービスを用いることで、後から運用に適したテーブル名に変更する事ができます。

  ![](/doc/img/uminoco_sample02.png)
  Naycoは新しいスキーマのデータ(カラム数, カラム名, データ型など)を受け取ると、新たにテーブルを作成します。
  そのため、収集データを増やすなど入力データが変化すると、新旧のデータが別のテーブルに格納されてしまいます。
  本サービスを用いることで、新しく作られたテーブルに、古いテーブルからデータを移行することができます。

  **ポート**
  + 5000: Webアクセス用ポート


### **[Node-RED](https://nodered.org/)**
  ![](/doc/img/nodered_sample.png)
  NaycoがSambaで共有するフォルダや、DWH内のデータに対するETLサービスとして利用できます。その他、外部から取得したデータをRabbitMQへMQTT送信することで、データ入力サービスとしても利用できます。

  **ポート**
  + 1880: Webアクセス用ポート


### **[Filebrowser](https://filebrowser.org/)**
  NaycoがSambaで共有するフォルダへブラウザベースからアクセスするためのサービスです。
  ![](/doc/img/filebrowser_sample.png)

  **初期設定**
  + Host: `filebrowser`
  + Port: `8082`
  + User: `admin`
  + Pass: `admin`

  **ポート**
  + 8082: Webアクセス用ポート


## ディレクトリ構成
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

+ 起動すると、`$NAYCO_HOME/volume` が作成されます。ここには各種設定や蓄積されたデータなど、各コンテナがマウントするボリュームが配置されます。特に、`$NAYCO_HOME/volume/storage_volume` は、Sambaで共有されるディレクトリです。その他のディレクトリについては気にする必要はありません。

+ `uminoco/docker-compose.yml` は Uminocoの開発環境のためのdocker-compose ファイルです。

## セットアップ
Naycoの主な動作要件は以下です
+ Docker: version 19.03.12 以降
+ docker-compose: version 1.26.2 以降

```sh
$ docker -v
Docker version 19.03.12

$ docker-compose -v
docker-compose version 1.26.2
```

リポジトリをクローンします。
```sh
$ git clone https://github.com/tac0x2a/nayco.git
$ cd nayco
```

### 起動

```sh
$ docker-compose up -d
```

動作に必要なイメージをダウンロードするため、
インターネットに接続可能な環境で初回起動してください。

### 停止
```sh
$ docker-compose down
```

### バックアップ
```sh
$ ./backup.sh
```
`volume`配下をマウントするサービスを停止し、`volume`配下をコピーして圧縮します。
リストアは、バックアップファイルを展開して `volume` を置き換えてください。


-------------------------------------------------
# データの入力
Naycoへのデータ入力は大きく2つの方法があります。

+ MQTTインタフェース: 任意のMQTTクライアントで、NaycoのRabbitMQへメッセージをPublishする
+ ファイルインタフェース: o-namazu が監視するSMB共有フォルダにファイルを置く/追記する

いずれの場合も、データはNayco内部のメッセージブローカーであるRabbitMQへ送信されます。送信されたデータは Grebe によってデータ型が推定され、DWHへ蓄積されます。


## MQTT インタフェース
MQTTによるデータ入力では、JSON, JSONL, またはヘッダ付きCSVフォーマットのテキストデータをペイロードに設定してNaycoホストの内部ブローカーへ送信します。トピック名は、データ格納先テーブルの名前の初期値に使用されます。

## ファイル インタフェース
ファイルインタフェースによるデータ入力は、Nayco上のSMB共有フォルダにJSON, JSONL, またはヘッダ付きCSVフォーマットのテキストファイルを配置して行います。
配置したファイルは [o-namazu](https://github.com/tac0x2a/o-namazu) によって、MQTTで内部のブローカーへ送信されます。

o-namazuでファイル入力を行うには、以下の準備が必要です。
1. 監視対象とするフォルダにマーカファイル(`onamazu.conf`)を配置する
2. (Portainer等のサービスから) o-namazu コンテナを再起動する

#### マーカファイルについて
マーカファイル(`onamazu.conf`) は、監視対象とするファイルのパターンや、最後にファイルが変更されてからアーカイブまたは削除するまでの時間などを指定します。

+ `onamazu.config` の例
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

+ `mqtt.host` および `mqtt.por` は常に上記の値を使用してください。これはNaycoのための特別な値なので、変更しないでください。
+ ファイルがCSVフォーマットである場合は `csv` を、JSON/JSONLフォーマットの場合は `txt` を指定します。

+ ファイルの読み込みは、ファイルが最後に書き込まれてから`callback_delay` 秒後に行われます。これは、ファイルの書き込みが完了する前にファイルを読み込まないようにするためです。大きなファイルをフォルダに配置したり、一度に大量のデータが追記されるようなケースでは、`callback_delay` を長めに設定するのが良いでしょう。

+ `topic` は ブローカーへ送信するMQTTのトピック名で、データ格納先テーブルの名前の初期値に使用されます。

+ 最後にファイルが変更されてから`tll` 秒以上経過したファイルは、`archive` で指定された方法で退避されるか削除されます。
  上記設定では、最後に書き込みがされてから5分以上が経過したファイルを、archive.zip に圧縮してアーカイブします。

パラメータの詳細については [o-namazu の README.md](https://github.com/tac0x2a/o-namazu/README.md) を参照してください。


#### 読み込みデータについて
+ `onamazu.config` が配置されたフォルダに `pattern` にマッチするファイルが配置されると、ファイルをすべて読みこんで、内部のブローカーへMQTTで送信します。
+ すでにデータを読み取られたことのあるファイルにデータが追記された場合、追記されたデータのみを新たに送信します。
  このとき、`mqtt.format` が `csv` である場合、ヘッダ行(ファイルの先頭行)と、追加されたデータを結合して送信します。つまり、ファイルに9行追記された場合はヘッダも含めて10行のデータを送信します。


-------------------------------------------------
# データの蓄積

## Grebeによるデータ型推定とテーブル作成
メッセージブローカに投入されたデータは [Grebe](https://github.com/tac0x2a/grebe)(と内部で使われている[Lake Weed](https://github.com/tac0x2a/lake_weed)) によってデータ型が推定され、DWH(ClickHouse)のスキーマを決定し、テーブルが自動作成されて蓄積されます。

Grebeは蓄積先のテーブルを以下のように決定します。
1. ペイロード中の各カラムデータをパースし、カラムごとのデータ型を推定する。
   ペイロードに複数行のデータが含まれている場合、同一カラムのデータを全て格納可能な型を選択する。例えば、日時フォーマットの文字列と実数が同一カラムに含まれる場合、このカラムは(両者を格納可能な)文字列型と推定する。
   データ型の推定および変換規則は [Lake Weed](https://github.com/tac0x2a/lake_weed/blob/master/tests/test_clickhouse.py) を参照。
   この、カラム名と推定されたデータ型のペアの集合を、ここではスキーマとする。
2. トピック中の '/' を '_' へ置換し、データソース名とする。
3. すでに同一データソース名かつ同一のスキーマでテーブルが作成されている場合、そのテーブルにデータを挿入する。
4. まだ上記のテーブルが存在しない場合、本スキーマに該当するテーブルを新たにテーブルを作成し、そのテーブルにデータを挿入する。テーブル名は `データソース名_%03d` とする。

データソース名およびスキーマは、DWH上の特別なテーブル`schema_table` に格納されており、Grebeはこのテーブルを参照してデータの格納先テーブルを決定します。
Grebeが新たにテーブルを作成する際は、`schema_table` にデータソース名、スキーマ、格納先テーブル名をInsertします。

後述のUminocoによってテーブル名を変更した場合、`schema_table` 上の格納先テーブル名の値も変更されます。
Grebe はデータソース名とスキーマを元に`schema_table` を参照して格納先テーブルを決定しているため、テーブル名を変更した後も、Grebeは名前変更後のテーブルにデータを格納し続ける事ができます。


## ClickHouseへ蓄積されたデータ
[ClickHouse](https://clickhouse.tech/) はRDBのように表形式でデータを格納するオープンソースの列指向DWHです。
列指向の特徴であるデータ圧縮は、クラウドのように潤沢なリソースのないオンプレミス環境でも高速に集計を行い、効率的にストレージを利用するために非常に適しています。
ClickHouseについてはドキュメント [ClickHouseとは?](https://clickhouse.tech/docs/ja/) を参照してください。

データは、`default` データベースに格納されます。(少なくとも現時点では)
`default` データベースには、Grebeが作成したデータテーブルと、前述の `schema_table` が配置されます。

各データテーブルおよび `schema_table` は通常、読み取り専用として参照してください。
これらのテーブルはGrebeおよびUminocoが管理しているため、手動で変更を加えると不整合が生じる場合があります。

テーブル名の変更, テーブルの削除, テーブルのデータを他のテーブルへコピーしたい場合は、 Uminoco から行ってください。



#### Tabixによる蓄積データの確認
TabixはDWH(ClickHouse)のSQLクライアントで、Naycoに同梱されています。
このサービスでDWHのデータをSQLでクエリすることができます。

+ Tabix: `http://<NAYCO_HOST>:8080`

  ![](/doc/img/tabix.png)

  + Name: 任意
  + `http://host:port` : `http://<host-of-nayco-running>:8123`
  + Login: `default`
  + Password: empty
  + (Experimental) HTTP Base auth: True

サインインしたら、左のペインのテーブルの一覧から、確認したいテーブルを開きます。

  ![](/doc/img/tabix_schema.png)

ダブルクリックすると、レコードを確認することができます。

  ![](/doc/img/tabix_table.png)

以下のように、RDBと同様にSQLでクエリすることができます。

  ![](/doc/img/tabix_query.png)

SQLについては ClickHouseの[SQLリファレンス](https://clickhouse.tech/docs/ja/sql-reference/)を参照してください。


-------------------------------------------------
# データの可視化と分析
DWHに蓄積されたデータは、DBとのI/Fを持つツールなどから参照し、可視化や分析が可能です。

### Metabaseによる可視化
NaycoはClickHouseと接続可能なBIサービス [Metabase](https://www.metabase.com/) を内蔵しており、サービスやツールの追加なしに利用可能です。
初回起動時にClickHouseをDBとして登録することで、以降ClickHouseに蓄積されたデータを参照することができます。

Metabaseの使い方については、[Metabaseのドキュメント](https://www.metabase.com/docs/latest/getting-started.html)を参照してください。


### 外部サービスからの接続
ClickHouseはMySQL互換のI/F(wire protocol)をサポートしており、一般的なMySQLクライアントでポート`9004`に接続することでクエリできます。


-------------------------------------------------
# 管理/監視

## ブローカの確認
RabbitMQのWeb管理コンソール(`http://<NAYCO_HOST>:15672`)にアクセスすることで、メッセージの流入量や、Grebeによる処理の状況などを確認できます。デフォルトの認証情報は `guest`:`guest` です。

## テーブルの管理
DWHに作成されたテーブルは Uminoco(`http://<NAYCO_HOST>:5000`) で確認/管理することができます。
+ テーブルの確認: テーブルのスキーマ、データサイズ、データ圧縮率
+ テーブル名の変更
+ テーブルの削除
+ テーブルデータの他テーブルへのコピー


#### テーブルのコピー
Naycoは新しいスキーマのデータ(カラム数, カラム名, データ型など)を受け取ると、新たにテーブルを作成します。
そのため、収集データを増やすなど入力データが変化すると、新旧のデータが別のテーブルに格納されてしまいます。
その場合、Uminocoから、古いテーブルから新しく作られたテーブルへデータをコピーして引き継ぐことができます。

![](/doc/img/uminoco_sample02.png)
1. `http://<NAYCO_HOST>:5000/table_migration` へアクセスし、`Select Tables` でコピー元とコピー先のテーブルを指定します。
2. 次に、`Select Columns` で、コピー先テーブルのカラムに格納する値を、コピー元テーブルのカラムから選択します。コピー元カラムが選択されていない場合、NULLまたは空の配列`[]` がコピーされます。
3. データ型が一致しないなど、データによってはコピーに失敗する可能性がある場合、中央のアイコンが警告表示となります。
4. カラムの選択が完了したら、`MIGRATE!` ボタンを押してデータコピーを行います。


## コンテナの管理
Naycoは全てのサービスがコンテナで実行されており、Portainer(`http://<NAYCO_HOST>:19000` )でコンテナの実行状況などを確認することができます。
また、o-namazuのマーカファイルの更新をした場合など、コンテナの再起動や停止を行うことができます。

Portainerの使い方については、[Portainer documentation](https://www.portainer.io/documentation/) を参照してください。


-------------------------------------------------
# Naycoの利用例

例: 私の部屋の温湿度。休暇中にも関わらず、ほぼ毎日自宅に居ることがわかる。
![](/doc/img/metabase_example.png)
Node-Redで [Nature Remo](https://nature.global/)から取得した温度/湿度/照度を RabbitMQへ投入し、Metabaseで可視化しています。
設定したのは Node-Red のデータ取得パイプラインと、Metabaseの画面だけです。途中のデータ変換やテーブル定義などの設定は不要です。
