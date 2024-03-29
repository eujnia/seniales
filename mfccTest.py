import numpy as np
import librosa as lib
import math as math
import scipy
import pathlib
import pyaudio
import wave
from dtw import dtw
import numpy as np
from numpy.linalg import norm
from numpy import fft
#import fftpack
from scipy.io import wavfile
from matplotlib import pyplot as plt 

def fmel(fhz):
    return 1000*np.log2(1+(fhz/1000))

def fmelinv(mel):
    return 1000*(2**(mel/1000)-1)

def makeFiltro(m, f,ksamples):
    y = np.zeros((ksamples))
    for k in range(ksamples):
        if(k<f[m-1]):
            y[k]=0
        elif(f[m-1]<=k and k<=f[m]):
            y[k]= (k-f[m-1])/(f[m]-f[m-1])
        elif (f[m]<=k and k<=f[m+1]):
            y[k]=(f[m+1]-k)/(f[m+1]-f[m])
        else:
            y[k]=0
    return y

#ARCHIVO PARA TESTEO DE LA FUNCION MFCC

def mfcc(signal, fm, windowLenght=25, windowStep=20):

    #VENTANEO--------------------------------------------------------
    samplesLength = math.floor((windowLenght*0.001)*fm)
    print("SamplesLen: ", samplesLength)

    samplesStep= math.floor((windowStep*0.001)*fm)
    print("SamplesStep: ", samplesStep)

    cantVentanas = math.ceil(signal.size/samplesStep)
    print("CantVentanas: ", cantVentanas)

    framedSignal = []

    for i in range(0, cantVentanas):

        #Tomo una porcion de la señal de longitud samplesLength
        frame = signal[i*samplesStep:i*samplesStep+samplesLength]
    
        #Si estamos en las ultimas ventana verifico que la ventana sea del tamaño samplesLength
        #De no ser asi agrego ceros al final
        if frame.shape[0] != samplesLength:
            #print("Ventana incompleta")
            frame = np.pad(frame,(0, samplesLength - frame.shape[0]), 'constant', constant_values=0)
            #print(frame)

        #Aplico Hamming a la ventana
        frame = np.hamming(samplesLength)*frame

        #Agrego ventana a la lista de ventanas
        framedSignal.append(frame)
            
    framedSignal = np.array(framedSignal)
    #print("framed signal shape: ", framedSignal.shape)

    fftSignal = []
    #CALCULO ENERGIA DE LA FFT (a cada ventana)
    for i in range(framedSignal.shape[0]):

        aux = framedSignal[i, :]
        auxfft = fft.fft(aux)
        espectro = (1/samplesLength)*(abs(auxfft)**2)

        #Debo quedarme con la primera mitad del espectrograma?
    
        fftSignal.append(espectro[: int(np.ceil(samplesLength/2))])

    #print("fftSignal Size ", len(fftSignal))
    #print("ventana fft ", fftSignal[0].shape[0])

    # BANCO DE FILTROS DE MEL
    # planteamos un minimo y un maximo en frecuencias, pasamos a mels, hacemos un equi espaciado entre esos valores en mel
    # convertimos los valores equiespaciados en Hz
    cantCoef = 26
    nfft = fftSignal[0].shape[0] #la cantidad de samples de media ventana del espectro dde fourier
    min = 300 #hz
    max = fm/2 #hz

    #pasamos a mels los limites

    minMel = fmel(min)
    maxMel = fmel(max)

    melAxis = np.linspace(minMel, maxMel, cantCoef+2)
    herzAxis = np.array([ fmelinv(melAxis[i]) for i in range(melAxis.shape[0])])

    samplesAxis = np.array([np.floor((nfft)*herzAxis[i]/(fm/2)) for i in range(herzAxis.shape[0])])

    filtros = np.zeros((cantCoef, nfft))
    for m in range(cantCoef):
        filtros[m]=makeFiltro(m+1,samplesAxis,nfft)
        #plt.plot(filtros[m,:])

    #plt.show()

    melArray=[]
    for i in range(nfft):
        aux=np.dot(fftSignal[0],filtros.T)
        melArray.append(aux)
    #print("shape de la matriz", melArray.shape)
    melArray = np.array(melArray)
    return melArray.T


if(__name__ == "__main__"):

    signal, fm = lib.load('dale_11k/dale_1.wav')
    melss = mfcc(signal, fm, 25, 10)
    print("mels: ",melss.shape)
    
    pass



