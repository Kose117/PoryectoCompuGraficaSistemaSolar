import numpy as np
import pygame
from math import *


from sistemaSolar.GLApp.Camera.Character import Character
from sistemaSolar.GLApp.Transformations.Transformations import identity_mat, rotate, translate
from sistemaSolar.GLApp.Utils.Uniform import Uniform
from sistemaSolar.config import set_orbit_paused, orbit_paused

def perspective_mat(angle_of_view, aspect_ratio, near_plane, far_plane):
    a = radians(angle_of_view)
    d = 1.0 / tan(a / 2.0)
    r = aspect_ratio
    b = (far_plane + near_plane) / (near_plane - far_plane)
    c = far_plane * near_plane / (near_plane - far_plane)
    return np.array([
        [d / r, 0, 0, 0],
        [0, d, 0, 0],
        [0, 0, b, c],
        [0, 0, -1, 0]
    ], np.float32)


class Camera:
    def __init__(self, program_id, width, height):
        self.screen_width = width
        self.screen_height = height
        self.program_id = program_id
        self.last_mouse = pygame.math.Vector2(0, 0)
        self.mouse_sensitivity = [0.02, 0.02]
        self.key_sensitivity = 0.005
        self.projection_matrix = perspective_mat(60, width / height, 0.01, 10000)
        self.projection = Uniform("mat4", self.projection_matrix)
        self.projection.find_variable(program_id, "projectionMatrix")
        # Inicializa el personaje (nave)
        self.transformation = identity_mat()
        self.transformation = translate(self.transformation, 0, 0, 0)
        self.character = Character(self.program_id, "../../assets/models/starDestroyer.obj", "../../assets/textures/destructor.jpg")



    def rotate(self, yaw, pitch):
        forward = pygame.Vector3(self.transformation[0, 2], self.transformation[1, 2], self.transformation[2, 2])
        up = pygame.Vector3(0, 1, 0)
        angle = forward.angle_to(up)
        self.transformation = rotate(self.transformation, yaw, "y")
        if angle < 170 and pitch > 0 or angle > 30 and pitch < 0:
            self.transformation = rotate(self.transformation, pitch, "x", True)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_change = self.last_mouse - pygame.math.Vector2(mouse_pos)
        pygame.mouse.set_pos((self.screen_width / 2, self.screen_height / 2))
        self.last_mouse = pygame.math.Vector2(pygame.mouse.get_pos())
        self.rotate(mouse_change.x * self.mouse_sensitivity[0], mouse_change.y * self.mouse_sensitivity[1])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.transformation = translate(self.transformation, 0, 0, self.key_sensitivity)
        if keys[pygame.K_w]:
            self.transformation = translate(self.transformation, 0, 0, -self.key_sensitivity)
        if keys[pygame.K_d]:
            self.transformation = translate(self.transformation, self.key_sensitivity, 0, 0)
        if keys[pygame.K_a]:
            self.transformation = translate(self.transformation, -self.key_sensitivity, 0, 0)
        if keys[pygame.K_SPACE]:
            # Movimiento vertical hacia arriba
            self.transformation = translate(self.transformation, 0, self.key_sensitivity, 0)
        if keys[pygame.K_LSHIFT]:
            # Movimiento vertical hacia abajo
            self.transformation = translate(self.transformation, 0, -self.key_sensitivity, 0)
        if keys[pygame.K_DOWN]:
            set_orbit_paused()
            print(f"Orbit paused: {orbit_paused}")


        self.projection.load()
        lookat = Uniform("mat4", self.transformation)
        lookat.find_variable(self.program_id, "viewMatrix")
        lookat.load()
        # Actualiza la posición del personaje (nave)
        self.character.update_position(self.transformation)

    def get_projection_matrix(self):
        return self.projection_matrix

    def get_view_matrix(self):
        return self.transformation
