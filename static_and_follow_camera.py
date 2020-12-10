# coding=utf-8

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

from controller import ctrl
from controller import on_key as _on_key
import model

import transformations as tr
import lighting_shaders as ls
import easy_shaders as es
import basic_shapes as bs
import obj_handler as obj


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Sphere", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, _on_key)

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
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

    # Generaremos diversas cámaras.
    static_view = tr.lookAt(
            np.array([10,10,5]), # eye
            np.array([0,0,0]), # at
            np.array([0,0,1])  # up
        )

    skyBox = bs.createTextureCube('skybox.png')
    shape = obj.readOBJ2("obj/Apple.obj", "obj/Apple.png")

    GPUsun = es.toGPUShape(shape , GL_REPEAT, GL_LINEAR)
    GPUSkyBox = es.toGPUShape(skyBox, GL_REPEAT, GL_LINEAR)

    skybox_transform = tr.uniformScale(20)
    shape_transform = tr.uniformScale(0.05)

    t0 = glfw.get_time()
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1
        ctrl.updatePos(t0)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if ctrl.followSun:
            view =  tr.lookAt(
                np.array([0,0,4]),
                ctrl.sunPos,  # The camera will be the sun
                np.array([0,0,1])
        )

        else:
            view = static_view

        # Setting light intensity
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 0.5, 0.5, 0.5)

        # Setting material composition
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 1, 1, 1)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.7, 0.7, 0.7)

        # Setting light position, camera position, and other parameters
        # Note that the lightPosition is where we are looking at
        # The view Position is our current position.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 20.0,20.0,20.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), 1.0,1.0,1.0)
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 500)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.001)


        glUseProgram(texture_pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texture_pipeline.shaderProgram, "model"), 1, GL_TRUE, skybox_transform)
        glUniformMatrix4fv(glGetUniformLocation(texture_pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texture_pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        texture_pipeline.drawShape(GPUSkyBox)
        

        # Telling OpenGL to use our shader program
        glUseProgram(pipeline.shaderProgram)
        transform = tr.matmul([tr.translate(*ctrl.sunPos), shape_transform, tr.rotationX(np.pi/2)])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, transform)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)


        pipeline.drawShape(GPUsun)
        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    
    glfw.terminate()
