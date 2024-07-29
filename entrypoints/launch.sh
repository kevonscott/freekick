#!/bin/bash

APP_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
export ENV=PRODUCTION && cd $APP_ROOT && .venv/bin/gunicorn --config freekick/gunicorn_config.py freekick.app:app
