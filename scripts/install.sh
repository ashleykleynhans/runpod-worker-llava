#!/usr/bin/env bash

TORCH_VERSION="2.1.2"

echo "Deleting LLaVA"
rm -rf /workspace/llava

echo "Deleting LLaVA Serverless Worker"
rm -rf /workspace/runpod-worker-llava

echo "Deleting venv"
rm -rf /workspace/venv

echo "Cloning LLaVA Serverless Worker repo to /workspace"
cd /workspace
git clone https://github.com/ashleykleynhans/runpod-worker-llava.git
cd runpod-worker-llava

echo "Installing Ubuntu updates"
apt update
apt -y upgrade

echo "Creating and activating venv"
python3 -m venv /workspace/venv
source /workspace/venv/bin/activate

echo "Installing Torch"
pip3 install torch==${TORCH_VERSION} torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo "Installing LLaVA"
cd /workspace
git clone https://github.com/haotian-liu/LLaVA.git llava
cd llava
pip3 install .
pip3 install ninja packaging
pip3 install flash-attn --no-build-isolation
pip3 install transformers==4.37.2
pip3 install protobuf

echo "Installing LLaVA Serverless Worker"
cd /workspace/runpod-worker-llava
pip3 install -r src/requirements.txt

echo "Downloading models"
cd /workspace/runpod-worker-llava/src
export HF_HOME="/workspace"
export MODEL="liuhaotian/llava-v1.6-mistral-7b"
python3 download_models.py

echo "Creating log directory"
mkdir -p /workspace/logs
