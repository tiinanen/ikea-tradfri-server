FROM python:3

RUN apt-get update -y && \
  apt-get install -y git autoconf automake libtool && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* build/

WORKDIR /app/libcoap
RUN mkdir /app/config

RUN pip install --upgrade pip setuptools wheel cython

COPY libcoap/install-coap-client.sh install-coap-client.sh
RUN ./install-coap-client.sh

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY lights/ lights/
COPY start_server.py .

EXPOSE 5000

CMD ["python", "start_server.py"]
