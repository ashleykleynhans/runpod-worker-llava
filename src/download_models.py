#!/usr/bin/env python3
import os
from huggingface_hub import snapshot_download


if __name__ == '__main__':
    model = os.getenv('MODEL', 'liuhaotian/llava-v1.6-mistral-7b')
    clip_model = 'openai/clip-vit-large-patch14-336'

    print(f'Downloading LLaVA model: {model}')
    snapshot_download(model)

    print(f'Downloading CLIP model: {model}')
    snapshot_download(clip_model)
