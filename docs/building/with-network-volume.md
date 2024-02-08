## Building the Worker with a Network Volume

This will store your application on a Runpod Network Volume and
build a light weight Docker image that runs everything
from the Network volume without installing the application
inside the Docker image.

1. [Create a RunPod Account](https://runpod.io?ref=2xxro4sy).
2. Create a [RunPod Network Volume](https://www.runpod.io/console/user/storage).
3. Attach the Network Volume to a Secure Cloud [GPU pod](https://www.runpod.io/console/gpu-secure-cloud).
4. Select the RunPod Pytorch template.
5. Deploy the GPU Cloud pod.
6. Once the pod is up, open a Terminal and install the required
   dependencies. This can either be done by using the installation
   script, or manually.

### Automatic Installation Script

You can run this automatic installation script which will
automatically install all of the dependencies that get installed
manually below, and then you don't need to follow any of the
manual instructions.

```bash
wget https://raw.githubusercontent.com/ashleykleynhans/runpod-worker-llava/main/scripts/install.sh
chmod +x install.sh
./install.sh
```

### Manual Installation

You only need to complete the steps below if you did not run the
automatic installation script above.

1. Upgrade OS packages:
```bash
apt update
apt -y upgrade
```
2. Create and activate venv:
```bash
python3 -m venv /workspace/venv
source /workspace/venv/bin/activate
```
3. Install Torch:
```bash
pip3 install --no-cache-dir torch==2.1.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
4. Install LLaVA module:
```bash
cd /workspace
git clone https://github.com/haotian-liu/LLaVA.git llava
cd llava
pip3 install .
pip3 install ninja packaging
pip3 install flash-attn --no-build-isolation
pip3 install transformers==4.37.2
pip3 install protobuf
```
5. Install LLaVA RunPod Serverless Worker:
```bash
cd /workspace
git clone https://github.com/ashleykleynhans/runpod-worker-llava.git
cd runpod-worker-llava
pip3 install -r src/requirements.txt
```
6. Download the models:
```bash
export HF_HOME="/workspace"
export MODEL="liuhaotian/llava-v1.6-mistral-7b"
python3 download_models.py
```
7. Create logs directory:
```bash
mkdir -p /workspace/logs
```

## Building the Docker Image

You can either build this Docker image yourself, your alternatively,
you can use my pre-built image:

```
ashleykza/runpod-worker-llava:1.2.6
```

1. Sign up for a Docker hub account if you don't already have one.
2. Build the Docker image and push to Docker hub:
```bash
docker build -t dockerhub-username/runpod-worker-llava:1.0.0 -f Dockerfile.Network_Volume .
docker login
docker push dockerhub-username/runpod-worker-llava:1.0.0
```
