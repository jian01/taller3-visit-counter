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

CACHE_TIME = 600
PARTITION_KEY_FORMAT = "%s_%d"
PARTITIONS_TO_USE = 100


class VisitCount(ndb.Model):
    key = ndb.StringProperty()
    amount = ndb.IntegerProperty()


@app.route('/visits', methods=['GET'])
@cross_origin()
def visits_get():
    visits = 1
    key_arg = request.args.get('key')
    cached_visits = memcache.get(key=key_arg)
    if cached_visits:
        return json.dumps({'visits': cached_visits})
    entities = VisitCount.query(VisitCount.key == key_arg).fetch()
    if entities:
        visits = sum([e.amount for e in entities])
        memcache.add(key=key_arg, value=visits, time=CACHE_TIME)
    return json.dumps({'visits': visits})

@app.route('/visits', methods=['POST'])
def visit_updater():
    payload = request.get_data(as_text=True)
    key_arg = json.loads(payload)['key']
    partition = random.randint(0, PARTITIONS_TO_USE)
    key_part_arg = PARTITION_KEY_FORMAT % (key_arg, partition)
    key = ndb.Key("VisitCount", key_part_arg)
    entity = key.get()
    if entity:
        entity.amount = entity.amount + 1
        entity.put()
    else:
        VisitCount(id=key_part_arg, key=key_arg,
                   amount=1).put()
    memcache.incr(key=key_arg)
    return '{"status": "OK"}'


@app.errorhandler(Exception)
def server_error(e):
    # Log the error and stacktrace.
    logger.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
