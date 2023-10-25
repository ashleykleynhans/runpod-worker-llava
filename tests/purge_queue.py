#!/usr/bin/env python3
from util import post_request


if __name__ == '__main__':
    # Create the payload dictionary
    payload = {}

    post_request(payload, '/purge-queue')
