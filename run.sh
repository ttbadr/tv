#!/bin/bash

cd "$(dirname "$0")"

python tv/update_sources.py
python tvbox/update_sources.py

echo "All scripts executed."