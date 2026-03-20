@echo off
pip install bpy-addon-build psutil colorama || pause
python "scripts/build_universal.py" || pause