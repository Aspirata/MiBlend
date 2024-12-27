@echo off
where python > NUL 2>&1 || (
    echo Python не установлен. Установка...
    start https://www.python.org/downloads/
    pause
    exit
)

python -c "import sys; sys.exit(0 if 'psutil' in sys.modules else 1)" || pip install psutil
python build_universal.py