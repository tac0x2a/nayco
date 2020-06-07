#!/bin/sh
docker-compose -f docker-compose-registry.yml down
docker stack rm --orchestrator=kubernetes  nayco