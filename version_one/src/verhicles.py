from __future__ import annotations # To type hint car in the car class
import pygame
from constants import  ColorPhase, RoadDirections, RoadType
from map import Road, TrafficLight
import logging
from random import randint

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    datefmt='%H:%M:%S'
)

class Car:
    _id_counter = 0
    
    def __init__(self, screen, x, y, direction: RoadDirections):
        Car._id_counter += 1
        self.id = f"car_{Car._id_counter}"
        
        self.screen = screen
        self.safety_distance = 40
        self.speed = 60
        self.img = pygame.image.load('version_one/images/Car.png')
        self.rotation = False
        
        self.driving = False
        self._driving_direction = direction
        self.next_direction: RoadDirections = None
        self.all_roads: list[Road] = None
        self.road_driving_on: Road = None
        self.prev_road_driving_on = self.road_driving_on

        self.x = x
        self.y = y
      
    def draw(self) -> None:
        self.screen.blit(self.img,(self.x, self.y))
    
    def move(self, delta_time: int, traffic_light: TrafficLight, all_cars: list[Car], all_roads: list[Road]) -> None:
        self.all_roads = all_roads
        
        if self.should_move(traffic_light, all_cars):
            new_direction = self.get_next_direction()
            
            if new_direction is not None:
                self.next_direction = new_direction
            
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
        if not self.road_driving_on:
            return

        if self.at_intersection():
            self.handle_turning(delta_time)
        else:
            self.rotation = False
            self.drive_straight(delta_time)    

    def at_intersection(self) -> bool:
        next_intersection = self.get_next_intersection()
        if next_intersection and next_intersection.on_road(self.x, self.y):
            return True
        return False

    def handle_turning(self, delta_time: int) -> None:
        next_intersection = self.get_next_intersection()
        if not next_intersection:
            self.drive_straight(delta_time)
            return

        directions = {
            RoadDirections.EAST: {
                RoadDirections.NORTH: next_intersection.lower_right_middle,
                RoadDirections.SOUTH: next_intersection.lower_left_middle,
            },
            RoadDirections.WEST: {
                RoadDirections.NORTH: next_intersection.upper_right_middle,
                RoadDirections.SOUTH: next_intersection.upper_left_middle,
            },
            RoadDirections.NORTH: {
                RoadDirections.EAST: next_intersection.lower_right_middle,
                RoadDirections.WEST: next_intersection.upper_right_middle,
            },
            RoadDirections.SOUTH: {
                RoadDirections.EAST: next_intersection.lower_left_middle,
                RoadDirections.WEST: next_intersection.upper_left_middle,
            },
        }

        # Find turn coordinates
        turn_coords = directions.get(self._driving_direction, {}).get(self.next_direction)

        if turn_coords and self._is_at_coordinates(turn_coords):
            self._driving_direction = self.next_direction
            self.rotate_car(self.next_direction)
            self.next_direction = None
           

        self.drive_straight(delta_time)

    def rotate_car(self, direction: RoadDirections):
        if self.rotation:
            return None
        match (direction.value):
            case (RoadDirections.NORTH.value):
                self.img = pygame.transform.rotate(self.img, 90)
                self.rotation = True
            
            case (RoadDirections.SOUTH.value):
                self.img = pygame.transform.rotate(self.img, -90)
                self.rotation = True
            
            case (RoadDirections.WEST.value):
                self.img = pygame.transform.rotate(self.img, 90)
                self.rotation = True
        
            case (RoadDirections.EAST.value):
                self.img = pygame.transform.rotate(self.img, -90)
                self.rotation = True
        
    def drive_straight(self, delta_time: int) -> None:
        match self._driving_direction:
            case RoadDirections.NORTH:
                self.y -= self.speed * delta_time
            case RoadDirections.SOUTH:
                self.y += self.speed * delta_time
            case RoadDirections.WEST:
                self.x -= self.speed * delta_time
            case RoadDirections.EAST:
                self.x += self.speed * delta_time

    def _is_at_coordinates(self, coords: tuple[int, int], tolerance: int = 3) -> bool:
        return (coords[0] - tolerance <= self.x <= coords[0] + tolerance and
                coords[1] - tolerance <= self.y <= coords[1] + tolerance)
    
    def get_next_direction(self) -> RoadDirections | None:
        # The road i am driving on is a road which was already detected
        if not self.set_road_driving_on():
            return None
        
        next_intersection = self.get_next_intersection()
        if not next_intersection:
            logging.info("Did not find a intersection")
            return None

        possible_turns_dict = next_intersection.get_possible_turns(self._driving_direction,  self.road_driving_on)
        if not possible_turns_dict:
            return None
        
        possible_turns = list(possible_turns_dict.keys())
        random_index = randint(0, len(possible_turns)-1)
        
        return possible_turns[random_index]
               
    def set_road_driving_on(self) -> bool:
        for road in self.all_roads:
            # Car must be on road and road should not be a intersection     
            if road.on_road(self.x, self.y) and road._road_type is not RoadType.INTERSECTION:
                # Update prev road driving variable
                if self.prev_road_driving_on != road:
                        self.prev_road_driving_on = self.road_driving_on
                        self.road_driving_on = road
                        
                        return True # new road was detected
                
                return True # old road
        
        return False # still on a detected road 
    
    def get_next_intersection(self) -> Road | None:
        # get the intersection which comes next        
        for road in self.all_roads:
            if road._road_type is RoadType.INTERSECTION: # road must be a intersection)
                if road.get_possible_turns(self._driving_direction,  self.road_driving_on): # when i get a list with elements i know the intersection is connected with my road
                    return road
        return None
    
    def is_off_screen(self) -> bool:
        return self.x > self.screen.get_width() or self.y > self.screen.get_height() or self.x < -10 or self.y < -10

    def get_cars_in_front(self, all_cars: list[Car]) -> list[Car]:
        # TODO: only sorts after the x value. Should be sorted after x and y value (maybe check on which road i am and which car is also on the road)
        all_cars_ids = [car.id for car in all_cars]
        
        index = all_cars_ids.index(self.id)
        cars_in_front_of_me = all_cars[index+1:]

        return cars_in_front_of_me
    
    def car_in_front_moving(self, car_in_front: list[Car]) -> bool:
        # TODO: to_close should also be for y value, if on a NORTH or SOUTH road
        car = car_in_front[0]
        too_close = abs(car.x - self.x) < self.safety_distance
        return car.driving_status or not too_close
    
    def driving_direction(self):
        return self._driving_direction
       
    @property
    def driving_status(self) -> bool:
        return self.driving
