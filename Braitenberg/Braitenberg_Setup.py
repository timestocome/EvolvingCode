
# http://github.com/timestocome

# Test run to see if I can do some software simulations
# then reproduce them in hardware


# Braitenberg Vehicle Simulation
# https://mitpress.mit.edu/books/vehicles
# Elements of Robotics, Springer 2018


# input is distance measure from sound echo, front, rear, left, right
# right and left wheels can turn individually


import pygame
import sys
import numpy as np
import time
import math



# environment
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
purple = (200, 0, 200)


size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
screen.fill(white)


n_cars = 9     # 9 possible image files
total_cars = 9
car_count = 0
cars = []

n_trees = 7    # 7 possible image files
total_trees = 21
tree_count = 0
trees = []


# HC SR204 object finder
sensor_max = 400    # 400 cm
sensor_angle = 15   # 15'


# wheel speed
speed = 5



##########################################################
# utility functions
##########################################################

def degrees_to_radians(d):
    return d / 57.3

def radians_to_degrees(r):
    return r * 57.3

def distance(x1, y1, x2, y2):
    return np.sqrt( (x1-x2)**2 + (y1-y2)**2 )



#########################################################
# sprites
#########################################################

# add obstacles
class Tree():

    
    def __init__(self):

        count = tree_count % n_trees + 1
        
        # load image
        self.image_file = 'tree_' + str(count) + '.png'
        self.image = pygame.image.load(self.image_file)
        self.rect = self.image.get_rect()
        self.copy = self.image

        # plant in random location
        self.x = np.random.randint(width)
        self.y = np.random.randint(height)

        # move to location
        self.rect = self.rect.move((self.x, self.y))
        self.rect = self.image.get_rect(center=self.rect.center)



        
# add cars
class Car():

    
    def __init__(self):

        count = car_count % n_cars + 1

        # sensors default is off
        self.left_sensor = 0
        self.right_sensor = 0
        self.front_sensor = 0
        self.rear_sensor = 0
       

        # motion when active sensors are tripped
        self.move_forward = 0    # move towards objects in sight
        self.move_reverse = 0    # move away from objects in sight
        self.turn_left = 0
        self.turn_right = 0
        
        
        if count == 1:
            self.left_sensor = 1
            self.right_sensor = 1
            
            self.move_forward = 1

        if count == 2:
            self.left_sensor = 1
            self.right_sensor = 1
            self.front_sensor = 1
            
            self.move_forward = 1
            
        if count == 3:
            self.rear_sensor = 1
            
            self.move_forward = 1
            
        if count == 4: 
            self.left_sensor = 1
            self.right_sensor = 1
            self.rear_sensor = 1

            self.move_forward = 1
            
        if count == 5: 
            self.front_sensor = 1

            self.move_forward = 1
            
        if count == 6: 
            self.left_sensor = 1

            self.move_forward = 1
            
        if count == 7: 
            self.left_sensor = 1
            self.right_sensor = 1
            
            self.move_forward = 1
            
        if count == 8: 
            self.front_sensor = 1

            self.move_forward = 1
            
        if count == 9: 
            self.rear_sensor = 1
            self.move_forward = 1
            
        

        # images
        image_file = 'car_' + str(count) + '.png'
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.copy = self.image

        # random starting location and angle
        degrees = np.random.randint(360)
        self.angle_rads = degrees_to_radians(degrees)
        self.x = np.random.randint(width)
        self.y = np.random.randint(height)

        # move to starting location
        self.rect = self.rect.move((self.x, self.y))
        self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))
        self.rect = self.image.get_rect(center=self.rect.center)



        
   
    def line_of_sight(self, x_obstacle, y_obstacle, direction):
        
        front = 0
        right = 0
        rear = 0
        left = 0

        r = np.sqrt( (x_obstacle - self.x)**2 + (y_obstacle - self.y)**2 )

        if r < sensor_max and r > 0:
            
             # front view
             view_angle = (direction - 180) % 360
             sensor_x = sensor_max * np.sin(view_angle/57.3) + self.x
             sensor_y = sensor_max * np.cos(view_angle/57.3) + self.y

             dot = (x_obstacle - self.x) * (sensor_x - self.x) + (y_obstacle - self.y) * (sensor_y - self.y)
             sensor_reach = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )
             angle = math.acos( dot / (r * sensor_reach)) * 57.3
            
             if angle < sensor_angle:
                pygame.draw.line(screen, red, (self.x, self.y), (x_obstacle, y_obstacle))
                front = 1


             # rear view
             view_angle = direction
             sensor_x = sensor_max * np.sin(view_angle/57.3) + self.x
             sensor_y = sensor_max * np.cos(view_angle/57.3) + self.y

             dot = (x_obstacle - self.x) * (sensor_x - self.x) + (y_obstacle - self.y) * (sensor_y - self.y) 
             sensor_reach = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )
             angle = math.acos( dot / (r * sensor_reach)) * 57.3

             if angle < sensor_angle:
                pygame.draw.line(screen, blue, (self.x, self.y), (x_obstacle, y_obstacle))
                rear = 1

                
             # left view
             view_angle = direction - 90
             sensor_x = sensor_max * np.sin(view_angle/57.3) + self.x
             sensor_y = sensor_max * np.cos(view_angle/57.3) + self.y
            
             dot = (x_obstacle - self.x) * (sensor_x - self.x) + (y_obstacle - self.y) * (sensor_y - self.y) 
             sensor_reach = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )
             angle = math.acos( dot / (r * sensor_reach)) * 57.3

             if angle < sensor_angle:
                pygame.draw.line(screen, green, (self.x, self.y), (x_obstacle, y_obstacle))
                left = 1
             

             # right view
             view_angle = direction + 90
             sensor_x = sensor_max * np.sin(view_angle/57.3) + self.x
             sensor_y = sensor_max * np.cos(view_angle/57.3) + self.y

             dot = (x_obstacle - self.x) * (sensor_x - self.x) + (y_obstacle - self.y) * (sensor_y - self.y) 
             sensor_reach = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )
             angle = math.acos( dot / (r * sensor_reach)) * 57.3

             if angle < sensor_angle:
                pygame.draw.line(screen, purple, (self.x, self.y), (x_obstacle, y_obstacle))
                right = 1
             
        return front, left, rear, right

            

            

    def move(self):


        self.x = self.rect.center[0]
        self.y = self.rect.center[1]
        
        # first check sensors [front, left, rear, right]
        tripped_sensor = np.zeros(4)

        # are there trees in view?
        for t in trees:
           tx = t.rect.center[0]
           ty = t.rect.center[1]

           f, l, rr, r = self.line_of_sight(tx, ty, radians_to_degrees(self.angle_rads))
           tripped_sensor[0] += f
           tripped_sensor[1] += l
           tripped_sensor[2] += rr
           tripped_sensor[3] += r

        
        # are there other cars in view?
        for c in cars:
            cx = c.rect.center[0]
            cy = c.rect.center[1]

            f, l, rr, r = self.line_of_sight(cx, cy, radians_to_degrees(self.angle_rads))
            tripped_sensor[0] += f
            tripped_sensor[1] += r
            tripped_sensor[2] += rr
            tripped_sensor[3] += l



        # find sensor that is on that has loudest incoming signal
        # void out sensors that aren't on
        if self.front_sensor == 0: tripped_sensor[0] = -1
        if self.left_sensor == 0: tripped_sensor[1] = -1
        if self.rear_sensor == 0: tripped_sensor[2] = -1
        if self.right_sensor == 0: tripped_sensor[3] = -1
            
        # find strongest signal
        max_sensor = np.argmax(tripped_sensor)
        direction = -1
        
        if max_sensor == 0: direction = 0      # front
        elif max_sensor == 1: direction = 1 # left
        elif max_sensor == 2: direction = 2 # rear
        elif max_sensor == 3: direction = 3 # right
        

        
        # move towards strongest sensor signal
        if self.move_forward > 0:

            if direction == 0:
                vx = -speed * np.sin(self.angle_rads)
                vy = -speed * np.cos(self.angle_rads)

                self.rect = self.rect.move(vx, vy)
                self.rect = self.image.get_rect(center=self.rect.center)

                
            elif direction == 1:
                
                self.angle_rads += 1/8
                self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))
                
                vx = -speed * np.sin(self.angle_rads)
                vy = -speed * np.cos(self.angle_rads)

                self.rect = self.rect.move(vx, vy)
                self.rect = self.image.get_rect(center=self.rect.center)
                
                
            elif direction == 2:

                 vx = speed * np.sin(self.angle_rads)
                 vy = speed * np.cos(self.angle_rads)

                 self.rect = self.rect.move(vx, vy)
                 self.rect = self.image.get_rect(center=self.rect.center)

                
            elif direction == 3:
                
                self.angle_rads -= 1/8
                self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

                vx = -speed * np.sin(self.angle_rads)
                vy = -speed * np.cos(self.angle_rads)
                
                self.rect = self.rect.move(vx, vy)
                self.rect = self.image.get_rect(center=self.rect.center)
                
    

            
        # edge detection, wrap
        x = self.rect.center[0]
        y = self.rect.center[1]

        if self.rect.center[0] < 0: x = width + self.rect.center[0]
        if self.rect.center[0] > width: x = self.rect.center[0] -  width
        if self.rect.center[1] < 0: y = height + self.rect.center[1]
        if self.rect.center[1] > height: y = self.rect.center[1] - height
        self.rect.center = (x, y)
    
    


# set up
for i in range(total_cars):
    new_car = Car()
    car_count += 1
    cars.append(new_car)


for i in range(total_trees):
    new_tree = Tree()
    tree_count += 1
    trees.append(new_tree)





# main loop
while(True):

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        
    screen.fill(white)

    for v in cars:        
        car = v
        car.move()
        screen.blit(car.image, car.rect)

    
    for t in trees:
        tree = t
        screen.blit(tree.image, tree.rect)
    

    pygame.display.flip()


        
        
        

   
