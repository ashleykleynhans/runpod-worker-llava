#!/usr/bin/env python3
from util import post_request


JOB_ID = 'sync-7bf0fb91-c4df-4ca8-b0ed-c91de1af29ca-e1'


if __name__ == '__main__':
    # Create the payload dictionary
    payload = {}

    post_request(payload, f'/cancel/{JOB_ID}')
