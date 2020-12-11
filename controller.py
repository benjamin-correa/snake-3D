"""
# A class to store the application control
"""
import glfw
import sys
import numpy as np

class Controller:
    def __init__(self):
        self.headPos = np.zeros(3)
        self.diagonalCam = False
        self.staticCam = False
        self.followCam = False
        self.model = None

    def updatePos(self):
        # update sun position
        x = self.model.posx
        y = self.model.posy
        if self.model.direction == "UP":
            self.headPos[0] = x
            self.headPos[1] = y - 4
            self.headPos[2] = 1.5

        elif self.model.direction == "DOWN":
            self.headPos[0] = x
            self.headPos[1] = y + 4
            self.headPos[2] = 1.5

        elif self.model.direction == "LEFT":
            self.headPos[0] = x + 4
            self.headPos[1] = y
            self.headPos[2] = 1.5

        elif self.model.direction == "RIGHT":
            self.headPos[0] = x - 4
            self.headPos[1] = y 
            self.headPos[2] = 1.5

    def set_model(self, m):
        self.model = m

    def on_key(self,window, key, scancode, action, mods):

        if action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        ##############
        elif (key == glfw.KEY_LEFT or key == glfw.KEY_A) and self.model.direction == "UP":
            self.model.direction = "LEFT"
            self.model.multiplier = 2
        
        elif (key == glfw.KEY_LEFT or key == glfw.KEY_A) and self.model.direction == "DOWN":
            self.model.direction = "RIGHT"
            self.model.multiplier = 0

        elif (key == glfw.KEY_LEFT or key == glfw.KEY_A) and self.model.direction == "LEFT":
            self.model.direction = "DOWN"
            self.model.multiplier = -1

        elif (key == glfw.KEY_LEFT or key == glfw.KEY_A) and self.model.direction == "RIGHT":
            self.model.direction = "UP"
            self.model.multiplier = 1

        elif (key == glfw.KEY_RIGHT or key == glfw.KEY_D) and self.model.direction == "UP":
            self.model.direction = "RIGHT"
            self.model.multiplier = 0
        
        elif (key == glfw.KEY_RIGHT or key == glfw.KEY_D) and self.model.direction == "DOWN":
            self.model.direction = "LEFT"
            self.model.multiplier = 2

        elif (key == glfw.KEY_RIGHT or key == glfw.KEY_D) and self.model.direction == "LEFT":
            self.model.direction = "UP"
            self.model.multiplier = 1

        elif (key == glfw.KEY_RIGHT or key == glfw.KEY_D) and self.model.direction == "RIGHT":
            self.model.direction = "DOWN"
            self.model.multiplier = -1

        ##############
        elif key == glfw.KEY_T:
            self.staticCam = False
            self.followCam = False
            self.diagonalCam = True

        elif key == glfw.KEY_E:
            self.diagonalCam = False
            self.followCam = False
            self.staticCam = True

        elif key == glfw.KEY_R:
            self.diagonalCam = False
            self.staticCam = False
            self.followCam = True

        else:
            print('Unknown key')


