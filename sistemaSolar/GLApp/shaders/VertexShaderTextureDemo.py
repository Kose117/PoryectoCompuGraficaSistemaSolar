import numpy as np
from OpenGL.GL import *
from sistemaSolar.GLApp.BaseApps.BaseScene import BaseScene
from sistemaSolar.GLApp.Camera.Camera import Camera
from sistemaSolar.GLApp.Mesh.Light.ObjTextureMesh import ObjTextureMesh
from sistemaSolar.GLApp.Transformations.Transformations import identity_mat, scale, translate
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
    lightPos = vec3(0, 0, 0);  // Sun's position at the center
    
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
    

    // Ambient
    float a_strength = 0.3;
    vec3 ambient = a_strength * lightColor;

    // Diffuse
    vec3 norm = normalize(normal);
    vec3 lightDirection = normalize(lightPos - fragPos);
    float diff = max(dot(norm, lightDirection), 0);
    vec3 diffuse = diff * lightColor;

    // Specular
    float s_strength = 0.8;
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 reflectDir = normalize(-lightDirection - norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = s_strength * spec * lightColor;

    // Add shine to the sun
    if (length(fragPos - lightPos) < 0.1) {
        fragColor = vec4(1.0, 1.0, 0.0, 1.0); // Yellow color
        return;
    }

    fragColor = vec4(color * (ambient + diffuse + specular), 1);
    fragColor = fragColor * texture(tex, uv);
    

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
        self.planets = {}
        self.valor = 0.0

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

    def draw_world_axes(self):
        glBindVertexArray(self.vao_axes)
        glDrawArrays(GL_LINES, 0, 6)
        glBindVertexArray(0)

    def initialize_orbits(self, radii):
        orbits = []
        for radius in radii:
            orbit_vertices = []
            for i in range(360):
                angle = np.radians(i)
                x = np.cos(angle) * radius
                z = np.sin(angle) * radius
                y = 0  # Mantener en el plano horizontal
                orbit_vertices.extend([x, y, z])
            orbits.append(orbit_vertices)

        self.vao_orbits = glGenVertexArrays(len(orbits))
        self.vbo_orbits = glGenBuffers(len(orbits))

        for i, orbit in enumerate(orbits):
            glBindVertexArray(self.vao_orbits[i])
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo_orbits[i])
            glBufferData(GL_ARRAY_BUFFER, np.array(orbit, dtype=np.float32), GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), None)
            glEnableVertexAttribArray(0)

    def draw_orbits(self):
        glLineWidth(2.0)
        glColor3f(1.0, 1.0, 1.0)
        for i in range(len(self.planets)):
            glBindVertexArray(self.vao_orbits[i])
            glDrawArrays(GL_LINE_LOOP, 0, 360)
        glBindVertexArray(0)

    def initialize(self):
        self.program_id = create_program(vertex_shader, fragment_shader)
        self.initialize_axes()
        self.initialize_planets()
        orbit_radii = [planet.orbit_radius for planet in self.planets.values()]
        self.initialize_orbits(orbit_radii)
        self.camera = Camera(self.program_id, self.screen.get_width(), self.screen.get_height())
        glEnable(GL_DEPTH_TEST)

    def initialize_planets(self):
        planets_data = {
            "mercury": {"scale": 0.076, "texture_path": "../../assets/textures/planetaMercurio.jpg", "orbit_radius": 10},
            "venus": {"scale": 0.19, "texture_path": "../../assets/textures/planetaVenus.jpg", "orbit_radius": 20},
            "earth": {"scale": 0.2, "texture_path": "../../assets/textures/planetaTierra.jpg", "orbit_radius": 30},
            "mars": {"scale": 0.106, "texture_path": "../../assets/textures/planetaMarte.jpg", "orbit_radius": 40},
            "jupiter": {"scale": 2.194, "texture_path": "../../assets/textures/planetaJupiter.jpg", "orbit_radius": 50},
            "saturn": {"scale": 1.828, "texture_path": "../../assets/textures/planetaSaturno.jpg", "orbit_radius": 60},
            "uranus": {"scale": 0.796, "texture_path": "../../assets/textures/planetaUrano.jpg", "orbit_radius": 70},
            "neptune": {"scale": 0.772, "texture_path": "../../assets/textures/planetaNeptuno.jpg", "orbit_radius": 80},
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

        # Dibujar ejes mundiales y órbitas
        self.draw_world_axes()
        self.draw_orbits()

        # Dibujar planetas
        for planet_name, data in self.planets.items():
            transformation = identity_mat()
            orbit_radius = data.orbit_radius
            # Calcular la posición en la órbita (en el plano XZ)
            x = orbit_radius * np.cos(self.valor)
            y = 0  # Mantener en el plano horizontal
            z = orbit_radius * np.sin(self.valor)
            transformation = translate(transformation, x, y, z)

            # Dibuja estrellas
            transformation_stars = identity_mat()
            transformation_stars = scale(transformation_stars, 160, 160, 160)
            transformation_stars = translate(transformation_stars, 0, 0, 0)
            self.stars.draw(transformation_stars)

            if planet_name != "sun":
                planet_transformation = scale(transformation, data.scale, data.scale, data.scale)
                self.draw_planet(planet_name, planet_transformation)
            else:
                self.draw_planet(planet_name, transformation)


if __name__ == '__main__':
    VertexShaderCameraDemo().main_loop()
