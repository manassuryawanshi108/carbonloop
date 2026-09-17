#!/usr/bin/env bash
# CarbonLoop Automated Test Suite Runner
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo " Running CarbonLoop Verification Suites"
echo "=========================================================="

# Clean environment to prevent ROS 2 plugin interference
export PYTHONPATH="$DIR"

if [ -f "$DIR/venv/bin/pytest" ]; then
    PYTEST="$DIR/venv/bin/pytest"
    PYTHON="$DIR/venv/bin/python"
else
    PYTEST="pytest"
    PYTHON="python3"
fi

echo "--- 1. Deterministic Engine Benchmarks (10 Hand-Calculated Tests) ---"
env -u PYTHONPATH "$PYTEST" tests/test_engine.py -v

echo ""
echo "--- 2. Live 10-Step Audit & Traceability Flow Verification ---"
env -u PYTHONPATH "$PYTHON" tests/verify_demo_flow.py

echo ""
echo "=========================================================="
echo " ALL TESTS AND VERIFICATION STEPS PASSED SUCCESSFULLY!"
echo "=========================================================="
