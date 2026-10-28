#!/bin/sh
set -eu
cd "$(dirname "$0")"
docker info >/dev/null 2>&1
docker compose up -d --build --wait
docker compose ps
printf '%s\n' 'App: http://localhost:3000 - Register your own first administrator account.' 'pgAdmin: http://localhost:5050 - See DOCKER_GUIDE.md.'
