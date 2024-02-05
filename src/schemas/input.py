INPUT_SCHEMA = {
    'model_path': {
        'type': str,
        'required': False,
        'default': 'liuhaotian/llava-v1.6-mistral-7b'
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
    'stream': {
        'type': bool,
        'required': False,
        'default': False
    }
}
