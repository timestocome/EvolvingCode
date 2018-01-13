

# http://github.com/timestocome

# Flocking example
# http://www.red3d.com/cwr/boids/



import pygame
import sys
import numpy as np



pygame.init()


size = width, height = 1000, 1000
white = 255, 255, 255
screen = pygame.display.set_mode(size)
screen.fill(white)



# boids
distance = 100 # max distance at which boid sees neighbors
separation = 5 # preferred minimum separation between boids
boids = []


class Boid():

    def __init__(self):

        # set up image
        self.boid_image = pygame.image.load("images.png")
        self.boid_rect = self.boid_image.get_rect()
        self.boid_copy = self.boid_image

        # random starting angle, location, speed
        self.angle = np.random.randint(360)
        
        self.x = np.random.randint(width)
        self.y = np.random.randint(height)

        self.vx = 0 
        self.vy = 0

        self.speed = np.random.randint(low=2, high=6)

        # move to starting position
        self.boid_rect = self.boid_rect.move((self.x, self.y))    
        self.boid_image = pygame.transform.rotate(self.boid_copy, self.angle)
        self.boid_rect = self.boid_image.get_rect(center=self.boid_rect.center)


        # start with no neighbors
        self.neighbors = []



    # still need to remove neighbors in blind spot
    def find_neigbors(self):

        self.neighbors = []
        flock_heading = 0
        center_x = 0
        center_y = 0
        crowding_heading = 0
        n_neighbors = -1  # remove self
        n_crowd = 0
        
        
        for i in range(len(boids)):

            r = np.sqrt( np.square(boids[i].x - self.x) + np.square(boids[i].y - self.y))

            if r < distance:
                self.neighbors.append(boids[i])
                center_x += boids[i].x
                center_y += boids[i].y
                flock_heading += boids[i].angle
                n_neighbors += 1
                
                
                if r < separation:
                    crowding_heading += boids[i].angle
                    n_crowd += 1

            
        if n_neighbors > 0:      
            # get means
            center_x /= n_neighbors
            center_y /= n_neighbors
            flock_heading /= n_neighbors
       
            
        if n_crowd > 0:
            crowding_heading /= n_crowd
            
        return n_neighbors, flock_heading, center_x, center_y, crowding_heading

        

    def move(self):

        
        # adjustments for flock
        n, flock_direction, flock_x, flock_y, crowd_heading = self.find_neigbors()

        if n > 0:
            self.angle = (self.angle + flock_direction) // 3
            self.angle -= crowd_heading // 5
            

        # move
        self.vx = -self.speed * np.sin(self.angle * 0.0174533) 
        self.vy = -self.speed * np.cos(self.angle * 0.0174533)
       # print('vx %d, vy %d, angle %d, %lf, speed %d' % (self.vx, self.vy, self.angle, self.angle * 0.0174533, self.speed))

        self.boid_rect = self.boid_rect.move((self.vx, self.vy))
        self.boid_rect = self.boid_image.get_rect(center=self.boid_rect.center)

        
        # rotate
        self.angle = (self.angle + 1) % 360
        self.boid_image = pygame.transform.rotate(self.boid_copy, self.angle)

       
        # deal with edges
        if self.boid_rect.center[0] < 0:
            self.boid_rect = self.boid_rect.move((width-self.vx, self.vy))
            
        if self.boid_rect.center[0] > width:
            self.angle = (self.angle - 30) % 360
            self.boid_rect = self.boid_rect.move((-2 * self.vx, self.vy))

        if self.boid_rect.center[1] < 0:
            self.boid_rect = self.boid_rect.move((self.vx, height-self.vy))

        if self.boid_rect.center[1] > height:
            self.angle = (self.angle + 30) %360
            self.boid_rect = self.boid_rect.move((self.vx, -2 * self.vy))

            
        self.boid_image = pygame.transform.rotate(self.boid_copy, self.angle)
            
        self.boid_rect = self.boid_rect.move((self.vx, self.vy))
        self.boid_rect = self.boid_image.get_rect(center=self.boid_rect.center)

        

            

# set up 
for i in range(50):
    new_boid = Boid()
    boids.append(new_boid)





    
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    screen.fill(white)
    
    for b in range(len(boids)):

        boid = boids[b]
        boid.move()
        screen.blit(boid.boid_image, boid.boid_rect)

    pygame.display.flip()

