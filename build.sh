#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python WeatherMapAPI/manage.py collectstatic --no-input
python WeatherMapAPI/manage.py migrate