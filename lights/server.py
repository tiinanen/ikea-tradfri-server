import asyncio
import os
from flask import Flask, request, jsonify
from lights.scheduler import LightScheduler
from lights.lights_api import create_api

loop = asyncio.get_event_loop()
api = loop.run_until_complete(create_api(os.getenv("CONFIG_PATH", None)))

scheduler = LightScheduler(os.getenv("SCHEDULER_DB_PATH", None))

app = Flask(__name__)

def set_lights(json):
    loop.run_until_complete(api.set_lights(json))

@app.route('/lights', methods=["GET", "POST"])
def lights():
    if request.method == 'POST':
        json = request.get_json()
        loop.run_until_complete(api.set_lights(json))
        return jsonify({"status": "ok"})
    elif request.method == 'GET':
        lights = api.get_lights()
        return jsonify(lights)

@app.route('/schedule', methods=['POST'])
def schedule():
    if request.method == 'POST':
        json = request.get_json()
        scheduler_params = json["scheduler_params"]
        light_config = json["light_config"]
        job = scheduler.add_job(set_lights, [light_config], **scheduler_params)
    return jsonify({'job_id': job.id})

@app.route('/list')
def list_jobs():
    jobs = scheduler.get_jobs()
    json = []
    for job in jobs:
        json.append({
            "id": job.id,
            "name": job.name,
            "func": job.func.__name__,
            "args": job.args,
            "kwargs": job.kwargs,
            "trigger": str(job.trigger)
        })
    return jsonify(json)

@app.route('/remove/<job_id>')
def remove_job(job_id):
    scheduler.remove_job(job_id)
    return jsonify({'status': 'ok'})
