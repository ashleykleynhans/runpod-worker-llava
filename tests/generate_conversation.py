from util import post_request_conversation, encode_image_to_base64
import json

# CONVERSATION SHOULD LIKE THIS:
# Human: What is unusual about this image?
# Assistant: The unusual aspect of this image is that a man is hanging out of the back of a yellow taxi cab, holding a clothesline with clothes on it. This is not a typical sight in urban environments, as it is not common for people to hang out of taxis or use clotheslines in public spaces. The scene also includes other vehicles, such as a truck and a car, which adds to the overall unconventional nature of the image.
# Human: I see, do you think that could happen in real life?

MODEL_PATH = 'liuhaotian/llava-v1.5-7b'
IMAGE_PATH = 'images/extreme_ironing.jpg'
TEMPERATURE = 0.2
MAX_NEW_TOKENS = 512

roles = ("Human", "Assistant")
if 'llama-2' in MODEL_PATH.lower():
    roles = ("USER", "ASSISTANT")
elif 'v1' in MODEL_PATH.lower():
    roles = ("USER", "ASSISTANT")
elif 'mpt' in MODEL_PATH.lower():
    conv_mode = 'mpt'
    roles = ('user', 'assistant')
PROMPT = ""

while True:
    user_prompt = input(f'{roles[0]}: ')
    PROMPT += f"{roles[0]}: {user_prompt}\n"
    # Create the payload dictionary
    payload = {
        "input": {
            "model_path": MODEL_PATH,
            "image": encode_image_to_base64(IMAGE_PATH),
            "prompt": PROMPT,
            "temperature": TEMPERATURE,
            "max_new_tokens": MAX_NEW_TOKENS,
            "stream": False
        }
    }

    resp_json = post_request_conversation(payload)
    if resp_json['status'] == 'COMPLETED':
        output_response = resp_json['output']['response']
        print(f"{roles[1]}:", output_response)
        PROMPT += f"{roles[1]}: {output_response}\n"
    else:
        print("Error:")
        print(json.dumps(resp_json, indent=4, default=str))