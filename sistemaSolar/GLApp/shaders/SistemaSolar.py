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
        self.deathStar = None
        self.ship = None
        self.stars = None

        self.vao_orbits = None
        self.vbo_orbits = None
        self.program_id = None
        self.simple_shader_program = None
        self.planets = {}
        self.valor = 0.0



    def initialize(self):
        self.program_id = create_program(vertex_shader, fragment_shader)


        self.initialize_planets()

        self.camera = Camera(self.program_id, self.screen.get_width(), self.screen.get_height())

        glEnable(GL_DEPTH_TEST)

    def initialize_planets(self):
        planets_data = {
            "sun": {"scale": 0.5, "texture_path": "../../assets/textures/sol.jpg", "orbit_radius": 0, "rotation_speeds_self": 0, "rotation_angles": 0, "rotation_speeds_sun": 0},

            "mercury": {"scale": 0.00174, "texture_path": "../../assets/textures/planetaMercurio.jpg", "orbit_radius": 1.053, "rotation_speeds_self": 0.017, "rotation_angles": 0, "rotation_speeds_sun": 0.2410},

            "venus": {"scale": 0.00435, "texture_path": "../../assets/textures/planetaVenus.jpg", "orbit_radius": 2.45, "rotation_speeds_self": 0.0042, "rotation_angles": 0, "rotation_speeds_sun": 0.6164},

            "earth": {"scale": 0.00458, "texture_path": "../../assets/textures/planetaTierra.jpg", "orbit_radius": 3.365, "rotation_speeds_self": 1.0, "rotation_angles": 0, "rotation_speeds_sun": 1.0},

            "mars": {"scale": 0.00243, "texture_path": "../../assets/textures/planetaMarte.jpg", "orbit_radius": 4.693, "rotation_speeds_self": 0.9756, "rotation_angles": 0, "rotation_speeds_sun": 1.8821},

            "jupiter": {"scale": 0.05023, "texture_path": "../../assets/textures/planetaJupiter.jpg", "orbit_radius": 8.482, "rotation_speeds_self": 2.4242, "rotation_angles": 0, "rotation_speeds_sun": 4.329},

            "saturn": {"scale": 0.04185, "texture_path": "../../assets/textures/planetaSaturno.jpg", "orbit_radius": 15.499, "rotation_speeds_self": 2.243, "rotation_angles": 0, "rotation_speeds_sun": 10.753},

            "uranus": {"scale": 0.01822, "texture_path": "../../assets/textures/planetaUrano.jpg", "orbit_radius": 31.456, "rotation_speeds_self": 1.3954, "rotation_angles": 0, "rotation_speeds_sun": 84.0109},

            "neptune": {"scale": 0.01767, "texture_path": "../../assets/textures/planetaNeptuno.jpg", "orbit_radius": 54.176, "rotation_speeds_self": 1.4906, "rotation_angles": 0, "rotation_speeds_sun": 90.411}


        }

        for planet_name, data in planets_data.items():
            self.planets[planet_name] = ObjTextureMesh(
                self.program_id,
                "../../assets/models/modeloPlaneta.obj",
                data["texture_path"]
            )
            self.planets[planet_name].orbit_radius = data["orbit_radius"]
            self.planets[planet_name].scale = data["scale"]
            self.planets[planet_name].rotation_speeds_self = data["rotation_speeds_self"]
            self.planets[planet_name].rotation_angles = data["rotation_angles"]
            self.planets[planet_name].rotation_speeds_sun = data["rotation_speeds_sun"]

        # estrellas
        self.stars = ObjTextureMesh(
            self.program_id,
            "../../assets/models/modeloPlaneta.obj",
            "../../assets/textures/estrellas.jpg"
        )
        # nave

    def draw_planet(self, planet_name, transformation):
        self.planets[planet_name].draw(transformation)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()

        self.valor += 0.00001  # Incremento muy pequeño para ralentizar el movimiento

        sun_position = np.array([0, 0, 0])

        # Pasar la posición del sol al shader
        sun_pos_location = glGetUniformLocation(self.program_id, 'sunPosition')
        glUniform3f(sun_pos_location, *sun_position)



        # Dibujar planetas
        for planet_name, planet_data in self.planets.items():
            orbit_radius = planet_data.orbit_radius
            orbital_speed = planet_data.rotation_speeds_sun
            angular_speed = 0
            # Calcular la posición orbital actual en función del tiempo
            if planet_name != 'sun':
                angular_speed = 2 * np.pi / orbital_speed  # Velocidad angular en radianes por segundo

            max_angle = 2 * np.pi  # Un círculo completo
            angular_position = (self.valor * angular_speed) % max_angle  # Ángulo actual en radianes

            x = orbit_radius * np.cos(angular_position)
            y = 0
            z = orbit_radius * np.sin(angular_position)

            # Preparar la transformación inicial
            transformation = identity_mat()
            transformation = translate(transformation, x, y, z)

            # Aplicar la rotación sobre su propio eje
            # Ajustar la velocidad de rotación para que no aumente con el tiempo
            planet_data.rotation_angles = (planet_data.rotation_angles + 0.1) % 360

            axial_rotation_angle = planet_data.rotation_angles
            transformation = rotate(transformation, axial_rotation_angle, 'y')
            # Aplicar la escala
            scale_factor = planet_data.scale
            transformation = scale(transformation, scale_factor, scale_factor, scale_factor)

            # Dibuja el planeta con su transformación
            self.draw_planet(planet_name, transformation)

        # Dibuja estrellas
        transformation_stars = identity_mat()
        transformation_stars = scale(transformation_stars, 100, 100, 100)
        transformation_stars = translate(transformation_stars, 0, 0, 0)
        self.stars.draw(transformation_stars)

        # Dibuja nave

if __name__ == '__main__':
    VertexShaderCameraDemo().main_loop()
