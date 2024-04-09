from OpenGL.GL import *

from sistemaSolar.GLApp.Mesh.texture.Texture import Texture
from sistemaSolar.GLApp.Utils.GraphicsData import GraphicsData
from sistemaSolar.GLApp.Utils.Uniform import Uniform


class BaseTextureMesh:
    def __init__(self, program_id, vertices, vertex_uvs, vertex_normals, vertex_colors, draw_type, texture_filename):
        self.program_id = program_id
        self.vertices = vertices
        self.vertex_uvs = vertex_uvs
        self.vertex_normals = vertex_normals
        self.draw_type = draw_type
        self.vao_ref = glGenVertexArrays(1)
        glBindVertexArray(self.vao_ref)
        position_variable = GraphicsData("vec3", self.vertices)
        position_variable.create_variable(program_id, "position")
        color_variable = GraphicsData("vec3", vertex_colors)
        color_variable.create_variable(program_id, "vertexColor")
        normal_variable = GraphicsData("vec3", self.vertex_normals)
        normal_variable.create_variable(program_id, "vertexNormal")
        uvs_variable = GraphicsData("vec2", self.vertex_uvs)
        uvs_variable.create_variable(program_id, "vertexUv")
        self.image = Texture(texture_filename)
        self.texture = Uniform("sampler2D", [self.image.texture_id, 1])
        self.texture.find_variable(self.program_id, "tex")

    def draw(
            self,
            transformation_matrix
    ):
        self.texture.load()
        transformation = Uniform("mat4", transformation_matrix)
        transformation.find_variable(self.program_id, "modelMatrix")
        transformation.load()
        glBindVertexArray(self.vao_ref)
        glDrawArrays(self.draw_type, 0, len(self.vertices))
