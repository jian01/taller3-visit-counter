from flask import Flask, render_template, url_for, request
from flask_cors import cross_origin
from google.cloud import datastore
import json

datastore_client = datastore.Client()
app = Flask(__name__)


@app.route('/visits', methods=['GET'])
@cross_origin()
def visits_get():
    visits = 1
    key_arg = request.args.get('key')
    key = datastore_client.key("Visit Count", key_arg)
    entity = datastore_client.get(key)
    if entity:
        visits = entity['amount']
    return json.dumps({'visits': visits})


@app.route('/visits', methods=['POST'])
def visit_updater():
    payload = request.get_data(as_text=True)
    key_arg = json.loads(payload)['key']
    key = datastore_client.key("Visit Count", key_arg)
    entity = datastore_client.get(key)
    if entity:
        entity["amount"] += 1
        datastore_client.put(entity)
    else:
        entity = datastore.Entity(key=key)
        entity.update(
            {
                "amount": 1,
            }
        )
        datastore_client.put(entity)
    return '{"status": "OK"}'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
