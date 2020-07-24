import sys

import wave
import aubio

import struct
import numpy as np
from numpy import save
from scipy.fftpack import fft

if len(sys.argv) < 2:
    print("Saves a numpy array of the fft of a wav file. Proper usage: python3 saveFFT.py <filename.wav>")
    sys.exit(-1)

filename = sys.argv[1]
wf = wave.open(filename, 'rb')

CHUNK = 1024 * 8
data = wf.readframes(CHUNK)

freqArray = np.empty([0, 1450])

# takes the average fft of the first nth chunks of the input file (or up untill theres no data left)
i = 0
while data and i < 1:

    # get raw data from wav file
    data_flt = struct.unpack("<" + str(CHUNK) + "h", data)
    y_fft = np.abs(fft(data_flt))[50:1500] / CHUNK

    freqArray = np.append(freqArray, [y_fft], axis=0)

    i += 1
    data = wf.readframes(CHUNK)

freqAvg = np.average(freqArray, axis=0)

# safe fft to file
if "/" in filename:
    filename = filename.split('/')[1]

filename = "recording_data/" + filename.split('.')[0] + "_data.npy"
save(filename, freqAvg)
print("saved " + filename)
