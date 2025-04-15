import pygame
from random import randint
from enum import Enum
from abc import ABC, abstractmethod


class Color(Enum):
    BLACK = ( 0, 0, 0)
    WHITE = ( 255, 255, 255)


class ColorPhase(Enum):
    RED = ( 255, 0, 0)
    YELLOW = ( 238, 210, 2)
    GREEN = ( 0, 128, 0)
    

class Car:
    def __init__(self, screen, position, color=Color.BLACK):
        self.radius = 5
        self.speed = 60
        self.screen = screen
        self.position: list[int,int] = position
        self.color = color.value
    
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
        
        if self.time_left == 2 or self.time_left == 1 :
            self.color_phase = ColorPhase.YELLOW
        
        elif self.time_left == 0:
            self.color_phase = ColorPhase.GREEN
            
        else: 
            self.color_phase = ColorPhase.RED
        
    def get_phase(self):
        return self.color_phase.name


class Road(ABC):
    def __init__(self, screen, start_x, start_y, lenght, width, lanes_amount=2, lane_width=6):
        self.screen = screen
        self.x = start_x
        self.y = start_y
        self.length = lenght
        self.width = width
        self.lanes_amount = lanes_amount
        self.lane_width = lane_width

    def create(self) -> None:
        pass
    
    def create_seperator(self) -> None:
        pass

   
class HorizontalRaod(Road):
    def __init__(self, screen, start_x, start_y, lenght, width, lanes_amount=2, lane_width=6):
        super().__init__(screen, start_x, start_y, lenght, width, lanes_amount, lane_width) 
        self.lane_middle = self.y + (self.width // 2) # Only works for 2 lanes!
    
    def create(self):
        # Road : Black lane
        pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x, self.y, self.length, self.lane_width))
        pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x, self.y+self.width, self.length, self.lane_width))
        
        # Innerroad : White space
        pygame.draw.rect(self.screen, Color.WHITE.value, pygame.Rect(self.x, self.y+self.lane_width, self.length, self.width-self.lane_width))

        # Road seperator : Black 
        self.create_seperator()
    
    def create_seperator(self) -> None:
        # Road separator (middle dashed line)
        separator_width = 10
        separator_height = 5
        separator_gap = 10

        # Middle y-position for the separator
        for i in range(self.x, self.x + self.length, separator_width + separator_gap):
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(i, self.lane_middle, separator_width, separator_height))
              

class Game():
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Traffic simulation")

        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 900
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.prev_time = pygame.time.get_ticks()
        self.active_game: bool = True
    
    def play(self) -> None:
        self.cars: Car = [Car(self.screen, [60,120]), Car(self.screen, [300,160])]
        self.traffic_light = TrafficLight(self.screen, 460, 100)
        
        self.h_road = HorizontalRaod(self.screen, 100, 400, 410, 80)
        self.game_loop()
    
    def update_time(self, prev_time) -> tuple[int, float]:
        current = pygame.time.get_ticks()
        delta = (current - prev_time) / 1000.0  # Consistent car movement regardless of frame rate
        return delta, current
    
    def game_loop(self) -> None:
        while self.active_game:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.active_game = False
                    pygame.quit()

            # Background color
            self.screen.fill(ColorPhase.GREEN.value)

            self.delta_time, self.prev_time = self.update_time(self.prev_time)    
            
            self.h_road.create() # create road
            self.traffic_light.draw() # create traffic light
            
            for car in self.cars: # create all cars
                car.draw()
                car.move(self.delta_time)
            
            # Refresh window
            pygame.display.flip()



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



if __name__ == "__main__":
    Game().play()