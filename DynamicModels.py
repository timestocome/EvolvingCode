

# https://github.com/timestocome

# https://www.stat.berkeley.edu/~aldous/157/Papers/Schelling_Seg_Models.pdf
# not a replication of his experiments more a toy for doing my own similar experiments

# 
# code is set up to easily change neighborhood size
# code is set up to easily move depending on number of strangers in neighborhood
# this is intended to be a bare-bones example for running lots of different scenerios 


import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib import animation
import copy



############################################################################
# Dynamic Segregation 
############################################################################
# create a 2d board to use for simulation
height = 40
width = 40


# animation setup
# how many time steps animation should perform
n_steps = 10000
sleep = 1


# start with two or more populations
n_red = 400
n_blue = 400

red_mark = 1
blue_mark = 2
open_mark = 0


# check to see if minimum number of friends in neighborhood, 
# if not then move.
min_friends = 2


class Bot(object):

    def __init__(self, x, y, c):

        self.x = x
        self.y = y
        self.color = c
    





class DynamicModel(object):
    

    # set up red and blue bots in random unoccupied locations
    def __init__(self, n_steps=100):
        
        self.n_steps = n_steps
        self.next = 0
        self.board = np.zeros((height, width), dtype=np.int8)
        self.red_bots = []
        self.blue_bots = []

        r = n_red
        while r > 0:

            # grab a random location
            x = np.random.randint(0, width-1)
            y = np.random.randint(0, height-1)
            
            # check square is unoccupied
            if self.board[x][y] == open_mark:
                new_bot = Bot(x, y, red_mark)
                r -= 1
                self.red_bots.append(new_bot)
                self.board[x][y] = red_mark


        b = n_blue
        while b > 0:
            
            # grab a random location
            x = np.random.randint(0, width-1)
            y = np.random.randint(0, height-1)
            
            # check square is unoccupied
            if self.board[x][y] == open_mark:
                new_bot = Bot(x, y, blue_mark)
                b -= 1
                self.blue_bots.append(new_bot)
                self.board[x][y] = blue_mark


    def count_neighbors(self, bot):

        # count neighbors 2 steps away
        x = bot.x
        y = bot.y


        # start at 0, end at n+1
        #n_1 = self.board[x-1:x+2,y-1:y+2]
        n_2 = self.board[x-2:x+3,y-2:y+3]

        # tally each kind of neighbor and remove self from count
        uniques, counts = np.unique(n_2, return_counts=True)
  
        count_none = counts[np.where(uniques == open_mark)]
        count_red = counts[np.where(uniques == red_mark)]
        count_blue = counts[np.where(uniques == blue_mark)]

        if bot.color == red_mark: count_red -= 1
        if bot.color == blue_mark: count_blue -= 1

        friends = 0
        strangers = 0

        if bot.color == red_mark:
            friends = count_red
            strangers = count_blue

        if bot.color == blue_mark:
            friends = count_blue
            strangers = count_red
        
        if len(friends) > 0: friends = friends[0]
        else: friends = 0

        if len(strangers) > 0: strangers = strangers[0]
        else: strangers = 0
        
        return (friends, strangers)
        



    def relocation(self, bot, friends, strangers):

        # update self.board
        # if friends < 1 move to random open location
        if friends < min_friends:
            move = 0
            while move == 0:
                 # grab a random location
                x = np.random.randint(0, width-1)
                y = np.random.randint(0, height-1)

                if self.board[x][y] == open_mark:
                
                    self.board[x][y] = bot.color
                    self.board[bot.x][bot.y] = open_mark
                
                    bot.x = x
                    bot.y = y
                
                    move = 1



    def step(self):

        self.next += 1

        # a red and a blue at random
        r_bot = self.red_bots[np.random.randint(0,len(self.red_bots)-1)]
        b_bot = self.blue_bots[np.random.randint(0,len(self.blue_bots)-1)]


        # count neighbors
        r_friends, r_strangers = self.count_neighbors(r_bot)
        b_friends, b_strangers = self.count_neighbors(b_bot)


        # move if no friends in neighborhood
        if r_friends < min_friends:
            self.relocation(r_bot, r_friends, r_strangers)
        
        if b_friends < min_friends:
            self.relocation(b_bot, b_friends, b_strangers)

        return self.board

    
    






########################################
# setup model
dynamicModel = DynamicModel(n_steps)


# convert game board to an image
def image_from_array(array):

    z_im = np.zeros((height, width, 3), 'uint8')

    for i in range(height):
        for j in range(width):
            if array[i][j] == open_mark: 
                z_im[i][j][0] = 240     # red
                z_im[i][j][1] = 240     # green 
                z_im[i][j][2] = 240     # blue
            if array[i][j] == red_mark: 
                z_im[i][j][0] = 150
                z_im[i][j][1] = 50
                z_im[i][j][2] = 50
            if array[i][j] == blue_mark: 
                z_im[i][j][0] = 0
                z_im[i][j][1] = 50
                z_im[i][j][2] = 150

    im = ax.imshow(z_im, interpolation='nearest')
    return im



# animation loop computes one row at a time for display
def animate(i):
    
    ax.clear()      # things get very slow if this line is missing
    im = image_from_array(dynamicModel.step())

    return (im, )
    


# set up graphics
figure = plt.figure(figsize=(12,12))
ax = figure.add_subplot(111)
plt.title("Dynamic Model")  
plt.axis('off')   

im = image_from_array(dynamicModel.board)



# run program
# note: blit=False needed to run on OSX, probably faster if set to True on other platforms
anim = animation.FuncAnimation(figure, animate, frames=(n_steps-2), interval=sleep, blit=False, repeat=False)

plt.show()

