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


def error(topic, msg):
    print(topic, msg)


client = SensemoreMQTTClient(gateway)

client.on_measurement_done = measurement_done
client.on_error = error


client.connect(host=host, port=port, ca_cert=ca_cert,
               certfile=certfile, keyfile=keyfile)


client.measure(5000, ACCELEROMETER_RANGE.RANGE_16G,
               SAMPLING_RATE.HZ_800, "CA:B8:31:00:00:1B")


client.loop_forever()
