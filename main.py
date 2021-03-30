import threading
from sensemoreMqttClient import SensemoreMQTTClient, ACCELEROMETER_RANGE, SAMPLING_RATE
import json
import os
import analyze

gateway = "CA:B8:28:00:00:1B"
ca_cert = "certs/ca.crt"
certfile = "certs/client.crt"
keyfile = "certs/client.key"
host = "192.168.43.104"
port = 8883


def measurement_accepted(measurementId, device):
    print("Measurement started {0}, device: {1}".format(measurementId, device))


def measurement_done(measurement):
    print(measurement)
    if not os.path.exists(measurement.id):
        os.makedirs(measurement.id)
    with open(measurement.id+"/accelerometer_x.csv", "w") as f:
        f.write("\n".join([str(i) for i in measurement.accelerometer_X]))
    with open(measurement.id+"/accelerometer_y.csv", "w") as f:
        f.write("\n".join([str(i) for i in measurement.accelerometer_Y]))
    with open(measurement.id+"/accelerometer_z.csv", "w") as f:
        f.write("\n".join([str(i) for i in measurement.accelerometer_Z]))

    with open(measurement.id+"/metadata.json", "w") as f:
        f.write(json.dumps(measurement.metadata))

    analyze.plotMeasurement(measurement)


def measurement_rejected(measurementId, device, message):
    print("Measurement failed {0}, device: {1}: {2}".format(
        measurementId, device, message))


def ota_device_rejected(device, message):
    print("Ota failed {0}, device: {1}".format(device, message))


def ota_device_accepted(device):
    print("Ota started {0}".format(device))


gateway = "CA:B8:28:00:00:1B"
ca_cert = "certs/ca.crt"
certfile = "certs/client.crt"
keyfile = "certs/client.key"
host = "192.168.43.104"
port = 8883
client = SensemoreMQTTClient(gateway)

device = "CA:B8:31:00:00:1B"


client.on_measurement_accepted = measurement_accepted
client.on_measurement_done = measurement_done
client.on_measurement_rejected = measurement_rejected

client.on_ota_device_rejected = ota_device_rejected
client.on_ota_device_accepted = ota_device_accepted


client.connect(host=host, port=port, ca_cert=ca_cert,
               certfile=certfile, keyfile=keyfile)


# client.measure(1600, ACCELEROMETER_RANGE.RANGE_16G,
#                SAMPLING_RATE.HZ_800, device)

url = "http://192.168.43.104:5501/Wiredv1_0_10.bin"
client.ota_device(url, device)
client.loop_forever()
