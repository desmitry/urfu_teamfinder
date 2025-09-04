#!/bin/sh

pybabel extract --input-dirs=./ -o src/bot/locales/messages.pot
pybabel update -i src/bot/locales/messages.pot -d src/bot/locales