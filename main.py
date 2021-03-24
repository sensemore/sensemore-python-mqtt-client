from sensemoreMqttClient import SensemoreMQTTClient, ACCELEROMETER_RANGE,SAMPLING_RATE


def measurement_done():
    pass


gateways = ["CA:B8:28:00:00:1B"]
devices = ["CA:B8:31:00:00:1B"]
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
ca_cert = "certs/ca.crt"
certfile = "certs/client.crt"
keyfile = "certs/client.key"
host = "192.168.43.104"
port = 8883

#
def measurement_done(measurement):
    print(measurement)
def error(er):
    print(er)


client = SensemoreMQTTClient(gateways, devices)

client.on_measurement_done = measurement_done
client.on_error = error

client.connect(host=host, port=port, ca_cert=ca_cert,
               certfile=certfile, keyfile=keyfile)



client.measure(10000,ACCELEROMETER_RANGE.RANGE_2G,SAMPLING_RATE.HZ_12800,"CA:B8:31:00:00:1B")

client.loop_forever()
