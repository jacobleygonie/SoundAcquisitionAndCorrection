import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 4
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()

print ("*")
print("* replaying")

stream=p.open(format=FORMAT,channels=CHANNELS,rate=RATE,output=1)
B=frames[0]
for i in range(1,len(frames)):
    B+=frames[i]
stream.write(B)

print("* done replaying")
stream.close()
p.terminate()

#__________________________________

#Sound
L=[]
for i in range(0,int(len(B)/2)):
    number = (B[2*i+1]<<8 )+ B[2*i]
    if (number<32768):
        L+=[number]
    else:
        L+=[number-65536]

Y=np.zeros(len(L))
for i in range(0,len(Y)):
    Y[i]=L[i]/32768
X=np.arange(0,len(Y)/44100,1/44100)

plt.plot(X,Y)

#__________________________________

#Envelope
A=np.zeros(len(X))

for k in range(70,len(Y)):
    A[k]=max(A[k-1]*np.exp(-4*np.pi/44100),abs(Y[k])/2)
plt.plot(X,A)

#__________________________________

#Event detection
D=np.zeros(len(Y))
for i in range(1,len(Y)):
    D[i]=(A[i]-A[i-1])*50

plt.plot(X,D)

plt.show()