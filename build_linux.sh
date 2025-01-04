#!/bin/bash

python -c "import sys; sys.exit(0 if 'psutil' in sys.modules else 1)" || pip install psutil
python "scripts/build_universal.py"