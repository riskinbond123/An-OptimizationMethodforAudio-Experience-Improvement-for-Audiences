# -*- coding: utf-8 -*-
"""
The module optimizes the speaker power output in such a way that all people are 
within the set limits  

@author: risha, jeyanth
"""

import numpy as np
import math
from scipy.optimize import minimize

people =input("How many people are there in the room? \n")
speaker = input("How many speakers are there in the room? \n")

people_position = []
for i in range(int(people)):
    people_position.append([])
    for j in range(1):
        temp = input("Enter x-co-ordinate of person %d \n" % (i+1))
        people_position[i].append(int(temp))
        temp = input("Enter y-co-ordinate of person %d \n" % (i+1))
        people_position[i].append(int(temp))

speaker_position = []
for i in range(int(speaker)):
    speaker_position.append([])
    for j in range(1):
        temp = input("Enter x-co-ordinate of speaker %d \n" % (i+1))
        speaker_position[i].append(int(temp))
        temp = input("Enter y-co-ordinate of speaker %d \n" % (i+1))
        speaker_position[i].append(int(temp))

def objective(x):
    return 0
# computes distance between two points (radius)
def distance(x1,y1, x2, y2):
    return math.hypot(x2-x1,y2-y1)

coefficient_matrix = np.zeros((len(people_position), len(speaker_position)))

def get_intensity_coefficient(r):
    return 1/(4*math.pi*r*r)

#block to generate sound intensity coefficients of the n intensity equations
for i in range(0, len(people_position)):
    for j in range(0, len(speaker_position)):
        r = distance(people_position[i][0],people_position[i][1],speaker_position[j][0],speaker_position[j][1])
        coefficient_matrix[i][j] = get_intensity_coefficient(r)


# initial guesses
n = 2
x0 = np.zeros(len(speaker_position))
for j in range(0,len(speaker_position)):
    x0[j] = 1.1

#calculate decibel value of speaker power
def decibel(pw):
    return 10*math.log10(pw/10**-12)

#flag to check if range has to be increased when constraints aren't satisfied
check = True

#power equivalent of 60dB
optimum_value = 10**-6

#initial step value
k=0

while(check):
    check = False
    print("Step value k: "+str(k))

    opt_l = 10**(-6-k)
    opt_ldb = decibel(opt_l)
    print('Lower limit: '+str(opt_ldb)+"dB ")
    opt_u = 10**(-6+k)
    opt_udb = decibel(opt_u)
    print('Upper limit: '+str(opt_udb)+"dB ")
    
    #print('')
    #print('Constraints')
    #print('')
    #constraints
    for i in range(0, 2*len(people_position)):
        #nonlocal eqn
        eqn=''
        #nonlocal feqn
        feqn=''
        if(i<len(people_position)):
          
            for j in range(0,len(speaker_position)):
                cof = coefficient_matrix[i%len(people_position)][j]
                #nonlocal var
                var = '*x['+str(int(j))+']'
                eqn = eqn+'+'+str(cof)+var
                #print(eqn)
                del cof
            feqn = eqn +'-'+str(opt_l)
            func_gen = 'def constraint'+str(int(i+1))+'(x):return '+feqn
            del feqn
            #print(func_gen)
            #print('')
            exec(func_gen)
        
        else:
          
            for j in range(0,len(speaker_position)):
                cof = coefficient_matrix[i%len(people_position)][j]
                #nonlocal var
                var = '*x['+str(int(j))+']'
                if(eqn==''):
                    eqn=str(cof)+var
                else:
                    eqn = eqn+'-'+str(cof)+var
                    #print(eqn)
                del cof
                feqn = str(opt_u) +'-'+eqn
                func_gen = 'def constraint'+str(int(i+1))+'(x):return '+feqn
                del feqn
                #print(func_gen)
                #print('')
                exec(func_gen)
        

    # optimize
    b = (0.0001,0.004)
    if(len(speaker_position)== 1):
        bnds = (b)
    else:
        bnds = (b,)
    for j in range(0,len(speaker_position)-1):
        bnds = bnds +(b,)
    template = "= {'type':'ineq','fun':constraint"
    cons=[]
    for i in range(0, 2*len(people_position)):
        #nonlocal rhs
        rhs = template+str(int(i+1))+'}'
        #nonlocal dict_var
        dict_var = 'con'+str(int(i))+rhs
        exec(dict_var)
        cons.append(eval('con'+str(int(i))))
        
    #speaker power solution array
    solution = minimize(objective,x0,method='SLSQP',\
                    bounds=bnds,constraints=cons)
    x = solution.x
    
    # print solution
    print('')
    print('Solution')
    power_matrix = []
    for j in range(0,len(speaker_position)):
        power_matrix.append(x[j])
        #print('x'+str(int(j))+' = ' + str(x[j]))


    i_matrix=[]
    for i in range(len(coefficient_matrix)):
        i_matrix.append(0)
        for j in range(len(power_matrix)):
            i_matrix[i]+=coefficient_matrix[i][j]*power_matrix[j]
    
    #get decibel value of intensity
    i_matrix_decibel = []
    for i in range(0, len(i_matrix)):
        i_matrix_decibel.append(0)
        i_matrix_decibel[i] = decibel(i_matrix[i])
        print("Person " + str(i+1) + " = " + str(i_matrix_decibel[i]) + " dB")
    print("-------------------------------------------------")
    #if out of range update k and rerun loop
    for i in range(0, len(i_matrix_decibel)):
        #loop exits when all decibels are in range
        current_intensity = round(i_matrix_decibel[i])
        if((current_intensity<opt_ldb)or(current_intensity>opt_udb)):
            check = True
    
    if(check):
        #k step calculation
        k = k+0.1
#final speaker power outputs
print("****************Speaker power output****************")
final_speaker_power = np.array(power_matrix)*1000
for i in range(0, len(final_speaker_power)):
    print('Speaker '+str(int(i+1))+': '+str(final_speaker_power[i])+' mW')
print("*****************************************************")