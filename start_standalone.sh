#!/usr/bin/env bash

echo "Worker Initiated"

echo "Starting RunPod Handler"
export PYTHONUNBUFFERED=1
export HF_HOME="/workspace"
source /workspace/venv/bin/activate
cd /workspace/runpod-worker-llava/src
python3 -u rp_handler.py
