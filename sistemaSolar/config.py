orbit_paused = False

# Función para obtener el estado de 'orbit_paused'
def get_orbit_paused():
    global orbit_paused
    return orbit_paused

# Función para establecer el estado de 'orbit_paused'
def set_orbit_paused():
    global orbit_paused
    orbit_paused = not orbit_paused