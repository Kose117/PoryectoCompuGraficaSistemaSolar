from OpenGL.GL import *
from OpenGL.GLU import *

from sistemaSolar.GLApp.BaseApps.BaseScene import BaseScene


class MainScene(BaseScene):

    def initialize(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, (self.screen.get_width() / self.screen.get_height()), 0.1, 500)

    def camera_init(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glViewport(0, 0, self.screen.get_width(), self.screen.get_height())
        glEnable(GL_DEPTH_TEST)
        self.camera.update(self.screen.get_width(), self.screen.get_height())

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_world_axes()
