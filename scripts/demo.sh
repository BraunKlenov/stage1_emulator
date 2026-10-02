#!/usr/bin/env sh
set -eu

python3 -m unittest discover -s tests -v
printf '\nЗапуск GUI-прототипа:\n'
python3 src/main.py
