#!/usr/bin/env python3
# Replace the single source face into the single target face
from util import post_request, encode_image_to_base64

MODEL_PATH = 'liuhaotian/llava-v1.5-7b'
IMAGE_PATH = '../data/extreme_ironing.jpg'
PROMPT = 'What is unusual about this image?'
TEMPERATURE = 0.2
MAX_NEW_TOKENS = 512
STREAM = False


if __name__ == '__main__':
    # Create the payload dictionary
    payload = {
        "input": {
            "model_path": MODEL_PATH,
            "image": encode_image_to_base64(IMAGE_PATH),
            "prompt": PROMPT,
            "temperature": TEMPERATURE,
            "max_new_tokens": MAX_NEW_TOKENS,
            "stream": STREAM
        }
    }

    post_request(payload)
