# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 12:50:47 2017

@author: c.senik
"""
import pyaudio
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

def PlusPetitEnchainement (sonTraite,bpm,fe):  ## On veut trouver les deux notes consécutives les moins espacées en temps. On s'intéresse uniquement aux moments où naissent les notes.
    ## On initialisera le plus petit enchaînement à bpm.
    plusPetitEnchainement=bpm
    date_Debut=0  ## Date_debut et Date_fin vont parcourir les notes consécutives et permettre d'actualiser PlusPetitEnchainement.
    date_Fin=0
    N=len(sonTraite)
    for i in range (N):
        M=len(sonTraite[i])
        Note_naissante=0     #On se demande si à la date courante, une note est née. 0 veut dire "false", 1 "true".
        for j in range (M):
            if (sonTraite[i][j][1]=="naissance"):  ## On trouve une note naissante à cette date parmi toutes les notes en cours
                Note_naissante=1
        if (Note_naissante):   #On a trouvé des notes naissantes à la date courrante.
            if (Note_naissante and date_Debut==0):
                date_Debut=i*N/fe    # c'est le cas où l'on croise la première note naissante.
            else:
                date_Fin=i*N/fe
                if (date_Fin-date_Debut<plusPetitEnchainement):   ## On peut voir si l'on a trouvé un enchaînement plus court
                    plusPetitEnchainement=date_Fin-date_Debut
                date_Debut=i*N/fe    
                
    return (plusPetitEnchainement)
    
def PasMinimal (sonTraite, bpm, fe, facteur):  ## Il faut néanmois corriger l'enchaînement ci-dessus pour que sa durée soit un diviseur de la durée de la mesure. 
##On divise l'enchaînement par un facteur pour plus de précision, à troquer contre du temps de calcul.
    plusPetitEnchainement= PlusPetitEnchainement (sonTraite,bpm,fe)
    pasMin=plusPetitEnchainement/facteur
    Mesure=60/bpm
    ratio= np.floor(Mesure/pasMin)
    pasMin=ratio*Mesure
    return (pasMin)
    
def CorrectionRythmique(sonTraite, bpm, fe, facteur, adaptation): ## On passe à la correction proprement dite. Adaptation a le sens suivant: dès qu'on croise une note, 
#on la recale, on repart de là où elle se trouve et on progresse à pasMin pendant "adaptation", puis 2*pasMin pendant "adaptation", ..., puis k*pasMin pendant "adaptation",
#jusqu'à trouver la naissance ou la mort d'une note. Puis on réitère.
    pasMin=PasMinimal (sonTraite, bpm, fe, facteur)
    pasCourant =pasMin
    N=len(sonTraite)
    correction=[]   ## C'est la liste qui contiendra les résultats. Les cases sont espacées de pasMin
    for k in range (np.floor(N/pasMin)):
        correction.append([])
    indice_adaptation=0 ## On remplace k*pasMin par (k+1)*pasMin quand indice_adaptation atteint adaptation
    nait_ou_meurt=0 #ce booléan dit à chaque boucle s'il existe une note naissante ou morte.
    for indice in range (N):
        M=len(sonTraite[indice])
        for j in range (M):
            if (sonTraite[indice][j][1]=="mort" or sonTraite[indice][j][1]=="naissance"):
                nait_ou_meurt=1       ##on a trouvé une naissance ou mort, il faudra donc ensuite remettre le pasCourant à valeur pasMin
                note=sonTraite[indice][j]  ## On extrait la note pour ensuite la recaler dans correction
                date_note=indice/fe
                grillage=np.floor(date_note/pasCourant)  #On veut savoir où placer la note dans la liste correction.
                if (((grillage+1)*pasCourant-date_note/pasCourant)<(date_note/pasCourant-grillage*pasCourant)): #Si la note est plus proche de la partie supérieure, 
                    k=pasCourant/pasMin
                    correction[k*(grillage+1)].append(note)     ## On la recale dans le futur
                else :  # sinon dans le passé
                    k=pasCourant/pasMin
                    correction[k*(grillage)].append(note)      
            if (nait_ou_meurt):   ## Si on avait croisé une naissance ou une mort, il faut repartir avec un grillage sur pasMin
                nait_ou_meurt=0
                indice_adaptation=0
                pasCourant=pasMin
            else:       ## Il faut éventuellement augmenter le pas de grillage
                if(indice_adaptation<adaptation):
                    indice_adaptation=indice_adaptation+1
                else:
                    pasCourant=pasCourant+pasMin
                    indice_adaptation=0
            return correction
## Le problème de cet algorithme est qu'il retourne une liste contenant les naissances et morts des notes, mais le simple faite que la note dure n'est pas enregistrée.
##Or pour resynthétiser le morceau corrigé, on a besoin de savoir si un note est en vie, ce que l'on indiquera part "vie", à l'endroit où l'on disait "mort" ou "naissance".
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
    
            
                    
                
                
                
                    
        
                
                
                
                
        
        
        
    
    
    
    

    
        
            
                
            
                
            