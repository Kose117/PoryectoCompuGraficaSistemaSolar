import random
from OpenGL.GL import *

from sistemaSolar.GLApp.Mesh.Light.BaseTextureMesh import BaseTextureMesh


def load_mesh(filename):
    vertices = []
    faces = []
    vertex_normals = []
    vertex_uvs = []
    with open(filename) as f:
        line = f.readline()
        vertices_aux = []
        normals_aux = []
        uvs_aux = []
        while line:
            line_tokens = line.split()
            if len(line_tokens) > 0:
                if line_tokens[0] == 'v':
                    vertices_aux.append([float(x) for x in line_tokens[1:]])
                elif line_tokens[0] == 'vn':
                    normals_aux.append([float(x) for x in line_tokens[1:]])
                elif line_tokens[0] == 'vt':
                    uvs_aux.append([float(x) for x in line_tokens[1:]])
                elif line_tokens[0] == 'f':
                    faces.append([x for x in line_tokens[1:]])
            line = f.readline()
        for face_info in faces:
            for vertex_info in face_info:
                tokens = [int(x) - 1 for x in vertex_info.split("/")]
                vertices.append(vertices_aux[tokens[0]])
                vertex_uvs.append(uvs_aux[tokens[1]])
                vertex_normals.append(normals_aux[tokens[2]])
        print(f'Loaded {len(vertices)} {len(faces)}')
    return vertices, vertex_uvs, vertex_normals, faces


class ObjTextureMesh(BaseTextureMesh):
    def __init__(self, program_id, filename, texture_filename):
        vertices, vertex_uvs, vertex_normals, faces = load_mesh(filename)
        colors = []
        for i in range(len(vertices)):
            colors.append([1, 1, 1])
        draw_type_aux = GL_TRIANGLES if len(faces[0]) == 3 else GL_QUADS
        super().__init__(program_id, vertices, vertex_uvs, vertex_normals, colors, draw_type_aux, texture_filename)
