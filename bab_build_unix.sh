#!/bin/bash
set -x off
pip3 install bpy-addon-build psutil colorama || read exit 1
python3 "scripts/build_universal.py" || read exit 1