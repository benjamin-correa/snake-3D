"""
# A class to store the application control
"""
import glfw
import sys
import numpy as np

class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.sunPos = np.zeros(3)
        self.followSun = False
        self.r = 5.0

    def updatePos(self, time):
        # update sun position
        self.sunPos[0] = self.r * np.cos(time) 
        self.sunPos[1] = self.r * np.sin(time)
        self.sunPos[2] = 1.5

# we will use the global controller as communication with the callback function
ctrl = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global ctrl

    if key == glfw.KEY_SPACE:
        ctrl.fillPolygon = not ctrl.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        sys.exit()

    elif key == glfw.KEY_E:
        ctrl.followSun = not ctrl.followSun 

    else:
        print('Unknown key')


