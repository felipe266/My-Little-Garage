from OpenGL.GL import *
import OpenGL.GL.shaders as gls

class Shader:
    def __init__(self, vertexPath, fragmentPath):
        with open(vertexPath, 'r') as file:
            vsSource = file.read()
        with open(fragmentPath, 'r') as file:
            fsSource = file.read()

        vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
        fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
        self.shaderId = gls.compileProgram(vsId, fsId)

    def bind(self):
        glUseProgram(self.shaderId)

    def unbind(self):
        glUseProgram(0)

    def setUniform3f(self, name, x, y = None, z=None, w=None):
        name_loc = glGetUniformLocation(self.shaderId, name)
        if y == None: glUniform1f(name_loc, x)
        elif z == None: glUniform2f(name_loc, x, y)
        elif w == None: glUniform3f(name_loc, x,y,z)
        else: glUniform4f(name_loc, x,y,z,w)

    def setUniformv(self, name, values):
        name_loc = glGetUniformLocation(self.shaderId, name)
        if len(values) == 1: glUniform1fv(name_loc, 1, values)
        elif len(values) == 2: glUniform2fv(name_loc,1,values)
        elif len(values) == 3: glUniform3fv(name_loc,1,values)
        else:glUniform4fv(name_loc,1,values)