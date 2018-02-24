

# http://github.com/timestocome



# adapted from http://natureofcode.com/book/chapter-9-the-evolution-of-code/


# 3 letter match ~ 20 generations
# 4 letters ~ 120 generations


import string as st
import re
import numpy as np
import copy


bots = []
new_bots = []
scores = []


n_letters = 4
n_bots = 100


target = ['c', 'a', 't', 's']


# def letters and symbols allowed
world = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
         'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z',
         'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
         'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
         ' ', '.', ',', '?')


# create a random string from world options
def create_random_string(length):

    random_array = []
    
    for i in range(length):
        l = np.random.randint(len(world))

        random_array.append(world[l])

    return random_array



# compute number of possible strings
def possibilities(length):
    return np.power(len(world), length)



# create starting generation
def init_generation():

    for b in range(n_bots):
        letters = create_random_string(n_letters)
        bots.append(letters)




# fitness test
def fitness(bot):

    score = 0
    for i in range(n_letters):
        if bot[i] == target[i]:
            score += 1
        
    return score


# use probabilistic fitness to chose next generation
def choose_fittest():

    candidates_array = []

    # add one vote for each score point per bot
    for i in range(n_bots):
        for j in range(int(scores[i]) + 1):   # include everyone, remove one to remove zero scoring bots
            candidates_array.append(i)   # add bot id to array once for each fitness point


    # shuffle array
    np.random.shuffle(candidates_array)

    # select first n_bots
    candidates_array = candidates_array[0:n_bots]

    # collect parents
    parents = []
    for i in range(n_bots):
        
        parents.append(bots[candidates_array[i]])

    np.random.shuffle(parents)
    return parents
            




# randomly choose 2 and combine

def mate_parents(parents):

    m = parents[0]
    d = parents[1]

    new_bot1 = []
    new_bot2 = []
    i = 0
    while i < n_letters:

        if i % 2 == 0:
            new_bot1.append(m[i])
            new_bot2.append(d[i])
        else:
            new_bot1.append(d[i])
            new_bot2.append(m[i])
        i += 1
    new_bots.append(new_bot1)
    new_bots.append(new_bot2)


    parents.pop(0)   # remove mom
    parents.pop(0)   # remove dad
    


def mutation(b):
    location = np.random.randint(n_letters)
    new_letter = np.random.randint(len(world))
    b[location] = world[new_letter]
    return b


##########################################################################

possible = possibilities(n_letters)
print('%ld combinations of length 5 can be formed from world possibilities' % possible)

# start a random collection of bots
init_generation()


####  main loop ###
generation = 0
best_score = -1

goal = 0
scores = np.zeros(n_bots)

#for z in range(10):
while goal == 0:

    
    # score bots
    for b in range(n_bots):
        s = fitness(bots[b])
        scores[b] = s

        if s == n_letters:
            
            print('Winner')
            print(bots[b], scores[b])
            goal = 1


            print('--------------------')
            for z in range(n_bots):
                print(bots[z])
            
            
            break
           
        if s > best_score:
            best_score = s


            
    # choose fittest
    parents = choose_fittest()


    # mate fittest
    new_bots = []
    for b in range(n_bots//2):
        mate_parents(parents)

    
    # re-set bots to new group
    bots = copy.copy(new_bots)
    new_bots = []


    # random mutations
    for b in range(n_bots):
    
        r = np.random.randint(20)
        if r == 14:
            bots[b] = mutation(bots[b])

    generation += 1
    print('Generation %d Best score %d ' % (generation, best_score))



