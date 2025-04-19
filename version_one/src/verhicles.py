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
        self.rotate = False
        
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
            new_direction = self.moving_direction()
            
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
        
        # TODO: CHANGE with coordinates !!!! 
        # TODO: self.rotate has to be done different. (better animation!!!)       
        
        # TODO: add other possibilities to drive and update the driving position        
        #       self.x -= self.speed * delta_time 
        #       self._driving_direction = RoadDirections.WEST

        #       self.y += self.speed * delta_time 
        #       self._driving_direction = RoadDirections.SOUTH
        
        if 569 <= self.x <= 573:            
            self._driving_direction = RoadDirections.NORTH
            self.y -= self.speed * delta_time
            
            if not self.rotate:
                #self.img = pygame.transform.rotate(self.img, 30)
                #self.img = pygame.transform.rotate(self.img, 60)
                self.img = pygame.transform.rotate(self.img, 90)
                self.rotate = True

        else:
            self._driving_direction = RoadDirections.EAST
            self.x += self.speed * delta_time
    
    def moving_direction(self) -> RoadDirections | None:
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
            if not road.on_road(self.x, self.y) or road._road_type is RoadType.INTERSECTION:
                continue
            # Update prev road driving variable
            if self.prev_road_driving_on != road:
                    self.prev_road_driving_on = self.road_driving_on
                    self.road_driving_on = road
                    return True # new road was detected
            
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
