@echo off
where python > NUL 2>&1 || (
    echo Python не установлен. Установка...
    start https://www.python.org/downloads/
    pause
    exit
)

pip install bpy-addon-build
pip install psutil
python build_universal.py