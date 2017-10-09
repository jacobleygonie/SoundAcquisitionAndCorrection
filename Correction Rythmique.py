# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 19:39:03 2017

@author: Hatim
"""

import pyaudio
import wave
import sys
import numpy as np
import matplotlib.pyplot as plt

#Crée un peigne de Dirac d"amplitude 1 de période T

def peigne(T, N, Duree):
    # N = nbre d'échantillons
    # Duree = Durée du signal -> Fe = N/Duree
    t=np.linspace(0,Duree,N) # liste de la variable temps
    Dt=Duree/N # Pas temporel
    
    x=[0 for n in t]
    for i in range(int(Duree/T)):
        x[int(i*T/Dt)]=10
    return x

def calcul_peigne(son, fe, pas_fin=0.2, bpm_debut=10, bpm_fin=20, pas_grossier=1):
    #Initialisation du calcul    
    pas = pas_grossier 
    trouve_grossier = 0
    trouve_bpm = 0
    
    #longueur du fichier son
    longueur = len(son)
    
    while (trouve_bpm==0):
        if trouve_grossier == 0:
            #plage de BPM a parcourir
            plage_bpm= np.linspace(bpm_debut,bpm_fin, bpm_fin-bpm_debut +1 )
       
            energie = np.zeros(bpm_fin - bpm_debut+1)
        
            print("Parcours de la plage ", bpm_debut, "; pas = ",  pas, ";", bpm_fin)        
        
            #Pour chacun des BPM
            for i in range(int(bpm_fin - bpm_debut)):
            #generation d'un peigne de dirac au bon bpm
                Peigne = peigne(60/(bpm_debut+i),longueur, longueur/fe)
            
            
                energie[i]=  sum(abs((np.fft.fft(son)*np.fft.fft(Peigne))**2))
            
            #Récuperation du bpm max de ce passage 
            energie_max, indice_max = max(energie), np.argmax(energie) 
            bpm= plage_bpm[indice_max]
            print(bpm)
            plt.plot(plage_bpm,energie)
        
            #On vient de faire le tour avec un pas grossier
            trouve_grossier = 1
            #La prochaine fois on fera un refinement
            bpm_fin_debut = bpm - pas_grossier+pas_fin
            bpm_fin_fin= bpm + pas_grossier-pas_fin
            #On sauvegarde les résultats pour affichage final
            energie_grossier_debut = energie[0 : indice_max]
            energie_grossier_fin = energie[indice_max +1 :]
            bpm_grossier_debut = plage_bpm[0:indice_max]
            bpm_grossier_fin = plage_bpm[indice_max+1:]
            
        else:
            #On vient de faire le deuxième passage (fin)
            trouve_bpm=1
            plage_bpm_fin = np.linspace(bpm_fin_debut , bpm_fin_fin,int(2*pas_grossier/pas_fin)-1)
            energie_fin = np.zeros(int(2*pas_grossier/pas_fin)-1)
            for i in range(int(2*pas_grossier/pas_fin)-1):
                energie_fin[i] = sum(abs((np.fft.fft(son)*np.fft.fft(peigne(60/(bpm_fin_debut+i*pas_fin),longueur, longueur/fe) ))**2))
            energie= np.append(energie_grossier_debut , energie_fin )
            energie=np.append(energie, energie_grossier_fin)
            
            plage_bpm  = np.append(bpm_grossier_debut, plage_bpm_fin)
            plage_bpm = np.append(plage_bpm, bpm_grossier_fin)
            indice_max_fin =  np.argmax(energie_fin) 
            bpm=plage_bpm_fin[indice_max_fin]
            print(bpm)
    plt.plot(plage_bpm_fin, energie_fin)
   # plt.xlabel('BPM du peigne de Dirac')
   # plt.ylabel('Energie de la corrélation du morceau avec le peigne')
   

        
        
        
        
        