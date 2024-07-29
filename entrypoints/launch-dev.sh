#!/bin/bash

APP_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
export ENV=DEVELOPMENT && cd $APP_ROOT && .venv/bin/flask --app freekick.app run --debug
