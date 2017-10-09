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

def calcul_peigne(son, fe, pas_fin=0.5, bpm_debut=120, bpm_fin=130, pas_grossier=2):
    #Initialisation du calcul    
    pas = pas_grossier 
    trouve_grossier = 0
    trouve_bpm = 0
    
    #longueur du fichier son
    longueur = len(son)
    
    while (trouve_bpm==0):
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
        if trouve_grossier == 0:
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
            plage_bpm_fin = np.linspace(bpm_fin_debut , bpm_fin_fin,int(2*pas_grossier/pas_fin))
            energie_fin = np.zeros(int(2*pas_grossier/pas_fin))
            for i in range(int(2*pas_grossier/pas_fin)):
                energie_fin[i] = sum(abs((np.fft.fft(son)*np.fft.fft(peigne(60/(bpm_fin_debut+i*0.05),longueur, longueur/fe) ))**2))
            energie= np.append(energie_grossier_debut , energie_fin )
            energie=np.append(energie, energie_grossier_fin)
            
            plage_bpm  = np.append(bpm_grossier_debut, plage_bpm_fin)
            plage_bpm = np.append(plage_bpm, bpm_grossier_fin)
            
    plt.plot(plage_bpm, energie)
   # plt.xlabel('BPM du peigne de Dirac')
   # plt.ylabel('Energie de la corrélation du morceau avec le peigne')
    #bpm retient la valeur qui nous intéresse.
    
    def DetecterPlusPetitsecarts(bpm, DateNotes):  ## DateNotes provient de la partie traitement, ici une liste de début et fin de notes. 
        mesure=4*60/bpm        ## On se donne une mesure à modifier certainement.
        indice_DateNotes=0       ## Cet indice détermine quelle note courrante est parcourue dans DateNotes
        NombreNotes=len(DateNotes)     
        Grillage=Duree/mesure           ##On obtient le nombre de mesures, incidemment le nombre d'écarts minimaux détecter.
        PlusPetitsEcarts= np.zeros(Grillage)    ##On initialise le tableau des plus petits écarts
        NombreMesuresParcourues=0
        PlusPetitEcart=500
        while ((NombreMesuresParcourues<Grillage)&&(indice_DateNotes<NombreNotes)):
            while (DateNotes[indice_DateNotes]<(NombreMesuresParcourus+1)*Grillage):
                if (DateNotes[indice_DateNotes+1]-DateNotes[indice_DateNotes]<PlusPetitEcart):
                    PlusPetitEcart=DateNotes[indice_DateNotes+1]-DateNotes[indice_DateNotes]
                Indice_DateNotes+=1
            PlusPetitsEcarts[NombreMesuresParcourues]=mesure/PlusPetitEcart   ##Renvoie donc pour la mesure courante la plus petite subdivision à considérer
            PlusPetitEcart=500
            NombreMesuresParcourues+=1
        return (PlusPetitsEcarts);
        
    
            
            
        
    
        
        
        
        