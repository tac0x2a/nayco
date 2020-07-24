#!/bin/bash

sudo whoami

# Stop Containers without RabbitMQ
docker-compose stop \
  grebe \
  onamazu \
  clickhouse \
  portainer \
  metabase \
  tabix \
  node-red \
  filebrowser \
  samba

mkdir -p backup
sudo tar czf backup/nayco_backup_$(date +%Y%m%d%H%M%S).tar.gz volume/

docker-compose up -d