import pygame
from random import randint
from enum import Enum


BLACK = ( 0, 0, 0)
WHITE = ( 255, 255, 255)

class ColorPhase(Enum):
    RED = ( 255, 0, 0)
    YELLOW = ( 238, 210, 2)
    GREEN = ( 0, 128, 0)
    

class Car:
    def __init__(self, screen, position, color=BLACK):
        self.radius = 5
        self.speed = 60
        self.screen = screen
        self.position: list[int,int] = position
        self.color = color
    
    def draw(self):
        pygame.draw.circle(self.screen, self.color, self.position, self.radius)
    
    def move(self, delta_time):
        self.position[0] += self.speed * delta_time     
    
    def position(self) -> list[int]:
        return self.position
   
   
class TrafficLight:
    def __init__(self, screen, x, y, color=ColorPhase.RED):
        self.screen = screen
        self.width = 10
        self.heihgt = 10
        self.x = x
        self.y = y
        self.color_phase = color
        
        self.countdown_start: int = randint(0,10)
        self.start_ticks = pygame.time.get_ticks()
        
    def draw(self):
        self.update_phase()
        pygame.draw.rect(self.screen, self.color_phase.value, pygame.Rect(self.x, self.y, self.width, self.heihgt))
    
    def update_phase(self):
        # Calculate how many full seconds have passed since the game started
        self.seconds_passed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        # Calculate how much time is left before the countdown ends (traffic light turns green)
        self.time_left = max(0, self.countdown_start - self.seconds_passed)
        
        if self.time_left == 2:
            self.color_phase = ColorPhase.YELLOW
        
        elif self.time_left == 0:
            self.color_phase = ColorPhase.GREEN
            
        else: 
            self.color_phase = ColorPhase.RED
        
    def get_phase(self):
        return self.color_phase.name
        

def draw_road(screen) -> None:
    road_width = 80
    
    # horizontal road
    hor_start_y = 100
    hor_end_y = hor_start_y + road_width
    hor_x = 50
    
    # vertical road
    ver_start_x = 640
    ver_end_x = ver_start_x + road_width
    
    road_height = 10
    street_width = 600
    
    # (x, y, width, height)
    # Road : horizontal 
    pygame.draw.rect(screen, BLACK, pygame.Rect(hor_x, hor_start_y, street_width, road_height))
    pygame.draw.rect(screen, BLACK, pygame.Rect(hor_x, hor_end_y, street_width, road_height))

    # Innerroad : horizontal
    pygame.draw.rect(screen, WHITE, pygame.Rect(hor_x, hor_start_y + road_height, street_width, 70))

    # Road separator : horizontal
    for i in range(hor_x, street_width+50, 20):
        pygame.draw.rect(screen, BLACK, pygame.Rect(i, round((hor_start_y+hor_end_y)/2), 10, 5))      
    
    ## TODO: Complete the vertical street
    
    # Road : Vertical 
    pygame.draw.rect(screen, BLACK, pygame.Rect(ver_start_x, hor_end_y, road_height, street_width))
    pygame.draw.rect(screen, BLACK, pygame.Rect(ver_end_x, hor_end_y, road_height, street_width))
    
    # Innerroad : Vertical
    pygame.draw.rect(screen, WHITE, pygame.Rect(ver_start_x + road_height, hor_end_y, 70, street_width))
     
def moving_logic(time_left, traffic_light) -> None:
    if time_left > 0:
        pygame.draw.rect(screen, RED, traffic_light)
    
        to_move = []
        car_pos = get_car_position()

        for index in range(len(car_pos)):
            # If car is 10 pixel infront of the traffic light, stop the car
            if car_pos[index] <= traffic_light.x - 10:
                to_move.append(index)
        
        move_car(to_move)
        
    elif time_left == 0:
        pygame.draw.rect(screen, GREEN, traffic_light)
        move_car(list(range(0, len(car_positions))))

def update_time(prev_time) -> tuple[int, float]:
    current = pygame.time.get_ticks()
    delta = (current - prev_time) / 1000.0  # Consistent car movement regardless of frame rate
    return delta, current
    



pygame.init()
pygame.display.set_caption("Traffic simulation")

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1200

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

prev_time = pygame.time.get_ticks()

active_game: bool = True



cars: Car = [Car(screen, [60,120]), Car(screen, [300,160])]
traffic_light = TrafficLight(screen, 460, 100)


while active_game:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active_game = False
            pygame.quit()

    # Background color
    screen.fill(ColorPhase.GREEN.value)

    delta_time, prev_time = update_time(prev_time)    
    
    draw_road(screen)
    traffic_light.draw()
    
    for car in cars:
        car.draw()
        car.move(delta_time)
    
    # Refresh window
    pygame.display.flip()
