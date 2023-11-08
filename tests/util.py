import sys
import time
import json
import base64
import requests
from dotenv import dotenv_values

STATUS_IN_QUEUE = 'IN_QUEUE'
STATUS_IN_PROGRESS = 'IN_PROGRESS'
STATUS_FAILED = 'FAILED'
STATUS_COMPLETED = 'COMPLETED'
STATUS_TIMED_OUT = 'TIMED_OUT'


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


def post_request(payload, api=None):
    api_key, endpoint_id = get_endpoint_details()

    if api_key is not None and endpoint_id is not None:
        base_uri = f'https://api.runpod.ai/v2/{endpoint_id}'
    else:
        base_uri = f'http://127.0.0.1:8000'

    if api is not None:
        uri = base_uri + '/' + api.lstrip('/')
    else:
        uri = f'{base_uri}/runsync'

    timer = Timer()

    r = requests.post(
        uri,
        headers={
            'Authorization': f'Bearer {api_key}'
        },
        json=payload
    )

    print(f'Status code: {r.status_code}')

    if r.status_code == 200:
        resp_json = r.json()

        if 'output' in resp_json:
            handle_response(resp_json, timer)
        else:
            if 'status' in resp_json:
                job_status = resp_json['status']
            else:
                job_status = STATUS_FAILED

            print(f'Job status: {job_status}')

            if job_status == STATUS_IN_QUEUE or job_status == STATUS_IN_PROGRESS:
                request_id = resp_json['id']
                request_in_queue = True

                while request_in_queue:
                    r = requests.get(
                        f'{base_uri}/status/{request_id}',
                        headers={
                            'Authorization': f'Bearer {api_key}'
                        },
                    )

                    print(f'Status code from RunPod status endpoint: {r.status_code}')

                    if r.status_code == 200:
                        resp_json = r.json()
                        job_status = resp_json['status']

                        if job_status == STATUS_IN_QUEUE or job_status == STATUS_IN_PROGRESS:
                            print(f'RunPod request {request_id} is {job_status}, sleeping for 5 seconds...')
                            time.sleep(5)
                        elif job_status == STATUS_FAILED:
                            request_in_queue = False
                            print(f'RunPod request {request_id} failed')
                            print(json.dumps(resp_json, indent=4, default=str))
                        elif job_status == STATUS_COMPLETED:
                            request_in_queue = False
                            print(f'RunPod request {request_id} completed')
                            handle_response(resp_json, timer)
                        elif job_status == STATUS_TIMED_OUT:
                            request_in_queue = False
                            print(f'ERROR: RunPod request {request_id} timed out')
                        else:
                            request_in_queue = False
                            print(f'ERROR: Invalid status response from RunPod status endpoint')
                            print(json.dumps(resp_json, indent=4, default=str))
            elif job_status == STATUS_COMPLETED \
                    and 'output' in resp_json \
                    and 'status' in resp_json['output'] \
                    and resp_json['output']['status'] == 'error':
                print(f'ERROR: {resp_json["output"]["message"]}')
            elif job_status == STATUS_FAILED:
                print('ERROR: Job FAILED!')

                try:
                    error = json.loads(resp_json['error'])
                    print(error['error_type'])
                    print(error['error_message'])
                    print(error['error_traceback'])
                except Exception as e:
                    print(json.dumps(resp_json, indent=4, default=str))
            else:
                print(json.dumps(resp_json, indent=4, default=str))
    else:
        print(f'ERROR: {r.content}')


def stream(payload):
    api_key, endpoint_id = get_endpoint_details()
    uri = 'https://api.runpod.ai/v2/{endpoint_id}/run'

    response = requests.post(
        uri,
        json=dict(input=payload),
        headers={
            'Authorization': f'Bearer {api_key}'
        }
    )

    if response.status_code == 200:
        data = response.json()
        task_id = data.get('id')
        return stream_output(task_id)


def stream_output(task_id):
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

                if len(data['stream']) > 0:
                    new_output = data['stream'][0]['output']
                    sys.stdout.write(new_output[len(previous_output):])
                    sys.stdout.flush()
                    previous_output = new_output

                if data.get('status') == 'COMPLETED':
                    break

            elif response.status_code >= 400:
                print(response)

            # Sleep for 0.1 seconds between each request
            time.sleep(0.1 if stream else 1)
    except Exception as e:
        print(e)
        cancel_task(task_id)
