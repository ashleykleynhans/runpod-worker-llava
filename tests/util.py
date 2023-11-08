import sys
import time
import json
import base64
import requests
from dotenv import dotenv_values

STATUS_COMPLETED = 'COMPLETED'


class Timer:
    def __init__(self):
        self.start = time.time()

    def restart(self):
        self.start = time.time()

    def get_elapsed_time(self):
        end = time.time()
        return round(end - self.start, 1)


def encode_image_to_base64(image_path):
    with open(image_path, 'rb') as image_file:
        return str(base64.b64encode(image_file.read()).decode('utf-8'))


def handle_response(resp_json, timer):
    print(json.dumps(resp_json, indent=4, default=str))
    total_time = timer.get_elapsed_time()
    print(f'Total time taken for RunPod Serverless API call {total_time} seconds')


def get_endpoint_details():
    env = dotenv_values('.env')
    api_key = env.get('RUNPOD_API_KEY', None)
    endpoint_id = env.get('RUNPOD_ENDPOINT_ID', None)

    return api_key, endpoint_id


def cancel_task(task_id):
    api_key, endpoint_id = get_endpoint_details()

    return requests.post(
        f'https://api.runpod.ai/v2/{endpoint_id}/cancel/{task_id}',
        headers={
            'Authorization': f'Bearer {api_key}'
        }
    )


def purge_queue():
    api_key, endpoint_id = get_endpoint_details()

    return requests.post(
        f'https://api.runpod.ai/v2/{endpoint_id}/purge-queue',
        headers={
            'Authorization': f'Bearer {api_key}'
        }
    )


def stream(payload, stream=False):
    api_key, endpoint_id = get_endpoint_details()
    uri = f'https://api.runpod.ai/v2/{endpoint_id}/run'

    r = requests.post(
        uri,
        json=dict(input=payload),
        headers={
            'Authorization': f'Bearer {api_key}'
        }
    )

    print(r.status_code)

    if r.status_code == 200:
        data = r.json()
        task_id = data.get('id')
        return stream_output(task_id, stream)


def stream_output(task_id, stream=False):
    api_key, endpoint_id = get_endpoint_details()

    uri = f'https://api.runpod.ai/v2/{endpoint_id}/stream/{task_id}'

    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    previous_output = ''

    try:
        while True:
            response = requests.get(uri, headers=headers)

            if response.status_code == 200:
                data = response.json()
                print(data)

                if len(data['stream']) > 0:
                    new_output = data['stream'][0]['output']
                    sys.stdout.write(new_output[len(previous_output):])
                    sys.stdout.flush()
                    previous_output = new_output

                if data.get('status') == STATUS_COMPLETED:
                    if not stream:
                        return previous_output
                    break

            elif response.status_code >= 400:
                print(response)

            # Sleep for 0.1 seconds between each request
            time.sleep(0.1 if stream else 1)
    except Exception as e:
        print(e)
        cancel_task(task_id)
