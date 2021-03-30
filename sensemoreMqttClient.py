
import paho.mqtt.client as mqtt
import ssl
import json
import time


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
        self.metadata = None
        self.chunks = {}
        self.accelerometerRangeIndex = accelerometerRangeIndex
        self.accelerometerRange = self.rangeIndexToRange(
            accelerometerRangeIndex)
        self.samplingRateIndex = samplingRateIndex
        self.sampleSize = sampleSize
        self.id = id
        self.time = None
        self.rangeCoefficient = self.rangeIndexToCoefficient(
            accelerometerRangeIndex)

    def setMetadata(self, metadata):
        self.metadata = metadata

    def setTelemetries(self, telemetries):
        self.telemetries = telemetries

    def on_measurement_done():
        pass

    def rangeIndexToRange(self, rangeIndex):
        return 2**rangeIndex

    def rangeIndexToCoefficient(self, rangeIndex):
        range = 2**rangeIndex
        return (range*2)/(2 ** 16)

    def addChunk(self, chunkNo, chunk):
        values = []
        for i in range(0, len(chunk), 2):
            int16_bytes = bytes(chunk[i:i+2])  # each 2 byte holds int16
            value = int.from_bytes(
                int16_bytes, byteorder='little', signed=True)
            value = value * self.rangeCoefficient
            values.append(value)
        self.chunks[chunkNo] = values

    def calculate_chunks(self):
        keys = self.chunks.keys()
        keys_sorted = sorted(keys, reverse=True)
        ordered = []

        for key in keys_sorted:
            ordered.extend(self.chunks[key])

        for i in range(0, len(ordered), 3):
            self.accelerometer_X.append(ordered[i])
            self.accelerometer_Y.append(ordered[i+1])
            self.accelerometer_Z.append(ordered[i+2])


class SensemoreMQTTClient:

    def __init__(self, gateway):
        self.gateway = gateway
        self.scanReslts = {}
        self.measurements = {}

    def on_measurement_done(self, measurement):
        pass

    def loop_forever(self):
        self.client.loop_forever()

    def connect(self, host, port, ca_cert, certfile, keyfile):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.tls_set(ca_certs=ca_cert, certfile=certfile, keyfile=keyfile,
                            cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.tls_insecure_set(True)
        self.client.connect(host, port, 60)

    # The callback for when the client receives a CONNACK response from the server.
    def ota_device(self, url, device):
        topic = "prod/gateway/{0}/device/{1}/ota".format(self.gateway, device)
        self.client.publish(topic, url)

    def on_ota_device_accepted(self, device):
        pass

    def on_ota_device_rejected(self, device, message):
        pass

    def on_ota_device_done(self, device, message):
        pass

    def on_measurement_accepted(self, measurementId, device):
        pass

    def on_measurement_rejected(self, measurementId, device, msg):
        pass

    def measure(self, sampleSize, accelerometerRange, samplingRate, device):
        measurement = Measurement(sampleSize, accelerometerRange, samplingRate)
        self.measurements[measurement.id] = measurement
        topic = "prod/gateway/{0}/device/{1}/measure/{2}".format(
            self.gateway, device, measurement.id)
        payload = "{0},{1},{2}".format(
            accelerometerRange, samplingRate, sampleSize)
        self.client.publish(topic, payload)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected, RC:", rc)
        self.client.subscribe("prod/gateway/"+self.gateway+"/#")
        self.client.subscribe('prod/device/#')

    def on_message(self, client, userdata, msg):
        print(msg.topic)
        splitted = msg.topic.split('/')
        # "prod/gateway/<gwmac>/scanDevice"
        if(len(splitted) == 4
           and splitted[0] == 'prod'
           and splitted[1] == 'gateway'
           and splitted[2] == self.gateway
           and splitted[3] == 'scanDevice'):
            message = str(msg.payload, 'utf-8')
            self.scanReslts = json.loads(message)
            print(self.scanReslts)
        # "prod/gateway/<gwmac>/device/<device-mac>/measure/<measurementId>/chunk/<chunkIndex>"
        elif (len(splitted) == 7 
        and splitted[0] == 'prod' and splitted[1] == 'device' and splitted[3] == 'measure' and splitted[4] in self.measurements.keys() and splitted[5] == 'chunk'):
            measurement = self.measurements[splitted[4]]
            measurement.addChunk(splitted[6], msg.payload)
        # "prod/gateway/<gwmac>/device/<device-mac>/measure/<measurementId>/done"
        elif (len(splitted) == 8 and splitted[0] == 'prod' and splitted[1] == 'gateway' and splitted[2] == self.gateway and splitted[3] == 'device' and splitted[5] == 'measure' and splitted[6] in self.measurements.keys() and splitted[7] == 'done'):
            measurement = self.measurements[splitted[6]]
            measurement.calculate_chunks()
            doneJson = json.loads(str(msg.payload, 'utf-8'))
            measurement.setMetadata(doneJson)
            self.on_measurement_done(measurement)
        # "prod/gateway/<gwmac>/device/<device-mac>/measure/<measurementId>/accepted"
        elif (len(splitted) == 8 and splitted[0] == 'prod' and splitted[1] == 'gateway' and splitted[2] == self.gateway and splitted[3] == 'device' and splitted[5] == 'measure' and splitted[6] in self.measurements.keys() and splitted[7] == 'accepted'):
            #                            measurementId,devicemac
            self.on_measurement_accepted(splitted[6], splitted[3])
        # "prod/gateway/<gwmac>/device/<device-mac>/measure/<measurementId>/rejected"
        elif (len(splitted) == 8 and splitted[0] == 'prod' and splitted[1] == 'gateway' and splitted[2] == self.gateway and splitted[3] == 'device' and splitted[5] == 'measure' and splitted[6] in self.measurements.keys() and splitted[7] == 'rejected'):
            self.on_measurement_rejected(
                splitted[6], splitted[4], str(msg.payload, 'utf-8'))
        # "prod/gateway/<gwmac>/device/<device-mac>/ota/accepted"
        elif (len(splitted) == 7 and splitted[0] == 'prod' and splitted[1] == 'gateway' and splitted[2] == self.gateway and splitted[3] == 'device' and splitted[5] == 'ota' and splitted[6] == 'accepted'):
            self.on_ota_device_accepted(splitted[4])
        # "prod/gateway/<gwmac>/device/<device-mac>/ota/rejected"
        elif (len(splitted) == 7 and splitted[0] == 'prod' and splitted[1] == 'gateway' and splitted[2] == self.gateway and splitted[3] == 'device' and splitted[5] == 'ota' and splitted[6] == 'rejected'):
            self.on_ota_device_rejected(splitted[4], str(msg.payload, 'utf-8'))
        # "prod/gateway/<gwmac>/device/<device-mac>/ota/done"
        elif (len(splitted) == 7 and splitted[0] == 'prod' and splitted[1] == 'gateway' and splitted[2] == self.gateway and splitted[3] == 'device' and splitted[5] == 'ota' and splitted[6] == 'done'):
            self.on_ota_device_done(splitted[4], str(msg.payload, 'utf-8'))
