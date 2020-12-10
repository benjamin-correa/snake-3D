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
    pipeline = es.SimpleModelViewProjectionShaderProgram()
    texture_pipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    lighting_pipeline = ls.SimplePhongShaderProgram() # Si tienen erorres usen gouraud.
    
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
    view = static_view

    skyBox = bs.createTextureCube('skybox.png')
    sun = model.generateSphereShapeNormals(20, 20)

    GPUsun = es.toGPUShape(sun)
    GPUSkyBox = es.toGPUShape(skyBox, GL_REPEAT, GL_LINEAR)

    skybox_transform = tr.uniformScale(20)

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

        # Drawing skybox. This shader doesn't use lights, it is not affected by lights.
        glUseProgram(texture_pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texture_pipeline.shaderProgram, "model"), 1, GL_TRUE, skybox_transform)
        glUniformMatrix4fv(glGetUniformLocation(texture_pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texture_pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        texture_pipeline.drawShape(GPUSkyBox)

        """ 
        Jueguen con los valores para la luz y observen los cambios.
        """
        glUseProgram(lighting_pipeline.shaderProgram)

        if ctrl.followSun:
            viewPos = ctrl.sunPos
            view =  tr.lookAt(
                np.array([0,0,4]),
                ctrl.sunPos,  # The camera will be the sun
                np.array([0,0,1])
            )

            # White light in all components: ambient, diffuse and specular.
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "La"), 0.1, 0.1, 0.1)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ld"), 0.3, 0.3, 0.3)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ls"), 0.3, 0.3, 0.3)

            # Object is barely visible at only ambient. Bright white for diffuse and specular components.
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ka"), 0.1, 0.1, 0.1)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Kd"), 0.3, 0.3, 0.3)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ks"), 0.3, 0.3, 0.3)

        else:
            viewPos = np.array((0.0, 0.0, 5.0))
            view = static_view

            # White light in all components: ambient, diffuse and specular.
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

            # Object is barely visible at only ambient. Bright white for diffuse and specular components.
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ka"), 0.4, 0.4, 0.4)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
            glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # Here we can see how we can change the light position and view position at the same time.
        glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "lightPosition"), ctrl.sunPos[0], ctrl.sunPos[1], ctrl.sunPos[2])
        glUniform3f(glGetUniformLocation(lighting_pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lighting_pipeline.shaderProgram, "shininess"), 10)

        glUniform1f(glGetUniformLocation(lighting_pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lighting_pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lighting_pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        transform = tr.translate(*ctrl.sunPos)
        glUniformMatrix4fv(glGetUniformLocation(lighting_pipeline.shaderProgram, "model"), 1, GL_TRUE, transform)
        glUniformMatrix4fv(glGetUniformLocation(lighting_pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lighting_pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        lighting_pipeline.drawShape(GPUsun)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)


    glfw.terminate()
