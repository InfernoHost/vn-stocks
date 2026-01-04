#!/bin/bash

# Test script to verify Python modules can be imported
# Uses virtual environment Python to ensure dependencies are available

# Use virtual environment Python if available
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python3"
fi

echo "Using Python: $PYTHON"
echo "Testing Python modules..."
echo ""

$PYTHON commands_admin.py
echo "✓ commands_admin.py"
$PYTHON commands_graph.py
echo "✓ commands_graph.py"
$PYTHON commands_info.py
echo "✓ commands_info.py"
$PYTHON commands_stock.py
echo "✓ commands_stock.py"
$PYTHON commands_user.py
echo "✓ commands_user.py"
$PYTHON config.py
echo "✓ config.py"
$PYTHON database.py
echo "✓ database.py"
$PYTHON graphing.py
echo "✓ graphing.py"
$PYTHON logger.py
echo "✓ logger.py"
$PYTHON market.py
echo "✓ market.py"
$PYTHON market_simulator.py
echo "✓ market_simulator.py"
$PYTHON market_updates.py
echo "✓ market_updates.py"
$PYTHON team_detection.py
echo "✓ team_detection.py"
$PYTHON utils.py
echo "✓ utils.py"
$PYTHON validators.py
echo "✓ validators.py"

echo ""
echo "All tests passed!"
