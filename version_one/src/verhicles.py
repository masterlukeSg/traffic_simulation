from __future__ import annotations # To type hint car in the car class
import pygame
import uuid
from constants import  ColorPhase, RoadDirections, RoadType
from map import Road, TrafficLight, LANE_WIDTH


class Car:
    def __init__(self, screen, x, y, direction: RoadDirections):
        self.screen = screen
        
        self.id = uuid.uuid4().hex[:6] # 6 chars for the id 
        self.safety_distance = 40
        self.speed = 60
        self.driving = False
        self._driving_direction = direction
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
    
    def driving_direction(self):
        return self._driving_direction
       
    @property
    def driving_status(self) -> bool:
        return self.driving
