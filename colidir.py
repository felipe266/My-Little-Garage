import glm

class AABB:
    def __init__(self,posi, tamanho):
        self.centro = glm.vec3(posi)
        self.tamanho = glm.vec3(tamanho)

    def Minimo(self):
        return self.centro - self.tamanho/2
    
    def Maximo(self):
        return self.centro + self.tamanho/2