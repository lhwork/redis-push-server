#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
File: rkpush.py
Author: LiHuan
Description: IPhone Push API
'''

import redis
import json
from redis.exceptions import ConnectionError

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
PUSH_APP_NAME = 'mixifarm'

class APNSNotification(object):
    
    _payload = {'aps' : {}}
    _maxPayloadLength = 256
    
    def __init__(self, alert=None, badge=None, sound=None):
        self.alert = alert
        self.badge = badge
        self.sound = sound

    def build(self):
        if self.alert:
            self._payload['aps']['alert'] = self.alert
        if self.badge:
            self._payload['aps']['badge'] = int(self.badge)
        if self.sound:
            self._payload['aps']['sound'] = self.sound

        if len(self._payload) > self._maxPayloadLength:
            raise Exception("Length of payload more than %d bytes." % self._maxPayloadLength)

        return self._payload

class Push(object):
    def __init__(self, app_name=None):
        super(Push, self).__init__()
        self._app_name = app_name

    def send_device_token(self, user_id=None, device_token=None):
        self._id = '%s:%s:%s' % ('user', 'id', user_id)
        try:
            _redis_server.hset(self._app_name, self._id, device_token)
        except ConnectionError, e:
            print 'Error connecting to Redis server.', e

    def publish(self, data=None):
        if data:
            try:
                return _redis_server.publish(self._app_name, json.dumps(data))
            except ConnectionError, e:
                print 'Error connecting to Redis server.', e
        else:
            print 'Push message is not None.'
        return False

def _init_redis_server():
        return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=3)

_redis_server = _init_redis_server()

if __name__ == '__main__':

    mixi_notification = APNSNotification(u'mixi Hello! 测试!', 1, 'default')
    mixi_data = mixi_notification.build()

    mixi_push = Push('mixifarm')
    mixi_push.publish(mixi_data)

    kddi_notification = APNSNotification(u'kddi Hello! 测试!', 5, 'default')
    kddi_data = kddi_notification.build()

    kddi_push = Push('kddidom')
    kddi_push.publish(kddi_data)

    """
    device_token = '18570a76 ec4378a0 f3088489 1296b22b 4cb02dd5 2e628211 005b6313 01e17339'
    push.send_device_token(25549537, device_token)
    print 'test push error.'
    """

    #data = {"aps":{"alert":"Hello!"}}
    #for i in xrange(1, 1):
    #    mixi_push.publish(mixi_data)
    #    kddi_push.publish(kddi_data)


