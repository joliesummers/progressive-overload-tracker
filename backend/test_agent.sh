#!/bin/bash
VENV_PYTHON="venv/bin/python"
if [ -f "$VENV_PYTHON" ]; then
    $VENV_PYTHON app/services/bedrock_agent_service.py
else
    echo "Error: Virtual environment Python not found at $VENV_PYTHON"
    exit 1
fi
