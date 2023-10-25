#!/usr/bin/env bash

echo "Worker Initiated"

echo "Symlinking files from Network Volume"
ln -s /runpod-volume /workspace

echo "Starting RunPod Handler"
export PYTHONUNBUFFERED=1
export HF_HOME="/runpod_volume"
source /workspace/runpod-worker-llava/venv/bin/activate
cd /workspace/runpod-worker-llava
python -u rp_handler.py
