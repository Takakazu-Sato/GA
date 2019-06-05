import random
from math import sin, cos, pi, exp, e, sqrt
from operator import mul
from functools import reduce

def McCormick(individual):
    
    mc = sin(individual[0] + individual[1]) + ((individual[0] - individual[1]) **2 ) - 1.5 * individual[0] + 2.5 * individual[1] + 1,

    return mc
    
   