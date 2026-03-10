#!/bin/bash

pip3 install bpy-addon-build psutil colorama || read -p "Error occurred. Press Enter to exit..."
python3 scripts/build_universal.py || read -p "Error occurred. Press Enter to exit..."