import numpy as np
import matplotlib.pyplot as plt
figureIndex = 1


def plotTime(measurement):
    global figureIndex
    time = measurement.sampleSize / \
        measurement.metadata["STAT"]["CALIBRATED_SAMPLINGRATE"]
    timeDomain = np.linspace(0, time, measurement.sampleSize)

    x = np.array(measurement.accelerometer_X)
    x = x - np.mean(x)  # DC offset

    figureIndex = figureIndex+1
    plt.figure(figureIndex)
    plt.plot(timeDomain, x)
    plt.title("accelerometer_x")
    plt.ylabel("Amplitude")
    plt.xlabel("Time")

    y = np.array(measurement.accelerometer_Y)
    y = y - np.mean(y)  # DC offset
    figureIndex = figureIndex+1
    plt.figure(figureIndex)
    plt.plot(timeDomain, y)
    plt.title("accelerometer_y")
    plt.ylabel("Amplitude")
    plt.xlabel("Time")

    z = np.array(measurement.accelerometer_Z)
    z = z - np.mean(z)  # DC offset
    figureIndex = figureIndex+1
    plt.figure(figureIndex)
    plt.plot(timeDomain, z)
    plt.title("accelerometer_z")
    plt.ylabel("Amplitude")
    plt.xlabel("Time")


def plotFFT(measurement):
    global figureIndex
    samplingRate = measurement.metadata["STAT"]["CALIBRATED_SAMPLINGRATE"]
    sampleSize = measurement.sampleSize

    nyquist_frequency_range = int(samplingRate/2)
    nyquist_sampleRange = int(sampleSize/2)
    frequency_domain = np.linspace(
        0, nyquist_frequency_range, nyquist_sampleRange)

    x = np.array(measurement.accelerometer_X)
    x = x - np.mean(x)  # DC offset
    fftX = np.fft.rfft(x)
    fftx_abs = np.abs(fftX)[1:]

    y = np.array(measurement.accelerometer_Y)
    y = y - np.mean(y)  # DC offset
    fftY = np.fft.rfft(y)
    ffty_abs = np.abs(fftY)[1:]

    z = np.array(measurement.accelerometer_Z)
    z = z - np.mean(z)  # DC offset
    fftZ = np.fft.rfft(z)
    fftz_abs = np.abs(fftZ)[1:]

    figureIndex = figureIndex+1
    plt.figure(figureIndex)
    plt.plot(frequency_domain, fftx_abs)
    plt.title("accelerometer_x")
    plt.ylabel("Amplitude")
    plt.xlabel("Frequency")

    figureIndex = figureIndex+1
    plt.figure(figureIndex)
    plt.plot(frequency_domain, ffty_abs)
    plt.title("accelerometer_y")
    plt.ylabel("Amplitude")
    plt.xlabel("Frequency")

    figureIndex = figureIndex+1
    plt.figure(figureIndex)
    plt.plot(frequency_domain, fftz_abs)
    plt.title("accelerometer_z")
    plt.ylabel("Amplitude")
    plt.xlabel("Frequency")


def DCOffset(signal):
    signal_np = np.array(signal)
    mean = signal_np.mean()
    return np.subtract(signal_np, mean)

def GRMS(signal):
    signal_np = DCOffset(signal)
    result = np.sqrt((((signal_np)**2)/len(signal)).sum())
    return float(result)


def plotMeasurement(measurement):
    plotTime(measurement)
    plotFFT(measurement)
    
    print("GRMS X", GRMS(measurement.accelerometer_X))
    print("GRMS Y", GRMS(measurement.accelerometer_Y))
    print("GRMS Z", GRMS(measurement.accelerometer_Z))
    plt.show()
