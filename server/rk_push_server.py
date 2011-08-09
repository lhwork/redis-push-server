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

class PushError(Exception):
    def __init__(self, message='Push error occured.'):
        self.message = message
        logging.error(self.message)
    def __str__(self):
        return repr(self.value)

class PushServer(object):

    def __init__(self, app_name=None):
        if configs.PUSH_APPS.has_key(app_name):
            logging.debug('push app %s' % app_name)
            self._push_ssl_sock = ssl.wrap_socket(socket.socket(socket.AF_INET,
                                                                socket.SOCK_STREAM),
                                                  certfile=configs.PUSH_APPS[app_name])
            self._redis_server = redis.Redis(host=configs.REDIS_HOST, port=configs.REDIS_PORT)
            self.subscribe(app_name)
        else:
            raise PushError('App %s is not exist.')

    def subscribe(self, app_name=None):
        logging.debug('redis subscribe.')
        _pubsub = self._redis_server.pubsub()
        try:
            _pubsub.subscribe(app_name)
        except ConnectionError, e:
            raise PushError('Error connecting to Redis server. %s.' % e)
        self._push_sock_connect()
        for message in _pubsub.listen():
            logging.debug(message)
            if message:
                if message['type'] == 'subscribe':
                    continue
                _all_user_device_tokens = self.get_all_user_device_tokens(app_name)
                for user_id, device_token in _all_user_device_tokens.iteritems():
                    logging.debug('redis hash data >>> %s, %s' % (user_id, device_token))
                    logging.debug('push data >>> %s' % message['data'])
                    self.send(device_token, message['data'])
        self._push_sock_close()

    def get_all_user_device_tokens(self, app_name=None):
        try:
            return self._redis_server.hgetall(app_name)
        except ConnectionError, e:
            raise PushError('Error connecting to Redis server. %s.' % e)

    def send(self, device_token=None, data=None):
        try:
            self._push_ssl_sock.write(chr(0) + chr(0) + chr(32)
                                      + device_token.replace(' ','').decode('hex')
                                      + chr(0) + chr(len(data)) + data)
        except socket.error, e:
            self._push_sock_close()
            raise PushError('Error while writing socket. %s.' % e)

    def _push_sock_connect(self):
        try:
            if configs.DEBUG:
                self._push_ssl_sock.connect((configs.APNS_DEV_HOST,
                                             configs.APNS_DEV_PORT))
            else:
                self._push_ssl_sock.connect((configs.APNS_PRD_HOST,
                                             configs.APNS_PRD_PORT))
        except socket.error, e:
            raise PushError('Error connecting to apple push server : %s' % e)

    def _push_sock_close(self):
        try:
            self._push_ssl_sock.close()
        except socket.error, e:
            pass

def main():
    PushServer('mixifarm')

if __name__ == '__main__':
    main()

