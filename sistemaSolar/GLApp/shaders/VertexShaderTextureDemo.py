import pygame
from OpenGL.GL import *
from sistemaSolar.GLApp.BaseApps.BaseScene import BaseScene
from sistemaSolar.GLApp.Camera.Camera import Camera
from sistemaSolar.GLApp.Mesh.Light.ObjTextureMesh import ObjTextureMesh
from sistemaSolar.GLApp.Transformations.Transformations import identity_mat, scale, rotate
from sistemaSolar.GLApp.Utils.Utils import create_program

vertex_shader = r'''
#version 330 core

in vec3 position;
in vec3 vertexColor;
in vec3 vertexNormal;
in vec2 vertexUv;

uniform mat4 projectionMatrix;
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;

out vec3 color;
out vec3 normal;
out vec3 fragPos;
out vec3 lightPos;
out vec3 viewPos;
out vec2 uv;
void main()
{
    lightPos = vec3(5, 5, 5);
    viewPos = vec3(inverse(modelMatrix) * vec4(viewMatrix[3][0], viewMatrix[3][1], viewMatrix[3][2], 1));
    gl_Position = projectionMatrix * inverse(viewMatrix) * modelMatrix * vec4(position, 1);
    normal = mat3(transpose(inverse(modelMatrix))) * vertexNormal;
    //normal = vertexNormal;
    fragPos = vec3(modelMatrix * vec4(position, 1));
    color = vertexColor;
    uv = vertexUv;
}
'''

fragment_shader = r'''
#version 330 core

in vec3 color;
in vec3 normal;
in vec3 fragPos;
in vec3 lightPos;
in vec3 viewPos;

in vec2 uv;
uniform sampler2D tex;

out vec4 fragColor;

void main(){
    
    vec3 lightColor = vec3(1, 1, 1);
    
    //ambient
    float a_strength = 0.1;
    vec3 ambient = a_strength * lightColor;
    
    //diffuse
    vec3 norm = normalize(normal);
    vec3 lightDirection = normalize(lightPos - fragPos);
    float diff = max(dot(norm, lightDirection), 0);
    vec3 diffuse = diff * lightColor;
    
    //specular
    float s_strength = 0.8;
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 reflectDir = normalize(-lightDirection - norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = s_strength * spec * lightColor;
     
    fragColor = vec4(color * (ambient + diffuse + specular), 1);
    fragColor = fragColor * texture(tex, uv);
}
'''


class VertexShaderCameraDemo(BaseScene):

    def __init__(self):
        super().__init__(1000, 800)
        self.vao_ref = None
        self.program_id = None
        self.axes = None
        self.ship = None
        self.ship_angle_info = [0, 0.1]

    def initialize(self):
        self.program_id = create_program(vertex_shader, fragment_shader)
        self.ship = ObjTextureMesh(
            self.program_id,
            "../../assets/models/jupiter.obj",
            "../../assets/textures/satelite_tierra.jpg"
        )
        self.camera = Camera(self.program_id, self.screen.get_width(), self.screen.get_height())
        # glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

    def camera_init(self):
        pass

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()
        transformation = identity_mat()
        transformation = scale(transformation, 0.1, 0.1, 0.1)
        # transformation = rotate(transformation, self.ship_angle_info[0], "y")
        self.ship.draw(transformation)
        # self.ship_angle_info[0] = (self.ship_angle_info[0] + self.ship_angle_info[1]) % 360


if __name__ == '__main__':
    VertexShaderCameraDemo().main_loop()
