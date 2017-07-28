
# http://github.com/timestocome

# Flocking, herds and schools
# https://www.siggraph.org/education/materials/HyperGraph/animation/art_life/flocks.htm

# more good stuff
# https://www.siggraph.org/education/materials/HyperGraph/animation/art_life/art_life0.htm

# Flock is a group of objects that exhibit the general class of polarized (aligned), non-colliding, aggregate motion.
# Boid is a simulated bird-like object, i.e., it exhibits this type of behavior. It can be a fish, dinosaur, etc.

# 3 rules
# Collision avoidance: avoid collisions with neighbors or obstacles
# Velocity Matching: attempt to match velocity (speed and direction) with neighbors
# Flock centering: attempt to stay close to neighbors


# experimented a little
# hard edges produces flocking
# wrap around edges produces more of schooling behavior
# 
# sometimes they move fast
# sometimes they travel the edges
# other times they all settle in clumps


import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from matplotlib import animation
import copy



# create a 2d board to use for simulation
height = 300
width = height


# animation setup
# how many time steps animation should perform
n_steps = 10000
sleep = 1


# set number of boids
n_boids = 100


# limits
min_velocity = 1
max_velocity = 10

min_distance = 2


# constants
north = 0           # y-1
north_east = 1      # y-1, x+1
east = 2            # x+1
south_east = 3      # x+1, y+1
south = 4           # y+1
south_west = 5      # y+1, x-1
west = 6            # x-1
north_west = 7      # x-1, y-1 




############################################################################
# utilities
############################################################################

def new_location(x, y, v, d):


    if v < min_velocity: v += 1
    if v > max_velocity: v -= 1


    edge = width - (3 * v)
    

    if d == north:
        if (y - v) > 0: y -= v 
        else: 
            y = v
            d = np.random.randint(0, 7)

    elif d == north_east:
        if (y - v) > 0: y -= v 
        else: 
            y = v
            d = np.random.randint(0, 7)


        if (x + v) < edge: x += v
        else: 
            x = edge
            d = np.random.randint(0, 7)

    elif d == east:
        if (x + v) < edge: x += v
        else: 
            x = edge
            d = np.random.randint(0, 7)

    elif d == south_east:
        if (y + v) < edge: y += v
        else: 
            y = edge
            d = np.random.randint(0, 7)

        if (x + v) < edge: x += v
        else: 
            x = edge
            d = np.random.randint(0, 7)

    elif d == south:
        if (y + v) < edge: y += v
        else: 
            y = edge
            d = np.random.randint(0, 7)

    elif d == south_west:
        if (y + v) < edge: y += v
        else: 
            y = edge
            d = np.random.randint(0, 7)

        if (x - v) > 0: x -= v
        else: 
            x = v
            d = np.random.randint(0, 7)


    elif d == west:
        if (x - v) > 0: x -= v
        else: 
            x = v
            d = np.random.randint(0, 7)


    elif d == north_west:
        if (y - v) > 0: y -= v
        else: 
            y = v
            d = np.random.randint(0, 7)


        if (x - v) > 0: x -= v
        else: 
            x = v
            d = np.random.randint(0, 7)


    return int(x), int(y), v, d




############################################################################
# Flocking
############################################################################
class Boid(object):

    def __init__(self):

        self.x = np.random.randint(0, width-1)
        self.y = np.random.randint(0, height-1)
        self.velocity = np.random.randint(min_velocity, max_velocity)
        self.direction = np.random.randint(0, 7)





class FlockingModel(object):
    

    # set up boids in random locations, at random speeds and directions
    def __init__(self, n_steps=100):
        
        self.n_steps = n_steps
        self.next = 0

        self.board = np.zeros((height, width))
        self.boids = []


        # randomly place boids on board
        for i in range(n_boids):
            new_boid = Boid()
            self.boids.append(new_boid)
            self.board[new_boid.x][new_boid.y] = i



    # find neighbors and adjust boid speed, direction to mean
    def check_neighbors(self):

        #----------------------------------------------------------------------------------
        # count neighbors 2 steps away
        for i in range(1, n_boids):         # skip zero for now will deal with 0 issues later

            # get location of this bot
            boid = self.boids[i]
            x = boid.x
            y = boid.y

            # see if we have neighbors and stuff them in a list to process
            # start at 0, end at n+1
            #n_1 = self.board[x-1:x+2,y-1:y+2]
            neighbors = self.board[x-min_distance:x+min_distance+1, y-min_distance:y+min_distance+1]
            
            # update x, y, velocity, direction and board
            # yes, this includes self, that way we keep going same direction, velocity if no one else is nearby
            neighbor_boids = np.unique(neighbors)
            neighbor_boids = neighbor_boids[1:-1]       # remove zeros, lots of empty space around us
            n_neighbors = len(neighbor_boids)
            
            #--------------------------------------------------------------------------------
            # adapt speed and heading to local mean
            if n_neighbors > 0:

                velocity_mean = 0.
                direction_mean = 0.
                distance = 0.

                for i in range(0, n_neighbors):     # skip 0
                    #distance = np.sqrt((x - self.boids[int(neighbor_boids[i])].x) **2 +  (y - self.boids[int(neighbor_boids[i])].y) **2 )
                    distance += 1       # divide by zero

                    velocity_mean += self.boids[int(neighbor_boids[i])].velocity / distance **2
                    direction_mean += self.boids[int(neighbor_boids[i])].direction / distance **2
                    
                velocity_mean /= n_neighbors
                direction_mean /= n_neighbors
            
            # no neighbors - maintain speed and heading
            else:
                velocity_mean = boid.velocity
                direction_mean = boid.direction



            # ------------------------------------------------------------------------
            # move boid, update boid, update self.board

            # remove boid from self.board
            self.board[boid.x][boid.y] = 0


            # update boid x, y, velocity, direction
            if velocity_mean < max_velocity: 
                boid.velocity = velocity_mean

            if direction_mean <= 7 and direction_mean >=0:
                boid.direction = direction_mean

            # move if not off edge of world or on top of another boid
            boid.x, boid.y, boid.velocity, boid.direction = new_location(boid.x, boid.y, boid.velocity, boid.direction)

            # update self. board
            self.board[boid.x][boid.y] = i


        




    def step(self):

        self.next += 1

        self.check_neighbors()

        # make a copy of the board for animation 
        new_board = copy.copy(self.board)

        return new_board




    
    






########################################
# setup model
flockingModel = FlockingModel(n_steps)


# convert game board to an image
def image_from_array(array):

    z_im = np.zeros((height, width, 3), 'uint8')

    for i in range(n_boids):
        x = flockingModel.boids[i].x
        y = flockingModel.boids[i].y
        
        z_im[x][y][0] = 55      # red
        z_im[x][y][1] = 155     # green 
        z_im[x][y][2] = 255     # blue

    im = ax.imshow(z_im, interpolation='nearest')
    return im



# animation loop computes one row at a time for display
def animate(i):
    
    ax.clear()      # things get very slow if this line is missing
    im = image_from_array(flockingModel.step())

    return (im, )
    


# set up graphics
figure = plt.figure(figsize=(12,12))
ax = figure.add_subplot(111)
plt.title("Flocking Model")  
plt.axis('off')   

im = image_from_array(flockingModel.board)



# run program
# note: blit=False needed to run on OSX, probably faster if set to True on other platforms
anim = animation.FuncAnimation(figure, animate, frames=(n_steps-2), interval=sleep, blit=False, repeat=False)

plt.show()

