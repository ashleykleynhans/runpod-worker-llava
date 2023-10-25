import torch
import requests
import base64

import runpod
from runpod.serverless.utils.rp_validator import validate
from runpod.serverless.modules.rp_logger import RunPodLogger

from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import process_images, tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria

from PIL import Image
from io import BytesIO
from transformers import TextStreamer
from schemas.input import INPUT_SCHEMA


class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)


TMP_PATH = '/tmp/llava'
logger = RunPodLogger()


# ---------------------------------------------------------------------------- #
# Application Functions                                                        #
# ---------------------------------------------------------------------------- #
def load_image(image_file):
    if image_file.startswith('http://') or image_file.startswith('https://'):
        response = requests.get(image_file)
        image = Image.open(BytesIO(response.content)).convert('RGB')
    else:
        image = Image.open(image_file).convert('RGB')
    return image


def load_image_from_base64(base64_str):
    image_bytes = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    return image


def run_inference(data):
    # Model
    disable_torch_init()
    model_name = get_model_name_from_path(data['model_path'])

    tokenizer, model, image_processor, context_len = load_pretrained_model(
        data['model_path'],
        data['model_base'],
        model_name,
        data['load_8bit'],
        data['load_4bit'],
        device='cuda'
    )

    if 'llama-2' in model_name.lower():
        conv_mode = 'llava_llama_2'
    elif 'v1' in model_name.lower():
        conv_mode = 'llava_v1'
    elif 'mpt' in model_name.lower():
        conv_mode = 'mpt'
    else:
        conv_mode = 'llava_v0'

    if data['conv_mode'] is not None and conv_mode != data['conv_mode']:
        print('[WARNING] the auto inferred conversation mode is {}, while `--conv-mode` is {}, using {}'.format(
            conv_mode,
            data['conv_mode'],
            data['conv_mode']
        ))
    else:
        data['conv_mode'] = conv_mode

    conv = conv_templates[data['conv_mode']].copy()

    if 'mpt' in model_name.lower():
        roles = ('user', 'assistant')
    else:
        roles = conv.roles

    image = load_image_from_base64(data['image_base64'])
    image_tensor = process_images([image], image_processor, DictToObject(data))

    if type(image_tensor) is list:
        image_tensor = [image.to(model.device, dtype=torch.float16) for image in image_tensor]
    else:
        image_tensor = image_tensor.to(model.device, dtype=torch.float16)

    inp = data['prompt']

    if image is not None:
        # first message
        if model.config.mm_use_im_start_end:
            inp = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + inp
        else:
            inp = DEFAULT_IMAGE_TOKEN + '\n' + inp
        conv.append_message(conv.roles[0], inp)
        image = None
    else:
        # later messages
        conv.append_message(conv.roles[0], inp)

    conv.append_message(conv.roles[1], None)
    prompt = conv.get_prompt()

    input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).cuda()
    stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
    keywords = [stop_str]
    stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)

    if data['stream']:
        streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    else:
        streamer = None

    with torch.inference_mode():
        output_ids = model.generate(
            input_ids,
            images=image_tensor,
            do_sample=True,
            temperature=data['temperature'],
            max_new_tokens=data['max_new_tokens'],
            streamer=streamer,
            use_cache=True,
            stopping_criteria=[stopping_criteria])

    outputs = tokenizer.decode(output_ids[0, input_ids.shape[1]:]).strip()
    conv.messages[-1][-1] = outputs
    return outputs


def handler(job):
    validated_input = validate(job['input'], INPUT_SCHEMA)

    if 'errors' in validated_input:
        return {
            'error': validated_input['errors']
        }

    try:
        payload = validated_input['validated_input']

        outputs = run_inference({
            'model_path': payload.get('model_path'),
            'model_base': payload.get('model_base'),
            'image': payload.get('image'),
            'prompt': payload.get('prompt'),
            'conv_mode': payload.get('conv_mode'),
            'temperature': payload.get('temperature'),
            'max_new_tokens': payload.get('max_new_tokens'),
            'load_8bit': payload.get('load_8bit'),
            'load_4bit': payload.get('load_4bit'),
            'image_aspect_ratio': payload.get('image_aspect_ratio'),
            'stream': payload.get('stream')
        })

        return outputs.replace('</s>', '')
    except Exception as e:
        raise


# ---------------------------------------------------------------------------- #
# RunPod Handler                                                               #
# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    logger.info('Starting RunPod Serverless...')
    runpod.serverless.start(
        {
            'handler': handler
        }
    )