import numpy as np
import matplotlib.pyplot as plt

"""
This function takes two points, the current time, bank angle, velocity, and precision as inputs
Outputs an array of arrays, where each sub array contains an x-y coordinate
and the time at which the plane hits that point

Turns are modeled as circles, the plane turns until it is facing the end point

Theta is measured as radians clockwise from the positive y direction

Radius is the radius of the end circle the plane is aiming at

The code may not work if you put in a velocity that is too high, depending on how close the end point is.
It isn't smart enough to stop on it's own so be ready to force stop it.

Precision is essentially the time step

Phi is constant bank angle

"""

#copy and paste "path = path_calc(0, 0, 0, -100, -110, np.pi/6, 8, 0, .01, 5)" into the idle to see an example plot

g = 9.81

def path_calc(x_init, y_init, theta_init, x_f, y_f, phi, v, t, precision, radius):

    path = [[],[],[]] #initializing path array with 3 lists for t, x, y
    omega = g*np.tan(phi)/v  #this is rate of turn, a constant
    direction = 1
    correction = 0
    x = x_init
    y = y_init
    theta = theta_init
    dx = x_f - x
    dy = y_f - y
    
    if dx < 0:
        direction = -1; #This tells the plane to turn counter-clockwise

        
    if dy<0 and dx > 0:
        correction = np.pi     #This gives the correct theta for the 4th quadrant
    elif dy < 0 and dx < 0:
        correction = np.pi*-1      #This gives the correct theta for the third quadrant

    
    if dy:                         #This only runs if dy is not zero
        theta_d = np.arctan(dx/dy) + correction
    else:                          #if dy is zero, it assumes the angle is pi/2
        theta_d = np.pi/2 * np.sign(dx)
        
        
    while np.abs(theta-theta_d) > np.pi*precision:   #This plots the path during the turn

        t += precision
        
        theta += omega*precision*direction   
        
        x = x + v*np.sin(theta)*precision
        y = y + v*np.cos(theta)*precision

        correction = 0
        
        dx = x_f - x
        dy = y_f - y
        
        if dy<0 and dx > 0:          
            correction = np.pi
            
        elif dy < 0 and dx < 0:      
            correction = np.pi*-1
        
        path[0].append(t)
        path[1].append(x)
        path[2].append(y)
    
        if dy:   
            theta_d = np.arctan(dx/dy) + correction 
        else: 
            theta_d = np.pi/2 * np.sign(dx)
            

    while (np.abs(x_f - x) > radius) or (np.abs(y_f - y) > radius):  #This completes the straight portion of the path

        x = x + v*np.sin(theta)*precision
        y = y + v*np.cos(theta)*precision
        t = t + precision

        path[0].append(t)
        path[1].append(x)
        path[2].append(y)

    #plotting the path

    end_circle = plt.Circle((x_f,y_f), radius, color = 'r', fill=False)
    plane = plt.Triangle((x_f
    fig, ax = plt.subplots()
    ax.plot(path[1],path[2])
    ax.add_artist(end_circle)
    fig.show()
    fig.savefig('path.png')
        
    return path 
