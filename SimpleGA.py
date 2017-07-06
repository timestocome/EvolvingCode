
# http://github.com/timestocome


# simple genetic algorithm
# optimize a list of N numbers that sum to X



# started with this:
# https://lethain.com/genetic-algorithms-cool-name-damn-simple/

# updated to python 3
# streamlined code 
# fixed a couple of things




from random import randint, random
import numpy as np
from operator import add 




def create_bot(length, min, max):
    return [randint(min, max) for x in range(length)]


def create_population(count, length, min, max):
    return [create_bot(length, min, max) for x in range(count)]


def fitness(bot, target):
    return np.abs(np.sum(bot) - target)


def create_child(d, m):
    half_d = len(d) // 2
    half_m = len(m) // 2
    c = d[:half_d] + m[half_m:]
    return c


def mutate_bot(c):
    location = randint(0, len(c)-1)
    c[location] = randint(0, 100)
    return c



def evolve(pop, target=200, retain=0.3, random_select=0.3, mutate=0.3):

    graded = [ (fitness(x, target), x) for x in pop ] 
    graded = [ x[1] for x in sorted(graded)]

    n_keep = int(len(graded) * retain)
    parents = graded[:n_keep]


    # add some random choices to parents list
    for i in range(n_keep):
        if random_select > random():
            parents.append(graded[i])

    # breed 
    n_parents = len(parents)
    n_children = len(pop) - n_parents
    children = []

    while len(children) < n_children:
        d = randint(0, n_parents-1)
        m = randint(0, n_parents-1)
     
        if d != m:
            c = create_child(parents[d], parents[m])
            c1 = mutate_bot(c)
            children.append(c1)

    parents.extend(children)
    return parents


######################################################

target = 200
bottom = 0
top = target // 2
size = 20
n = 15
p = create_population(n, size, bottom, top)

max_generation = 2000
generation = 0
while(generation < max_generation):

    print('Generation:', generation)
    
    new_p = evolve(p)
    mean_fitness = 0.0

    for i in range(len(new_p)):
    
        score = fitness(target, new_p[i])
        
        if score[i] == target: 
            generation = max_generation
            print("Winner", score[i])
            print(new_p[i])
            generation = max_generation

   
    
    print('Mean score: %.1lf' % (np.sum(score) / len(new_p)))
    generation += 1
    p = new_p


##########################################
