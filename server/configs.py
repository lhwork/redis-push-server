#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# APNS constants
MAX_PAYLOAD_LENGTH = 256
DEVICE_TOKEN_LENGTH = 32

APNS_PRD_HOST = 'gateway.push.apple.com'
APNS_PRD_PORT = 2195
APNS_DEV_HOST = 'gateway.sandbox.push.apple.com'
APNS_DEV_PORT = 2195

# Push Server configure
DEBUG = True

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

PUSH_APPS = {'mixifarm':'rekoo.pem'}


