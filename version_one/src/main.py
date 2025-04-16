from __future__ import annotations # To type hint car in the car class
import pygame
from random import randint
from enum import Enum
from abc import ABC
import uuid


class Color(Enum):
    BLACK = ( 0, 0, 0)
    WHITE = ( 255, 255, 255)
    GRAY = ( 128, 128, 128)


class ColorPhase(Enum):
    RED = ( 255, 0, 0)
    YELLOW = ( 238, 210, 2)
    GREEN = ( 0, 128, 0)


class RoadDirections(Enum):
    NORTH = "up"
    EAST = "right"
    SOUTH = "down"
    WEST = "left"


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
        self.green_red_phase = randint (5,9)
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

    
class Car:
    def __init__(self, screen, x, y, color=Color.BLACK):
        self.screen = screen
        
        self.id = uuid.uuid4().hex[:6] # 6 chars for the id 
        self.radius = 4.5
        self.safety_distance = self.radius * 5
        self.speed = 60
        self.driving = False
        self.color = color.value
        
        self.x = x
        self.y = y
      
    def draw(self) -> None:
        pygame.draw.circle(self.screen, self.color, [self.x, self.y], self.radius)
    
    def move(self, delta_time: int, traffic_light: TrafficLight, all_cars: list[Car]) -> None:
        if self.should_move(traffic_light, all_cars):
            self.apply_move(delta_time)
            self.driving = True
            
        else:
            self.driving = False
            
    def should_move(self, traffic_light: TrafficLight, all_cars: list[Car]) -> bool:
        phase = traffic_light.get_phase()
        traffic_light_x= traffic_light.get_location()[0]
        
        car_front = self.x + self.safety_distance
        wait_phases = [ColorPhase.RED.name, ColorPhase.YELLOW.name]

        cars_in_front = self.get_cars_in_front(all_cars)
        
        if cars_in_front: 
            if not self.car_in_front_moving(cars_in_front):
                return False
            
        # Car is near the traffic light & must wait as it is yellow or red
        if traffic_light_x - car_front <= 10 and traffic_light_x - car_front >= 1 and phase in wait_phases:    
            return False

        return True
    
    def apply_move(self, delta_time: int) -> None:
        self.driving = True
        self.x += self.speed * delta_time

    def position(self) -> tuple[int, int]:
        return (self.x, self.y)
   
    def is_off_screen(self) -> bool:
        return self.x > self.screen.get_width() or self.y > self.screen.get_height()
   
    def get_driving_status(self) -> bool:
        return self.driving
        
    def get_cars_in_front(self, all_cars: list[Car]) -> list[Car]:
        all_cars_ids = [car.id for car in all_cars]
        
        index = all_cars_ids.index(self.id)
        cars_in_front_of_me = all_cars[index+1:]

        return cars_in_front_of_me

        # TODO: detect if a car is infront of me or am i the first car ?
        # safty distance to the next car in front of me 
    
    def car_in_front_moving(self, car_in_front: list[Car]) -> bool:
        car = car_in_front[0]
        too_close = abs(car.x - self.x) < self.safety_distance
        return car.get_driving_status() or not too_close
        

class Road(ABC):
    def __init__(self, screen, start_x, start_y, lenght, width, directions: list[RoadDirections], lanes_amount=2, lane_width=6):
        self.screen = screen
        self.x: float = start_x
        self.y: float = start_y
        self.length: int = lenght
        self.width: int = width
        self.lanes_amount: int = lanes_amount
        self.lane_width: int = lane_width
        self.directions: list[RoadDirections] = directions

    def draw(self) -> None:
        pass
    
    def create_seperator(self) -> None:
        pass

    def get_directions(self) -> list[RoadDirections]:
        return self.directions
  
 
class HorizontalRaod(Road):
    def __init__(self, screen, start_x, start_y, lenght, width, directions, lanes_amount=2, lane_width=5):
        super().__init__(screen, start_x, start_y, lenght, width, directions, lanes_amount, lane_width) 
        self.lane_middle = self.y + (self.width // 2) # Only works for 2 lanes!
    
    def get_directions(self) -> list[RoadDirections]:
        return super().get_directions()
    
    def draw(self) -> None:
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


class VerticalRoad(Road):
    def __init__(self, screen, start_x, start_y, lenght, width, directions, lanes_amount=2, lane_width=5):
        super().__init__(screen, start_x, start_y, lenght, width, directions, lanes_amount, lane_width)
        self.lane_middle = self.x + (self.width // 2) # Only works for 2 lanes!
        
    def get_directions(self) -> list[RoadDirections]:
        return super().get_directions()          

    def draw(self) -> None:
        # Road : Black lane
        pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x, self.y+self.lane_width, self.lane_width, self.length))
        pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x+self.width, self.y+self.lane_width, self.lane_width, self.length))
        
        # Innerroad : White space
        pygame.draw.rect(self.screen, Color.WHITE.value, pygame.Rect(self.x+self.lane_width, self.y+self.lane_width, self.width-self.lane_width, self.length))

        # Road seperator : Black 
        self.create_seperator()        

    def create_seperator(self) -> None:
        # Road separator (middle dashed line)
        separator_width = 10
        separator_height = 5
        separator_gap = 10

        # Middle y-position for the separator
        for i in range(self.y+self.lane_width, self.y + self.length, separator_width + separator_gap):
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.lane_middle, i,  separator_height, separator_width))
        
    
class Intersection():
    def __init__(self, screen, start_x, start_y, side_length, directions):
        self.screen = screen
        self.x: int = start_x
        self.y: int = start_y
        self.side_length: int = side_length
        self.directions: list[RoadDirections] = directions
        self.lane_width = 5
    
    def draw(self):
        pygame.draw.rect(self.screen, Color.WHITE.value, pygame.Rect(self.x, self.y, self.side_length-self.lane_width, self.side_length-self.lane_width))
        self.create_boundries()
        
    def create_boundries(self):
        ## for all the road directions that are in the self.directions there should a pixel be added in the corner
        if RoadDirections.EAST not in self.directions:
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x+self.side_length-self.lane_width, self.y,self.lane_width, self.side_length-self.lane_width))
        
        if RoadDirections.WEST not in self.directions:
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x, self.y,self.lane_width, self.side_length-self.lane_width))

        if RoadDirections.NORTH not in self.directions:
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x, self.y-self.lane_width, self.side_length-self.lane_width, self.lane_width))

        if RoadDirections.SOUTH not in self.directions:
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.x, self.y-self.lane_width + self.side_length, self.side_length-self.lane_width, self.lane_width))
        
        
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
        self.car_spawn_rate: int = 2 # every ... seconds a car should spawn
        self.last_car_spawn_time: int = pygame.time.get_ticks() - self.car_spawn_rate * 1000.

    def play(self) -> None:
        self.generate_map()
        self.game_loop()
    
    def generate_map(self) -> None:
        road_x = 100
        road_y = 350
        road_length = 420
        road_width = 80
        
        end_street_x = road_x + road_length
        end_y = road_y + 5 
        
        intersec_side_lengths = road_width # to compensate the seperators
        
        first_road_directions = [RoadDirections.WEST, RoadDirections.SOUTH]
        
        self.first_road = HorizontalRaod(self.screen, road_x, road_y, road_length, road_width, first_road_directions)
        self.intersection = Intersection(self.screen, end_street_x, end_y, intersec_side_lengths, first_road_directions)
        
        self.traffic_light = TrafficLight(self.screen, end_street_x-10, road_y-10)       

        
        self.second_road = VerticalRoad(self.screen, end_street_x-5, road_y+intersec_side_lengths-5, road_length, road_width, first_road_directions)              
        
    def spawn_car(self, x: int = 120, y: int = 220) -> None:
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
       
        self.cars = [car for car in self.cars if not car.is_off_screen()] # delete cras, which are not in the screen
        self.cars.sort(key=lambda car: car.x) # sort the cars after x value
 
        for car in self.cars:
            car.move(self.delta_time, self.traffic_light, self.cars)

    def draw(self) -> None:
        self.screen.fill(Color.GRAY.value)
        self.first_road.draw()
        self.second_road.draw()
        self.traffic_light.draw()
        self.intersection.draw()
        
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


if __name__ == "__main__":
    Game().play()
