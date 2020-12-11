# coding=utf-8

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

from controller import *
from model import *

import transformations2 as tr
import lighting_shaders as ls
import easy_shaders as es
import basic_shapes as bs
import obj_handler as obj


if __name__ == "__main__":

    ctrl = Controller()
    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1000
    height = 1000

    window = glfw.create_window(width, height, "Snake 3D", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, ctrl.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = ls.SimpleTextureGouraudShaderProgram()
    texture_pipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Using the same view and projection matrices in the whole application
    projection = tr.perspective(90, float(width)/float(height), 0.1, 100)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Generaremos diversas cámaras.
    static_view = tr.lookAt(
            np.array([0,0,10]), # eye
            np.array([0,0,-5]), # at
            np.array([0,1,0])  # up
        )
    N = 10
    apple = Apple(N)
    scene = Scene()
    snake = Snake()
    logic = Logic(snake)
    ctrl.set_model(snake)
    end = EndScreeen()

    t0 = glfw.get_time()
    t02 = glfw.get_time()
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()
        t1 = glfw.get_time()
        dt = t1 - t0
        ctrl.updatePos()

        glUseProgram(pipeline.shaderProgram)
        # Setting light intensity
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 0.5, 0.5, 0.5)

        # Setting material composition
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.5, 0.5, 0.5)

        # Setting light position, camera position, and other parameters
        # Note that the lightPosition is where we are looking at
        # The view Position is our current position.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 10,10,10)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), 10,10,10)
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 10000)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), (np.cos(t1)*0.00052 + 0.002))
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), np.cos(t1)*0.00052 + 0.002)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), np.cos(t1)*0.00052 + 0.002)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if ctrl.diagonalCam:
            view =  tr.lookAt(
                np.array([0,-10,5]),  # eye
                np.array([0,0,-5]),   # at
                np.array([0,0,1]))   # up

        elif ctrl.staticCam:
            view =  static_view

        else:
            view = tr.lookAt(
                ctrl.headPos,  # eye
                np.array([snake.posx, snake.posy,-5]),   # at
                np.array([0,0,1]))   # up

        
        snake.draw(texture_pipeline, projection, view, N)
        # Drawing the apple.
        apple.draw(pipeline, projection, view, N, t1)
        scene.draw(texture_pipeline, projection, view, N)
        logic.draw(texture_pipeline, projection, view, N)


        if dt >= 0.25 and snake.on:
            logic.movement(N)
            logic.borderCollision(N)
            logic.bodyCollision(N)
            logic.appleEaten(N, apple)
            t0 = t1
        elif not snake.on:
            end.draw(texture_pipeline, projection, view, N, t1)
            

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    
    glfw.terminate()
