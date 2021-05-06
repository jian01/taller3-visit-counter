import logging

logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)
logger.debug("Logging started")

from flask import Flask, request

logger.debug("Creating app")
app = Flask(__name__)

from flask_cors import cross_origin
from google.appengine.api import memcache
from google.appengine.ext import ndb
import json
import random

logger.debug("Creating datastore client")

CACHE_TIME = 60
KIND_PARTITION_FORMAT = "VisitCount%d"
from visit_counters import *

@app.route('/visits', methods=['GET'])
@cross_origin()
def visits_get():
    visits = 1
    key_arg = request.args.get('key')
    cached_visits = memcache.get(key=key_arg)
    if cached_visits:
        return json.dumps({'visits': cached_visits})
    entity_visits = []
    for i in range(1, len(VISIT_COUNT_CLASSES)+1):
        key = ndb.Key(KIND_PARTITION_FORMAT % i, key_arg)
        entity = key.get()
        if entity:
            entity_visits.append(entity.amount)
    if entity_visits:
        visits = sum(entity_visits)
        memcache.add(key=key_arg, value=visits, time=CACHE_TIME)
    return json.dumps({'visits': visits})

@ndb.transactional(retries=1)
def increase_counter(partition, key_wout_partition):
    """
    :param partition: the partition
    :param key_wout_partition: the counter name
    """
    key = ndb.Key(KIND_PARTITION_FORMAT % partition, key_wout_partition)
    entity = key.get()
    if entity:
        entity.amount = entity.amount + 1
        entity.put()
    else:
        VISIT_COUNT_CLASSES[partition-1](id=key_wout_partition, amount=1).put()

@app.route('/visits', methods=['POST'])
def visit_updater():
    payload = request.get_data(as_text=True)
    key_arg = json.loads(payload)['key']
    partition = random.randint(1, len(VISIT_COUNT_CLASSES))
    increase_counter(partition, key_arg)
    memcache.incr(key=key_arg)
    return '{"status": "OK"}'


@app.errorhandler(Exception)
def server_error(e):
    # Log the error and stacktrace.
    logger.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
