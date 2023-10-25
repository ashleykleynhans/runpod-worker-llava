# Local Testing (not required if you don't want to test locally)

## Clone the repo, create a venv and install the requirements

```bash
git clone https://github.com/ashleykleynhans/runpod-worker-llava.git
cd runpod-worker-llava
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## Install the Models

```bash
TODO
```

## Start the local RunPod Handler API

Use `--rp_serve_api` command line argument to serve the API locally.

```bash
python3 -u rp_handler.py --rp_serve_api
```

**NOTE:** You need to keep the RunPod Handler API running in order to
run the tests, so open a new terminal window to run the tests. 

## Set your test data files

You can either overwrite the images in the `data` directory with your
own source and target files, or alternatively, you can edit the
scripts in the `tests` directory to reference the source and target
images somewhere else on your system.

## Remove credentials from .env

If you have added your `RUNPOD_API_KEY` and
`RUNPOD_ENDPOINT_ID` to the `.env` file within
this directory, you should first comment them
out before attempting to test locally.  If
the .env file exists and the values are provided,
the tests will attempt to send the requests to
your RunPod endpoint instead of running locally.

### Run test scripts

1. Ensure that the RunPod Handler API is still running.
2. Change directory to the `tests` directory and run
   one of the scripts, for example:
```bash
cd tests
python3 all_1_source_into_all_1_target.py
```
3. This will display the HTTP status code and the filename
   of the output image, for example:
```
Status code: 200
Saving image: 792a7e9f-9c36-4d35-b408-0d45d8e2bbcb.jpg
```

You can then open the output image (in this case
`792a7e9f-9c36-4d35-b408-0d45d8e2bbcb.jpg`) to view the
results of the face swap.

You obviously need to edit the payload within the
script to achieve the desired results.
