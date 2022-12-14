#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 06:41:49 2022

@author: alejandroguzman
"""
import time
import heapq
import random
import copy
import numpy as np
import matplotlib.pyplot as plt

inicio = time.time()

class job():
    def __init__(self, numero, liste_durees=[]):
        

        
        self.numero = numero

        
        self.duree_operation = [i for i in liste_durees]

        
        self.date_debut = [None for i in liste_durees]
        
       
        self.duree = 0
        for i in liste_durees:
            self.duree += i


    def afficher(self):
        print("Job", self.numero,"duración total", self.duree, ":")
        for numero in range(len(self.duree_operation)):
            print("  operacion", numero, 
                  ": duración =", self.duree_operation[numero], 
                  "empieza =", self.date_debut[numero])


class ordonnancement:

    #constructor para un horario vacío
    def __init__(self, nombre_machines):
       
        self.sequence = []

        
        self.nombre_machines = nombre_machines

        
        self.duree = 0

       
        self.date_disponibilite = [0 for i in range(self.nombre_machines)]

    def sequence(self):
        return self.sequence

    def nombre_machines(self):
        return self.nombre_machines

    def duree(self):
        return self.duree

    def date_disponibilite(self, machine):
        return self.date_disponibilite[machine]

    def changer_date_disponibilite(self, date, machine):
        self.date_disponibilite[machine] = date

    def fixer_date_debut(self, job, operation, date):
        job.date_debut[operation] = date


    def afficher(self):
        print("Ordre des jobs :", end='')
        for job in self.sequence:
            print(" ",job.numero," ", end='')
        print()
        for job in self.sequence:
            print("Job", job.numero, ":", end='')
            for machine in range(self.nombre_machines):
                print(" op", machine,
                      "à t =", job.date_debut[machine],
                      "|", end='')
            print()
        print("Cmax =", self.duree)

    def ordonnancer_job(self, job):
        self.sequence.append(job)
        
        self.fixer_date_debut(job, 0, self.date_disponibilite[0]) 
        self.changer_date_disponibilite(job.date_debut[0] + job.duree_operation[0], 0) 
       
        if self.nombre_machines > 0:
            for i in range(1, self.nombre_machines):
                if self.date_disponibilite[i] > job.date_debut[i-1] + job.duree_operation[i-1]:
                    self.fixer_date_debut(job, i, self.date_disponibilite[i])
                    self.changer_date_disponibilite(job.date_debut[i] + job.duree_operation[i], i)
                else:
                    self.fixer_date_debut(job, i, job.date_debut[i-1] + job.duree_operation[i-1])
                    self.changer_date_disponibilite(job.date_debut[i] + job.duree_operation[i], i)


        self.duree = job.date_debut[self.nombre_machines -1] + job.duree_operation[self.nombre_machines-1]
    
    
    def ordonnancer_liste_job(self, liste_jobs):
        for job in liste_jobs:
            self.ordonnancer_job(job)



import heapq


MAXINT = 10000
max_iteration= 50
max_memory=1000000
R = 4

class Flowshop():
    def __init__(self, nombre_jobs=0, nombre_machines=0, liste_jobs=None):
        
        self.nombre_jobs = nombre_jobs
       
        self.nombre_machines = nombre_machines
        
        self.liste_jobs = liste_jobs
        
    def definir_desde_archivo(self, nom):
       
        
        fdonnees = open(nom,"r")
        
        ligne = fdonnees.readline() 
        print(ligne)
        l = ligne.split() 
        print(l)
        self.nombre_jobs = int(l[1])
        print(self.nombre_jobs)
        self.nombre_machines = int(l[0])
        print(self.nombre_machines)
       
        self.liste_jobs = []
        for i in range(self.nombre_jobs):
            ligne = fdonnees.readline() 
            print(ligne)
            l = ligne.split()
            
            l = [int(i) for i in l]
            
            j = job(i, l)
         
            self.liste_jobs.append(j)
        
        
        
        fdonnees.close()


#                     GENERATE INITIAL SOLUTION                    #


def GenerateInitialSolution(liste_jobs, nombre_machines):
    lenght = len(liste_jobs)
    sequence = []
    while len(sequence)!=lenght:
        L = []
        for job in liste_jobs:
            sequence.append(job)
            ordo = ordonnancement(nombre_machines)
            ordo.ordonnancer_liste_job(sequence)
            if len(L)==0:
                L.append([job, ordo.duree])
            for j in range(0,len(L)):
                if ordo.duree < L[j][1]:
                    L.insert(j,[job, ordo.duree])
            if len(L)>R:
                L.pop()
            sequence.pop()
        rang=random.randint(0,min(R-1, len(L)-1))
        job=L[rang][0]
        sequence.append(job)
        liste_jobs.remove(job)
    ordo = ordonnancement(nombre_machines)
    ordo.ordonnancer_liste_job(sequence)
    return ordo



def best_neighbor(ordo, last_solutions):                
    nombre_jobs = len(ordo.sequence)
    best_ordo = ordo
    for k in range(nombre_jobs-1):
        for i in range(k+1,nombre_jobs):
            sequence = copy.copy(ordo.sequence)
            sequence[k],sequence[i] = sequence [i],sequence[k]
            ordo2 = ordonnancement(ordo.nombre_machines)
            ordo2.ordonnancer_liste_job(sequence)
            if best_ordo == ordo and (ordo2.sequence not in last_solutions):
                best_ordo = ordo2
            if ordo2.duree < best_ordo.duree and (ordo2.sequence not in last_solutions):
                best_ordo = ordo2
    return best_ordo


def TaBUSearch(liste_jobs, nombre_machines):
    """     TABU Algorithm    """
    S = ordonnancement(nombre_machines) 
    S.ordonnancer_liste_job(liste_jobs) # Generating a starting solution     
    S_best = S # Updating best solution found so far  
    last_solutions = [S.sequence] # Initializing a list containting Last solutions
    i = 0
    while i < max_iteration : #  stop criterion :  maximum number of iterations is achieved 
        S = best_neighbor(S, last_solutions) # Test and update better solution
        if S.duree < S_best.duree:
            S_best = S
        
        last_solutions.append(S.sequence)
        if len(last_solutions) > max_memory:
            last_solutions.pop(0)
        i+=1
    return S_best


#                         PERTURBATION                             #

def perturbation(ordo):  # Swap + Reversion perturbation ( should be strong enought to o kick-out the solution from the local optima) 
    sequence = copy.copy(ordo.sequence)
    center = len(sequence)//2 # Look for the center of the List
    demi_seq1 = sequence[:center] # Divid the sequence into two equal parts ( left and right)
    demi_seq2 = sequence[center:]
    demi_seq1.reverse() # reverse the right part
    sequence_bis=demi_seq2+demi_seq1 # re-organised the whole sequence
    ordo_changed = ordonnancement(ordo.nombre_machines)
    ordo_changed.ordonnancer_liste_job(sequence_bis)
    return ordo_changed

#                       ACCEPTANCE CRIETERION                      #

def AcceptanceCriterion(ordo1, ordo2):
    if ordo2.duree < ordo1.duree: 
        return ordo2
    else:
        return ordo1

#                       ITERATED LOCAL SEARCH                      #

def IteratedLocalSearch(liste_jobs, nombre_machines):
    So = GenerateInitialSolution(liste_jobs,nombre_machines) # So is the initial solution  
    S_op = TaBUSearch(So.sequence, nombre_machines) #  Initial solution So is intensified to reach a local optimum S_op
    i=0
    while i < max_iteration : # stop criterion :  maximum number of iterations is achieved 
        S_prime = perturbation(S_op) # perturbs the solution to escape local optima, S_prime is the changed optimal solution.
        S_prime_op = TaBUSearch(S_prime.sequence, nombre_machines) # uses LocalSearch method to find the new local optima S_prime_op.
        S_op = AcceptanceCriterion(S_op, S_prime_op) # Test and update, accepts non improving solutions along the process.
        i+=1
    return S_op


                              

prob = Flowshop()
prob.definir_desde_archivo('tai10.txt')
result=IteratedLocalSearch(prob.liste_jobs, prob.nombre_machines)


print(" duración = ", result.duree)
fin = time.time()
print(fin-inicio)
