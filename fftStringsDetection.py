import aubio
import pyaudio

import time
import struct

import math
import numpy as np
from scipy.fftpack import fft
from scipy.signal import find_peaks

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def getMIDINote(freq):
    if(freq < 8):
        return -1

    return 12 * math.log2(freq / 440) + 69


def getClosestNote(note):
    NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    if (note <= -1):
        return "invalid"
    return NOTES[int(round(note)) % 12] + str(int(note // 12 - 1))

# called on button press
# replaces the current fft date of the detected note with what is currently buffered
def tuneDetectorCallback():
    string_ffts[:, noteMap[note]-1] = ydata[50:1500]
    return


def getFFTMatrix(files):
    string_ffts = np.empty([0, 1450])
    for i in files:
        data = np.load("recording_data/"+i+"_data.npy")

        # multiply amplitude by frequency because high frequencies have low amplitudes
        data = np.array([data[j]*(j + 50) for j in range(1450)])
        string_ffts = np.append(string_ffts, [data], axis=0)

    string_ffts = string_ffts.transpose()
    return string_ffts

# draw figures and update window
def updateGraphics():
    fig.canvas.draw()
    fig.canvas.flush_events()
    root.update_idletasks()
    root.update()


def displayPitchText(pitch, note):
    pitchText.set_position((pitch, 15))
    pitchText.set_text(note)
    pitchLine.set_xdata(pitch)


noteMap = {
    "E4": 6,
    "B3": 5,
    "G3": 4,
    "D3": 3,
    "A2": 2,
    "E2": 1
}
note = "E2"  # default note

# read fft data of prerecorded strings and append to matrix for least squares note detection
FILES = ["1-E4", "2-B3", "3-G3", "4-D3", "5-A2", "6-E2"]
string_ffts = getFFTMatrix(FILES)

# constants for pyaudio
WIDTH = 2
CHANNELS = 1
RATE = 44100
FORMAT = pyaudio.paFloat32
CHUNK = 1024 * 8

# set up pyaudio for real time audio input
p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# set up aubio for pitch detection
pDetection = aubio.pitch("default", CHUNK * 2, CHUNK, 44100)
pDetection.set_unit("Hz")

# set up tkinter
root = tk.Tk()
root.title("Note Detection")
B = tk.Button(root, text="Tune to String", command=tuneDetectorCallback)
B.pack()

# set up pyplot
fig, (ax, ax2, ax3) = plt.subplots(3, constrained_layout=True)
chart_type = FigureCanvasTkAgg(fig, root)
chart_type.get_tk_widget().pack()

x = np.arange(0, 2 * CHUNK, 2)       # samples (waveform)
xf = np.linspace(0, RATE, CHUNK)     # frequencies (spectrum)

line, = ax.plot(x, np.random.randn(CHUNK), '-')
line_fft, = ax2.semilogx(xf, np.random.randn(CHUNK), '-')
line_string, = ax3.plot([0.0, 1.0, 0, 0, 0, 0])
ydata = np.random.randn(CHUNK)

ax.set_ylim(-1, 1)
ax2.set_xlim(20, RATE/2)
ax2.set_ylim(0, 16)
pitchText = ax2.text(0, 15, "hi")
pitchLine = ax2.axvline(x=0, linestyle='dashed', alpha=0.5)

ax.set_title('Level')
ax2.set_title('Frequency')
ax3.set_title('Strings')
fig.canvas.set_window_title('Waveform Visualiser')


stream.start_stream()  # start pyaudio
count = 0
while stream.is_active():
    count += 1
    data = stream.read(CHUNK, exception_on_overflow=False)

    # set fig 1 values to raw audio data
    data_int = np.frombuffer(data, dtype=aubio.float_type)
    line.set_ydata(data_int)

    # set fig 2 values to fourier transform of audio
    y_fft = fft(data_int)
    ydata = np.abs(y_fft[0:CHUNK]) / CHUNK
    ydata = np.array([ydata[i]*i for i in range(CHUNK)])
    line_fft.set_ydata(ydata * 10)

    # find peaks in the fft (kind of unreliable to find component frequencies)
    m = max(ydata[50:3000])
    if m > 0.2:
        peaks = find_peaks(ydata[50:1500], height=0.3 * m)
        #print(m, peaks[0]+50)

    # get note using aubio pitch. only reliable if a single note is played
    # normally, the root note of a chord is detected
    pitch = pDetection(data_int)[0]
    midi = getMIDINote(pitch)
    note = getClosestNote(midi)
    print(str(pitch) + '\t' + str(midi) + '\t' + note)
    displayPitchText(pitch, note)

    # detect what notes/strings are being played based on the least squares approximation of ffts
    # this doesn't work as well as I would like it to but I dont have a better method of approximation
    weights = np.linalg.lstsq(string_ffts, ydata[50:1500], rcond=None)[0]
    line_string.set_ydata(weights)

    updateGraphics()


stream.stop_stream()
stream.close()
p.terminate()
