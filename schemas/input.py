INPUT_SCHEMA = {
    'model_path': {
        'type': str,
        'required': False,
        'default': 'liuhaotian/llava-v1.5-13b'
    },
    'model_base': {
        'type': str,
        'required': False,
        'default': None
    },
    'image': {
        'type': str,
        'required': True
    },
    'prompt': {
        'type': str,
        'required': True
    },
    'conv_mode': {
        'type': str,
        'required': False,
        'default': None
    },
    'temperature': {
        'type': float,
        'required': False,
        'default': 0.2
    },
    'max_new_tokens': {
        'type': int,
        'required': False,
        'default': 512
    },
    'codeformer_fidelity': {
        'type': float,
        'required': False,
        'default': 0.5
    },
    'load_8bit': {
        'type': bool,
        'required': False,
        'default': False
    },
    'load_4bit': {
        'type': bool,
        'required': False,
        'default': False
    },
    'image_aspect_ratio': {
        'type': str,
        'required': False,
        'default': 'pad'
    },
    'stream': {
        'type': bool,
        'required': False,
        'default': False
    }
}
