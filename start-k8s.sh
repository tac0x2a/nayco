#!/bin/sh
./build-registry.sh
docker stack deploy --orchestrator=kubernetes -c docker-compose.yml nayco
