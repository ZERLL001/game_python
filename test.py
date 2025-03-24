import pygame
import random
import sys
import json
import os
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 500
FPS = 60
GRAVITY = 0.8  # Reduced gravity for easier control
JUMP_STRENGTH = -12  # Less powerful jump for better control

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
RED = (255, 50, 50)
GREEN = (0, 255, 0)
PURPLE = (147, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
DARK_BLUE = (20, 30, 70)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 20, 147)
NEON_BLUE = (0, 191, 255)
NEON_ORANGE = (255, 103, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Clone")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont('Arial', 48, bold=True)
menu_font = pygame.font.SysFont('Arial', 36)
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)

MAIN_MENU = 0
LEVEL_SELECT = 1
PLAYING = 2
GAME_OVER = 3
CHALLENGES = 4
PAUSE = 5

CUBE = 0
SHIP = 1
BALL = 2
UFO = 3
WAVE = 4

game_state = MAIN_MENU
current_level = 0
score = 0
high_scores = [0, 0, 0]
challenges_completed = []
game_mode = CUBE
game_speed = 1.0

LEVELS = [
    {
        "name": "Stereo Madness",
        "description": "The beginning of your journey!",
        "background_color": (20, 30, 70),
        "ground_color": (0, 180, 80),
        "obstacle_colors": [(255, 50, 50), (255, 100, 100)],
        "player_color": NEON_BLUE,
        "decoration_colors": [NEON_GREEN, NEON_BLUE, NEON_PINK],
        "base_scroll_speed": 4,  # Reduced speed
        "obstacle_frequency": 2000,  # More time between obstacles
        "background_elements": 30,
        "has_ship_mode": False,
        "has_ball_mode": False,
        "has_ufo_mode": False,
        "has_wave_mode": False,
        "has_speed_changes": True,
        "obstacle_patterns": [
            "basic_spike_row",
            "basic_block",
            "double_spike",
            "platform_jump"
        ]
    },
    {
        "name": "Back On Track",
        "description": "Find your rhythm!",
        "background_color": (70, 20, 90),
        "ground_color": (255, 140, 0),
        "obstacle_colors": [(0, 191, 255), (0, 150, 200)],
        "player_color": NEON_ORANGE,
        "decoration_colors": [NEON_PINK, YELLOW, CYAN],
        "base_scroll_speed": 5,  # Reduced speed
        "obstacle_frequency": 1800,  # More time between obstacles
        "background_elements": 40,
        "has_ship_mode": True,
        "has_ball_mode": False,
        "has_ufo_mode": False,
        "has_wave_mode": False,
        "has_speed_changes": True,
        "obstacle_patterns": [
            "basic_spike_row",
            "basic_block",
            "double_spike",
            "platform_jump",
            "ship_tunnel",
            "ship_columns"
        ]
    },
    {
        "name": "Polargeist",
        "description": "Master all game modes!",
        "background_color": (20, 70, 90),
        "ground_color": (180, 0, 180),
        "obstacle_colors": [(255, 20, 147), (200, 0, 100)],
        "player_color": NEON_GREEN,
        "decoration_colors": [NEON_BLUE, NEON_ORANGE, YELLOW],
        "base_scroll_speed": 6,  # Reduced speed
        "obstacle_frequency": 1600,  # More time between obstacles
        "background_elements": 50,
        "has_ship_mode": True,
        "has_ball_mode": True,
        "has_ufo_mode": True,
        "has_wave_mode": True,
        "has_speed_changes": True,
        "obstacle_patterns": [
            "basic_spike_row",
            "basic_block",
            "double_spike",
            "platform_jump",
            "ship_tunnel",
            "ship_columns",
            "ball_platforms",
            "ufo_pillars",
            "wave_corridor"
        ]
    }
]

CHALLENGES = [
    {"id": 0, "name": "Beginner", "description": "Score 5 points in any level", "requirement": 5, "completed": False},  # Easier requirement
    {"id": 1, "name": "Intermediate", "description": "Score 10 points in any level", "requirement": 10, "completed": False},  # Easier requirement
    {"id": 2, "name": "Expert", "description": "Score 15 points in any level", "requirement": 15, "completed": False},  # Easier requirement
    {"id": 3, "name": "Level Master", "description": "Complete all levels", "requirement": 3, "completed": False},
    {"id": 4, "name": "Perfect Run", "description": "Score 10 without jumping more than 20 times", "requirement": 10, "completed": False},  # Easier requirement
    {"id": 5, "name": "Mode Master", "description": "Use all game modes in a single run", "requirement": 5, "completed": False}
]

def save_game_data():
    data = {
        "high_scores": high_scores,
        "challenges": [c["completed"] for c in CHALLENGES]
    }
    with open("geometry_dash_save.json", "w") as f:
        json.dump(data, f)

def load_game_data():
    global high_scores
    if os.path.exists("geometry_dash_save.json"):
        try:
            with open("geometry_dash_save.json", "r") as f:
                data = json.load(f)
                high_scores = data.get("high_scores", [0, 0, 0])
                challenge_status = data.get("challenges", [False] * len(CHALLENGES))
                for i, status in enumerate(challenge_status):
                    if i < len(CHALLENGES):
                        CHALLENGES[i]["completed"] = status
        except:
            print("Error loading save data")

class CubePlayer:
    def __init__(self, color=BLUE):
        self.width = 30
        self.height = 30
        self.x = 100
        self.y = HEIGHT - 50 - self.height
        self.vel_y = 0
        self.jumping = False
        self.on_ground = True
        self.color = color
        self.rotation = 0
        self.jump_count = 0
        self.mode = CUBE
        self.invincible = False  # Add invincibility frames
        self.invincible_timer = 0
    
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            self.jumping = True
            self.jump_count += 1
    
    def update(self, scroll_speed):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        if self.y >= HEIGHT - 50 - self.height:
            self.y = HEIGHT - 50 - self.height
            self.vel_y = 0
            self.on_ground = True
            self.jumping = False
            self.rotation = 0
        else:
            self.rotation = (self.rotation - 5) % 360
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def make_invincible(self, duration=30):
        self.invincible = True
        self.invincible_timer = duration
    
    def draw(self):
        player_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.invincible and self.invincible_timer % 4 < 2:  # Flashing effect when invincible
            draw_color = WHITE
        else:
            draw_color = self.color
            
        pygame.draw.rect(player_surface, draw_color, (0, 0, self.width, self.height))
        
        pygame.draw.line(player_surface, BLACK, (0, 0), (self.width, 0), 2)
        pygame.draw.line(player_surface, BLACK, (0, 0), (0, self.height), 2)
        pygame.draw.line(player_surface, BLACK, (self.width, 0), (self.width, self.height), 2)
        pygame.draw.line(player_surface, BLACK, (0, self.height), (self.width, self.height), 2)
        
        pygame.draw.circle(player_surface, WHITE, (self.width//4, self.height//3), 5)
        pygame.draw.circle(player_surface, WHITE, (3*self.width//4, self.height//3), 5)
        pygame.draw.circle(player_surface, BLACK, (self.width//4, self.height//3), 2)
        pygame.draw.circle(player_surface, BLACK, (3*self.width//4, self.height//3), 2)
        
        if self.jumping:
            rotated_surface = pygame.transform.rotate(player_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(rotated_surface, rotated_rect.topleft)
        else:
            screen.blit(player_surface, (self.x, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)  # Smaller hitbox

class ShipPlayer:
    def __init__(self, color=BLUE):
        self.width = 40
        self.height = 20
        self.x = 100
        self.y = HEIGHT // 2
        self.vel_y = 0
        self.color = color
        self.rotation = 0
        self.mode = SHIP
        self.invincible = False
        self.invincible_timer = 0
    
    def jump(self):
        self.vel_y = -1.5  # Gentler upward force
    
    def release(self):
        self.vel_y = 0
    
    def update(self, scroll_speed):
        self.vel_y += 0.15  # Gentler gravity
        
        self.y += self.vel_y
        
        self.vel_y = max(-4, min(4, self.vel_y))  # Limit velocity
        
        self.y = max(10, min(HEIGHT - 60, self.y))
        
        self.rotation = -self.vel_y * 5
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def make_invincible(self, duration=30):
        self.invincible = True
        self.invincible_timer = duration
    
    def draw(self):
        ship_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.invincible and self.invincible_timer % 4 < 2:
            draw_color = WHITE
        else:
            draw_color = self.color
        
        pygame.draw.polygon(ship_surface, draw_color, [
            (0, self.height//2),
            (self.width//4, 0),
            (self.width, self.height//2),
            (self.width//4, self.height)
        ])
        
        pygame.draw.line(ship_surface, BLACK, (0, self.height//2), (self.width//4, 0), 2)
        pygame.draw.line(ship_surface, BLACK, (self.width//4, 0), (self.width, self.height//2), 2)
        pygame.draw.line(ship_surface, BLACK, (self.width, self.height//2), (self.width//4, self.height), 2)
        pygame.draw.line(ship_surface, BLACK, (self.width//4, self.height), (0, self.height//2), 2)
        
        pygame.draw.circle(ship_surface, WHITE, (self.width//2, self.height//2), 5)
        
        rotated_surface = pygame.transform.rotate(ship_surface, self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(rotated_surface, rotated_rect.topleft)
    
    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + 8, self.width - 16, self.height - 16)  # Even smaller hitbox for ship

class BallPlayer:
    def __init__(self, color=BLUE):
        self.radius = 15
        self.x = 100
        self.y = HEIGHT - 50 - self.radius
        self.vel_y = 0
        self.color = color
        self.rotation = 0
        self.on_ground = True
        self.on_ceiling = False
        self.mode = BALL
        self.invincible = False
        self.invincible_timer = 0
    
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
        elif self.on_ceiling:
            self.vel_y = -JUMP_STRENGTH
            self.on_ceiling = False
    
    def update(self, scroll_speed):
        if self.on_ceiling:
            self.vel_y -= GRAVITY
        else:
            self.vel_y += GRAVITY
        
        self.y += self.vel_y
        
        if self.y >= HEIGHT - 50 - self.radius:
            self.y = HEIGHT - 50 - self.radius
            self.vel_y = 0
            self.on_ground = True
            self.on_ceiling = False
        elif self.y <= self.radius:
            self.y = self.radius
            self.vel_y = 0
            self.on_ceiling = True
            self.on_ground = False
        else:
            self.on_ground = False
            self.on_ceiling = False
        
        self.rotation = (self.rotation + scroll_speed * 2) % 360
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def make_invincible(self, duration=30):
        self.invincible = True
        self.invincible_timer = duration
    
    def draw(self):
        if self.invincible and self.invincible_timer % 4 < 2:
            draw_color = WHITE
        else:
            draw_color = self.color
            
        pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        angle = math.radians(self.rotation)
        end_x = self.x + math.cos(angle) * self.radius
        end_y = self.y + math.sin(angle) * self.radius
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius + 5, self.y - self.radius + 5, self.radius * 2 - 10, self.radius * 2 - 10)  # Smaller hitbox

class UfoPlayer:
    def __init__(self, color=BLUE):
        self.width = 30
        self.height = 20
        self.x = 100
        self.y = HEIGHT // 2
        self.vel_y = 0
        self.color = color
        self.mode = UFO
        self.hover_offset = 0
        self.hover_direction = 1
        self.invincible = False
        self.invincible_timer = 0
    
    def jump(self):
        self.vel_y = -6  # Less powerful jump
    
    def update(self, scroll_speed):
        self.vel_y += 0.3  # Gentler gravity
        
        self.y += self.vel_y
        
        self.vel_y = max(-8, min(6, self.vel_y))  # Limit velocity
        
        self.y = max(10, min(HEIGHT - 60, self.y))
        
        self.hover_offset += 0.1 * self.hover_direction
        if abs(self.hover_offset) > 2:
            self.hover_direction *= -1
            
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def make_invincible(self, duration=30):
        self.invincible = True
        self.invincible_timer = duration
    
    def draw(self):
        if self.invincible and self.invincible_timer % 4 < 2:
            draw_color = WHITE
        else:
            draw_color = self.color
            
        pygame.draw.ellipse(screen, draw_color, (self.x, self.y + self.hover_offset, self.width, self.height))
        pygame.draw.ellipse(screen, BLACK, (self.x, self.y + self.hover_offset, self.width, self.height), 2)
        
        pygame.draw.arc(screen, draw_color, (self.x + 5, self.y + self.hover_offset - 10, self.width - 10, 20), 
                        math.pi, 2 * math.pi, 3)
        pygame.draw.arc(screen, BLACK, (self.x + 5, self.y + self.hover_offset - 10, self.width - 10, 20), 
                        math.pi, 2 * math.pi, 2)
        
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + self.width // 2, self.y + self.hover_offset + self.height),
            (self.x + self.width // 2 - 5, self.y + self.hover_offset + self.height + 10),
            (self.x + self.width // 2 + 5, self.y + self.hover_offset + self.height + 10)
        ])
    
    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + self.hover_offset + 8, self.width - 16, self.height - 10)  # Smaller hitbox

class WavePlayer:
    def __init__(self, color=BLUE):
        self.width = 30
        self.height = 10
        self.x = 100
        self.y = HEIGHT // 2
        self.direction = 1
        self.color = color
        self.mode = WAVE
        self.wave_points = []
        self.trail_length = 20
        self.invincible = False
        self.invincible_timer = 0
    
    def jump(self):
        self.direction = -1
    
    def release(self):
        self.direction = 1
    
    def update(self, scroll_speed):
        self.y += self.direction * 3  # Slower movement
        
        self.y = max(10, min(HEIGHT - 60, self.y))
        
        self.wave_points.insert(0, (self.x, self.y))
        if len(self.wave_points) > self.trail_length:
            self.wave_points.pop()
            
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def make_invincible(self, duration=30):
        self.invincible = True
        self.invincible_timer = duration
    
    def draw(self):
        if self.invincible and self.invincible_timer % 4 < 2:
            draw_color = WHITE
        else:
            draw_color = self.color
            
        if len(self.wave_points) > 1:
            for i in range(len(self.wave_points) - 1):
                alpha = 255 - int(255 * (i / self.trail_length))
                if self.invincible and self.invincible_timer % 4 < 2:
                    trail_color = (255, 255, 255, alpha)
                else:
                    trail_color = (*self.color, alpha)
                pygame.draw.line(screen, trail_color, 
                                self.wave_points[i], self.wave_points[i+1], 
                                3 - int(2 * (i / self.trail_length)))
        
        pygame.draw.circle(screen, draw_color, (int(self.x), int(self.y)), 5)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 5, 1)
    
    def get_rect(self):
        return pygame.Rect(self.x - 3, self.y - 3, 6, 6)  # Much smaller hitbox for wave

class Obstacle:
    def __init__(self, x, height, color=RED):
        self.width = 30
        self.height = height
        self.x = x
        self.y = HEIGHT - 50 - self.height
        self.color = color
        self.passed = False
        self.decoration = random.randint(0, 3)
    
    def update(self, scroll_speed):
        self.x -= scroll_speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        if self.decoration == 0:
            for i in range(0, self.height, 10):
                pygame.draw.line(screen, BLACK, (self.x, self.y + i), (self.x + self.width, self.y + i), 1)
        elif self.decoration == 1:
            for i in range(0, self.height, 10):
                for j in range(0, self.width, 10):
                    pygame.draw.circle(screen, BLACK, (self.x + j + 5, self.y + i + 5), 2)
        elif self.decoration == 2:
            pygame.draw.line(screen, BLACK, (self.x, self.y), (self.x + self.width, self.y + self.height), 2)
            pygame.draw.line(screen, BLACK, (self.x + self.width, self.y), (self.x, self.y + self.height), 2)
        else:
            pygame.draw.line(screen, BLACK, (self.x + 5, self.y + 5), (self.x + self.width - 5, self.y + 5), 2)
            pygame.draw.line(screen, BLACK, (self.x + 5, self.y + self.height - 5), 
                            (self.x + self.width - 5, self.y + self.height - 5), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x + 3, self.y + 3, self.width - 6, self.height - 6)  # Smaller hitbox

class Spike:
    def __init__(self, x, color=RED, upside_down=False):
        self.width = 30
        self.height = 30
        self.x = x
        self.upside_down = upside_down
        if upside_down:
            self.y = 0
        else:
            self.y = HEIGHT - 50 - self.height
        self.color = color
        self.passed = False
        self.glow = False
    
    def update(self, scroll_speed):
        self.x -= scroll_speed
        self.glow = random.random() < 0.02
    
    def draw(self):
        if self.upside_down:
            points = [
                (self.x, self.y),
                (self.x + self.width//2, self.y + self.height),
                (self.x + self.width, self.y)
            ]
        else:
            points = [
                (self.x, self.y + self.height),
                (self.x + self.width//2, self.y),
                (self.x + self.width, self.y + self.height)
            ]
        
        if self.glow:
            glow_color = (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50))
            pygame.draw.polygon(screen, glow_color, points)
        else:
            pygame.draw.polygon(screen, self.color, points)
        
        pygame.draw.polygon(screen, BLACK, points, 2)
        
        if self.upside_down:
            pygame.draw.line(screen, BLACK, 
                            (self.x + 10, self.y + 10), 
                            (self.x + self.width - 10, self.y + 10), 2)
        else:
            pygame.draw.line(screen, BLACK, 
                            (self.x + 10, self.y + self.height - 10), 
                            (self.x + self.width - 10, self.y + self.height - 10), 2)
    
    def get_rect(self):
        if self.upside_down:
            return pygame.Rect(self.x + 8, self.y + 8, self.width - 16, self.height - 16)  # Smaller hitbox
        else:
            return pygame.Rect(self.x + 8, self.y + 8, self.width - 16, self.height - 16)  # Smaller hitbox

class Platform:
    def __init__(self, x, y, width, height, color=GREEN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.passed = False
    
    def update(self, scroll_speed):
        self.x -= scroll_speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        for i in range(0, self.width, 20):
            pygame.draw.line(screen, BLACK, (self.x + i, self.y), (self.x + i, self.y + self.height), 1)
        for i in range(0, self.height, 10):
            pygame.draw.line(screen, BLACK, (self.x, self.y + i), (self.x + self.width, self.y + i), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x + 3, self.y + 3, self.width - 6, self.height - 6)  # Smaller hitbox

class Ground:
    def __init__(self, color=GREEN):
        self.width = WIDTH
        self.height = 50
        self.x = 0
        self.y = HEIGHT - self.height
        self.color = color
        self.offset = 0
    
    def update(self, scroll_speed):
        self.offset = (self.offset + scroll_speed) % 20
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        for i in range(-int(self.offset), WIDTH, 20):
            pygame.draw.line(screen, BLACK, (i, self.y), (i, HEIGHT), 1)
        for i in range(self.y, HEIGHT, 10):
            pygame.draw.line(screen, BLACK, (0, i), (WIDTH, i), 1)

class Portal:
    def __init__(self, x, target_mode, color):
        self.width = 40
        self.height = 80
        self.x = x
        self.y = HEIGHT - 50 - self.height
        self.target_mode = target_mode
        self.color = color
        self.passed = False
        self.particles = []
        self.particle_timer = 0
    
    def update(self, scroll_speed):
        self.x -= scroll_speed
        
        self.particle_timer += 1
        if self.particle_timer >= 5:
            self.particle_timer = 0
            self.particles.append({
                'x': self.x + self.width//2,
                'y': random.randint(int(self.y), int(self.y + self.height)),
                'size': random.randint(2, 5),
                'life': 30
            })
        
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2, border_radius=10)
        
        for i in range(0, self.height, 10):
            pygame.draw.arc(screen, WHITE, 
                           (self.x + 5, self.y + i, self.width - 10, 10), 
                           0, math.pi, 2)
        
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            particle_color = (*self.color, alpha)
            pygame.draw.circle(screen, particle_color, 
                              (int(particle['x']), int(particle['y'])), 
                              particle['size'])
        
        if self.target_mode == CUBE:
            pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 30, 20, 20))
        elif self.target_mode == SHIP:
            pygame.draw.polygon(screen, WHITE, [
                (self.x + 10, self.y + 40),
                (self.x + 20, self.y + 30),
                (self.x + 30, self.y + 40),
                (self.x + 20, self.y + 50)
            ])
        elif self.target_mode == BALL:
            pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 40), 10)
        elif self.target_mode == UFO:
            pygame.draw.ellipse(screen, WHITE, (self.x + 10, self.y + 40, 20, 10))
        elif self.target_mode == WAVE:
            pygame.draw.line(screen, WHITE, (self.x + 10, self.y + 40), (self.x + 30, self.y + 40), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

class SpeedPortal:
    def __init__(self, x, speed_multiplier, color):
        self.width = 30
        self.height = 60
        self.x = x
        self.y = HEIGHT - 50 - self.height
        self.speed_multiplier = speed_multiplier
        self.color = color
        self.passed = False
        self.particles = []
    
    def update(self, scroll_speed):
        self.x -= scroll_speed
        
        if random.random() < 0.2:
            self.particles.append({
                'x': self.x + self.width//2,
                'y': random.randint(int(self.y), int(self.y + self.height)),
                'vx': -random.uniform(1, 3),
                'vy': random.uniform(-1, 1),
                'size': random.randint(2, 4),
                'life': 20
            })
        
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2, border_radius=8)
        
        if self.speed_multiplier == 0.5:
            pygame.draw.polygon(screen, WHITE, [
                (self.x + 15, self.y + 20),
                (self.x + 5, self.y + 30),
                (self.x + 15, self.y + 40)
            ])
        elif self.speed_multiplier == 1:
            pygame.draw.polygon(screen, WHITE, [
                (self.x + 10, self.y + 20),
                (self.x + 20, self.y + 30),
                (self.x + 10, self.y + 40)
            ])
        elif self.speed_multiplier == 1.5:
            for i in range(2):
                pygame.draw.polygon(screen, WHITE, [
                    (self.x + 5 + i*10, self.y + 20),
                    (self.x + 15 + i*10, self.y + 30),
                    (self.x + 5 + i*10, self.y + 40)
                ])
        elif self.speed_multiplier == 2:
            for i in range(3):
                pygame.draw.polygon(screen, WHITE, [
                    (self.x + 5 + i*7, self.y + 20),
                    (self.x + 12 + i*7, self.y + 30),
                    (self.x + 5 + i*7, self.y + 40)
                ])
        
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 20))
            particle_color = (*self.color, alpha)
            pygame.draw.circle(screen, particle_color, 
                              (int(particle['x']), int(particle['y'])), 
                              particle['size'])
    
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 10)

class Decoration:
    def __init__(self, x, y, decoration_type, color):
        self.x = x
        self.y = y
        self.type = decoration_type
        self.color = color
        self.size = random.randint(10, 30)
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-1, 1)
    
    def update(self, scroll_speed):
        self.x -= scroll_speed
        self.rotation = (self.rotation + self.rotation_speed) % 360
    
    def draw(self):
        if self.type == "square":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surface, self.color, (0, 0, self.size, self.size))
            pygame.draw.rect(surface, BLACK, (0, 0, self.size, self.size), 1)
            
            rotated = pygame.transform.rotate(surface, self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect.topleft)
            
        elif self.type == "triangle":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.polygon(surface, self.color, [
                (self.size//2, 0),
                (0, self.size),
                (self.size, self.size)
            ])
            pygame.draw.polygon(surface, BLACK, [
                (self.size//2, 0),
                (0, self.size),
                (self.size, self.size)
            ], 1)
            
            rotated = pygame.transform.rotate(surface, self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect.topleft)
            
        elif self.type == "circle":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size//2)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size//2, 1)
            
            angle = math.radians(self.rotation)
            end_x = self.x + math.cos(angle) * (self.size//2)
            end_y = self.y + math.sin(angle) * (self.size//2)
            pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 1)
            
        elif self.type == "star":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            points = []
            for i in range(5):
                angle = math.radians(i * 72)
                points.append((
                    self.size//2 + math.cos(angle) * (self.size//2),
                    self.size//2 + math.sin(angle) * (self.size//2)
                ))
                
                angle = math.radians(i * 72 + 36)
                points.append((
                    self.size//2 + math.cos(angle) * (self.size//4),
                    self.size//2 + math.sin(angle) * (self.size//4)
                ))
            
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, BLACK, points, 1)
            
            rotated = pygame.transform.rotate(surface, self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect.topleft)

class BackgroundElement:
    def __init__(self, bg_color):
        self.size = random.randint(10, 30)
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT - 100)
        self.speed = random.uniform(0.5, 2)
        self.color = self.get_contrasting_color(bg_color)
        self.shape = random.choice(["circle", "square", "triangle", "star"])
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
    
    def get_contrasting_color(self, bg_color):
        r, g, b = bg_color
        return ((r + 128) % 256, (g + 128) % 256, (b + 128) % 256)
    
    def update(self, scroll_speed):
        self.x -= self.speed * (scroll_speed / 5)
        self.rotation = (self.rotation + self.rotation_speed) % 360
        if self.x + self.size < 0:
            self.x = WIDTH + self.size
            self.y = random.randint(0, HEIGHT - 100)
            self.size = random.randint(10, 30)
            self.speed = random.uniform(0.5, 2)
    
    def draw(self):
        if self.shape == "circle":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size//2)
        elif self.shape == "square":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surface, self.color, (0, 0, self.size, self.size))
            
            rotated = pygame.transform.rotate(surface, self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect.topleft)
        elif self.shape == "triangle":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.polygon(surface, self.color, [
                (self.size//2, 0),
                (0, self.size),
                (self.size, self.size)
            ])
            
            rotated = pygame.transform.rotate(surface, self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect.topleft)
        elif self.shape == "star":
            surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            points = []
            for i in range(5):
                angle = math.radians(i * 72)
                points.append((
                    self.size//2 + math.cos(angle) * (self.size//2),
                    self.size//2 + math.sin(angle) * (self.size//2)
                ))
                
                angle = math.radians(i * 72 + 36)
                points.append((
                    self.size//2 + math.cos(angle) * (self.size//4),
                    self.size//2 + math.sin(angle) * (self.size//4)
                ))
            
            pygame.draw.polygon(surface, self.color, points)
            
            rotated = pygame.transform.rotate(surface, self.rotation)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect.topleft)

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=CYAN):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = menu_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class LevelButton:
    def __init__(self, x, y, width, height, level_index, level_data):
        self.rect = pygame.Rect(x, y, width, height)
        self.level_index = level_index
        self.level_data = level_data
        self.is_hovered = False
        self.locked = level_index > 0 and high_scores[level_index-1] < 10  # Easier to unlock (10 instead of 15)
    
    def draw(self):
        if self.locked:
            color = (100, 100, 100)
        else:
            color = self.level_data["player_color"] if self.is_hovered else (100, 100, 200)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        name_surf = menu_font.render(self.level_data["name"], True, WHITE)
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 25))
        screen.blit(name_surf, name_rect)
        
        desc_surf = small_font.render(self.level_data["description"], True, WHITE)
        desc_rect = desc_surf.get_rect(center=(self.rect.centerx, self.rect.centery))
        screen.blit(desc_surf, desc_rect)
        
        score_text = f"High Score: {high_scores[self.level_index]}"
        score_surf = small_font.render(score_text, True, WHITE)
        score_rect = score_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 25))
        screen.blit(score_surf, score_rect)
        
        if self.locked:
            lock_text = "🔒 Complete previous level"
            lock_surf = small_font.render(lock_text, True, WHITE)
            lock_rect = lock_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 50))
            screen.blit(lock_surf, lock_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click and not self.locked

class ChallengeButton:
    def __init__(self, x, y, width, height, challenge):
        self.rect = pygame.Rect(x, y, width, height)
        self.challenge = challenge
        self.is_hovered = False
    
    def draw(self):
        if self.challenge["completed"]:
            color = GREEN
        else:
            color = BLUE if self.is_hovered else (100, 100, 200)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        name_surf = font.render(self.challenge["name"], True, WHITE)
        name_rect = name_surf.get_rect(midleft=(self.rect.x + 20, self.rect.centery - 15))
        screen.blit(name_surf, name_rect)
        
        desc_surf = small_font.render(self.challenge["description"], True, WHITE)
        desc_rect = desc_surf.get_rect(midleft=(self.rect.x + 20, self.rect.centery + 15))
        screen.blit(desc_surf, desc_rect)
        
        if self.challenge["completed"]:
            status_text = "✓ Completed"
            status_color = GREEN
        else:
            status_text = "⚪ Incomplete"
            status_color = WHITE
        
        status_surf = small_font.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(midright=(self.rect.right - 20, self.rect.centery))
        screen.blit(status_surf, status_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

player = None
ground = None
obstacles = []
decorations = []
bg_elements = []
obstacle_timer = 0
used_game_modes = set()
lives = 3  # Add lives system

main_menu_buttons = [
    Button(WIDTH//2 - 150, 200, 300, 60, "Play"),
    Button(WIDTH//2 - 150, 280, 300, 60, "Challenges"),
    Button(WIDTH//2 - 150, 360, 300, 60, "Quit")
]

level_buttons = [
    LevelButton(WIDTH//2 - 200, 150 + i*120, 400, 100, i, LEVELS[i])
    for i in range(len(LEVELS))
]

back_button = Button(50, HEIGHT - 80, 120, 50, "Back")

challenge_buttons = [
    ChallengeButton(WIDTH//2 - 300, 120 + i*80, 600, 70, CHALLENGES[i])
    for i in range(len(CHALLENGES))
]

def init_level(level_index):
    global player, ground, obstacles, decorations, bg_elements, obstacle_timer, score, game_mode, game_speed, used_game_modes, lives
    
    level_data = LEVELS[level_index]
    
    game_mode = CUBE
    player = CubePlayer(level_data["player_color"])
    ground = Ground(level_data["ground_color"])
    obstacles = []
    decorations = []
    bg_elements = [BackgroundElement(level_data["background_color"]) for _ in range(level_data["background_elements"])]
    obstacle_timer = pygame.time.get_ticks()
    score = 0
    game_speed = 1.0
    used_game_modes = {CUBE}
    lives = 3  # Reset lives

def generate_obstacle_pattern(level_index, x_start):
    level_data = LEVELS[level_index]
    pattern = random.choice(level_data["obstacle_patterns"])
    obstacle_color = random.choice(level_data["obstacle_colors"])
    decoration_color = random.choice(level_data["decoration_colors"])
    
    new_obstacles = []
    
    if pattern == "basic_spike_row":
        count = random.randint(1, 2)  # Fewer spikes (1-2 instead of 1-3)
        for i in range(count):
            new_obstacles.append(Spike(x_start + i*40, obstacle_color))  # More space between spikes (40 instead of 30)
    
    elif pattern == "basic_block":
        height = random.randint(30, 60)  # Lower blocks (30-60 instead of 40-80)
        new_obstacles.append(Obstacle(x_start, height, obstacle_color))
    
    elif pattern == "double_spike":
        new_obstacles.append(Spike(x_start, obstacle_color))
        # 50% chance to add ceiling spike to make it easier
        if random.random() > 0.5:
            new_obstacles.append(Spike(x_start, obstacle_color, upside_down=True))
    
    elif pattern == "platform_jump":
        platform_width = random.randint(80, 150)  # Smaller platforms
        platform_height = random.randint(30, 50)  # Lower platforms
        platform_y = HEIGHT - 50 - platform_height - random.randint(30, 60)  # Lower height
        
        new_obstacles.append(Platform(x_start, platform_y, platform_width, platform_height, level_data["ground_color"]))
        new_obstacles.append(Spike(x_start + platform_width + 70, obstacle_color))  # More space after platform (70 instead of 50)
    
    elif pattern == "ship_tunnel":
        if level_data["has_ship_mode"]:
            new_obstacles.append(Portal(x_start, SHIP, PURPLE))
            
            tunnel_length = random.randint(300, 500)
            gap_height = random.randint(150, 200)  # Wider gap (150-200 instead of 100-150)
            gap_y = random.randint(100, HEIGHT - 200 - gap_height)
            
            new_obstacles.append(Platform(x_start + 150, 0, tunnel_length, gap_y, level_data["ground_color"]))  # More space after portal
            new_obstacles.append(Platform(x_start + 150, gap_y + gap_height, tunnel_length, HEIGHT, level_data["ground_color"]))
            
            new_obstacles.append(Portal(x_start + tunnel_length + 200, CUBE, BLUE))  # More space after tunnel
    
    elif pattern == "ship_columns":
        if level_data["has_ship_mode"]:
            new_obstacles.append(Portal(x_start, SHIP, PURPLE))
            
            section_length = random.randint(400, 600)
            column_count = random.randint(2, 4)  # Fewer columns (2-4 instead of 3-6)
            spacing = section_length / column_count
            
            for i in range(column_count):
                column_x = x_start + 150 + i * spacing  # More space after portal
                gap_height = random.randint(120, 160)  # Wider gap
                gap_y = random.randint(100, HEIGHT - 200 - gap_height)
                
                new_obstacles.append(Obstacle(column_x, gap_y, obstacle_color))
                new_obstacles.append(Obstacle(column_x, HEIGHT - 50 - (gap_y + gap_height), obstacle_color))
            
            new_obstacles.append(Portal(x_start + section_length + 200, CUBE, BLUE))  # More space after section
    
    elif pattern == "ball_platforms":
        if level_data["has_ball_mode"]:
            new_obstacles.append(Portal(x_start, BALL, YELLOW))
            
            section_length = random.randint(400, 600)
            platform_count = random.randint(3, 5)  # Fewer platforms (3-5 instead of 4-7)
            spacing = section_length / platform_count
            
            for i in range(platform_count):
                platform_x = x_start + 150 + i * spacing  # More space after portal
                platform_width = random.randint(70, 120)  # Wider platforms
                
                if i % 2 == 0:
                    platform_y = HEIGHT - 50 - random.randint(30, 50)  # Lower platforms
                    platform_height = HEIGHT - platform_y
                    new_obstacles.append(Platform(platform_x, platform_y, platform_width, platform_height, level_data["ground_color"]))
                else:
                    platform_height = random.randint(30, 50)  # Lower platforms
                    new_obstacles.append(Platform(platform_x, 0, platform_width, platform_height, level_data["ground_color"]))
            
            new_obstacles.append(Portal(x_start + section_length + 200, CUBE, BLUE))  # More space after section
    
    elif pattern == "ufo_pillars":
        if level_data["has_ufo_mode"]:
            new_obstacles.append(Portal(x_start, UFO, CYAN))
            
            section_length = random.randint(400, 600)
            pillar_count = random.randint(3, 5)  # Fewer pillars (3-5 instead of 5-8)
            spacing = section_length / pillar_count
            
            for i in range(pillar_count):
                pillar_x = x_start + 150 + i * spacing  # More space after portal
                gap_height = random.randint(120, 160)  # Wider gap
                gap_y = random.randint(100, HEIGHT - 200 - gap_height)
                
                new_obstacles.append(Platform(pillar_x, 0, 30, gap_y, obstacle_color))
                new_obstacles.append(Platform(pillar_x, gap_y + gap_height, 30, HEIGHT - (gap_y + gap_height), obstacle_color))
            
            new_obstacles.append(Portal(x_start + section_length + 200, CUBE, BLUE))  # More space after section
    
    elif pattern == "wave_corridor":
        if level_data["has_wave_mode"]:
            new_obstacles.append(Portal(x_start, WAVE, NEON_PINK))
            
            section_length = random.randint(400, 600)
            corridor_width = random.randint(100, 140)  # Wider corridor (100-140 instead of 60-100)
            
            segments = random.randint(3, 6)  # Fewer segments (3-6 instead of 5-10)
            segment_length = section_length / segments
            
            for i in range(segments):
                segment_x = x_start + 150 + i * segment_length  # More space after portal
                
                if i % 2 == 0:
                    corridor_y = random.randint(100, HEIGHT - 250 - corridor_width)
                else:
                    corridor_y = random.randint(150, HEIGHT - 200 - corridor_width)
                
                new_obstacles.append(Platform(segment_x, 0, segment_length, corridor_y, obstacle_color))
                new_obstacles.append(Platform(segment_x, corridor_y + corridor_width, segment_length, HEIGHT - (corridor_y + corridor_width), obstacle_color))
            
            new_obstacles.append(Portal(x_start + section_length + 200, CUBE, BLUE))  # More space after section
    
    for _ in range(random.randint(3, 8)):
        decoration_x = x_start + random.randint(0, 300)
        decoration_y = random.randint(50, HEIGHT - 100)
        decoration_type = random.choice(["square", "triangle", "circle", "star"])
        decorations.append(Decoration(decoration_x, decoration_y, decoration_type, decoration_color))
    
    if level_data["has_speed_changes"] and random.random() < 0.2:  # Less frequent speed changes (0.2 instead of 0.3)
        speed_options = [0.7, 1.0, 1.3]  # Less extreme speed changes
        speed_multiplier = random.choice(speed_options)
        
        if speed_multiplier == 0.7:
            color = (0, 255, 0)
        elif speed_multiplier == 1.0:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        new_obstacles.append(SpeedPortal(x_start - 150, speed_multiplier, color))  # More space before speed portal
    
    return new_obstacles

def change_game_mode(new_mode, player_color):
    global player, game_mode, used_game_modes
    
    game_mode = new_mode
    used_game_modes.add(new_mode)
    
    if new_mode == CUBE:
        player = CubePlayer(player_color)
    elif new_mode == SHIP:
        player = ShipPlayer(player_color)
    elif new_mode == BALL:
        player = BallPlayer(player_color)
    elif new_mode == UFO:
        player = UfoPlayer(player_color)
    elif new_mode == WAVE:
        player = WavePlayer(player_color)
    
    player.make_invincible(60)  # Give invincibility after mode change

def check_challenges():
    for i in range(3):
        if score >= CHALLENGES[i]["requirement"] and not CHALLENGES[i]["completed"]:
            CHALLENGES[i]["completed"] = True
            save_game_data()
    
    if all(high_scores[i] >= 10 for i in range(len(LEVELS))) and not CHALLENGES[3]["completed"]:  # Easier requirement (10 instead of 15)
        CHALLENGES[3]["completed"] = True
        save_game_data()
    
    if score >= CHALLENGES[4]["requirement"] and (game_mode != CUBE or player.jump_count <= 20) and not CHALLENGES[4]["completed"]:
        CHALLENGES[4]["completed"] = True
        save_game_data()
    
    if len(used_game_modes) >= 5 and not CHALLENGES[5]["completed"]:
        CHALLENGES[5]["completed"] = True
        save_game_data()

load_game_data()

running = True
mouse_clicked = False
key_pressed = False

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                key_pressed = True
                if game_state == PLAYING:
                    player.jump()
                elif game_state == GAME_OVER:
                    game_state = LEVEL_SELECT
                elif game_state == PAUSE:
                    game_state = PLAYING
            
            if event.key == pygame.K_ESCAPE:
                if game_state == PLAYING:
                    game_state = PAUSE
                elif game_state == PAUSE:
                    game_state = PLAYING
                elif game_state in [LEVEL_SELECT, CHALLENGES]:
                    game_state = MAIN_MENU
                elif game_state == MAIN_MENU:
                    running = False
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                key_pressed = False
                if game_state == PLAYING and game_mode in [SHIP, WAVE]:
                    player.release()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_clicked = True
    
    if game_state == MAIN_MENU:
        for i, button in enumerate(main_menu_buttons):
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                if i == 0:
                    game_state = LEVEL_SELECT
                elif i == 1:
                    game_state = CHALLENGES
                elif i == 2:
                    running = False
    
    elif game_state == LEVEL_SELECT:
        for i, button in enumerate(level_buttons):
            button.locked = i > 0 and high_scores[i-1] < 10  # Easier to unlock levels
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, mouse_clicked):
                current_level = i
                init_level(current_level)
                game_state = PLAYING
        
        back_button.check_hover(mouse_pos)
        if back_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = MAIN_MENU
    
    elif game_state == CHALLENGES:
        for button in challenge_buttons:
            button.check_hover(mouse_pos)
        
        back_button.check_hover(mouse_pos)
        if back_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = MAIN_MENU
    
    elif game_state == PLAYING:
        level_data = LEVELS[current_level]
        current_scroll_speed = level_data["base_scroll_speed"] * game_speed
        
        player.update(current_scroll_speed)
        
        ground.update(current_scroll_speed)
        
        for bg in bg_elements:
            bg.update(current_scroll_speed)
        
        for decoration in decorations[:]:
            decoration.update(current_scroll_speed)
            if decoration.x + decoration.size < 0:
                decorations.remove(decoration)
        
        current_time = pygame.time.get_ticks()
        if current_time - obstacle_timer > level_data["obstacle_frequency"] / game_speed:
            new_obstacles = generate_obstacle_pattern(current_level, WIDTH)
            obstacles.extend(new_obstacles)
            obstacle_timer = current_time
            level_data["obstacle_frequency"] = max(1200, level_data["obstacle_frequency"] - 5)  # Slower difficulty increase
        
        for obstacle in obstacles[:]:
            obstacle.update(current_scroll_speed)
            
            if not obstacle.passed and player.x > obstacle.x + (obstacle.width if hasattr(obstacle, 'width') else 30):
                obstacle.passed = True
                
                if not isinstance(obstacle, Portal) and not isinstance(obstacle, SpeedPortal):
                    score += 1
                    if score > high_scores[current_level]:
                        high_scores[current_level] = score
                        save_game_data()
                    
                    check_challenges()
            
            if isinstance(obstacle, Portal) and not obstacle.passed and player.get_rect().colliderect(obstacle.get_rect()):
                obstacle.passed = True
                change_game_mode(obstacle.target_mode, level_data["player_color"])
            
            if isinstance(obstacle, SpeedPortal) and not obstacle.passed and player.get_rect().colliderect(obstacle.get_rect()):
                obstacle.passed = True
                game_speed = obstacle.speed_multiplier
            
            if obstacle.x + (obstacle.width if hasattr(obstacle, 'width') else 30) < 0:
                obstacles.remove(obstacle)
            
            # Check for collision with obstacles (except portals and speed portals)
            if not isinstance(obstacle, Portal) and not isinstance(obstacle, SpeedPortal) and not player.invincible and player.get_rect().colliderect(obstacle.get_rect()):
                lives -= 1
                if lives <= 0:
                    game_state = GAME_OVER
                else:
                    player.make_invincible(90)  # Give invincibility after hit
        
        if key_pressed and game_state == PLAYING:
            if game_mode in [SHIP, WAVE]:
                player.jump()
    
    elif game_state == PAUSE:
        resume_button = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60, "Resume")
        resume_button.check_hover(mouse_pos)
        if resume_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = PLAYING
        
        quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, "Quit to Menu")
        quit_button.check_hover(mouse_pos)
        if quit_button.is_clicked(mouse_pos, mouse_clicked):
            game_state = LEVEL_SELECT
    
    if game_state == MAIN_MENU:
        screen.fill((30, 30, 60))
        
        for bg in bg_elements:
            bg.update(1)
            bg.draw()
        
        title_text = title_font.render("GEOMETRY DASH", True, NEON_BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))
        
        subtitle_text = font.render("Enhanced Edition", True, NEON_PINK)
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 140))
        
        for button in main_menu_buttons:
            button.draw()
        
        version_text = small_font.render("v2.0 Ultimate Edition", True, WHITE)
        screen.blit(version_text, (WIDTH - version_text.get_width() - 10, HEIGHT - 30))
    
    elif game_state == LEVEL_SELECT:
        screen.fill((30, 30, 60))
        
        for bg in bg_elements:
            bg.update(1)
            bg.draw()
        
        title_text = title_font.render("SELECT LEVEL", True, NEON_ORANGE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        for button in level_buttons:
            button.draw()
        
        back_button.draw()
    
    elif game_state == CHALLENGES:
        screen.fill((30, 30, 60))
        
        title_text = title_font.render("CHALLENGES", True, NEON_GREEN)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        for button in challenge_buttons:
            button.draw()
        
        back_button.draw()
    
    elif game_state == PLAYING or game_state == PAUSE:
        level_data = LEVELS[current_level]
        
        screen.fill(level_data["background_color"])
        
        for bg in bg_elements:
            bg.draw()
        
        for decoration in decorations:
            decoration.draw()
        
        ground.draw()
        
        for obstacle in obstacles:
            obstacle.draw()
        
        player.draw()
        
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        high_score_text = font.render(f'High Score: {high_scores[current_level]}', True, WHITE)
        screen.blit(high_score_text, (10, 40))
        
        level_text = font.render(f'Level: {level_data["name"]}', True, WHITE)
        screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
        
        mode_names = ["CUBE", "SHIP", "BALL", "UFO", "WAVE"]
        mode_text = small_font.render(f'Mode: {mode_names[game_mode]}', True, WHITE)
        screen.blit(mode_text, (WIDTH - mode_text.get_width() - 10, 40))
        
        speed_text = small_font.render(f'Speed: {game_speed}x', True, WHITE)
        screen.blit(speed_text, (WIDTH - speed_text.get_width() - 10, 70))
        
        # Draw lives
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        screen.blit(lives_text, (10, 70))
        
        if game_state == PAUSE:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            pause_text = title_font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 120))
            
            resume_button = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 60, "Resume")
            resume_button.check_hover(mouse_pos)
            resume_button.draw()
            
            quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60, "Quit to Menu")
            quit_button.check_hover(mouse_pos)
            quit_button.draw()
    
    elif game_state == GAME_OVER:
        level_data = LEVELS[current_level]
        
        screen.fill(level_data["background_color"])
        for bg in bg_elements:
            bg.draw()
        for decoration in decorations:
            decoration.draw()
        ground.draw()
        for obstacle in obstacles:
            obstacle.draw()
        player.draw()
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        game_over_text = title_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        
        score_text = font.render(f'Final Score: {score}', True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 50))
        
        if score > high_scores[current_level]:
            high_score_text = font.render(f'New High Score!', True, NEON_GREEN)
        else:
            high_score_text = font.render(f'High Score: {high_scores[current_level]}', True, WHITE)
        screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2))
        
        restart_text = font.render('Press SPACE to return to level select', True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
        
        if any(not c["completed"] for c in CHALLENGES):
            challenge_text = small_font.render('Check the Challenges menu for new goals!', True, CYAN)
            screen.blit(challenge_text, (WIDTH//2 - challenge_text.get_width()//2, HEIGHT//2 + 100))
    
    pygame.display.flip()
    
    clock.tick(FPS)

pygame.quit()
sys.exit()