# Importaciones y configuración inicial
import numpy as np
import pygame
from OpenGL.GL import *
from sistemaSolar.GLApp.BaseApps.BaseScene import BaseScene
from sistemaSolar.GLApp.Camera.Camera import Camera

from sistemaSolar.GLApp.Mesh.Light.ObjTextureMesh import ObjTextureMesh
from sistemaSolar.GLApp.Transformations.Transformations import identity_mat, scale, translate, rotate
from sistemaSolar.GLApp.Utils.Utils import create_program
from sistemaSolar.config import get_orbit_paused,set_orbit_paused

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


class VertexShaderCameraDemo(BaseScene):

    def __init__(self):
        super().__init__(1600, 800)
        self.ship = None
        self.stars = None
        self.program_id = None
        self.planets = {}
        self.valor = 0.0



    def initialize(self):
        pygame.init()
        self.program_id = create_program(vertex_shader, fragment_shader)
        self.initialize_planets()
        self.camera = Camera(self.program_id, self.screen.get_width(), self.screen.get_height())
        glEnable(GL_DEPTH_TEST)

    def initialize_planets(self):
        planets_data = {
            "sun": {"scale": 0.5, "texture_path": "../../assets/textures/sol.jpg", "orbit_radius": 0, "rotation_speeds_self": 0, "rotation_angles": 0, "rotation_speeds_sun": 0},

            "mercury": {"scale": 0.00174, "texture_path": "../../assets/textures/planetaMercurio.jpg", "orbit_radius": 1.053, "rotation_speeds_self": 0.017, "rotation_angles": 0, "rotation_speeds_sun": 0.2410},

            "venus": {"scale": 0.00435, "texture_path": "../../assets/textures/planetaVenus.jpg", "orbit_radius": 2.45, "rotation_speeds_self": 0.0042, "rotation_angles": 0, "rotation_speeds_sun": 0.6164},


            "earth": {
                "scale": 0.00458, "texture_path": "../../assets/textures/planetaTierra.jpg",
                "orbit_radius": 3.365, "rotation_speeds_self": 1.0, "rotation_angles": 0, "rotation_speeds_sun": 1.0,
                "satellites": [
                    {
                        "name": "moon",
                        "scale": 0.001,  # Scaled to be visible but proportionally smaller than Earth
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.1,  # Adjusted for visibility
                        "rotation_speeds_self": 0.1,  # Realistic rotation period adjusted for simulation speed
                        "rotation_angles": 0
                    }
                ]
            },

            # Mars with its two moons
            "mars": {
                "scale": 0.00243, "texture_path": "../../assets/textures/planetaMarte.jpg",
                "orbit_radius": 4.693, "rotation_speeds_self": 0.9756, "rotation_angles": 0,
                "rotation_speeds_sun": 1.8821,
                "satellites": [
                    {
                        "name": "phobos",
                        "scale": 0.00015,  # Adjusted for simulation
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.009,  # Proportional to Mars
                        "rotation_speeds_self": 0.001,  # High speed for visibility
                        "rotation_angles": 0
                    },
                    {
                        "name": "deimos",
                        "scale": 0.0001,  # Adjusted for simulation
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.012,  # Proportional to Mars
                        "rotation_speeds_self": 0.01,  # High speed for visibility
                        "rotation_angles": 0
                    }
                ]
            },

            # Adjustments for Jupiter's moons
            "jupiter": {
                "scale": 0.05023, "texture_path": "../../assets/textures/planetaJupiter.jpg",
                "orbit_radius": 8.482, "rotation_speeds_self": 2.4242, "rotation_angles": 0,
                "rotation_speeds_sun": 4.329,
                "satellites": [
                    {
                        "name": "io",
                        "scale": 0.0018*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.06,
                        "rotation_speeds_self": 0.04,
                        "rotation_angles": 0
                    },
                    {
                        "name": "europa",
                        "scale": 0.0015*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.07,
                        "rotation_speeds_self": 0.08,
                        "rotation_angles": 0
                    },
                    {
                        "name": "ganymede",
                        "scale": 0.002*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.09,
                        "rotation_speeds_self": 0.01,
                        "rotation_angles": 0
                    },
                    {
                        "name": "callisto",
                        "scale": 0.0019*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.18,
                        "rotation_speeds_self": 0.04,
                        "rotation_angles": 0
                    },
                    {
                        "name": "amalthea",
                        "scale": 0.0005*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.1,
                        "rotation_speeds_self": 0.011,
                        "rotation_angles": 0
                    },
                    {
                        "name": "himalia",
                        "scale": 0.0007*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.08,
                        "rotation_speeds_self": 0.25,
                        "rotation_angles": 0
                    }
                ]
            },

            # Adjustments for Saturn's moons
            "saturn": {
                "scale": 0.04185, "texture_path": "../../assets/textures/planetaSaturno.jpg",
                "orbit_radius": 15.499, "rotation_speeds_self": 2.243, "rotation_angles": 0,
                "rotation_speeds_sun": 10.753,
                "satellites": [
                    {
                        "name": "titan",
                        "scale": 0.0017*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.8,
                        "rotation_speeds_self": 0.38,
                        "rotation_angles": 0
                    },
                    {
                        "name": "rhea",
                        "scale": 0.0008*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.3,
                        "rotation_speeds_self": 0.1,
                        "rotation_angles": 0
                    },
                    {
                        "name": "iapetus",
                        "scale": 0.0007*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.2,
                        "rotation_speeds_self": 0.19,
                        "rotation_angles": 0
                    },
                    {
                        "name": "dione",
                        "scale": 0.0006*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.28,
                        "rotation_speeds_self": 0.65,
                        "rotation_angles": 0
                    },
                    {
                        "name": "tethys",
                        "scale": 0.0005*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.19,
                        "rotation_speeds_self": 0.45,
                        "rotation_angles": 0
                    },
                    {
                        "name": "enceladus",
                        "scale": 0.0003*2,
                        "texture_path": "../../assets/textures/meme.jpg",
                        "orbit_radius": 0.13,
                        "rotation_speeds_self": 0.32,
                        "rotation_angles": 0
                    }
                ]
            },

            # Adjustments for Uranus's moons
            "uranus": {
                "scale": 0.01822, "texture_path": "../../assets/textures/planetaUrano.jpg",
                "orbit_radius": 31.456, "rotation_speeds_self": 1.3954, "rotation_angles": 0,
                "rotation_speeds_sun": 84.0109,
                "satellites": [
                    {"name": "titania", "scale": 0.002, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.08, "rotation_speeds_self": 0.28, "rotation_angles": 0},
                    {"name": "oberon", "scale": 0.0025, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.1, "rotation_speeds_self": 0.323, "rotation_angles": 0},
                    {"name": "umbriel", "scale": 0.002, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.2, "rotation_speeds_self": 0.9, "rotation_angles": 0},
                    {"name": "ariel", "scale": 0.0015, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.3, "rotation_speeds_self": 0.6, "rotation_angles": 0},
                    {"name": "miranda", "scale": 0.002, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.4, "rotation_speeds_self": 0.34, "rotation_angles": 0},
                    {"name": "puck", "scale": 0.003, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.5, "rotation_speeds_self": 0.18, "rotation_angles": 0}
                ]
            },

            # Adjustments for Neptune's moons
            "neptune": {
                "scale": 0.01767, "texture_path": "../../assets/textures/planetaNeptuno.jpg",
                "orbit_radius": 54.176, "rotation_speeds_self": 1.4906, "rotation_angles": 0,
                "rotation_speeds_sun": 90.411,
                "satellites": [
                    {"name": "triton", "scale": 0.003, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.25, "rotation_speeds_self": -0.14, "rotation_angles": 0},
                    {"name": "proteus", "scale": 0.004, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.3, "rotation_speeds_self": 0.25, "rotation_angles": 0},
                    {"name": "nereid", "scale": 0.0045, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.35, "rotation_speeds_self": 0.36, "rotation_angles": 0},
                    {"name": "larissa", "scale": 0.003, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.4, "rotation_speeds_self": 0.13, "rotation_angles": 0},
                    {"name": "galatea", "scale": 0.005, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.45, "rotation_speeds_self": 0.1, "rotation_angles": 0},
                    {"name": "despina", "scale": 0.004, "texture_path": "../../assets/textures/meme.jpg",
                     "orbit_radius": 0.5, "rotation_speeds_self": 0.8, "rotation_angles": 0}
                ]
            }
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
            self.planets[planet_name].satellites = []

            for sat_data in data.get("satellites", []):
                satellite = ObjTextureMesh(self.program_id, "../../assets/models/modeloPlaneta.obj",
                                           sat_data["texture_path"])
                satellite.orbit_radius = sat_data["orbit_radius"]
                satellite.scale = sat_data["scale"]
                satellite.rotation_speeds_self = sat_data["rotation_speeds_self"]
                satellite.rotation_angles = sat_data["rotation_angles"]
                self.planets[planet_name].satellites.append(satellite)
            #self.planets[planet_name] = planet

        # estrellas
        self.stars = ObjTextureMesh(
            self.program_id,
            "../../assets/models/modeloPlaneta.obj",
            "../../assets/textures/estrellas.jpg"
        )

    def draw_planet(self, planet_name, transformation):
        planet = self.planets[planet_name]
        planet.draw(transformation)
        for satellite in planet.satellites:
            self.draw_satellite(transformation, satellite)

    def draw_satellite(self, planet_transform, satellite):
        # La rotación del satélite debe ser independiente de si los planetas están pausados
        rotation_angle = (pygame.time.get_ticks() * satellite.rotation_speeds_self) % 360

        x = satellite.orbit_radius * np.cos(np.radians(rotation_angle))
        z = satellite.orbit_radius * np.sin(np.radians(rotation_angle))

        transform = translate(identity_mat(), planet_transform[0][3] + x, planet_transform[1][3],
                              planet_transform[2][3] + z)
        transform = rotate(transform, satellite.rotation_angles, 'y')
        transform = scale(transform, satellite.scale, satellite.scale, satellite.scale)

        satellite.draw(transform)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()

        if get_orbit_paused() == False:
            self.valor += 0.00001  # Incrementar solo si no está pausada la rotación

        sun_position = np.array([0, 0, 0])
        sun_pos_location = glGetUniformLocation(self.program_id, 'sunPosition')
        glUniform3f(sun_pos_location, *sun_position)

        for planet_name, planet_data in self.planets.items():
            orbit_radius = planet_data.orbit_radius
            orbital_speed = planet_data.rotation_speeds_sun
            angular_speed = 2 * np.pi / orbital_speed if orbital_speed != 0 else 0

            if get_orbit_paused() == False:
                angular_position = (self.valor * angular_speed) % (2 * np.pi)
            else:
                angular_position = 0  # No cambiar la posición si está pausado

            x = orbit_radius * np.cos(angular_position)
            y = 0
            z = orbit_radius * np.sin(angular_position)

            transformation = identity_mat()
            transformation = translate(transformation, x, y, z)

            if get_orbit_paused() == False:
                planet_data.rotation_angles = (planet_data.rotation_angles + 0.1) % 360
            axial_rotation_angle = planet_data.rotation_angles
            transformation = rotate(transformation, axial_rotation_angle, 'y')

            scale_factor = planet_data.scale
            transformation = scale(transformation, scale_factor, scale_factor, scale_factor)

            self.draw_planet(planet_name, transformation)

        # Dibuja estrellas
        transformation_stars = identity_mat()
        transformation_stars = scale(transformation_stars, 100, 100, 100)
        self.stars.draw(transformation_stars)


if __name__ == '__main__':
    VertexShaderCameraDemo().main_loop()
