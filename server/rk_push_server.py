#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import redis
import socket
import ssl
try:
    import json
except ImportError:
    import simplejson as json

import logging
import configs
from redis.exceptions import ConnectionError

#logging setting
logging.basicConfig(filename='rk_push_server.log', level=logging.DEBUG)
log = logging.getLogger('PushServer')

class PushError(Exception):
    def __init__(self, message='Push error occured.'):
        self.message = message
        log.error(self.message)
    def __str__(self):
        return repr(self.value)

class APNSConnection(object):
    def __init__(self, cert_file=None):
        super(APNSConnection, self).__init__()
        self.cert_file = cert_file
        self._ssl_socket = None

    def _connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ssl_socket = ssl.wrap_socket(self._socket, certfile=self.cert_file)
        try:
            if configs.DEBUG:
                self._ssl_socket.connect((configs.APNS_DEV_HOST,
                                          configs.APNS_DEV_PORT))
            else:
                self._ssl_socket.connect((configs.APNS_PRD_HOST,
                                          configs.APNS_PRD_PORT))
        except socket.error, e:
            raise PushError('Error connecting to apple push server : %s' % e)

    def close(self):
        if self._ssl_socket:
            self._ssl_socket.close()
        self._ssl_socket = None
        
    def write(self, device_token=None, data=None):
        try:
            if not self._ssl_socket:
                self._connect()
        
            self._ssl_socket.write(chr(0) + chr(0) + chr(32)
                                      + device_token.replace(' ','').decode('hex')
                                      + chr(0) + chr(len(data)) + data)
        except socket.error, e:
            raise PushError('Error while writing socket. %s.' % e)


class PushServer(object):

    _push_app = {}

    def __init__(self):
        super(PushServer, self).__init__()
        for app_name, cert_file in configs.PUSH_APPS.iteritems():
            self._push_app[app_name] = APNSConnection(cert_file)

        self.subscribe()

    def subscribe(self):
        log.debug('redis subscribe.')
        self._redis_server = redis.Redis(host=configs.REDIS_HOST, port=configs.REDIS_PORT)

        pubsub = self._redis_server.pubsub()
        try:
            pubsub.subscribe(self._push_app.keys())
        except ConnectionError, e:
            raise PushError('Error connecting to Redis server. %s.' % e)

        for message in pubsub.listen():
            log.debug(message)
            if message:
                if message['type'] == 'subscribe':
                    continue
                apns_connection = self._push_app[message['channel']]
                all_user_device_tokens = self.get_all_user_device_tokens(message['channel'])
                for user_id, device_token in all_user_device_tokens.iteritems():
                    log.info('push redis hash data >>> %s, %s, %s' % (user_id,
                                                                       device_token,
                                                                      message['data']))
                    apns_connection.write(device_token, message['data'])
                apns_connection.close()

    def get_all_user_device_tokens(self, app_name=None):
        try:
            return self._redis_server.hgetall(app_name)
        except ConnectionError, e:
            raise PushError('Error connecting to Redis server. %s.' % e)


def main():
    PushServer()

if __name__ == '__main__':
    main()

