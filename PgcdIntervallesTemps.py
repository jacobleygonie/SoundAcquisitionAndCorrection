# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 00:35:04 2017

@author: c.senik
"""
import Grille as grille
import numpy as np
def Euclide(a,b):
    if(a==0 or b==0):
        return a
    if(b<a):
        r=a%b
        if(r==0):
            return b
        else :
            l=0
            w=b%r
            while (w!=0):
                l=w
                w=r%l
                r=l
            return r
    else:
        r=b%a
        if(r==0):
            return a
        else :
            l=0
            w=b%r
            while (w!=0):
                l=w
                w=r%l
                r=l
            return r
            
def EuclideMultiple(T):
    pgcd=T[0]
    n=len(T)
    if(n==1):
        return pgcd
    else:
        for i in range (n-1):
            pgcd=Euclide(pgcd,T[i+1])
        return pgcd

def offset (sonTraite):
    offset=0
    N=len(sonTraite)
    while (offset<N and sonTraite[offset]==0):
        offset+=1
    return offset
def tatum(sonTraite,fe): ##Precision est un entier définissant le nombre de chiffres après la virgule que l'on conserve pour les dates.
        
    Dates=[]
    Intervalles =[]
    N=len(sonTraite)
    i=0
    while(i<N):
        if (sonTraite[i]==0):
            i+=1
        else:
            Dates.append(i)
            i=grille.trouverMort(sonTraite, i)+1
    M=len(Dates)
    for j in range (1,M):
        for k in range (j):
            Intervalles.append(Dates[j]-Dates[k])
    
    return EuclideMultiple(Intervalles)

def tatum_consecutif(sonTraite,fe): ##Precision est un entier définissant le nombre de chiffres après la virgule que l'on conserve pour les dates.
    Dates=[]
    Intervalles =[]
    N=len(sonTraite)
    i=0
    while(i<N):
        if (sonTraite[i]==0):
            i+=1
        else:
            Dates.append(i)
            i=grille.trouverMort(sonTraite, i)+1
    M=len(Dates)
    for j in range (1,M):
        Intervalles.append(Dates[j]-Dates[j-1])
    
    return (EuclideMultiple(Intervalles))



def find_errors(sonTraite,fe,interdit,opt):  ##En enlevant une note de la piste, peut-être une note erronée, peut-être obtient on un cohérence rythmique meilleure
    son=np.copy(sonTraite)                  ##On s'interdit de retirer les dates présentes dans la liste "interdit".
    i=0                             ##opt désigne l'option, si l'on choisit 0, on aura le tatum usuel
                                   ## Sinon, on utilise le tatum_consecutif
    tat= 1
    res=[]
    N=len(sonTraite)
    while (i<N):
        if (sonTraite[i]==0):
            i+=1
        else:
            if(interdit.__contains__(i)):
                i+=1
            else:
                j=i
                while (j<N and son[j]!=0):
                    son[j]=0
                    j+=1
                if (opt==0):
                    tat=tatum(son,fe)
                else:
                    tat=tatum_consecutif(son,fe)
                res.append([i,tat])
                son=np.copy(sonTraite)
                i=j
                
    indice_max=0
    for k in range (len(res)):
        if (res[k][1]>res[indice_max][1]):
            indice_max=k
    return res[indice_max]

def iterer_find_errors(sonTraite,fe,interdit,opt,it):#On répète l'opération précédente it fois
   son=sonTraite
   for i in range(it):
      res=find_errors(son,fe,interdit,opt)
      for k in range (res[0],grille.trouverMort(sonTraite,res[0])):
          son[k]=0
   return res[1]
                      


#def optimiser_tatum(sonTraite,fe,Precision,opt,amp): ##On va déplacer un petit peu le notes, au maximum de amp (pour amplitude) cases pour optimiser le tatum

def liste_pistes(sonTraite,amp): ## Retourne la liste des différentes pistes possibles, obtenues en décalant des notes de amp maximum
   init=one_note(sonTraite)
   N=len(sonTraite)
   res=[]
   
   if(init[0]):
       if(init[1]==-1):
           res.append([sonTraite])
       else:
           son=np.copy(sonTraite)      ##On élargit d'abord l'intervalle des deux côtés de la note
           sonbis=np.copy(son)
           premiere_note=find_premiere_note(sonTraite) 
           note=sonTraite[premiere_note]
           deuxieme_note=init[1]
           amp_deb=min(amp, premiere_note)
           amp_end=min(amp,N-deuxieme_note)
           for offset_end in range (amp_end):
               sonbis[deuxieme_note+offset_end-1]=note
               son=np.copy(sonbis)   
               for offset_deb in range (amp_deb):
                   son[premiere_note-offset_deb]=note
                   res.append(np.copy(son))
               son=np.copy(sonTraite)
           
   else:
       
      premiere_note=find_premiere_note(sonTraite) 
  
      mort_note=init[1]
  
      deuxieme_note=find_premiere_note(sonTraite[mort_note:])+mort_note
      
      amp_deb=min(amp, premiere_note)
      amp_end=min(amp,deuxieme_note-mort_note)

      son2=np.copy(sonTraite[mort_note+amp_end:])
      son=np.copy(sonTraite[0:mort_note+amp_end])
  
      
      res2=liste_pistes(son2,amp)     ##Appel récursif
      res1=liste_pistes(son,amp)    ##cas initial (se référer à la boucle précédente)
      N1=len(res1)
      N2=len(res2)

      print(res1[0])
      for i in range (N1):
         for j in range (N2):
            c=res1[i]+res2[j]
            res.append(c)
     
   return res        
           
def one_note(sonTraite):   ## la fonction liste_pistes est récursive, et s'appuie sur le nombre de notes maintenues dans la pistes. Ici on code la fonction qui détecte
##si il y a une ou plusieurs notes. Elle renvoie true s'il y a une note ou 0, faux sinon, et renvoie toujours l'indice de mort de la première note, et -1 s'il n'y en a pas 
    premiere_note=0
    N=len(sonTraite)
    if(N==0): 
        return [True,-1]
    if(N==1):
        if (sonTraite[0]==0):
            return [True,-1]
        else:
            return [True,0]
    while(premiere_note<N and sonTraite[premiere_note]==0):
        premiere_note+=1
    if (premiere_note==N):
        return [True, -1]
    else:
        note= sonTraite[premiere_note]
        deuxieme_note=premiere_note
        while (deuxieme_note<N and sonTraite[deuxieme_note]==note):
            deuxieme_note+=1
        if (deuxieme_note==N):
            return [True, -1]
        else:
            troisieme_note=deuxieme_note
            if(sonTraite[deuxieme_note]!=0):
                return [False, deuxieme_note]
            else:
                while (troisieme_note<N and sonTraite[troisieme_note]==0):
                    troisieme_note+=1
                if(troisieme_note==N):
                    return [True, deuxieme_note]
                else:
                    return [False, deuxieme_note]
                
def find_premiere_note(sonTraite):
    indice=0
    N=len(sonTraite)
    while (indice<N and sonTraite[indice]==0):
        indice+=1
    return indice                
##print(Euclide(2,3));
T=[6,3,9,30]
##print(EuclideMultiple(T));
sonTraite=[0,0,1.12,1.12,1.12,0,0,0,0,9.11,9.11,9.11,0,0,0,0,22.120,22.120,22.120,0,0,0,1.89,1.89,1.89,8.9992,8.9992,8.9992,8.9992,0,0,018.3289,18.3289,18.3289,18.3289,2.405,2.405]
##print(tatum(sonTraite,30))
#print(tatum_consecutif(sonTraite,30))
#print(find_errors(sonTraite,30,[],0))
#print(find_errors(sonTraite,30,[],1))
#print(iterer_find_errors(sonTraite,30,[],0,10))
#print(iterer_find_errors(sonTraite,30,[],1,10))
sonTest=[0,0,0,1,1,1,0,0,0,0,0,0,0,0,2,2,2,2,2,0,0,0,0,0,0,0,0,3,3,3,3,3,0,0,0,0,0]
#print(one_note(sonTest))
#print(find_premiere_note(sonTest))
print(liste_pistes(sonTest,3))

