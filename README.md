# sensemore-python-mqtt-client
sensemore-python-mqtt-client

Simple example project for integrating Senseways to custom MQTT broker.
All test have done with Ubuntu 18.04 and Mosquitto as a Broker service.

Details documentation can be found at [code.sensemore.io](https://code.sensemore.io/#/mqtt_integration)

## Prerequests

A MQTT Broker should be configured to with TLS1.2 security
Server and Client certificates should be generated from same CA properly(commonname field should be the domain name of broker server)

## dependencies
- pahomqtt
- numpy
- matplotlib
