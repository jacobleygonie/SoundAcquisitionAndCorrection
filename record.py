import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate
import scipy.fftpack
 
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1.5
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
X=np.arange(0,len(Y)/RATE,1/RATE)
 
#plt.plot(X,Y)
 
#__________________________________
 
#Envelope
A=np.zeros(len(X))
 
for k in range(3000,len(Y)):
    A[k]=max(A[k-1]*np.exp(-10*np.pi/RATE),abs(Y[k]))
 
Yn=np.zeros(len(A))
Yf=np.zeros(len(A))
 
#1er lissage large
for i in range(0,1500):
    Yn[750]+=A[i]
Yn[750]/=1501
for k in range(751,len(A)-750):
    Yn[k]=Yn[k-1]*1501-A[k-751]+A[k+750]
    Yn[k]/=1501
 
#2e lissage plus précis
p=600
 
for i in range(750,750+2*p):
    Yf[750+p]+=Yn[i]
Yf[750+p]/=2*p+1
for k in range(751+p,len(A)-750-p):
    Yf[k]=Yf[k-1]*(2*p+1)-Yn[k-p-1]+Yn[k+p]
    Yf[k]/=2*p+1
 
 
#plt.plot(X,Yf)
 
#__________________________________
 
#Event detection
 
Dn=np.zeros(len(Yf))
Df=np.zeros(len(Yf))
D=np.zeros(len(Yf))
B=np.zeros(len(Yf))
for i in range(1,len(Yf)-300):
    Dn[i]=(Yf[i]-Yf[i-1])*50
 
Dn*=100
 
for i in range(0,2*p):
    D[p]+=Dn[i]
D[p]/=2*p+1
for k in range(p+1,len(D)-p):
    D[k]=D[k-1]*(2*p+1)-Dn[k-p-1]+Dn[k+p]
    D[k]/=2*p+1
 
for i in range(0,2*p):
    Df[p]+=D[i]
Df[p]/=2*p+1
for k in range(p+1,len(D)-p):
    Df[k]=Df[k-1]*(2*p+1)-D[k-p-1]+D[k+p]
    Df[k]/=2*p+1
 
#plt.plot(X,Df)
 
 
#__________________________________
 
#Séparation:
 
for i in range(0,len(D)):
    D[i]=D[i]*D[i]*D[i]
 
max=max(D)
min=min(D)
d=0
s=""
 
 
for i in range(0,len(D)):
    if D[i]>0.6*max and d==0:
        d=1
        L=[]
        s+="Note repérée, de "+str(i/RATE)+"s à "
    if  d==1:
        if D[i]<0.4*min:
            d=0
            s+=str(i/RATE)+"s"
            print(s)
            s=""
        else:
            L+=[X[i]]
 
 
 
#___________________________________
 
# FFT
 
 
 
T = 1.0 / RATE
x=np.arange(0,len(Lf),T)
N = len(Lf)
y=np.asarray(Lf)
 
yf = scipy.fftpack.fft(y)
xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
 
fig, ax = plt.subplots()
ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
 
plt.show()