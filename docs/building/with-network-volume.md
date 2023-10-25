## Building the Worker with a Network Volume

This will store your application on a Runpod Network Volume and
build a light weight Docker image that runs everything
from the Network volume without installing the application
inside the Docker image.

1. [Create a RunPod Account](https://runpod.io?ref=2xxro4sy).
2. Create a [RunPod Network Volume](https://www.runpod.io/console/user/storage).
3. Attach the Network Volume to a Secure Cloud [GPU pod](https://www.runpod.io/console/gpu-secure-cloud).
4. Select a light-weight template such as RunPod Pytorch.
5. Deploy the GPU Cloud pod.
6. Once the pod is up, open a Terminal and install the required dependencies:
```bash
cd /workspace
git clone https://github.com/ashleykleynhans/runpod-worker-llava.git
cd runpod-worker-llava
python3 -m venv venv
source venv/bin/activate
pip3 install --no-cache-dir torch==2.0.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
pip3 install --no-cache-dir xformers==0.0.22
pip3 install -r requirements.txt
pip3 install transformers==4.34.1
```
7. Download the models:
```bash
export HUGGINGFACE_HUB_CACHE="/workspace/huggingface-cache/hub"
export TRANSFORMERS_CACHE="/workspace/huggingface-cache/hub"
export MODEL="liuhaotian/llava-v1.5-7b"
python3 download_models.py
```
8. Sign up for a Docker hub account if you don't already have one.
9. Build the Docker image and push to Docker hub:
```bash
docker build -t dockerhub-username/runpod-worker-llava:1.0.0 -f Dockerfile.Network_Volume .
docker login
docker push dockerhub-username/runpod-worker-llava:1.0.0
```
