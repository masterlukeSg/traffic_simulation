import pygame
from random import randint
from enum import Enum
from abc import ABC


class Color(Enum):
    BLACK = ( 0, 0, 0)
    WHITE = ( 255, 255, 255)
    GRAY = ( 128, 128, 128)


class ColorPhase(Enum):
    RED = ( 255, 0, 0)
    YELLOW = ( 238, 210, 2)
    GREEN = ( 0, 128, 0)
    

class Car:
    def __init__(self, screen, x, y, color=Color.BLACK):
        self.radius = 4.5
        self.speed = 60
        self.screen = screen
        self.color = color.value
        self.x = x
        self.y = y
        
    def draw(self) -> None:
        pygame.draw.circle(self.screen, self.color, [self.x, self.y], self.radius)
    
    def move(self, delta_time) -> None:
        self.x += self.speed * delta_time     
    
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)
   
    def is_off_screen(self) -> bool:
        return self.x > self.screen.get_width() or self.y > self.screen.get_height()
   

class TrafficLight:
    def __init__(self, screen, x, y, color=ColorPhase.RED):
        self.screen = screen
        self.width = 10
        self.heihgt = 10
        self.x = x
        self.y = y
        self.color_phase = color
        self.starting_color_phase = color

        # how long a phase should take (in seconds)
        self.green_red_phase = 8
        self.yellow_phase = 2
              
        self.countdown_start: int = self.green_red_phase
        self.start_ticks = pygame.time.get_ticks()
        self.time_left = self.countdown_start
            
    def draw(self) -> None:
        self.update_phase()
        pygame.draw.rect(self.screen, self.color_phase.value, pygame.Rect(self.x, self.y, self.width, self.heihgt))
    
    def update_phase(self) -> None:
        # Calculate how many full seconds have passed since the traffic light was created
        self.seconds_passed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        # Calculate how much time is left before the countdown ends (traffic light turns red or green)
        self.time_left = max(0, self.countdown_start - self.seconds_passed)
        
        # when 2 and 1 seconds are left: Yellow 
        if self.time_left <= self.yellow_phase and self.time_left != 0:
            if self.starting_color_phase == ColorPhase.RED:
                self.color_phase = ColorPhase.YELLOW
                
            elif self.starting_color_phase == ColorPhase.GREEN:
                self.color_phase = ColorPhase.YELLOW

        # when 0 seconds are letf, change the starting_color to red or green
        elif self.time_left == 0:
            if self.starting_color_phase == ColorPhase.RED:
                self.color_phase = ColorPhase.GREEN
                self.starting_color_phase = ColorPhase.GREEN
                
            elif self.starting_color_phase == ColorPhase.GREEN:
                self.color_phase = ColorPhase.RED
                self.starting_color_phase = ColorPhase.RED
            
            # restart the countdown for the timer
            self.countdown_start: int = self.green_red_phase
            self.start_ticks = pygame.time.get_ticks()
            
    def get_phase(self) -> str:
        return self.color_phase.name

    def get_starting_phase(self) -> str:
        return self.starting_color_phase.name

    def get_next_phase(self) -> str:  
        red = ColorPhase.RED.name
        yellow = ColorPhase.YELLOW.name
        green = ColorPhase.GREEN.name
        
        phase = self.get_phase()
        start = self.get_starting_phase() 
        
        transition = {
            red : {red: yellow , yellow: green},
            green : {green: yellow, yellow: red},
        }
        
        # first dict and then go into second dict
        return transition.get(start, {}).get(phase, {})
    
    def remaining_time(self) -> int:
        red = ColorPhase.RED.name
        green = ColorPhase.GREEN.name
        
        phase = self.get_phase()

        if phase == red or phase == green:
            return int(self.time_left - self.yellow_phase)
        else:        
            return int(self.time_left)
    
    def get_location(self) -> tuple[int, int]:
        return (self.x, self.y) 
    

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
        self.my_font = pygame.font.SysFont('Freeroad', 20)

        self.cars: list[Car] = []
        self.car_spawn_rate: int = 4 # every ... seconds a car should spawn
        self.last_car_spawn_time: int = pygame.time.get_ticks() - self.car_spawn_rate * 1000.

    def play(self) -> None:
        self.traffic_light = TrafficLight(self.screen, 500, 390)
        self.h_road = HorizontalRaod(self.screen, 100, 400, 410, 80)
        
        self.game_loop()
    
    def spawn_car(self, x: int = 120, y: int = 420) -> None:
        self.cars.append(Car(self.screen, x, y))

    def create_cars(self) -> None:
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_car_spawn_time) >= self.car_spawn_rate * 1000:
            self.spawn_car()
            self.last_car_spawn_time = current_time
                  
    def update_time(self, prev_time) -> tuple[int, float]:
        current = pygame.time.get_ticks()
        delta = (current - prev_time) / 1000.0  # Consistent car movement regardless of frame rate
        return delta, current
    
    def remaining_time_text(self) -> None:
        # Text
        time_left = str(self.traffic_light.remaining_time())
        next_pahse = self.traffic_light.get_next_phase().title()
        combined = f'In {time_left} seconds the traffic light will change to {next_pahse}'
        self.text1 = self.my_font.render(combined, True, Color.BLACK.value)
        self.screen.blit(self.text1,(10, 10))
    
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def update(self) -> None:
        self.delta_time, self.prev_time = self.update_time(self.prev_time)
        self.create_cars()
        self.cars = [car for car in self.cars if not car.is_off_screen()]
        print(len(self.cars))

        
        for car in self.cars:
            car.move(self.delta_time)

    def draw(self) -> None:
        self.screen.fill(Color.GRAY.value)
        self.h_road.create()
        self.traffic_light.draw()
        
        for car in self.cars:
            car.draw()
        
        self.remaining_time_text()
        pygame.display.flip()
        
    def game_loop(self) -> None:
        while True:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()




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
