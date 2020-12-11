import numpy as np

import transformations2 as tr
import easy_shaders as es
import scene_graph as sg
import basic_shapes as bs
from OpenGL.GL import *
import obj_handler as obj

class Snake (object):
    """
    Creates the snake's head, and implements
    the head movement logic.
    """

    def __init__ (self):
        gpu_head_quad = es.toGPUShape(
            bs.createTextureCube("img/face.png"), GL_REPEAT, GL_NEAREST)
        head = sg.SceneGraphNode("head")
        head.childs += [gpu_head_quad]
        gpu_face = es.toGPUShape(
            bs.createTextureCube("img/Snake_Head.png"), GL_REPEAT, GL_NEAREST)
        face = sg.SceneGraphNode("face")
        face.childs += [gpu_face]
        face.transform = tr.matmul([
            tr.scale(0.9,0.9,0.9), tr.translate(0,0,0.1)])
        face_head = sg.SceneGraphNode('face_head')
        face_head.childs += [face, head]

        self.posx = 0
        self.posy = -1
        self.direction = "UP"
        self.multiplier = 1
        self.model = face_head
        self.on = True
        
    def draw (self, pipeline, projection, view, N):
        self.model.transform = tr.matmul([
            tr.translate(self.posx, self.posy, -4.5),
            tr.rotationZ((np.pi*self.multiplier)/2)])
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'face_head'), pipeline, 'model')

    def update(self, N):
        if self.direction == "UP":
            self.posy += 10/(N)
        elif self.direction == "DOWN":
            self.posy -= 10/(N)
        elif self.direction == "LEFT":
            self.posx -= 10/(N)
        elif self.direction == "RIGHT":
            self.posx += 10/(N)

class Body(object):
    """
    Draws and implements the body of the snake.
    """
    def __init__ (self, x, y):
        gpu_body_quad = es.toGPUShape(
            bs.createTextureCube("img/Snake_Body.png"), GL_REPEAT, GL_NEAREST)
        body = sg.SceneGraphNode("body")
        body.childs += [gpu_body_quad]
        self.posx = x
        self.posy = y
        self.model = body
    
    def draw(self, pipeline, projection, view, N):
        self.model.transform = tr.matmul([
            tr.translate(self.posx, self.posy, -4.5)])
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'body'), pipeline,"model")


class Logic(object):
    """
    This holds the main logic of the game, the movement
    of the body logic, the adding of a body logic, the collisions logics
    and the apple logics
    """
    def __init__ (self, snake):
        self.head = snake
        self.body = []

    def addBody (self):
        """
        Appends a body part on the end
        """
        if len(self.body) == 0:
            self.body.append(Body(self.head.posx, self.head.posy))
        else:
            self.body.append(Body(self.body[len(self.body)-1].posx, self.body[len(self.body)-1].posy))

    def movement (self, N):
        """
        Movement of the body
        """
        x_head = self.head.posx
        y_head = self.head.posy
        self.head.update(N)

        for i in range(len(self.body)):
            x_copy = self.body[i].posx
            y_copy = self.body[i].posy
            self.body[i].posx = x_head
            self.body[i].posy = y_head
            x_head = x_copy
            y_head = y_copy
        
    def bodyCollision(self, N):
        """
        Checks if the snake is colliding with his body
        """
        x_head = self.head.posx
        y_head = self.head.posy
        for i in self.body:
            if ((i.posx - 1/(2*N) < x_head < i.posx +1/(2*N)) and
                (i.posy - 1/(2*N) < y_head < i.posy +1/(2*N))):
                self.head.on = False
                print("Game Over, tu puntaje es: ", len(self.body))
    
    def borderCollision (self, N):
        """
        Checks if the snake is colliding with the border
        """

        x_head = self.head.posx
        y_head = self.head.posy
        if x_head >= 10 - (10/(2*N)) or y_head >= 10 - (10/(2*N)):
            self.head.on = False
            print("Game Over, tu puntaje es: ", len(self.body))
        elif x_head <= -10 + (10/(2*N)) or y_head <= -10 + (10/(2*N)):
            self.head.on = False
            print("Game Over, tu puntaje es: ", len(self.body))

    def appleEaten (self, N, apple):
        """
        First we check if the apple is goin to be eaten by the snake,
        then we a start a cycle where generates 2 random numbers and
        those numbers will be the candidate coordinates, the we check
        if the apple is goin to be in a empty space, if is not going on
        a empty space, we generate 2 new numbers.
        """
        x_head = self.head.posx
        y_head = self.head.posy
        if ((apple.posx - 10/(2*N) < x_head < apple.posx +10/(2*N)) and 
            (apple.posy - 10/(2*N) < y_head < apple.posy +10/(2*N))):

            self.addBody()

            while True:

                aux = 0 #Helps to see if the apple is goin to go on a empty space
                x = np.random.randint(-10 , 10)
                y = np.random.randint(-10 , 10)
                for i in self.body:
                    if x < 0 and y < 0:
                        apple.posx = x + (10/(N))
                        apple.posy = y + (10/(N))
                        if not ((apple.posx - 10/N < i.posx < apple.posx +10/N) and 
                            (apple.posy - 10/N < i.posy < apple.posy +10/N)): 
                            aux += 1
                        else:
                            break

                    elif x >= 0 and y < 0:
                        apple.posx = x - (10/(N))
                        apple.posy = y + (10/(N))
                        if not ((apple.posx - 10/N < i.posx < apple.posx +10/N) and 
                            (apple.posy - 10/N < i.posy < apple.posy +10/N)): 
                            aux += 1
                        else:
                            break
                    elif x >= 0 and y >= 0:
                        apple.posx = x - (10/(N))
                        apple.posy = y - (10/(N))
                        if not ((apple.posx - 10/N < i.posx < apple.posx +10/N) and 
                            (apple.posy - 10/N < i.posy < apple.posy +10/N)): 
                            aux += 1
                        else:
                            break
                    elif x < 0 and y >= 0:
                        apple.posx = x + (10/(N))
                        apple.posy = y - (10/(N))
                        if not ((apple.posx - 10/N < i.posx < apple.posx +10/N) and 
                            (apple.posy - 10/N < i.posy < apple.posy +10/N)): 
                            aux += 1
                        else:
                            break
                if aux == len(self.body):
                    break
                
            #print("Comiste ñam")

    def draw(self, pipeline, projection, view, N):
        for x in self.body:
            x.draw(pipeline, projection, view, N)


class Scene (object):
    """
    Creates the borders of the map
    """
    def __init__ (self):
        gpu_head_quad = es.toGPUShape(
            bs.createTextureCube('img/skybox.png'), GL_REPEAT, GL_LINEAR)
        border = sg.SceneGraphNode("border")
        border.childs += [gpu_head_quad]
        border.transform = tr.uniformScale(2)
        gpu_floor = es.toGPUShape(
            bs.createTextureCube('img/pasto.png'), GL_REPEAT, GL_LINEAR)
        floor = sg.SceneGraphNode("floor")
        floor.childs += [gpu_floor]
        floor.transform = tr.matmul([
            tr.translate(0,0,-0.5), tr.scale(1,1,0.5)])

        gpu_side0 = es.toGPUShape(
            bs.createTextureCube('img/border.png'), GL_REPEAT, GL_LINEAR)
        side0 = sg.SceneGraphNode("side0")
        side0.childs += [gpu_side0]
        side0.transform = tr.matmul([
            tr.translate(0, 0.5, -0.25), tr.scale(1, 0.05, 0.05)])

        gpu_side1 = es.toGPUShape(
            bs.createTextureCube('img/border.png'), GL_REPEAT, GL_LINEAR)
        side1 = sg.SceneGraphNode("side1")
        side1.childs += [gpu_side1]
        side1.transform = tr.matmul([
            tr.translate(0, -0.5, -0.25), tr.scale(1, 0.05, 0.05)])

        gpu_side2 = es.toGPUShape(
            bs.createTextureCube('img/border.png'), GL_REPEAT, GL_LINEAR)
        side2 = sg.SceneGraphNode("side2")
        side2.childs += [gpu_side2]
        side2.transform = tr.matmul([
            tr.translate(0.5, 0, -0.25), tr.scale(0.05, 1, 0.05)])

        gpu_side3 = es.toGPUShape(
            bs.createTextureCube('img/border.png'), GL_REPEAT, GL_LINEAR)
        side3 = sg.SceneGraphNode("side3")
        side3.childs += [gpu_side3]
        side3.transform = tr.matmul([
            tr.translate(-0.5, 0, -0.25), tr.scale(0.05, 1, 0.05)])
        
        transform_border = sg.SceneGraphNode('borderTR')
        transform_border.childs += [floor, border, side0, side1, side2, side3]
    

        self.model = transform_border
        self.posx = 0
        self.posy = 0

    def draw (self, pipeline, projection, view, N):
        self.model.transform = tr.uniformScale(20)
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'borderTR'), pipeline, 'model')

class Apple (object):
    """
    Creates the apple shape
    """
    def __init__ (self,N):
        gpu_apple_obj = es.toGPUShape(
            obj.readOBJ2("obj/Apple.obj", "obj/Apple.png"),
             GL_REPEAT, GL_LINEAR)
        apple = sg.SceneGraphNode("apple")
        apple.childs += [gpu_apple_obj]
        self.model = apple
        self.posx = 0
        self.posy = 1/N

    def draw (self, pipeline, projection, view, N, t1):
        self.model.transform = tr.matmul([
            tr.translate(self.posx,self.posy,-3.75 + np.cos(t1*2)*0.052 + 0.2), tr.uniformScale(1/(10*N)),
            tr.rotationX(np.pi/2)])
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'apple'), pipeline,"model")

     

class EndScreeen(object):

    """
    Displays the game over texture
    """

    def __init__(self):
        gpu_end_quad = es.toGPUShape(
                bs.createTextureCube("img/GO.png"), GL_REPEAT, GL_NEAREST)
        end = sg.SceneGraphNode("end")
        end.childs += [gpu_end_quad]
        self.posx = 0 
        self.posy = 0
        self.model = end
        
    def draw (self, pipeline, projection, view, N, time):
        self.model.transform = tr.matmul([
            tr.translate(0.5,0,-0.5), tr.uniformScale(8),
            tr.rotationZ(np.cos(time))])
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        sg.drawSceneGraphNode(sg.findNode(self.model, 'end'), pipeline, 'model')