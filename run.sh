#!/usr/bin/env bash
# CarbonLoop Application Launcher
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo " Starting CarbonLoop Platform"
echo " Problem Statement ES-02: Verifiable Carbon Accounting"
echo "=========================================================="

# Clean PYTHONPATH to isolate from system ROS packages
export PYTHONPATH="$DIR"

if [ -f "$DIR/venv/bin/uvicorn" ]; then
    PYTHON="$DIR/venv/bin/python"
    UVICORN="$DIR/venv/bin/uvicorn"
else
    PYTHON="python3"
    UVICORN="uvicorn"
fi

echo "Access the platform at: http://localhost:8000"
echo "API Docs at:            http://localhost:8000/docs"
echo "Press Ctrl+C to stop."
echo "----------------------------------------------------------"

exec "$UVICORN" app.main:app --host 0.0.0.0 --port 8000 --reload
