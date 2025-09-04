#!/bin/sh

docker buildx build -t ghcr.io/desmitry/urfu_teamfinder-bot:1.0.0 -f src/bot/Dockerfile .
docker buildx build -t ghcr.io/desmitry/urfu_teamfinder-scripts:1.0.0 -f scripts/Dockerfile .