# ikea-tradfri-server
Simple REST API for controlling IKEA Trådfri lights.

### Building and running the server

Build the Docker image with:

```
docker build  -t lights-server .
```

Run the server with:

```
docker run -d --restart=always -p 5000:5000 -e GATEWAY_IP=<your_gateway_ip> -e GATEWAY_KEY=<your_gateway_key> lights-server
```

### Usage

Status of the lights can be seen with

```
curl -H 'Content-Type: application/json' http://localhost:5000/lights
```

which returns a list of JSON objects like

```
{
    "can_set_color": null,
    "can_set_dimmer": true,
    "can_set_temp": true,
    "can_set_xy": true,
    "color_temp": 450,
    "dimmer": 175,
    "id": 65537,
    "max_hue": 65535,
    "max_mireds": 454,
    "max_saturation": 65279,
    "min_hue": 0,
    "min_mireds": 250,
    "min_saturation": 0,
    "name": "Living room",
    "state": true
  }
```

Lights can be adjusted by posting a list of JSON objects describing the new state of the lights.
The JSON objects must include the id of the light and new values for the settings you want to change.

Example JSON:

```
[
    {
        "color_temp": 450,
        "dimmer": 175,
        "id": 65537,
        "state": true
    },
    {
        "color_temp": 450,
        "dimmer": 175,
        "id": 65538,
        "state": true
    },
    {
        "color_temp": 450,
        "dimmer": 175,
        "id": 65539,
        "state": true
    }
]
```

which you can then use to adjust the lights by:

```
curl -H 'Content-Type: application/json' -d @lights.json http://localhost:5000/lights
```