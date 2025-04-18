from __future__ import annotations # To type hint car in the car class
import pygame
import uuid
from constants import Color, ColorPhase, RoadDirections, RoadType
from map import Road, HorizontalRaod, VerticalRoad, TrafficLight, Intersection, LANE_WIDTH

class Car:
    def __init__(self, screen, x, y, direction):
        self.screen = screen
        
        self.id = uuid.uuid4().hex[:6] # 6 chars for the id 
        self.safety_distance = 40
        self.speed = 60
        self.driving = False
        self.direction = direction
        self.img = pygame.image.load('version_one/images/Car.png')
        self.rotate = False

        self.x = x
        self.y = y
      
    def draw(self) -> None:
        self.screen.blit(self.img,(self.x, self.y))
    
    def move(self, delta_time: int, traffic_light: TrafficLight, all_cars: list[Car], all_roads: list[Road]) -> None:
        if self.should_move(traffic_light, all_cars):
            self.apply_move(delta_time)
            self.driving = True
            
        else:
            self.driving = False
            
    def should_move(self, traffic_light: TrafficLight, all_cars: list[Car]) -> bool:
        phase = traffic_light.get_phase()
        traffic_light_x= traffic_light.get_location[0]
        
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
        
        
        # TODO: CHANGE with coordinates !!!! 
        # TODO: self.rotate has to be done different.        
        
        if 569 <= self.x <= 573:            
            self.y -= self.speed * delta_time
            if not self.rotate:
                #self.img = pygame.transform.rotate(self.img, 30)
                #self.img = pygame.transform.rotate(self.img, 60)
                self.img = pygame.transform.rotate(self.img, 90)
                self.rotate = True

            
        else:
            self.x += self.speed * delta_time
         
        # TODO: check which road he drives and then how he should drive
       
    # TODO: check if we need it
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)
   
    def is_off_screen(self) -> bool:
        return self.x > self.screen.get_width() or self.y > self.screen.get_height() or self.x < -10 or self.y < -10

    def get_cars_in_front(self, all_cars: list[Car]) -> list[Car]:
        all_cars_ids = [car.id for car in all_cars]
        
        index = all_cars_ids.index(self.id)
        cars_in_front_of_me = all_cars[index+1:]

        return cars_in_front_of_me
    
    def car_in_front_moving(self, car_in_front: list[Car]) -> bool:
        car = car_in_front[0]
        too_close = abs(car.x - self.x) < self.safety_distance
        return car.driving_status or not too_close
       
    @property
    def driving_status(self) -> bool:
        return self.driving
              
        
class Game():
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Traffic simulation")

        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 900
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.prev_time = pygame.time.get_ticks()
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
        
        self.west_traffic_light = TrafficLight(self.screen, end_street_x-30, road_y+90)
        
        self.create_road(road_x, road_y, road_length, road_width, road_directions, RoadType.HORIZONTAL)
        self.create_road(end_street_x+intersec_side_lengths-LANE_WIDTH, road_y, road_length, road_width, road_directions, RoadType.HORIZONTAL)
        self.create_road(end_street_x-LANE_WIDTH, road_y+intersec_side_lengths-LANE_WIDTH, road_length, road_width, road_directions, RoadType.VERTICAL)
        self.create_road(end_street_x-LANE_WIDTH, road_y-road_length, road_length, road_width, road_directions, RoadType.VERTICAL)
        self.create_road(end_street_x, end_y, intersec_side_lengths, intersec_side_lengths, road_directions, RoadType.INTERSECTION)

    def spawn_road(self, road: Road) -> None:
        self.roads.append(road)
    
    def create_road(self, x:float, y:float, width:float, height:float, road_directions: list[RoadDirections], type: RoadType=RoadType.HORIZONTAL):
        match (type):
            case (RoadType.HORIZONTAL):
                hr = HorizontalRaod(self.screen, x, y, width, height, road_directions)
                self.spawn_road(hr)
                return hr 

            case (RoadType.VERTICAL):
                vr = VerticalRoad(self.screen, x, y, width, height, road_directions)
                self.spawn_road(vr)
                return vr 

            case (RoadType.INTERSECTION):
                # A intersection should have the same number for width and height
                if width != height:
                    print(f"Error: The intersection has not got the same width: {width} and height: {height}.")
                
                it = Intersection(self.screen, x, y, width, road_directions)
                self.spawn_road(it)
                return it 
                    
    def spawn_car(self, x: int = 300, y: int = 405) -> None:
        if len(self.cars) < 4:
            self.cars.append(Car(self.screen, x, y, RoadDirections.EAST))       
            self.cars.sort(key=lambda car: car.x) # sort the cars after x value

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
 
        for car in self.cars:
            car.move(self.delta_time, self.west_traffic_light, self.cars ,self.roads)

    def draw(self) -> None:
        self.screen.fill(Color.GRAY.value)

        self.west_traffic_light.draw()
        
        [road.draw() for road in self.roads]
        
        [car.draw() for car in self.cars]        
        
        #self.remaining_time_text()
        pygame.display.flip()
        
    def game_loop(self) -> None:
        while True:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().play()
