#!/usr/bin/env python3
import os
from huggingface_hub import snapshot_download


if __name__ == '__main__':
    model = os.getenv('MODEL', 'liuhaotian/llava-v1.5-7b')
    snapshot_download(model)
