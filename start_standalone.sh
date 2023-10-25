#!/usr/bin/env bash

echo "Worker Initiated"

echo "Starting RunPod Handler"
export PYTHONUNBUFFERED=1
export HF_HOME="/workspacex"
source /workspace/runpod-worker-llava/venv/bin/activate
cd /workspace/runpod-worker-llava
python -u rp_handler.py
