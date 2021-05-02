from flask import Flask, render_template, url_for, request
from google.cloud import tasks_v2
from functools import lru_cache
import json

app = Flask(__name__)

PROJECT_NAME = "taller3-proca"
DEFAULT_LOCATION = "us-east1"
VISITS_QUEUE_NAME = "visits-queue"
URI_FOR_VISIT_COUNT = "/visits"
URI_FOR_VISIT_COUNT_GET = URI_FOR_VISIT_COUNT + "?key=%s"
VISIT_ENDPOINT = "https://visit-counter-dot-taller3-proca.ue.r.appspot.com"


def create_task(project, queue, uri, location, payload):
    """Create a task for a given queue with an arbitrary payload."""
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(project, location, queue)
    task = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': tasks_v2.HttpMethod.POST,
            'relative_uri': uri
        }
    }
    if payload is not None:
        if isinstance(payload, dict):
            payload = json.dumps(payload)
            task["app_engine_http_request"]["headers"] = {"Content-type": "application/json"}
        converted_payload = payload.encode()

        task['app_engine_http_request']['body'] = converted_payload

    response = client.create_task(parent=parent, task=task)

    return response


def register_visit_for_key(key):
    visit_payload = {'key': key}
    create_task(PROJECT_NAME, VISITS_QUEUE_NAME,
                URI_FOR_VISIT_COUNT, DEFAULT_LOCATION,
                visit_payload)


@lru_cache
def render_template_w_url(template_path, url):
    return render_template(template_path, url=url)


@app.route('/')
def home():
    key = 'institutional_home'
    register_visit_for_key(key)
    return render_template_w_url('home.html', url=(VISIT_ENDPOINT+URI_FOR_VISIT_COUNT_GET)%key)


@app.route('/about')
def about():
    key = 'institutional_about'
    register_visit_for_key(key)
    return render_template_w_url('about.html', url=(VISIT_ENDPOINT+URI_FOR_VISIT_COUNT_GET)%key)


@app.route('/jobs')
def jobs():
    key = 'institutional_jobs'
    register_visit_for_key(key)
    return render_template_w_url('jobs.html', url=(VISIT_ENDPOINT+URI_FOR_VISIT_COUNT_GET)%key)


@app.route('/legal')
def legal():
    key = 'institutional_legal'
    register_visit_for_key(key)
    return render_template_w_url('legal.html', url=(VISIT_ENDPOINT+URI_FOR_VISIT_COUNT_GET)%key)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
