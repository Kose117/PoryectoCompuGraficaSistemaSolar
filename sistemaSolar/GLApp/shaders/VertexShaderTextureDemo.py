# Importaciones y configuración inicial
import numpy as np
from OpenGL.GL import *
from sistemaSolar.GLApp.BaseApps.BaseScene import BaseScene
from sistemaSolar.GLApp.Camera.Camera import Camera
from sistemaSolar.GLApp.Mesh.Light.ObjTextureMesh import ObjTextureMesh
from sistemaSolar.GLApp.Transformations.Transformations import identity_mat, scale, translate, rotate
from sistemaSolar.GLApp.Utils.Utils import create_program

# Actualización del shader para usar la posición del sol
vertex_shader = r'''
#version 330 core

in vec3 position;
in vec3 vertexColor;
in vec3 vertexNormal;
in vec2 vertexUv;

uniform mat4 projectionMatrix;
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform vec3 sunPosition; // Posición del sol como variable uniforme

out vec3 color;
out vec3 normal;
out vec3 fragPos;
out vec3 lightPos;
out vec3 viewPos;
out vec2 uv;
void main()
{
    lightPos = sunPosition; // Usar la posición del sol para la iluminación
    viewPos = vec3(inverse(modelMatrix) * vec4(viewMatrix[3][0], viewMatrix[3][1], viewMatrix[3][2], 1));
    gl_Position = projectionMatrix * inverse(viewMatrix) * modelMatrix * vec4(position, 1);
    normal = mat3(transpose(inverse(modelMatrix))) * vertexNormal;
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
    float a_strength = 0.5;
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


simple_vertex_shader = '''
#version 330 core
layout (location = 0) in vec3 position;

uniform mat4 projectionViewMatrix;

void main() {
    gl_Position = projectionViewMatrix * vec4(position, 1.0);
}
'''

simple_fragment_shader = '''
#version 330 core
out vec4 FragColor;

void main() {
    FragColor = vec4(1.0, 1.0, 1.0, 1.0); // Blanco
}
'''


class VertexShaderCameraDemo(BaseScene):

    def __init__(self):
        super().__init__(1600, 800)
        self.stars = None
        self.vao_axes = None
        self.vbo_axes = None
        self.vao_orbits = None
        self.vbo_orbits = None
        self.program_id = None
        self.simple_shader_program = None
        self.planets = {}
        self.valor = 0.0

        self.rotation_speeds = {
            "mercury": 4.0,  # Valores de ejemplo, ajusta según necesites
            "venus": 3.0,
            "earth": 5.0,
            "mars": 3.5,
            "jupiter": 2.0,
            "saturn": 1.5,
            "uranus": 1.0,
            "neptune": 0.8,
            "sun": 0.0
            # Añade velocidades para los demás planetas aquí...
        }
        self.rotation_angles = {planet: 0.0 for planet in self.rotation_speeds}  # Inicializar ángulos a 0

    def initialize_axes(self):
        # Coordinates of the axes with colors
        axes = np.array([
            # X axis in red (R, G, B)
            -1000, 0, 0, 1, 0, 0,
            1000, 0, 0, 1, 0, 0,
            # Y axis in green
            0, -1000, 0, 0, 1, 0,
            0, 1000, 0, 0, 1, 0,
            # Z axis in blue
            0, 0, -1000, 0, 0, 1,
            0, 0, 1000, 0, 0, 1,
        ], dtype=np.float32)

        self.vao_axes = glGenVertexArrays(1)
        self.vbo_axes = glGenBuffers(1)

        glBindVertexArray(self.vao_axes)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_axes)
        glBufferData(GL_ARRAY_BUFFER, axes.nbytes, axes, GL_STATIC_DRAW)

        # Position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * axes.itemsize, None)
        glEnableVertexAttribArray(0)
        # Color attribute
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * axes.itemsize, ctypes.c_void_p(3 * axes.itemsize))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    @staticmethod
    def create_simple_shader_program():
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, simple_vertex_shader)
        glCompileShader(vertex_shader)
        # Aquí deberías verificar si la compilación fue exitosa

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, simple_fragment_shader)
        glCompileShader(fragment_shader)
        # Verificar también la compilación del fragment shader

        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)
        # Verificar el enlace del programa

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program

    def draw_world_axes(self):
        glBindVertexArray(self.vao_axes)
        glDrawArrays(GL_LINES, 0, 6)
        glBindVertexArray(0)


    def initialize(self):
        self.program_id = create_program(vertex_shader, fragment_shader)
        self.simple_shader_program = self.create_simple_shader_program()
        self.initialize_axes()
        self.initialize_planets()
        orbit_radii = [planet.orbit_radius for planet in self.planets.values()]

        self.camera = Camera(self.program_id, self.screen.get_width(), self.screen.get_height())
        glEnable(GL_DEPTH_TEST)

    def initialize_planets(self):
        planets_data = {
            "mercury": {"scale": 0.076, "texture_path": "../../assets/textures/planetaMercurio.jpg",
                        "orbit_radius": 46.0},
            "venus": {"scale": 0.19, "texture_path": "../../assets/textures/planetaVenus.jpg", "orbit_radius": 107.0},
            "earth": {"scale": 0.2, "texture_path": "../../assets/textures/planetaTierra.jpg", "orbit_radius": 147.0},
            "mars": {"scale": 0.106, "texture_path": "../../assets/textures/planetaMarte.jpg", "orbit_radius": 205.0},
            "jupiter": {"scale": 2.194, "texture_path": "../../assets/textures/planetaJupiter.jpg",
                        "orbit_radius": 370.5},
            "saturn": {"scale": 1.828, "texture_path": "../../assets/textures/planetaSaturno.jpg",
                       "orbit_radius": 677.0},
            "uranus": {"scale": 0.796, "texture_path": "../../assets/textures/planetaUrano.jpg",
                       "orbit_radius": 1374.0},
            "neptune": {"scale": 0.772, "texture_path": "../../assets/textures/planetaNeptuno.jpg",
                        "orbit_radius": 2366.4},
            "sun": {"scale": 21.84, "texture_path": "../../assets/textures/sol.jpg", "orbit_radius": 0},
        }

        for planet_name, data in planets_data.items():
            self.planets[planet_name] = ObjTextureMesh(
                self.program_id,
                "../../assets/models/modeloPlaneta.obj",
                data["texture_path"]
            )
            self.planets[planet_name].orbit_radius = data["orbit_radius"]
            self.planets[planet_name].scale = data["scale"]  # Set the scale

        # estrellas
        self.stars = ObjTextureMesh(
            self.program_id,
            "../../assets/models/modeloPlaneta.obj",
            "../../assets/textures/estrellas.jpg"
        )

    def draw_planet(self, planet_name, transformation):
        self.planets[planet_name].draw(transformation)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()

        # Incrementar el ángulo de rotación para simular la órbita
        self.valor += 0.0001  # Hacer que los planetas vayan más lentos

        # Calcular la posición del sol (ejemplo simplificado)
        sun_position = np.array([0, 0, 0])  # Aquí puedes ajustar la posición real del sol si es necesario

        # Pasar la posición del sol al shader
        sun_pos_location = glGetUniformLocation(self.program_id, 'sunPosition')
        glUniform3f(sun_pos_location, *sun_position)

        # Dibujar ejes mundiales y órbitas
        self.draw_world_axes()

        # Dibujar planetas
        for planet_name, data in self.planets.items():
            planet = self.planets[planet_name]
            # Rotación sobre su propio eje
            self.rotation_angles[planet_name] += self.rotation_speeds[planet_name]
            self.rotation_angles[planet_name] %= 360  # Mantener el ángulo dentro de 0-360 grados

            # Preparar la transformación inicial
            transformation = identity_mat()

            # Aplicar la traslación para mover el planeta a su posición orbital
            orbit_radius = planet.orbit_radius
            x = orbit_radius * np.cos(self.valor)
            y = 0
            z = orbit_radius * np.sin(self.valor)
            transformation = translate(transformation, x, y, z)

            # Aplicar la rotación sobre su propio eje
            axial_angle = self.rotation_angles[planet_name]
            transformation = rotate(transformation, axial_angle, 'y')  # Ajusta el eje si es necesario

            # Escalar según el tamaño del planeta
            planet_scale = planet.scale

            # Dibuja estrellas
            transformation_stars = identity_mat()
            transformation_stars = scale(transformation_stars, 2500, 2500, 2500)
            transformation_stars = translate(transformation_stars, 0, 0, 0)
            self.stars.draw(transformation_stars)

            planet_transformation = scale(transformation, data.scale, data.scale, data.scale)
            self.draw_planet(planet_name, planet_transformation)

        glUseProgram(self.program_id)


if __name__ == '__main__':
    VertexShaderCameraDemo().main_loop()
