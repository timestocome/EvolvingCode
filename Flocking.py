
# http://github.com/timestocome

# Flocking take 2

# Flocking, herds and schools
# https://www.siggraph.org/education/materials/HyperGraph/animation/art_life/flocks.htm

# more good stuff
# https://www.siggraph.org/education/materials/HyperGraph/animation/art_life/art_life0.htm
# http://www.red3d.com/cwr/papers/1987/SIGGRAPH87.pdf

# Flock is a group of objects that exhibit the general class of polarized (aligned), non-colliding, aggregate motion.
# Boid is a simulated bird-like object, i.e., it exhibits this type of behavior. It can be a fish, dinosaur, etc.

# 3 rules
# Collision avoidance: avoid collisions with neighbors or obstacles
# Velocity Matching: attempt to match velocity (speed and direction) with neighbors
# Flock centering: attempt to stay close to neighbors



import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import copy


# create a 2d board to use for simulation
height = 300
width = height

# how many time steps animation should perform
n_steps = 10000
sleep = 1


# set number of boids
n_boids = 140

# distance neighbors are visable
radius = 30

# max number of pixels moved per time step
max_speed = 12





# smoother
def deg_to_rad(d): return d / 57.3
def rad_to_deg(r): return r * 57.3

n_directions = 360
directions = range(0, 360)

############################################################################
# utilities
############################################################################

# not optimal but it's a toy problem
def neighborhood(x, y, boids):

    neighbors = []
     
    for b in boids:

        d = b.d % 360

        # see if other boid is close to us
        dx = np.sqrt( (b.x-x)*(b.x-x) + (b.y-y)*(b.y-y) )
        
        # it's inside circle
        if dx <= radius:

            # see if it's in ~180' of direction we're facing
            if (d > 45) and (d < 135):    # N  
                if b.y > y: neighbors.append(b)
                
            if (d > 0) and (d < 90):    # NE   equation written out for clarity
                if b.y > (-1)*b.x + (x+y): neighbors.append(b) 
                
            if ((d > 315) and (d < 360)) or ((d > 0) and (d < 45)):    # E 
                if b.x > x: neighbors.append(b)
                
            if (d > 270) and (d < 360):    # SE 
                if b.y < b.x + (y-x): neighbors.append(b)
                
            if (d > 225) and (d < 315):    # S 
                if b.y < y: neighbors.append(b)
                    
            if (d > 180) and (d < 270):    # SW 
                if b.y < -b.x + (x+y): neighbors.append(b)
                
            if (d > 135) and (d < 225):    # W 
                if b.x < x: neighbors.append(b)
                
            if (d < 90) and (d < 180):    # NW
                if b.y > b.x + (y-x): neighbors.append(b)


    return neighbors





    

############################################################################
# Flocking
############################################################################
class Boid(object):

    def __init__(self):

        self.x = np.random.randint(0, width-1)
        self.y = np.random.randint(0, height-1)
        self.d = np.random.randint(n_directions)
        self.v = np.random.randint(max_speed)
        

    def update(self, neighbors):

        # adjust to neighbors
        n_neighbors = len(neighbors)

        if n_neighbors > 0:

            dv = 0.
            dd = np.zeros(n_directions)
            dx = 0.
            dy = 0.
            crowding = 0
            
            for n in neighbors:
 
                # alignment: get average heading and speed
                dv += n.v / n_neighbors
                dd[int(n.d)] += 1
               
                        
                # separation: check for crowding and spread out
                dr = np.sqrt( (n.x-self.x)*(n.x-self.x) + (n.y-self.y)*(n.y-self.y) )
                if dr < 5:
                    crowding += 1

                else:
                    
                    # cohesion: center of flock
                    dx += n.x / n_neighbors
                    dy += n.y / n_neighbors


                
            # alignment: change heading closer to neighbors
            popular = np.max(dd)               # find n max agreeing
            winners = np.argwhere(dd == popular)   # get most popular headings

            if len(winners) > 1:               # if more than one randomly choose one
                new_idx = np.random.randint(len(winners))
                self.d = winners[new_idx]
            else: self.d = np.argmax(dd)      # else just go with single most popular

                        
            
            # cohesion: move towards center of flock
            if self.x > dx: dx -= self.v // 2
            else: dx += self.v 

            if self.y > dy: dy -= self.v // 2
            else: dy += self.v
            

           
            
            #print(' d %d, v %d neighbors %d' %( self.d, self.v, n_neighbors))
            
        else:   # no neighbors occasionally decide to change direction or move
            z = np.random.randint(max_speed * 2)
            if z % 4 == 0:
                self.v = z
                self.d = np.random.randint(n_directions)


        

        # move in direction boid is facing
        dx = int(self.v * np.cos(deg_to_rad(self.d)))
        self.x += dx
                  
        dy = int(self.v * np.sin(deg_to_rad(self.d)))
        self.y += dy



        # wrap on or rebound at edges
        new_d = np.random.randint(n_directions)

        if self.x <= 0:
            self.x = self.v
            self.d = new_d
            
        if self.y <= 0:
            self.y = self.v
            self.d = new_d

        if self.x >= width:
            self.x = self.v
            self.d = new_d

        if self.y >= height:
            self.y = self.v
            self.d = new_d
        

        
################################################################################
# run code
###############################################################################

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

        for i in range(n_boids):      
            
            # get location of this boid
            boid = self.boids[i]
            x = boid.x
            y = boid.y

                        
            # get neighbors boid can see
            neighbors = neighborhood(x, y, self.boids)
            n_neighbors = len(neighbors)

            # adapt speed and heading to local mean
            boid.update(neighbors)
               
            
            # remove boid from self.board
            self.board[x][y] = 0
            
            # update self. board
            self.board[boid.x][boid.y] = i


        
    # next time step
    def step(self):

        self.next += 1
        self.check_neighbors()

        # make a copy of the board for animation 
        new_board = copy.copy(self.board)

        return new_board




    
    






#####################################################################################
# setup model
#####################################################################################

flockingModel = FlockingModel(n_steps)



#####################################################################################
# animation
#####################################################################################

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

