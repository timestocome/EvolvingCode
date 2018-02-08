
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


n_love_cars = 6
n_explorer_cars = 6
n_coward_cars = 6
n_aggressive_cars = 6


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




        


class Car_Love():

    def __init__(self):

        # images
        image_file = 'car_1.png'
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.copy = self.image

        # random starting point
        degrees = np.random.randint(360)
        self.angle_rads = degrees_to_radians(degrees)
        self.x = np.random.randint(width)
        self.y = np.random.randint(height)

        # move to starting location
        self.rect = self.rect.move((self.x, self.y))
        self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))
        self.rect = self.image.get_rect(center=self.rect.center)



    def line_of_sight(self, x_obstacle, y_obstacle, direction):
        

        # check front only
        dr = np.sqrt((x_obstacle - self.x)**2 + (y_obstacle - self.y)**2)
        dx = x_obstacle - self.x
        dy = y_obstacle - self.y

        

        # if object in sensor range
        if dr > 0 and dr < sensor_max:

            # compute angle
            r_view_angle = (direction - 183) % 360  # game board has rotated compass
            l_view_angle = (direction - 177) % 360
            view_angle = (direction - 180) % 360

            
            # look left
            xl = sensor_max * np.sin(degrees_to_radians(l_view_angle)) + self.x
            yl = sensor_max * np.cos(degrees_to_radians(l_view_angle)) + self.y
            rl = np.sqrt( (xl - self.x)**2 + (yl - self.y)**2 )
            pygame.draw.line(screen, green, (self.x, self.y), (xl, yl))

            
            if (dr * rl) > 0:
                dot_l = dx * (xl - self.x) + dy * (yl - self.y)
                angle_l = radians_to_degrees(math.acos(dot_l / (dr * rl)))
        

            # look right
            xr = sensor_max * np.sin(degrees_to_radians(r_view_angle)) + self.x
            yr = sensor_max * np.cos(degrees_to_radians(r_view_angle)) + self.y
            rr = np.sqrt( (xr - self.x)**2 + (yr - self.y)**2)
            pygame.draw.line(screen, blue, (self.x, self.y), (xr, yr))

            if (dr * rr) > 0:
                dot_r = dx * (xr - self.x) + dy * (yr - self.y)
                angle_r = radians_to_degrees(math.acos(dot_r / (dr * rr)))
           

                
            # point sensor_max and sensor angle away from car
            sensor_x = sensor_max * np.sin(degrees_to_radians(view_angle)) + self.x
            sensor_y = sensor_max * np.cos(degrees_to_radians(view_angle)) + self.y
            sensor_r = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )

            pygame.draw.line(screen, red, (self.x, self.y), (sensor_x, sensor_y))

            # angle between line of sight and object
            if dr > 0:
                dot = dx * (sensor_x - self.x) + dy * (sensor_y - self.y)     
                angle = radians_to_degrees( math.acos( dot / (dr * sensor_r)) )


            

            
            # check if angle in sensor range
            if angle < sensor_angle:
                if angle_l < angle_r:
                    return (1, 1)
                else:
                    return (1, -1)
           
        return (0,0)

                

    def move(self):


        # update location
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

       
        # check sensor
        tripped_sensor = 0
        object_angle = 0
        
        for t in trees:
            tx = t.rect.center[0]
            ty = t.rect.center[1]

            object_detected, angle = self.line_of_sight(tx, ty, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle

        for c in cars:
            cx = c.rect.center[0]
            cy = c.rect.center[1]

            object_detected, angle = self.line_of_sight(cx, cy, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle
        
        # something is in our view range
        if object_angle < 0:
            self.angle_rads -= 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

        if object_angle > 0:
            self.angle_rads += 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

            
        if tripped_sensor > 0:

            vx = -speed * np.sin(self.angle_rads)
            vy = -speed * np.cos(self.angle_rads)

            self.rect = self.rect.move(vx, vy)
            self.rect = self.image.get_rect(center=self.rect.center)

     
    

        # edge detection, wrapping
        x = self.rect.center[0]
        y = self.rect.center[1]

        if self.rect.center[0] < 0: x = width + self.rect.center[0]
        if self.rect.center[0] > width: x = self.rect.center[0] -  width
        if self.rect.center[1] < 0: y = height + self.rect.center[1]
        if self.rect.center[1] > height: y = self.rect.center[1] - height
        self.rect.center = (x, y)
    
    



                



class Car_Explorer():

    def __init__(self):

        # images
        image_file = 'car_2.png'
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.copy = self.image

        # random starting point
        degrees = np.random.randint(360)
        self.angle_rads = degrees_to_radians(degrees)
        self.x = np.random.randint(width)
        self.y = np.random.randint(height)

        # move to starting location
        self.rect = self.rect.move((self.x, self.y))
        self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))
        self.rect = self.image.get_rect(center=self.rect.center)



    def line_of_sight(self, x_obstacle, y_obstacle, direction):
        

        # check front only
        dr = np.sqrt((x_obstacle - self.x)**2 + (y_obstacle - self.y)**2)
        dx = x_obstacle - self.x
        dy = y_obstacle - self.y

        

        # if object in sensor range
        if dr > 0 and dr < sensor_max:

            # compute angle
            r_view_angle = (direction - 183) % 360  # game board has rotated compass
            l_view_angle = (direction - 177) % 360
            view_angle = (direction - 180) % 360

            
            # look left
            xl = sensor_max * np.sin(degrees_to_radians(l_view_angle)) + self.x
            yl = sensor_max * np.cos(degrees_to_radians(l_view_angle)) + self.y
            rl = np.sqrt( (xl - self.x)**2 + (yl - self.y)**2 )
            pygame.draw.line(screen, green, (self.x, self.y), (xl, yl))

            
            if (dr * rl) > 0:
                dot_l = dx * (xl - self.x) + dy * (yl - self.y)
                angle_l = radians_to_degrees(math.acos(dot_l / (dr * rl)))
        

            # look right
            xr = sensor_max * np.sin(degrees_to_radians(r_view_angle)) + self.x
            yr = sensor_max * np.cos(degrees_to_radians(r_view_angle)) + self.y
            rr = np.sqrt( (xr - self.x)**2 + (yr - self.y)**2)
            pygame.draw.line(screen, blue, (self.x, self.y), (xr, yr))

            if (dr * rr) > 0:
                dot_r = dx * (xr - self.x) + dy * (yr - self.y)
                angle_r = radians_to_degrees(math.acos(dot_r / (dr * rr)))
           

                
            # point sensor_max and sensor angle away from car
            sensor_x = sensor_max * np.sin(degrees_to_radians(view_angle)) + self.x
            sensor_y = sensor_max * np.cos(degrees_to_radians(view_angle)) + self.y
            sensor_r = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )

            pygame.draw.line(screen, red, (self.x, self.y), (sensor_x, sensor_y))

            # angle between line of sight and object
            if dr > 0:
                dot = dx * (sensor_x - self.x) + dy * (sensor_y - self.y)     
                angle = radians_to_degrees( math.acos( dot / (dr * sensor_r)) )


            

            
            # check if angle in sensor range
            if angle < sensor_angle:
                if angle_l < angle_r:
                    return (1, 1)
                else:
                    return (1, -1)
           
        return (0,0)

                

    def move(self):


        # update location
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

       
        # check sensor
        tripped_sensor = 0
        object_angle = 0
        
        for t in trees:
            tx = t.rect.center[0]
            ty = t.rect.center[1]

            object_detected, angle = self.line_of_sight(tx, ty, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle

        for c in cars:
            cx = c.rect.center[0]
            cy = c.rect.center[1]

            object_detected, angle = self.line_of_sight(cx, cy, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle
        
        # something is in our view range
        if object_angle < 0:
            self.angle_rads += 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

        if object_angle > 0:
            self.angle_rads -= 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

            
        if tripped_sensor > 0:

            vx = -speed * np.sin(self.angle_rads)
            vy = -speed * np.cos(self.angle_rads)

            self.rect = self.rect.move(vx, vy)
            self.rect = self.image.get_rect(center=self.rect.center)

     
    

        # edge detection, wrapping
        x = self.rect.center[0]
        y = self.rect.center[1]

        if self.rect.center[0] < 0: x = width + self.rect.center[0]
        if self.rect.center[0] > width: x = self.rect.center[0] -  width
        if self.rect.center[1] < 0: y = height + self.rect.center[1]
        if self.rect.center[1] > height: y = self.rect.center[1] - height
        self.rect.center = (x, y)
    
    






class Car_Coward():

    def __init__(self):

        # images
        image_file = 'car_3.png'
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.copy = self.image

        # random starting point
        degrees = np.random.randint(360)
        self.angle_rads = degrees_to_radians(degrees)
        self.x = np.random.randint(width)
        self.y = np.random.randint(height)

        # move to starting location
        self.rect = self.rect.move((self.x, self.y))
        self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))
        self.rect = self.image.get_rect(center=self.rect.center)



    def line_of_sight(self, x_obstacle, y_obstacle, direction):
        

        # check front only
        dr = np.sqrt((x_obstacle - self.x)**2 + (y_obstacle - self.y)**2)
        dx = x_obstacle - self.x
        dy = y_obstacle - self.y

        

        # if object in sensor range
        if dr > 0 and dr < sensor_max:

            # compute angle
            r_view_angle = (direction - 183) % 360  # game board has rotated compass
            l_view_angle = (direction - 177) % 360
            view_angle = (direction - 180) % 360

            
            # look left
            xl = sensor_max * np.sin(degrees_to_radians(l_view_angle)) + self.x
            yl = sensor_max * np.cos(degrees_to_radians(l_view_angle)) + self.y
            rl = np.sqrt( (xl - self.x)**2 + (yl - self.y)**2 )
            pygame.draw.line(screen, green, (self.x, self.y), (xl, yl))

            
            if (dr * rl) > 0:
                dot_l = dx * (xl - self.x) + dy * (yl - self.y)
                angle_l = radians_to_degrees(math.acos(dot_l / (dr * rl)))
        

            # look right
            xr = sensor_max * np.sin(degrees_to_radians(r_view_angle)) + self.x
            yr = sensor_max * np.cos(degrees_to_radians(r_view_angle)) + self.y
            rr = np.sqrt( (xr - self.x)**2 + (yr - self.y)**2)
            pygame.draw.line(screen, blue, (self.x, self.y), (xr, yr))

            if (dr * rr) > 0:
                dot_r = dx * (xr - self.x) + dy * (yr - self.y)
                angle_r = radians_to_degrees(math.acos(dot_r / (dr * rr)))
           

                
            # point sensor_max and sensor angle away from car
            sensor_x = sensor_max * np.sin(degrees_to_radians(view_angle)) + self.x
            sensor_y = sensor_max * np.cos(degrees_to_radians(view_angle)) + self.y
            sensor_r = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )

            pygame.draw.line(screen, red, (self.x, self.y), (sensor_x, sensor_y))

            # angle between line of sight and object
            if dr > 0:
                dot = dx * (sensor_x - self.x) + dy * (sensor_y - self.y)     
                angle = radians_to_degrees( math.acos( dot / (dr * sensor_r)) )


            

            
            # check if angle in sensor range
            if angle < sensor_angle:
                if angle_r < angle_r:   # swap angles
                    return (1, 1)
                else:
                    return (1, -1)
           
        return (0,0)

                

    def move(self):


        # update location
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

       
        # check sensor
        tripped_sensor = 0
        object_angle = 0
        
        for t in trees:
            tx = t.rect.center[0]
            ty = t.rect.center[1]

            object_detected, angle = self.line_of_sight(tx, ty, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle

        for c in cars:
            cx = c.rect.center[0]
            cy = c.rect.center[1]

            object_detected, angle = self.line_of_sight(cx, cy, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle
        
        # something is in our view range
        if object_angle < 0:
            self.angle_rads += 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

        if object_angle > 0:
            self.angle_rads -= 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

            
        if tripped_sensor > 0:

            vx = -speed * np.sin(self.angle_rads)
            vy = -speed * np.cos(self.angle_rads)

            self.rect = self.rect.move(vx, vy)
            self.rect = self.image.get_rect(center=self.rect.center)

     
    

        # edge detection, wrapping
        x = self.rect.center[0]
        y = self.rect.center[1]

        if self.rect.center[0] < 0: x = width + self.rect.center[0]
        if self.rect.center[0] > width: x = self.rect.center[0] -  width
        if self.rect.center[1] < 0: y = height + self.rect.center[1]
        if self.rect.center[1] > height: y = self.rect.center[1] - height
        self.rect.center = (x, y)
    
    





class Car_Aggressive():

    def __init__(self):

        # images
        image_file = 'car_4.png'
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.copy = self.image

        # random starting point
        degrees = np.random.randint(360)
        self.angle_rads = degrees_to_radians(degrees)
        self.x = np.random.randint(width)
        self.y = np.random.randint(height)

        # move to starting location
        self.rect = self.rect.move((self.x, self.y))
        self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))
        self.rect = self.image.get_rect(center=self.rect.center)



    def line_of_sight(self, x_obstacle, y_obstacle, direction):
        

        # check front only
        dr = np.sqrt((x_obstacle - self.x)**2 + (y_obstacle - self.y)**2)
        dx = x_obstacle - self.x
        dy = y_obstacle - self.y

        

        # if object in sensor range
        if dr > 0 and dr < sensor_max:

            # compute angle
            r_view_angle = (direction - 183) % 360  # game board has rotated compass
            l_view_angle = (direction - 177) % 360
            view_angle = (direction - 180) % 360

            
            # look left
            xl = sensor_max * np.sin(degrees_to_radians(l_view_angle)) + self.x
            yl = sensor_max * np.cos(degrees_to_radians(l_view_angle)) + self.y
            rl = np.sqrt( (xl - self.x)**2 + (yl - self.y)**2 )
            pygame.draw.line(screen, green, (self.x, self.y), (xl, yl))

            
            if (dr * rl) > 0:
                dot_l = dx * (xl - self.x) + dy * (yl - self.y)
                angle_l = radians_to_degrees(math.acos(dot_l / (dr * rl)))
        

            # look right
            xr = sensor_max * np.sin(degrees_to_radians(r_view_angle)) + self.x
            yr = sensor_max * np.cos(degrees_to_radians(r_view_angle)) + self.y
            rr = np.sqrt( (xr - self.x)**2 + (yr - self.y)**2)
            pygame.draw.line(screen, blue, (self.x, self.y), (xr, yr))

            if (dr * rr) > 0:
                dot_r = dx * (xr - self.x) + dy * (yr - self.y)
                angle_r = radians_to_degrees(math.acos(dot_r / (dr * rr)))
           

                
            # point sensor_max and sensor angle away from car
            sensor_x = sensor_max * np.sin(degrees_to_radians(view_angle)) + self.x
            sensor_y = sensor_max * np.cos(degrees_to_radians(view_angle)) + self.y
            sensor_r = np.sqrt( (sensor_x - self.x)**2 + (sensor_y - self.y)**2 )

            pygame.draw.line(screen, red, (self.x, self.y), (sensor_x, sensor_y))

            # angle between line of sight and object
            if dr > 0:
                dot = dx * (sensor_x - self.x) + dy * (sensor_y - self.y)     
                angle = radians_to_degrees( math.acos( dot / (dr * sensor_r)) )


            

            
            # check if angle in sensor range
            if angle < sensor_angle:
                if angle_l > angle_r:    # swap angles
                    return (1, 1)
                else:
                    return (1, -1)
           
        return (0,0)

                

    def move(self):


        # update location
        self.x = self.rect.center[0]
        self.y = self.rect.center[1]

       
        # check sensor
        tripped_sensor = 0
        object_angle = 0
        
        for t in trees:
            tx = t.rect.center[0]
            ty = t.rect.center[1]

            object_detected, angle = self.line_of_sight(tx, ty, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle

        for c in cars:
            cx = c.rect.center[0]
            cy = c.rect.center[1]

            object_detected, angle = self.line_of_sight(cx, cy, radians_to_degrees(self.angle_rads))
            tripped_sensor += object_detected
            object_angle += angle
        
        # something is in our view range
        if object_angle < 0:
            self.angle_rads -= 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

        if object_angle > 0:
            self.angle_rads += 1/10
            self.image = pygame.transform.rotate(self.copy, radians_to_degrees(self.angle_rads))

            
        if tripped_sensor > 0:

            vx = -speed * np.sin(self.angle_rads)
            vy = -speed * np.cos(self.angle_rads)

            self.rect = self.rect.move(vx, vy)
            self.rect = self.image.get_rect(center=self.rect.center)

     
    

        # edge detection, wrapping
        x = self.rect.center[0]
        y = self.rect.center[1]

        if self.rect.center[0] < 0: x = width + self.rect.center[0]
        if self.rect.center[0] > width: x = self.rect.center[0] -  width
        if self.rect.center[1] < 0: y = height + self.rect.center[1]
        if self.rect.center[1] > height: y = self.rect.center[1] - height
        self.rect.center = (x, y)
    
    




        

# set up
for i in range(n_love_cars):
    new_car = Car_Love()
    car_count += 1
    cars.append(new_car)

for i in range(n_explorer_cars):
    new_car = Car_Explorer()
    car_count += 1
    cars.append(new_car)


for i in range(n_coward_cars):
    new_car = Car_Coward()
    car_count += 1
    cars.append(new_car)



for i in range(n_aggressive_cars):
    new_car = Car_Aggressive()
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


        
        
        

   
