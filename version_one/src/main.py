from __future__ import annotations # To type hint car in the car class
import pygame
import uuid
from constants import Color, ColorPhase, RoadDirections, RoadType
from map import Road, HorizontalRaod, VerticalRoad, TrafficLight, Intersection, LANE_WIDTH
from verhicles import Car


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
        # starting road is coming from the west
        road_x = 300 
        road_y = 350
        road_length = 220
        road_width = 80
        
        end_street_x = road_x + road_length
        end_y = road_y + LANE_WIDTH 
        
        intersec_side_lengths = road_width # to compensate the seperators
        
        road_directions_hor = [RoadDirections.WEST, RoadDirections.SOUTH]
        road_directions_ver = [RoadDirections.NORTH, RoadDirections.EAST]
        
        self.west_traffic_light = TrafficLight(self.screen, end_street_x-30, road_y+90)
        
        #TODO: update the road_directions 
        # For intersect maybe disable it as we can call it with sync_intersects_with_roads() -> will have to implement the code
        
        # TODO: The traffic ligth should be given to the road (delete from the car)
        # then check which for which direction the traffig light is needed 
        # the safety_distance for the car is then not the traffic light, but the end of the road (must be changed in the car class)
        
        self.create_road(road_x, road_y, road_length, road_width, road_directions_hor, RoadType.HORIZONTAL)
        self.create_road(end_street_x+intersec_side_lengths-LANE_WIDTH, road_y, road_length, road_width, road_directions_hor, RoadType.HORIZONTAL)
        self.create_road(end_street_x-LANE_WIDTH, road_y+intersec_side_lengths-LANE_WIDTH, road_length, road_width, road_directions_ver, RoadType.VERTICAL)
        self.create_road(end_street_x-LANE_WIDTH, road_y-road_length, road_length, road_width, road_directions_ver, RoadType.VERTICAL)
        self.create_road(end_street_x, end_y, intersec_side_lengths, intersec_side_lengths, road_directions_hor + road_directions_ver, RoadType.INTERSECTION)
        
        self.sync_intersects_with_roads()
        
     
    def sync_intersects_with_roads(self) -> None:
        # intersections will know which roads are connected with them
        for road in self.roads:
            road.find_connected_roads(self.roads)
           
    def spawn_road(self, road: Road) -> None:
        self.roads.append(road)
    
    def create_road(self, x:float, y:float, width:float, height:float, road_directions: list[RoadDirections], type: RoadType=RoadType.HORIZONTAL):
        match (type):
            case (RoadType.HORIZONTAL):
                hr = HorizontalRaod(self.screen,RoadType.HORIZONTAL, x, y, width, height, road_directions)
                self.spawn_road(hr)
                return hr 

            case (RoadType.VERTICAL):
                vr = VerticalRoad(self.screen, RoadType.VERTICAL, x, y, width, height, road_directions)
                self.spawn_road(vr)
                return vr 

            case (RoadType.INTERSECTION):
                # A intersection should have the same number for width and height
                if width != height:
                    print(f"Error: The intersection has not got the same width: {width} and height: {height}.")
                
                it = Intersection(self.screen, RoadType.INTERSECTION, x, y, width, road_directions)
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
        
        pygame.display.flip()
        
    def game_loop(self) -> None:
        while True:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().play()
