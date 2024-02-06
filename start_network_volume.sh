#!/usr/bin/env bash

echo "Worker Initiated"

if [[ ! -L /workspace ]]; then
    echo "Symlinking files from Network Volume"
    ln -s /runpod-volume /workspace
fi

if [ -f "/workspace/venv/bin/activate" ]; then
    echo "Starting RunPod Handler"
    export PYTHONUNBUFFERED=1
    export HF_HOME="/workspace"
    source /workspace/venv/bin/activate
    cd /workspace/runpod-worker-llava/src
    python3 -u rp_handler.py
else
    echo "ERROR: The Python Virtual Environment (/workspace/venv/bin/activate) could not be activated"
    echo "1. Ensure that you have followed the instructions at: https://github.com/ashleykleynhans/runpod-worker-llava/blob/main/docs/building/with-network-volume.md"
    echo "2. Ensure that you have used the Pytorch image for the installation and NOT a LLaVA image."
    echo "3. Ensure that you have attached your Network Volume to your endpoint."
    echo "4. Ensure that you didn't assign any other invalid regions to your endpoint."
fi
