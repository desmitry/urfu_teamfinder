#!/bin/sh

docker buildx build -t ghcr.io/desmitry/urfu_teamfinder-bot:1.0.0 -f src/bot/Dockerfile .