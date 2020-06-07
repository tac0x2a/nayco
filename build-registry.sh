#!/bin/sh

# Build
docker-compose -f docker-compose-build.yml build

# Regitry
docker-compose -f docker-compose-registry.yml up -d

docker image tag metabase-nayco localhost:5000/metabase-nayco
docker push localhost:5000/metabase-nayco

docker image tag rabbitmq-nayco localhost:5000/rabbitmq-nayco
docker push localhost:5000/rabbitmq-nayco

# Clean registry
# docker-compose -f docker-compose-registry.yml down
