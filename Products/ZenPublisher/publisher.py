##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2007, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################

import json
import redis 
import uuid

import logging
log = logging.getLogger("zen.Publisher")

class ZenPublisher(object):
    """
    Publish metrics to redis
    """

    def __init__(self, host="localhost", port=6379):
        """
        Initializer

        @param host: redis hostname
        @param port: redis port
        """
        self._redis = redis.Redis(host, port)

    def put(self, metric, value, timestamp):
        mv = json.dumps({ "name": metric, "value": value, "timestamp": timestamp, "tags": { "uuid": uuid.uuid4() } })
        log.debug("publishing metric document: %s", mv)
        self._redis.lpush("metrics", mv)
