# Uminoco

Uminoco is an discovery ship on the data lake. It will work with [nayco](https://github.com/tac0x2a/nayco).

## For Development

```sh
$ cd uminoco
$ docker-compose up
```

+ Frontend(Vue.js) http://localhost:8081
+ Backend(Flask) http://localhost:5000


## Deploy
In root directory

```sh
cd $NAYCO_ROOT
$ docker-compose build
$ docker-compose up -d
```

+ Uminoco http://host:5000