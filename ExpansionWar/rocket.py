import math

from config import *

class Rocket:
    def __init__(self, scene, planet, other_planet):
        if planet.color == other_planet.color:
            self.rocket_texture = rocket_assets["spaceRockets_001"]
        else:
            self.rocket_texture = rocket_assets["spaceRockets_002"]

        self.rocket_texture = pygame.transform.scale(self.rocket_texture, (20 * 2, 20 * 2))

        self.rocket_texture = pygame.transform.rotate(self.rocket_texture,-math.degrees(math.atan2(other_planet.center_y - planet.center_y, other_planet.center_x - planet.center_x)) - 90)

        self.scene = scene
        self.planet = planet
        self.other_planet = other_planet

        self.current_time = 0
        self.target_time = ((planet.center_x - other_planet.center_x)**2 + (planet.center_y - other_planet.center_y)**2)**0.5/5

        self.x = planet.center_x
        self.y = planet.center_y

    def draw(self, base_x, base_y, screen):
        self.current_time +=1

        if self.current_time >= self.target_time:
            self.other_planet.value += 1
            self.scene.rocket_finished(self)

        self.x = lerp(0, self.target_time, self.planet.center_x, self.other_planet.center_x, self.current_time)
        self.y = lerp(0, self.target_time, self.planet.center_y, self.other_planet.center_y, self.current_time)

        rotated_rect = self.rocket_texture.get_rect(center=(base_x + self.x, base_y + self.y))
        screen.blit(self.rocket_texture, rotated_rect)
