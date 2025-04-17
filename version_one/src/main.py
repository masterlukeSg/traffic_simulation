from __future__ import annotations # To type hint car in the car class
import pygame
import uuid
from constants import Color, ColorPhase, RoadDirections
from map import Road, HorizontalRaod, VerticalRoad, TrafficLight, Intersection, LANE_WIDTH


class Car:
    def __init__(self, screen, x, y, direction, color=Color.BLACK):
        self.screen = screen
        
        self.id = uuid.uuid4().hex[:6] # 6 chars for the id 
        self.radius = 4.5
        self.safety_distance = self.radius * 5
        self.speed = 60
        self.driving = False
        self.direction = direction
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
    
    def apply_move(self, delta_time: int, next_direction: RoadDirections=RoadDirections.EAST) -> None:
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
    
    def car_in_front_moving(self, car_in_front: list[Car]) -> bool:
        car = car_in_front[0]
        too_close = abs(car.x - self.x) < self.safety_distance
        return car.get_driving_status() or not too_close
            
        
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
        self.roads: list[Road] = [] # TODO: Implement the list and add all roads to it. Give it to the car ojects
        self.car_spawn_cooldown: int = 2
        self.last_car_spawn_time: int = pygame.time.get_ticks() - self.car_spawn_cooldown * 1000.

    def play(self) -> None:
        self.generate_map()
        self.game_loop()
    
    def generate_map(self) -> None:
        # starting road is the west_road
        road_x = 300 
        road_y = 350
        road_length = 220
        road_width = 80
        
        end_street_x = road_x + road_length
        end_y = road_y + LANE_WIDTH 
        
        intersec_side_lengths = road_width # to compensate the seperators
        
        road_directions = [RoadDirections.WEST, RoadDirections.SOUTH, RoadDirections.NORTH, RoadDirections.EAST]
        
        
        self.west_road = HorizontalRaod(self.screen, road_x, road_y, road_length, road_width, road_directions)
        self.west_traffic_light = TrafficLight(self.screen, end_street_x-15, road_y-10)
        
        self.east_road = HorizontalRaod(self.screen, end_street_x+intersec_side_lengths-LANE_WIDTH, road_y, road_length, road_width, road_directions)
        
        self.south_road = VerticalRoad(self.screen, end_street_x-LANE_WIDTH, road_y+intersec_side_lengths-LANE_WIDTH, road_length, road_width, road_directions)              
        
        self.north_road = VerticalRoad(self.screen, end_street_x-LANE_WIDTH, road_y-road_length, road_length, road_width, road_directions)
        
        self.intersection = Intersection(self.screen, end_street_x, end_y, intersec_side_lengths, road_directions)
    
    def spawn_car(self, x: int = 300, y: int = 370) -> None:
        if len(self.cars) < 4:
            self.cars.append(Car(self.screen, x, y, RoadDirections.EAST))

    def create_cars(self) -> None:
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_car_spawn_time) >= self.car_spawn_cooldown * 1000:
            self.spawn_car()
            self.last_car_spawn_time = current_time
                  
    def update_time(self, prev_time) -> tuple[int, float]:
        current = pygame.time.get_ticks()
        delta = (current - prev_time) / 1000.0  # Consistent car movement regardless of frame rate
        return delta, current
    
    def remaining_time_text(self) -> None:
        time_left = str(self.west_traffic_light.remaining_time())
        next_pahse = self.west_traffic_light.get_next_phase().title()
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
            car.move(self.delta_time, self.west_traffic_light, self.cars)

    def draw(self) -> None:
        self.screen.fill(Color.GRAY.value)
        self.west_road.draw()
        self.west_traffic_light.draw()
        self.east_road.draw()
        self.south_road.draw()
        self.north_road.draw()
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
