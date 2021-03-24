
import paho.mqtt.client as mqtt
import time
import ssl
import json


class ACCELEROMETER_RANGE:
    RANGE_2G = 1
    RANGE_4G = 2
    RANGE_8G = 3
    RANGE_16G = 4


class SAMPLING_RATE:
    HZ_800 = 5
    HZ_1600 = 6
    HZ_3200 = 7
    HZ_6400 = 8
    HZ_12800 = 9


class Measurement:

    def __init__(self,  sampleSize=1000, accelerometerRangeIndex=1, samplingRateIndex=5, id="0"*24):
        self.accelerometer_X = []
        self.accelerometer_Y = []
        self.accelerometer_Z = []
        self.calibratedSamplingRate = None
        self.chunks = []
        self.metadata = None
        self.accelerometerRangeIndex = accelerometerRangeIndex
        self.samplingRateIndex = samplingRateIndex
        self.sampleSize = sampleSize
        self.id = id
        self.rangeCoefficient = self.rangeIndexToCoefficient(
            accelerometerRangeIndex)

    def on_measurement_done():
        pass

    def rangeIndexToCoefficient(rangeIndex):
        range = 2**rangeIndex
        return (range*2)/(2 ** 16)

    def addChunk(self, chunk):

        values = []
        for i in range(0, len(chunk), 2):
            int16_bytes = bytes(chunk[i:i+2])  # each 2 byte holds int16
            value = int.from_bytes(
                int16_bytes, byteorder='little', signed=True)
            value = value * self.rangeCoefficient
            values.append(value)

        for i in range(0, len(values), 3):
            self.accelerometer_X.append(values[i])
            self.accelerometer_Y.append(values[i+1])
            self.accelerometer_Z.append(values[i+2])


class SensemoreMQTTClient:

    def __init__(self, gateway):
        self.gateway = gateway
        self.scanReslts = {}
        self.measurements = {}

    def loop_forever(self):
        self.client.loop_forever()

    def on_error(self):
        pass

    def connect(self, host, port, ca_cert, certfile, keyfile):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.tls_set(ca_certs=ca_cert, certfile=certfile,
                            keyfile=keyfile, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.tls_insecure_set(True)
        self.client.connect(host, port, 60)

    # The callback for when the client receives a CONNACK response from the server.

    def measure(self, sampleSize, accelerometerRange, samplingRate, device):
        measurement = Measurement(sampleSize, accelerometerRange, samplingRate)
        self.measurements[measurement.id] = measurement
        self.client.publish("prod/gateway/"+self.gateway+"/device/"+device+"/measure/" +
                            measurement.id, "{0},{1},{2}".format(accelerometerRange, samplingRate, sampleSize))
        pass

    def on_connect(self, client, userdata, flags, rc):
        print("Connected, RC:", rc)
        self.client.subscribe("prod/gateway/"+self.gateway+"/#")

        # client.publish(
        #     'prod/gateway/CA:B8:28:00:00:1B/device/CA:B8:31:00:00:1B/measure/098765432109876543214321', '1,5,1000')
    # The callback for when a PUBLISH message is received from the server.

    def on_message(self, client, userdata, msg):
        splitted = msg.topic.split('/')
        if(len(splitted) == 4 and splitted[0] == 'prod' and splitted[1] == 'gateway' and splitted[2] in self.gateways and splitted[3] == 'scanDevice'):
            message = str(msg.payload, 'utf-8')
            self.scanReslts = json.loads(message)
            print(self.scanReslts)
        elif (len(splitted) == 7 and splitted[0] == 'prod' and splitted[1] == 'device' and splitted[3] == 'measure' and splitted[4] in self.measurements.keys() and splitted[5] == 'chunk')
