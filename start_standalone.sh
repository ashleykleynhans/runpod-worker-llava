#!/usr/bin/env bash

echo "Worker Initiated"

echo "Symlinking files from Network Volume"
rm -rf /root/.cache
ln -s /workspace/.cache /root/.cache

echo "Starting RunPod Handler"
export PYTHONUNBUFFERED=1
source /workspace/runpod-worker-llava/venv/bin/activate
cd /workspace/runpod-worker-llava
python -u rp_handler.py
