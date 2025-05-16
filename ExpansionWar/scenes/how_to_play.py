import pygame
import random
import config
from entities.planet import Planet


class HowToPlayScene:
    def __init__(self):
        self.title_font = pygame.font.Font(config.assets[config.FONT_NAME], 100)
        self.text_font = pygame.font.Font(config.assets[config.FONT_NAME], 20)
        self.button_font = pygame.font.Font(config.assets[config.FONT_NAME], 36)

        self.title_text = self.title_font.render("How To Play", True, (255, 255, 255))

        self.instructions = [
            "Planets:",
            "Click on your planet",
            "then click on an enemy or neutral planet",
            "to create a connection",
            "",
            "",
            "Units:",
            "Planet sends units to connected planet",
            "Drag a card onto one of your planets",
            "to activate its effect.",
            "",
            "",
            "Cards:",
            "Rockets: send one unit more in rocket",
            "Satellites: gain one unit more every second"
            "",
            "",
            "Colors:",
            "Green: player",
            "Gray: neutral",
            "Every other: enemy"
            "",
            "",
            "Use quick thinking and tactical moves",
            "to outmaneuver your opponent and take over the galaxy!"
        ]

        self.back_text = self.button_font.render("Back", True, (0, 0, 0))
        button_width, button_height = 350, 90
        self.back_button_rect = pygame.Rect(
            (config.SCREEN_WIDTH - button_width) // 2,
            (config.SCREEN_HEIGHT - button_height - 80),
            button_width,
            button_height
        )

        self.floating_planets = []
        for _ in range(3):
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            radius = random.uniform(30, 150)

            x = random.uniform(radius * 2, config.GAME_SCENE_WIDTH - radius * 2)
            y = random.uniform(radius * 2, config.GAME_SCENE_HEIGHT - radius * 2)

            planet = Planet(x, y, color, radius, False)
            planet.velocity = (random.uniform(-10, 10), random.uniform(-10, 10))
            self.floating_planets.append(planet)

        self.black_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.black_surface.set_alpha(200)
        self.black_surface.fill((0, 0, 0))


    def move_entities(self, dt):
        for planet in self.floating_planets:
            planet.x += planet.velocity[0] * dt
            planet.y += planet.velocity[1] * dt

            planet.center_x = planet.x + planet.radius
            planet.center_y = planet.y + planet.radius

            if planet.center_x - planet.radius < 0 or planet.center_x + planet.radius > config.SCREEN_WIDTH:
                vx, vy = planet.velocity
                planet.velocity = (-vx, vy)
            if planet.center_y - planet.radius < 0 or planet.center_y + planet.radius > config.SCREEN_HEIGHT:
                vx, vy = planet.velocity
                planet.velocity = (vx, -vy)

    def draw(self, surface):
        self.move_entities(1 / 60)

        screen_width, screen_height = surface.get_size()

        # Draw floating planets in the background
        for planet in self.floating_planets:
            planet.draw(surface, 0, 0, 0)

        # Draw black surface
        surface.blit(self.black_surface, (0,0))

        # Draw How To Play text
        title_rect = self.title_text.get_rect(midtop=(screen_width // 2, 80))
        surface.blit(self.title_text, title_rect)

        # Draw instructions (centered text block)
        y_offset = title_rect.bottom + 80
        for line in self.instructions:
            line_surface = self.text_font.render(line, True, (255, 255, 255))
            line_rect = line_surface.get_rect(center=(screen_width // 2, y_offset))
            surface.blit(line_surface, line_rect)
            y_offset += line_surface.get_height() + 10

        # Draw the back button
        pygame.draw.rect(surface, (255, 255, 255), self.back_button_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.back_button_rect, 2)
        back_text_rect = self.back_text.get_rect(center=self.back_button_rect.center)
        surface.blit(self.back_text, back_text_rect)

    def handle_click(self, pos):
        if self.back_button_rect.collidepoint(pos):
            from scenes.menu_scene import MenuScene
            config.set_scene(MenuScene())
            return True
        return False
