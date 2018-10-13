import json

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory

import asyncio
import uuid
import os


async def create_api(config_path=None):
    api = LightApi()
    await api._async_init(config_path)
    return api


class LightApi:

    LIGHT_TIMEOUT = 10
    DEFAULT_CONFIG_PATH = "config/lights.conf"

    def __init__(self):
        pass

    async def set_lights(self, states):
        async def set_light(state):
            light = self.find(state["id"])
            if "color_temp" in state:
                await self.set_temperature(light, state["color_temp"])
            if "dimmer" in state:
                await self.set_brightness(light, state["dimmer"])
            if "state" in state:
                await self.set_state(light, state["state"])
        tasks = [set_light(s) for s in states]
        await asyncio.wait(tasks, timeout=LightApi.LIGHT_TIMEOUT)

    async def set_brightness(self, light, level):
        command = light.light_control.set_dimmer(level)
        await self.api(command)

    async def set_temperature(self, light, mired=None):
        min_mired = light.light_control.min_mireds
        max_mired = light.light_control.max_mireds
        if mired is None:
            mired = max_mired
        if min_mired > mired:
            mired = min_mired
        if max_mired < mired:
            mired = max_mired
        command = light.light_control.set_color_temp(mired)
        await self.api(command)

    async def set_state(self, light, state):
        command = light.light_control.set_state(state)
        await self.api(command)

    def get_lights(self):
        def light_stats(light):
            return {
                "name": light.name,
                "id": light.id,
                "color_temp": light.light_control.lights[0].color_temp,
                "dimmer": light.light_control.lights[0].dimmer,
                "state": light.light_control.lights[0].state,
                "can_set_color": light.light_control.can_set_color,
                "can_set_dimmer": light.light_control.can_set_dimmer,
                "can_set_temp": light.light_control.can_set_temp,
                "can_set_xy": light.light_control.can_set_xy,
                "min_mireds": light.light_control.min_mireds,
                "min_hue": light.light_control.min_hue,
                "min_saturation": light.light_control.min_saturation,
                "max_mireds": light.light_control.max_mireds,
                "max_hue": light.light_control.max_hue,
                "max_saturation": light.light_control.max_saturation,
            }
        return [light_stats(l) for l in self.lights]

    def get_config(self, config_path=None):
        config = None
        if config_path is None:
            config_path = LightApi.DEFAULT_CONFIG_PATH
        if os.path.isfile(config_path):
            with open(config_path) as f:
                config = json.load(f)
        return config

    def find(self, id):
        for light in self.lights:
            if light.id == id:
                return light
        return None

    async def create_api_factory(self, config_path):
        config = self.get_config(config_path)
        if config is None:
            assert "GATEWAY_IP" in os.environ and "GATEWAY_KEY" in os.environ, "Gateway IP or key missing"
            host = os.environ["GATEWAY_IP"]
            key = os.environ["GATEWAY_KEY"]
            identity = uuid.uuid4().hex
            api_factory = APIFactory(host=host, psk_id=identity)
            psk = await api_factory.generate_psk(key)
            config = {
                "host": host,
                "psk_id": identity,
                "psk": psk,
            }
            self.save_config(config, config_path)
        else:
            api_factory = APIFactory(host=config["host"], psk_id=config["psk_id"], psk=config["psk"])
        return api_factory

    def save_config(self, config, config_path=None):
        if config_path is None:
            config_path = LightApi.DEFAULT_CONFIG_PATH
        with open(config_path, "w") as f:
            json.dump(config, f)

    async def _async_init(self, config_path):
        self.api_factory = await self.create_api_factory(config_path)
        self.api = self.api_factory.request
        self.gateway = Gateway()
        self.devices_command = self.gateway.get_devices()
        self.devices_commands = await self.api(self.devices_command)
        self.devices = await self.api(self.devices_commands)
        self.lights = [dev for dev in self.devices if dev.has_light_control]
