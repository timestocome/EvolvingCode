
# http://github.com/timestocome


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import copy


# https://en.wikipedia.org/wiki/Turmite

# https://en.wikipedia.org/wiki/Langton%27s_ant
# Langton's ant is a two-dimensional universal Turing machine 
# with a very simple set of rules but complex emergent behavior. 
# It was invented by Chris Langton in 1986 and runs on a square 
# lattice of black and white cells.[1] The universality of Langton's 
# ant was proven in 2000.[2] The idea has been generalized in 
# several different ways, such as turmites which add more colors
# and more states.
# 
# ~100 steps creates simple, often symmetric patterns
# ~10,000 creates chaotic patterns
# later emergent order appears ( strange attractor )
# 104 step highway that repeats endlessly is always the final state


# Rules:
# Start with empty array or randomly colored array
# place ant on the array
# if square is white 
#       turn 90' to right
#       change square to black
#       move one step forward
# if square is black
#       turn 90' to left
#       change square to white
#       move one step forward




###########################################################################
# utilities
###########################################################################

############################################################################
# Langton's Ant
#############################################################################
height = 100
width = 100
board = []


# start ant in center
up = 0
right = 1
down = 2
left = 3


class LangtonsAnt(object):
    
    def __init__(self, n_steps=100):
        
        self.n_steps = n_steps
        self.board = np.zeros((height, width), dtype=np.int8)
        self.ant_direction = np.random.randint(0, 4)
        self.ant_x = width // 2
        self.ant_y = height // 2
        self.next = 0



    # Starts with one cell in the middle of the board
    def start_single(self):
        
        self.board[height // 2, width // 2] = 1
        self.next += 1


    # Start with random values 
    def start_random(self):

        random_start = np.random.random((height, width))
    
        for i in range(height):
            for j in range(width):
                if random_start[i][j] > .9:     # the lower to start with more black squares
                    self.board[i][j] = 1
        self.next += 1


    # Executes one time step 
    def step(self):

        self.next += 1

        if self.board[self.ant_x][self.ant_y] == 0:       # white
            self.ant_direction = (self.ant_direction + 1) % 4    # turn 90' right
            self.board[self.ant_x][self.ant_y] = 1       # flip sq color

        else:                                               # black
            self.ant_direction = (self.ant_direction - 1) % 4   # turn 90' left
            self.board[self.ant_x][self.ant_y] = 0         # flip sq color


        # update ant location
        if self.ant_direction == up and self.ant_y > 0:
            self.ant_y -= 1
        if self.ant_direction == right and self.ant_x - 2 < width:
            self.ant_x += 1
        if self.ant_direction == down and self.ant_y - 2 < height:
            self.ant_y += 1
        if self.ant_direction == left and self.ant_x > 0:
            self.ant_x -= 1

        # make a copy of the board for animation 
        new_board = copy.copy(self.board)

        # show ant on the animation copy of the board
        new_board[self.ant_x][self.ant_y] = 2

        return new_board






########################################
# animation init
sleep = 10
n_steps = 20000

langtonsAnt = LangtonsAnt(n_steps)
#langtonsAnt.start_random()        # start with a random selection
langtonsAnt.start_single()          # start with center square turned on, rest off


# animation loop computes one row at a time for display
def animate(i):
    
    new_state = langtonsAnt.step()
    ax.clear()      # things get very slow if this line is missing
    im = ax.imshow(new_state, cmap=plt.cm.bone, interpolation='nearest')

    return (im, )
    


# set up graphics
figure = plt.figure(figsize=(12,12))
ax = figure.add_subplot(111)
plt.title("Langton's ant")  
plt.axis('off')   
im = ax.imshow(langtonsAnt.board, cmap=plt.cm.bone, interpolation='nearest')


# run program
# note: blit=False needed to run on OSX, probably faster if set to True on other platforms
anim = animation.FuncAnimation(figure, animate, frames=(n_steps-2), interval=sleep, blit=False, repeat=False)


plt.show()

