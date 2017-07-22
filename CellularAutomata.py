
# http://github.com/timestocome


import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib import animation


# Wolfram cellular automata
# http://mathworld.wolfram.com/ElementaryCellularAutomaton.html



###########################################################################
# utilities
###########################################################################
# Returns a tuple of binary ints representing the decimal n in binary.  
# For example, binary(18,8) returns (0,1,0,0,1,0,0,0)
def binary(n, digits):

    t = []
    for i in range(digits):
        n, r = divmod(n, 2)
        t.append(r)

    return tuple(reversed(t))


############################################################################
# Wolfram's automata
#############################################################################


class CellularAutomata(object):
    
    def __init__(self, rule, n_steps=100):
        
        self.table = self.make_table(rule)
        self.n_steps = n_steps
        self.width = 2 * n_steps + 1
        self.array = np.zeros((n_steps, self.width), dtype=np.int8)
        self.next = 0


    # Returns a look up table for the given CellularAutomata rule.  
    # The table is a dictionary that maps 3-tuples to binary values.
    # above row of 3 tuples 111, 110, 101, 100, 011, 010, 001, 000
    # rule is the 8 digit binary version of rule in decimal form
    # so rule 30 -> 11110
    def make_table(self, rule):
            
        table = {}
        for i, bit in enumerate(binary(rule, 8)):
            t = binary(7-i, 3)      # the 3 digit binary tuple
            table[t] = bit          # the binary digit of the rule
        return table


    # Starts with one cell in the middle of the top row.
    def start_single(self):
        
        self.array[0, self.width // 2] = 1
        self.next += 1


    # Start with random values in the top row.
    def start_random(self):

        self.array[0] = np.random.random([1,self.width]).round()
        self.next += 1



    # Executes one time step by computing the next row of the array.
    def step(self):

        i = self.next
        self.next += 1

        a = self.array
        t = self.table

        for j in range(1,self.width-1):
            a[i,j] = t[tuple(a[i-1, j-1:j+2])]

        return self.array







########################################
rule = 110
n_steps = 100
sleep = 50


# set up rule lookup table and array for image
ca = CellularAutomata(rule, n_steps)
#ca.start_single()       # start with 1 in center of top row, could also chose random 
ca.start_random()

# animation loop computes one row at a time for display
def animate(i):
    
    new_state = ca.step()
    ax.clear()      # things get very slow if this line is missing
    im = ax.imshow(new_state, cmap=plt.cm.magma, interpolation='nearest')

    return (im, )
    


# set up graphics
figure = plt.figure(figsize=(12,12))
ax = figure.add_subplot(111)
plt.title("Wolfram's Cellular Automata")  
plt.axis('off')   
im = ax.imshow(ca.array, cmap=plt.cm.binary, interpolation='nearest')


# run program
# note: blit=False needed to run on OSX, probably faster if set to True on other platforms
anim = animation.FuncAnimation(figure, animate, frames=(n_steps-2), interval=sleep, blit=False, repeat=False)


plt.show()

