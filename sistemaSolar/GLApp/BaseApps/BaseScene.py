import os

import pygame
from OpenGL.GL import *
from pygame.locals import *

from sistemaSolar.GLApp.Camera.Camera import Camera


class BaseScene:
    def __init__(self, screen_width, screen_height):
        os.environ["SDL_VIDEO_CENTERED"] = '1'
        pygame.init()
        # antialiasing
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        self.screen = pygame.display.set_mode([screen_width, screen_height], DOUBLEBUF | OPENGL)
        pygame.display.set_caption("PyOpenGLApp")
        self.camera = None

    def initialize(self):
        pass

    def display(self):
        pass

    def camera_init(self):
        pass

    def main_loop(self):
        self.initialize()
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    run = False
            self.camera_init()
            self.display()
            pygame.display.flip()
        pygame.quit()

    @staticmethod
    def draw_world_axes():
        glLineWidth(4)
        glBegin(GL_LINES)
        glColor(1, 0, 0)
        glVertex3d(-1000, 0, 0)
        glVertex3d(1000, 0, 0)
        glColor(0, 1, 0)
        glVertex3d(0, -1000, 0)
        glVertex3d(0, 1000, 0)
        glColor(0, 0, 1)
        glVertex3d(0, 0, -1000)
        glVertex3d(0, 0, 1000)
        glEnd()
