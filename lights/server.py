import asyncio
import os
from flask import Flask, request, jsonify
from lights.lights_api import create_api

loop = asyncio.get_event_loop()
api = loop.run_until_complete(create_api(os.getenv("CONFIG_PATH", None)))

app = Flask(__name__)

@app.route('/lights', methods=["GET", "POST"])
def lights():
    if request.method == 'POST':
        json = request.get_json()
        loop.run_until_complete(api.set_lights(json))
        return jsonify({"status": "ok"})
    elif request.method == 'GET':
        lights = api.get_lights()
        return jsonify(lights)


