import os

import torch
import requests
import base64

import runpod
from runpod.serverless.utils.rp_validator import validate
from runpod.serverless.modules.rp_logger import RunPodLogger

from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import process_images, tokenizer_image_token, get_model_name_from_path

from PIL import Image
from io import BytesIO
from transformers.generation.streamers import TextStreamer, TextIteratorStreamer
from contextlib import redirect_stdout
from schemas.input import INPUT_SCHEMA


DEFAULT_MODEL = 'liuhaotian/llava-v1.6-mistral-7b'
INITIAL_MODEL_PATH = os.getenv('MODEL', DEFAULT_MODEL)
CURRENT_MODEL_PATH = INITIAL_MODEL_PATH
MODEL_BASE = None
LOAD_4BIT = False
LOAD_8BIT = False
logger = RunPodLogger()
disable_torch_init()


class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)


# ---------------------------------------------------------------------------- #
# Application Functions                                                        #
# ---------------------------------------------------------------------------- #
def load_image(image_file: str):
    if image_file.startswith('http://') or image_file.startswith('https://'):
        response = requests.get(image_file)
        image = Image.open(BytesIO(response.content)).convert('RGB')
    else:
        image = load_image_from_base64(image_file)
    return image


def load_image_from_base64(base64_str: str):
    image_bytes = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    return image


def run_inference(data: dict):
    global CURRENT_MODEL_PATH, tokenizer, model, image_processor, context_len

    model_path = data.get('model_path')
    model_name = get_model_name_from_path(model_path)

    if CURRENT_MODEL_PATH != model_path:
        CURRENT_MODEL_PATH = model_path

        tokenizer, model, image_processor, context_len = load_pretrained_model(
            CURRENT_MODEL_PATH,
            MODEL_BASE,
            model_name,
            LOAD_8BIT,
            LOAD_4BIT,
            device='cuda'
        )

    if 'llama-2' in model_name.lower():
        conv_mode = 'llava_llama_2'
    elif 'mistral' in model_name.lower():
        conv_mode = 'mistral_instruct'
    elif 'v1.6-34b' in model_name.lower():
        conv_mode = 'chatml_direct'
    elif 'v1' in model_name.lower():
        conv_mode = 'llava_v1'
    elif 'mpt' in model_name.lower():
        conv_mode = 'mpt'
    else:
        conv_mode = 'llava_v0'

    if data['conv_mode'] is not None and conv_mode != data['conv_mode']:
        logger.warn('The auto inferred conversation mode is {}, while `--conv-mode` is {}, using {}'.format(
            conv_mode,
            data['conv_mode'],
            data['conv_mode']
        ))
    else:
        data['conv_mode'] = conv_mode

    conv = conv_templates[data['conv_mode']].copy()
    image = load_image(data['image'])
    image_size = image.size
    image_tensor = process_images([image], image_processor, DictToObject(data))

    if type(image_tensor) is list:
        image_tensor = [image.to(model.device, dtype=torch.float16) for image in image_tensor]
    else:
        image_tensor = image_tensor.to(model.device, dtype=torch.float16)

    prompt = data['prompt']

    if image is not None:
        # first message
        if model.config.mm_use_im_start_end:
            prompt = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + prompt
        else:
            prompt = DEFAULT_IMAGE_TOKEN + '\n' + prompt
        conv.append_message(conv.roles[0], prompt)
        image = None
    else:
        # later messages
        conv.append_message(conv.roles[0], prompt)

    conv.append_message(conv.roles[1], None)
    prompt = conv.get_prompt()
    input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).cuda()

    if data['stream']:
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, timeout=20.0)
    else:
        streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    with torch.inference_mode():
        output_ids = model.generate(
            input_ids,
            images=image_tensor,
            image_sizes=[image_size],
            do_sample=True if data['temperature'] > 0 else False,
            temperature=data['temperature'],
            max_new_tokens=data['max_new_tokens'],
            streamer=streamer,
            use_cache=True
        )

    outputs = tokenizer.decode(output_ids[0]).strip()
    conv.messages[-1][-1] = outputs

    # Clean the output
    outputs = outputs.replace('<s>', '')
    outputs = outputs.replace('</s>', '')
    outputs = outputs.strip()

    return outputs


def handler(job):
    validated_input = validate(job['input'], INPUT_SCHEMA)

    if 'errors' in validated_input:
        return {
            'error': validated_input['errors']
        }

    try:
        payload = validated_input['validated_input']

        outputs = run_inference(
            {
                'model_path': payload.get('model_path'),
                'model_base': payload.get('model_base'),
                'image': payload.get('image'),
                'prompt': payload.get('prompt'),
                'conv_mode': payload.get('conv_mode'),
                'temperature': payload.get('temperature'),
                'max_new_tokens': payload.get('max_new_tokens'),
                'load_8bit': payload.get('load_8bit'),
                'load_4bit': payload.get('load_4bit'),
                'stream': payload.get('stream')
            }
        )

        return {
            'response': outputs
        }
    except Exception as e:
        raise


# ---------------------------------------------------------------------------- #
# RunPod Handler                                                               #
# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    model_name = get_model_name_from_path(INITIAL_MODEL_PATH)
    logger.info(f'Loading model: {model_name}')

    tokenizer, model, image_processor, context_len = load_pretrained_model(
        INITIAL_MODEL_PATH,
        MODEL_BASE,
        model_name,
        LOAD_8BIT,
        LOAD_4BIT,
        device='cuda'
    )

    logger.info('Starting RunPod Serverless...')
    runpod.serverless.start(
        {
            'handler': handler
        }
    )