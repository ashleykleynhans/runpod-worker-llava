#!/usr/bin/env python3
import base64
import json

MODEL_PATH = 'liuhaotian/llava-v1.5-7b'
IMAGE_PATH = 'data/extreme_ironing.jpg'
PROMPT = 'What is unusual about this image?'
TEMPERATURE = 0.2
MAX_NEW_TOKENS = 512
STREAM = False


def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        encoded_data = base64.b64encode(image_data).decode('utf-8')
        return encoded_data


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

    # Save the payload to a JSON file
    with open('test_input.json', 'w') as output_file:
        json.dump(payload, output_file)

    print('Payload saved to: test_input.json')

