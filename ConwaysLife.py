
# http://github.com/timestocome


# started here:
# http://jakevdp.github.io/blog/2013/08/07/conways-game-of-life/
# https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life


import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib import animation



def setup_board():

    global board

    board = np.random.random((w, h))
    board = np.where(board > 0.7, 1, 0 )   # random

    return board



def count_neighbors():

    global board

    kernal = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    n = signal.convolve2d(board, kernal)

    return n[1:-1, 1:-1]



# if n >= 3 die
# if n == 2, 3 stay
# if n < 2 die
# if n == 3 birth
def update_board(n, b):

    for i in range(w):
        for j in range(h):
            if n[i,j] >= 3: b[i,j] = 0                # die
            if n[i,j] == 2 or n[i,j] == 3: b[i,j] = b[i,j]      # stay
            if n[i,j] < 2: b[i,j] = 0                 # die
            if n[i,j] == 3: b[i,j] = 1                # birth

    return b






w = 60
h = 60


# random setup
board = setup_board()
'''
# glider gun
board = np.zeros((w,h))
glider_gun = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
 [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
 [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

board[10:19,1:37] = glider_gun
'''


def init():

    global board 

    im.set_data(board)
    return (im, )


def animate(i):
    
    global board

    neighbors = count_neighbors()
    new_board = update_board(neighbors, board)
    board = new_board

    im = ax.imshow(new_board, cmap=plt.cm.magma, interpolation='nearest')

    return (im, )







# set up graphics
figure = plt.figure(figsize=(12,12))
ax = figure.add_subplot(111)
im = ax.imshow(board, cmap=plt.cm.binary, interpolation='nearest')
im.set_clim(-0.05, 1 )



anim = animation.FuncAnimation(figure, animate, init_func=init, frames=100, interval=1000, blit=False)


plt.title("Conway's Life")  
plt.axis('off')          
plt.show()

