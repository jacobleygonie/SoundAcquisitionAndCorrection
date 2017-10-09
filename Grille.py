# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 15:28:29 2017

@author: Hatim
"""

# -*- coding: utf-8 -*-

#import pyaudio
import wave
import sys
import numpy as np
import matplotlib.pyplot as plt

##Le problème par rapport à la partie précédente, c'est que l'on a besoin des dates précises de début et de fin des notes du signal d'entrée. 
# On a donc besoin de la partie de Lina,Thomas et Nicolas pour avoir ces informations. 
#Ce que je suppose ici c'est que l'on dispose donc d'une liste SonTraite, de même taille que la liste son précédente. 
# Tout comme dans son, les cellules de la listes SonTraite correspondent à une date discrétisée.
#Dans la case i, correspondant à t_i, je suppose qu'il y a une liste de couples. 
# Ces couples sont les (note, statut) où note est une note qui est jouée à cette instant, et statut détermine si elle naît, meurt ou vit. 
# Ainsi dans la case i, je lis toutes les notes jouées en t_i et leurs statuts.

#La partie acquisition du signal renvoie un tableau sonTraite qui est de longueur len(echantillon) et a un 0 s'il n'y a pas de notes
# et vaut la fréquence de la note s'il y en a une
    
def PlusPetitEnchainement (sonTraite,bpm,fe):  ## On veut trouver les deux notes consécutives les moins espacées en temps. On s'intéresse uniquement aux moments où naissent les notes.
    ## On initialisera le plus petit enchaînement à bpm.
    plusPetitEnchainement=60/bpm
    
    N=len(sonTraite)
    for date_note_1 in range (N):
       if ( sonTraite(date_note_1) != 0 ):
           note_1=sonTraite(date_note_1)
           continuer =True
           date_note_2=date_note_1+1
           meme_note =False
           while(continuer and (date_note_2<N)):
               if( sonTraite(date_note_2) ==0 ):
                   meme_note=True
               else:
                   if ( note_1 !=sonTraite(date_note_2)):
                       continuer=False
                       plusPetitEnchainement = min(plusPetitEnchainement, date_note_2-date_note_1)  
                   else:
                        if (meme_note):
                            continuer=False
                            plusPetitEnchainement = min(plusPetitEnchainement, date_note_2-date_note_1)  
               date_note_2+=1              
    return (plusPetitEnchainement)
        
def PasMinimal (sonTraite, bpm, fe, facteur):  ## Il faut néanmois corriger l'enchaînement ci-dessus pour que sa durée soit un diviseur de la durée de la mesure. 
##On divise l'enchaînement par un facteur pour plus de précision, à troquer contre du temps de calcul.
    plusPetitEnchainement= PlusPetitEnchainement (sonTraite,bpm,fe)
    pasMin=plusPetitEnchainement/facteur
    Mesure=60/bpm
    ratio= np.floor(Mesure/pasMin)
    pasMin=Mesure/ratio
    return (pasMin)
    
def trouverMort(sonTraite, indice_note):
    N=len(sonTraite)
    indice_mort=indice_note+1
    if(indice_mort>=N):
        return N
    note=sonTraite[indice_note]
    
    while(indice_mort<N and sonTraite[indice_mort]==note):
        indice_mort+=1
    return indice_mort-1
    
def trouverPasCourrant(sonTraite, indice_debut_pas_min, indice_note,fe,pasMin, adaptation):
    
    nb_pas = (indice_note -indice_debut_pas_min)/fe  /pasMin
    pas_courrant=1
    indice_courrant= 0
    indice_adaptation=0
    while(indice_courrant< nb_pas):
        indice_courrant+=pas_courrant
        indice_adaptation+=1
        if (indice_adaptation>=adaptation):
            pas_courrant+=1
            indice_adaptation=0
    return pas_courrant*pasMin
    
    
    
def CorrectionRythmique(sonTraite, bpm, fe, facteur, adaptation): ## On passe à la correction proprement dite. Adaptation a le sens suivant: dès qu'on croise une note, 
#on la recale, on repart de là où elle se trouve et on progresse à pasMin pendant "adaptation", puis 2*pasMin pendant "adaptation", ..., puis k*pasMin pendant "adaptation",
#jusqu'à trouver la naissance ou la mort d'une note. Puis on réitère.

    pasMin=PasMinimal (sonTraite, bpm, fe, facteur)
    pasCourant =pasMin
    N=len(sonTraite)
    correction=[]   ## C'est la liste qui contiendra les résultats. Les cases sont espacées de pasMin
    for k in range (np.floor(N/pasMin)):
        correction.append(0)
        
    indice_adaptation=0 ## On remplace k*pasMin par (k+1)*pasMin quand indice_adaptation atteint adaptation
    indice_note=0
    while (indice_note<N):
        if (sonTraite(indice_note)==0):
            indice_note=indice_note+1
            indice_adaptation+=1
            if (indice_adaptation>=adaptation):
                indice_adaptation=0
                pasCourant+=pasMin
        else:
            indice_mort=trouverMort(sonTraite, indice_note)
            pasCourantMort=trouverPasCourrant(sonTraite, indice_note, indice_mort,fe,pasMin, adaptation)
            pasCourantNaissance=pasCourant
            grillageNaissance=np.floor(indice_note/(fe*pasMin))
            grillageMort=np.floor(indice_mort/(fe*pasMin))
            DecalageNaissance= np.floor(pasCourantNaissance/pasMin)
            DecalageMort=np.floor(pasCourantMort/pasMin)
            ## On décale dans une V0 tout vers la droite, il faudra faire une comparaison pour savoir en réalité s'il est plus judicieux de décaler à droite ou à gauche
            for i in range (grillageMort+DecalageMort-grillageNaissance-DecalageNaissance):
                correction[i]=sonTraite(indice_note)
            pasCourant=pasCourantMort
            indice_note=indice_mort+1
                
        return (correction,pasMin)
## Le problème de cet algorithme est qu'il retourne une liste contenant les naissances et morts des notes, mais le simple faite que la note dure n'est pas enregistrée.
##Or pour resynthétiser le morceau corrigé, on a besoin de savoir si un note est en vie, ce que l'on indiquera part "vie", à l'endroit où l'on disait "mort" ou "naissance".

##obscolète
def vie (correction,plage_note_debut,plage_note_fin): ## On a besoin a priori de savoir le nombre de notes traitées. On peut les ordonner de 1 à N en prenant tous les tons audibles.
    faire_vivre=[]
    for k in range (plage_note_fin - plage_note_debut):
        faire_vivre.append([0,[]])    #0 veut dire faux. Au début, aucune note n'est vivante. 
        #On aura 0 si la note n'apparaît nulle part, et 1 si elle apparaît, auquel cas la liste contiendra les dates de vie.
    
    for indice in range (len(correction)):  # D'abord on remplit la liste des notes en disant si elles apparaissent ou non, puis en indiquant les indices de début et fin
        for j in range (len(correction[indice])):
            if (correction[indice][j][1]=='naissance'):
                faire_vivre[correction[indice][j][0]][0]=1
                faire_vivre[correction[indice][j][0]][1].append(indice)
            if (correction[indice][j][1]=='mort'):
                faire_vivre[correction[indice][j][0]]=0
                faire_vivre[correction[indice][j][0]][1].append(indice)
    
    for k in range (len(correction)):  ## puis on parcourt faire_vivre et on modifie correction
        if (faire_vivre[k][0]): ## Si la note numéro k apparaît au moins une fois dans le morceau
            j=0
            while (j<len(faire_vivre[k][1])): ##On parcourt la liste des dates de naissance et mort de la note
                for m in range (len(faire_vivre[k][1][j+1])-len(faire_vivre[k][1][j])-1):  ## On veut remplir correction strictement entre les dates de naissance et de mort
                    correction[faire_vivre[k][1][j]+m+1].append([k,'vie'])  # k est le nom de la note
                j=j+2
    return(correction)
    
            
                    
                
                
                
                    
        
                
                
                
                
        
        
        
    
    
    
    

    
        
            
                
            
                
            
