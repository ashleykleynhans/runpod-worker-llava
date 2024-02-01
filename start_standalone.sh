#!/usr/bin/env bash

echo "Worker Initiated"

echo "Starting RunPod Handler"
export PYTHONUNBUFFERED=1
export HF_HOME="/workspace"
cd /workspace/runpod-worker-llava
python3 -u rp_handler.py
