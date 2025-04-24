from __future__ import annotations # To type hint car in the car class
import pygame
from constants import  ColorPhase, RoadDirections, RoadType
from map import Road
import logging
from random import randint

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s',
    datefmt='%H:%M:%S'
)

class Car:
    _id_counter = 0
    
    def __init__(self, screen, start_x, start_y, direction: RoadDirections):
        Car._id_counter += 1
        
        self.id = f"car_{Car._id_counter}"
        self.x = start_x
        self.y = start_y
        self.screen = screen
        
        img = pygame.image.load('version_one/images/Car.png')

        self.ui_handler = CarUI(self.screen, direction, img)
        self.logic = CarLogic(self.id, start_x, start_y, direction, self.ui_handler)
        self.ui_handler.first_rotation(direction) 

    def draw(self) -> None:
        self.__update_coordinates()
        self.ui_handler.draw(self.x, self.y)
    
    def move(self, delta_time: int, all_cars: list[Car], all_roads: list[Road]) -> None:
        self.logic.move(delta_time, all_cars, all_roads)
    
    def deleteable(self) -> bool:
        self.__update_coordinates()
        return self.x > self.screen.get_width() or self.y > self.screen.get_height() or self.x < -10 or self.y < -10
    
    def __update_coordinates(self):
        self.x, self.y = self.logic.coordinates
    
    @property
    def driving_status(self) -> bool:
        return self.logic.driving_status
    

class CarLogic:
    def __init__(self, id, start_x, start_y, direction: RoadDirections, ui_handler: CarUI):
        self.id = id
        self.ui_handler = ui_handler
        
        self.x = start_x
        self.y = start_y        
        
        self.safety_distance = 60
        self.speed = 60
        self.driving = False
        self._driving_direction = direction
        self.next_direction: RoadDirections = None
        
        self.rotation = False
            
        self.all_roads: list[Road] = None
        self.road_driving_on: Road = None
        self.prev_road_driving_on = None

    def move(self, delta_time: int, all_cars: list[Car], all_roads: list[Road]) -> None:
        self.all_roads = all_roads
        self.__set_road_driving_on() # needs the all_roads var
        
        if self.__should_move(all_cars):
            new_direction = self.__get_next_direction()

            if new_direction is not None:
                self.next_direction = new_direction
            
            self.__apply_move(delta_time)
            self.driving = True
            
        else:
            self.driving = False
    
    def __should_move(self, all_cars: list[Car]) -> bool:
        cars_in_front = self.__get_cars_in_front(all_cars)
        if cars_in_front: 
            if not self.__car_in_front_moving(cars_in_front):
                return False
        
        
        wait_phases = [ColorPhase.RED.name, ColorPhase.YELLOW.name]
        road = self.road_driving_on
        
        road_safety_distance = 30
        
        if road and road.road_type is not RoadType.INTERSECTION: # An intersection has no traffic light
            traffic_lights = road.traffic_light # Get the traffic light in both directions
            traffic_light = traffic_lights.get(self._driving_direction, {}) # The traffic light for our direction
            
            if traffic_light:
                phase = traffic_light.get_phase()
            
                if traffic_light:    
                    match(self._driving_direction): # Determine the coordinates where the road ends in our driving direction, along with the corresponding car position
                        case (RoadDirections.EAST):
                            car_front = self.x + road_safety_distance
                            street_end = road.street_end(RoadDirections.EAST)[0] 
                        case (RoadDirections.WEST):
                            car_front = self.x - road_safety_distance / 2
                            street_end = road.x
                        case(RoadDirections.NORTH):
                            car_front = self.y - road_safety_distance / 2
                            street_end = road.y
                        case(RoadDirections.SOUTH):
                            car_front = self.y + road_safety_distance
                            street_end = road.street_end(RoadDirections.SOUTH)[1] 
                    
                    if street_end - car_front <= 5 and street_end - car_front >= 1 and phase in wait_phases:
                        return False
                    
        return True
           
    def __apply_move(self, delta_time: int) -> None:
        self.driving = True
        if not self.road_driving_on:
            return

        if self.__at_intersection():
            self.__handle_turning(delta_time)
        else:
            self.rotation = False
            self.__drive_straight(delta_time)   
                  
    def __at_intersection(self) -> bool:
        next_intersection = self.__get_next_intersection()
        if next_intersection and next_intersection.on_road(self.x, self.y):
            return True
        return False

    def __handle_turning(self, delta_time: int) -> None:
        next_intersection = self.__get_next_intersection()
        if not next_intersection:
            self.__drive_straight(delta_time)
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

        if turn_coords and self.__is_at_coordinates(turn_coords):
            self._driving_direction = self.next_direction
            if not self.rotation:
                self.ui_handler.rotate_car(self.next_direction)
                self.rotation = True
                
            self.next_direction = None
           

        self.__drive_straight(delta_time)

    def __drive_straight(self, delta_time: int) -> None:
        match self._driving_direction:
            case RoadDirections.NORTH:
                self.y -= self.speed * delta_time
            case RoadDirections.SOUTH:
                self.y += self.speed * delta_time
            case RoadDirections.WEST:
                self.x -= self.speed * delta_time
            case RoadDirections.EAST:
                self.x += self.speed * delta_time

    def __is_at_coordinates(self, coords: tuple[int, int], tolerance: int = 3) -> bool:
        return (coords[0] - tolerance <= self.x <= coords[0] + tolerance and
                coords[1] - tolerance <= self.y <= coords[1] + tolerance)
    
    def __get_next_direction(self) -> RoadDirections | None:
        # The road i am driving on is a road which was already detected
        if not self.__set_road_driving_on():
            return None
        
        next_intersection = self.__get_next_intersection()
        if not next_intersection:
            #logging.info("Did not find a intersection")
            return None

        possible_turns_dict = next_intersection.get_possible_turns(self._driving_direction,  self.road_driving_on)
        if not possible_turns_dict:
            return None
        
        possible_turns = list(possible_turns_dict.keys())
        random_index = randint(0, len(possible_turns)-1)
        
        return possible_turns[random_index]
               
    def __set_road_driving_on(self) -> bool:
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
    
    def __get_next_intersection(self) -> Road | None:
        # get the intersection which comes next        
        for road in self.all_roads:
            if road._road_type is RoadType.INTERSECTION: # road must be a intersection)
                if road.get_possible_turns(self._driving_direction,  self.road_driving_on): # when i get a list with elements i know the intersection is connected with my road
                    return road
        return None

    def __get_cars_in_front(self, all_cars: list[Car]) -> list[Car]:
        cars_in_front = []

        for car in all_cars:
            if car.id == self.id:
                continue

            # Check whether the car is traveling on the same road and in the same direction
            same_road = car.logic.road_driving_on == self.road_driving_on
            same_direction = car.logic._driving_direction == self._driving_direction

            if same_road and same_direction:
                # Check whether it is actually in front of the current car
                match self._driving_direction:
                    case RoadDirections.EAST:
                        if car.x > self.x:
                            cars_in_front.append(car)
                    case RoadDirections.WEST:
                        if car.x < self.x:
                            cars_in_front.append(car)
                    case RoadDirections.NORTH:
                        if car.y < self.y:
                            cars_in_front.append(car)
                    case RoadDirections.SOUTH:
                        if car.y > self.y:
                            cars_in_front.append(car)

        # Sort by distance to the current car
        if self._driving_direction in (RoadDirections.EAST, RoadDirections.WEST):
            cars_in_front.sort(key=lambda c: abs(c.x - self.x))
        else:
            cars_in_front.sort(key=lambda c: abs(c.y - self.y))

        return cars_in_front
        
    def __car_in_front_moving(self, car_in_front: list[Car]) -> bool:
        car = car_in_front[0]
        if self.road_driving_on.road_type is RoadType.HORIZONTAL:
            too_close = abs(car.x - self.x) < self.safety_distance
        else:
            too_close = abs(car.y - self.y) < self.safety_distance  
        
        return car.driving_status or not too_close
       
    @property
    def driving_status(self) -> bool:
        return self.driving
    
    @property
    def coordinates(self) -> tuple[float, float]:
        return (self.x, self.y)
    
    
class CarUI:
    def __init__(self, screen, start_rotation, img):
        self.screen = screen
        self.img = img
        self.current_rotation = start_rotation
          
    def draw(self, x, y) -> None:
        self.screen.blit(self.img,(x, y))
    
    def first_rotation(self, rotate_to: RoadDirections):
        angle = {   RoadDirections.EAST.value: 0,
                    RoadDirections.NORTH.value: 90,
                    RoadDirections.SOUTH.value: 270,
                    RoadDirections.WEST.value: 180
                }
        self.img = pygame.transform.rotate(self.img, angle.get(rotate_to.value, 0))
    
    def rotate_car(self, rotate_to: RoadDirections):              
        angle = {
            RoadDirections.EAST: {
                RoadDirections.NORTH: 90,
                RoadDirections.SOUTH: 270,
                RoadDirections.WEST: 180,
            },
            RoadDirections.NORTH: {
                RoadDirections.EAST: 270,
                RoadDirections.WEST: 90,
                RoadDirections.SOUTH: 180,
            },
            RoadDirections.SOUTH: {
                RoadDirections.EAST: 90,
                RoadDirections.WEST: 270,
                RoadDirections.NORTH: 180,
            },
            RoadDirections.WEST: {
                RoadDirections.NORTH: 270,
                RoadDirections.SOUTH: 90,
                RoadDirections.EAST: 180,
            }
        }

        rotation = angle.get(self.current_rotation, {}).get(rotate_to, {})
        if not rotation:
            logging.info("The calling function has a error, as this function should not be callen, when there is no turn")
        
        self.img = pygame.transform.rotate(self.img, rotation)
        self.current_rotation = rotate_to
