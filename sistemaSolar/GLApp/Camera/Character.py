import numpy as np

from sistemaSolar.GLApp.Mesh.Light.ObjTextureMesh import ObjTextureMesh
from sistemaSolar.GLApp.Transformations.Transformations import identity_mat, translate, scale, rotate


class Character:
    def __init__(self, program_id, obj, texture):
        self.program_id = program_id
        self.transformation = identity_mat()  # Inicialmente, la nave está en la posición y orientación inicial

        self.skin = ObjTextureMesh(self.program_id, obj, texture)

    def update_position(self, translation):
        # Actualiza la posición de la nave aplicando una matriz de traslación
        translation = translate(translation, -0.0035, -0.005, -0.016) #x negativa hacia la izquierda, z negativo hacia adelante
        translation = rotate(translation, 90, 'y')
        #translation = rotate(translation, 45, 'z')
        self.transformation = np.dot(self.transformation, translation)

        translation = scale(translation, 0.005, 0.005, 0.005)  # 0.001
        self.skin.draw(translation)




