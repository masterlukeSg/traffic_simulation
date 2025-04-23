from __future__ import annotations
import pygame
import uuid
from abc import ABC
from constants import Color, ColorPhase, RoadDirections, RoadType, LANE_WIDTH
from random import randint


class Road(ABC):
    def __init__(self, screen, road_type: RoadType, start_x: float, start_y: float, lenght: float, width:float, directions: list[RoadDirections]):
        self.screen = screen
        self.x: float = start_x
        self.y: float = start_y
        self.length: float = lenght
        self.width: float = width
        self.lanes_amount: int = 2
        self.lane_width: float = LANE_WIDTH
        self._directions: list[RoadDirections] = directions
        self.id = uuid.uuid4().hex[:6] # 6 chars for the id
        self._road_type:RoadType = road_type
        self.connected_roads = {}
        self._all_traffic_lights = {}
        self._active_traffic_lights = {}

    def draw_rect(self, color, x: float, y: float, width:float , height: float) -> None:
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height))

    def draw(self) -> None:
        pass
    
    def _create_seperator(self) -> None:
        pass

    def street_end(self, direction: RoadDirections) -> tuple[int, int]:
        match (direction.value):
            case (RoadDirections.SOUTH.value):
                return (self.x, self.y + self.length)
            
            case(RoadDirections.NORTH.value):
                return (self.x, self.y + self.lane_width)
            
            case (RoadDirections.EAST.value):
                return (self.x+self.length-self.lane_width, self.y)
            
            case(RoadDirections.WEST.value):
                return (self.x, self.y)
            
            case (_):
                print("This direction is not compatible with the road")
                return None
    
    def find_connected_roads(self, roads: list[Road]) -> dict | None:
        if self._road_type != RoadType.INTERSECTION:
            return None
        
        margin = 5
        
        for road in roads:
            if road.id == self.id:
                continue

            # Check NORTH: road ends at top of intersection
            if abs(road.y + road.length - self.y) <= margin and road.x < self.x + self.width and road.x + road.width > self.x:
                self.connected_roads[RoadDirections.NORTH] = road

            # Check SOUTH: road starts at bottom of intersection
            elif abs(road.y - (self.y + self.length)) <= margin and road.x < self.x + self.width and road.x + road.width > self.x:
                self.connected_roads[RoadDirections.SOUTH] = road

            # Check WEST: road ends at left of intersection
            elif abs(road.x + road.length - self.x) <= margin and road.y < self.y + self.length and road.y + road.length > self.y:
                self.connected_roads[RoadDirections.WEST] = road

            # Check EAST: road starts at right of intersection
            elif abs(road.x - (self.x + self.width)) <= margin and road.y < self.y + self.length and road.y + road.length > self.y:
                self.connected_roads[RoadDirections.EAST] = road
            
        
        return self.connected_roads 
    
    def on_road(self, x: float, y: float) -> bool:
        in_x_range, in_y_range = 0,0
        
        if isinstance(self, HorizontalRaod):
            in_x_range = self.x <= x <= self.x + self.length
            in_y_range = self.y <= y <= self.y + self.width
        elif isinstance(self, VerticalRoad):
            in_x_range = self.x <= x <= self.x + self.width
            in_y_range = self.y <= y <= self.y + self.length
        elif isinstance(self, Intersection):
            in_x_range = self.x <= x <= self.x + self.width
            in_y_range = self.y <= y <= self.y + self.width
        
        return in_x_range and in_y_range
    
    def _create_traffic_ligts(self) -> None:
        for direction in self.directions:
            match(direction.value):
                case(RoadDirections.NORTH.value): # vertical road
                    self._all_traffic_lights[RoadDirections.NORTH] = TrafficLight(self.screen, self.street_end(RoadDirections.NORTH)[0] + self.width + 10, self.y + 20) # must be on the right side
                
                case(RoadDirections.SOUTH.value): # vertical road
                    self._all_traffic_lights[RoadDirections.SOUTH]= TrafficLight(self.screen, self.x - 25, self.street_end(RoadDirections.SOUTH)[1] - self.width + 5) # must be on the left side

                case(RoadDirections.WEST.value): # horizontal road
                    self._all_traffic_lights[RoadDirections.WEST] = TrafficLight(self.screen, self.x + 10 , self.y - self.width + 5) # must be on the upper side
                
                case(RoadDirections.EAST.value): # horizontal road
                    self._all_traffic_lights[RoadDirections.EAST]= TrafficLight(self.screen,  self.street_end(RoadDirections.EAST)[0] - 25  , self.street_end(RoadDirections.EAST)[1] + self.width + 15) # must be on the upper side
                    
    def draw_traffic_lights(self) -> None:
        for traf in self._active_traffic_lights.values():
            traf.draw()
    
    def set_traffic_lights(self, new_traffic_lights) -> None:
        self._active_traffic_lights.update(new_traffic_lights)
    
    @property
    def traffic_light(self) -> dict:
        return self._active_traffic_lights
    
    @property
    def road_type(self) -> RoadType: 
        return self._road_type
    
    @property
    def directions(self) -> list[RoadDirections]:
        return self._directions
    
    @property
    def middle_x(self) -> int:
        return self.x + (self.width // 2)
    
    @property
    def middle_y(self) -> int:
        return self.y + (self.width // 2) 


class HorizontalRaod(Road):
    def __init__(self, screen, road_type: RoadType, start_x: float, start_y: float, lenght: float, width: float, directions: list[RoadDirections]):
        super().__init__(screen, road_type, start_x, start_y, lenght, width, directions) 
        super()._create_traffic_ligts()
    
    def draw(self) -> None:
        black = Color.BLACK.value
        white = Color.WHITE.value
        
        # Road : Black lane
        self.draw_rect(black, self.x, self.y, self.length, self.lane_width)
        self.draw_rect(black, self.x, self.y+self.width, self.length, self.lane_width)
        
        # Innerroad : White space
        self.draw_rect(white, self.x, self.y+self.lane_width, self.length, self.width-self.lane_width)

        # Road seperator : Black 
        self._create_seperator()
        
        self.draw_traffic_lights()
    
    def _create_seperator(self) -> None:
        # Road separator (middle dashed line)
        separator_width = 10
        separator_height = 5
        separator_gap = 10

        # Middle y-position for the separator
        for i in range(self.x, self.x + self.length, separator_width + separator_gap):
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(i, self.middle_y, separator_width, separator_height))

    def street_end(self, direction: RoadDirections) -> tuple[int, int] | None:
        if direction is RoadDirections.NORTH.value or direction is RoadDirections.SOUTH.value:
            direction = None
        
        return super().street_end(direction)
    
    
class VerticalRoad(Road):
    def __init__(self, screen, road_type: RoadType, start_x, start_y, lenght, width, directions):
        super().__init__(screen,road_type, start_x, start_y, lenght, width, directions)
        super()._create_traffic_ligts()

    def draw(self) -> None:
        black = Color.BLACK.value
        white = Color.WHITE.value
        
        # Road : Black lane
        self.draw_rect(black, self.x, self.y+self.lane_width, self.lane_width, self.length)
        self.draw_rect(black,self.x+self.width, self.y+self.lane_width, self.lane_width, self.length)
                
        # Innerroad : White space
        self.draw_rect(white,self.x+self.lane_width, self.y+self.lane_width, self.width-self.lane_width, self.length)
        
        # Road seperator : Black 
        self._create_seperator()        
        
        self.draw_traffic_lights()

    def _create_seperator(self) -> None:
        # Road separator (middle dashed line)
        separator_width = 10
        separator_height = 5
        separator_gap = 10

        # Middle y-position for the separator
        for i in range(self.y+self.lane_width, self.y + self.length, separator_width + separator_gap):
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.middle_x, i,  separator_height, separator_width))
    
    def street_end(self, direction: RoadDirections) -> tuple[int, int] | None:
        if direction is RoadDirections.EAST.value or direction is RoadDirections.WEST.value:
            direction = None
        
        return super().street_end(direction)
   
    
class Intersection(Road):
    def __init__(self, screen, road_type: RoadType, start_x: float, start_y: float, side_length: float, directions: list[RoadDirections]):
        super().__init__(screen, road_type, start_x, start_y, side_length, side_length, directions)
        
        reduced_side = side_length - self.lane_width
        
        self.side_length = reduced_side
        self.width = reduced_side
        self.length = reduced_side        

    def draw(self) -> None:
        white = Color.WHITE.value
        self.draw_rect(white,self.x, self.y, self.side_length, self.side_length)
        
        self.__create_boundries()
        
    def __draw_corner_pixel(self, x, y, w, h):
        pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(x, y, w, h))
    
    def __create_boundries(self) -> None:
        lane = self.lane_width
        size = self.side_length
        max_x = self.x + size
        max_y = self.y + size
        corner_size = LANE_WIDTH


        # Side boundaries
        if RoadDirections.EAST not in self.directions:
            self.__draw_corner_pixel(max_x, self.y, lane, size)

        if RoadDirections.WEST not in self.directions:
            self.__draw_corner_pixel(self.x, self.y, lane, size )

        if RoadDirections.NORTH not in self.directions:
            self.__draw_corner_pixel(self.x, self.y - lane, size , lane)

        if RoadDirections.SOUTH not in self.directions:
            self.__draw_corner_pixel(self.x, self.y+ size, size , lane)


        # Draw corners
        corners = [
            (self.x - corner_size, self.y - corner_size),       # Top Left
            (max_x, self.y - corner_size),                      # Top Right
            (self.x - corner_size, max_y),                      # Bottom Left
            (max_x, max_y),                                      # Bottom Right
        ]
        
        for cx, cy in corners:
            self.__draw_corner_pixel(cx, cy, corner_size, corner_size)
    
    def get_possible_turns(self, direction: RoadDirections, road: RoadType) -> dict[RoadDirections]:
        translate_direction = { RoadDirections.NORTH: RoadDirections.SOUTH,
                                RoadDirections.WEST: RoadDirections.EAST,
                              }
        
        # switch the key with the value and it to the dict
        translate_direction.update({value: key  for key, value in translate_direction.items()})
        
        new_direction = translate_direction.get(direction, None)
            
        if new_direction is None:
            raise ValueError("The direction is not found")
       
        found_road = self.connected_roads.get(new_direction, None)

        # When the found road is the given road we know the road and the intersection are connected
        # Only return the key value pairs with out the own road and direction
        if found_road == road:
            non_self_roads = self.connected_roads.copy()
            non_self_roads.pop(new_direction)
            return non_self_roads
        
        else:
            return None
    
    def activate_needed_traffic_lights(self) -> None:
        translate_direction = { RoadDirections.NORTH: RoadDirections.SOUTH,
                                RoadDirections.WEST: RoadDirections.EAST,
                              }
        
        # switch the key with the value and it to the dict
        translate_direction.update({value: key  for key, value in translate_direction.items()})
        
        # for each connected road get the traffic lights and check if they are needed
        for road_direction, road in self.connected_roads.items(): 
            new_traffic_lights = {}
            
            for traffic_light_direction, traffic_light in road._all_traffic_lights.items():
                translated_road_direction = translate_direction.get(road_direction, None)
                
                if translated_road_direction == traffic_light_direction:
                    new_traffic_lights[translated_road_direction] = traffic_light

            if new_traffic_lights:
                road.set_traffic_lights(new_traffic_lights)
    
    @property
    def upper_left_middle(self):
        return (((self.x + self.middle_x) // 2) -2, ((self.y + self.middle_y) // 2) - 2)
    
    @property 
    def upper_right_middle(self):
        return (((self.middle_x + (self.x + self.width)) // 2) - 2,((self.y + self.middle_y) // 2) - 2)
    
    @property
    def lower_left_middle(self):
        return (((self.x + self.middle_x) // 2) - 2, ((self.middle_y + (self.y + self.width)) // 2) - 2)
    
    @property
    def lower_right_middle(self):
       return (((self.middle_x + (self.x + self.width)) // 2) - 2, ((self.middle_y + (self.y + self.width)) // 2) - 2)
    
    @property
    def middle_y(self) -> int: 
        return self.y + (self.width // 2) -2

    @property
    def middle_x(self) -> int:
        return self.x + (self.width // 2) -2
   
 
class TrafficLight:
    def __init__(self, screen, x, y, color=ColorPhase.RED):
        self.screen = screen
        self.x = x
        self.y = y
        self.color_phase = color
        self.starting_color_phase = color
        
        # how long a phase should take (in seconds)
        self.red_phase =  randint (4,8)
        self.green_phase = randint(5,9)
        self.yellow_phase = 2
              
        self.countdown_start: int = self.red_phase
        self.start_ticks = pygame.time.get_ticks()
        self.time_left = self.countdown_start
        
        self.my_font = pygame.font.SysFont('Freeroad', 20)
        self.img_green, self.img_red, self.img_yellow = None, None, None  
        self.__set_img()
    
    def draw(self) -> None:
        self.__update_phase()
        self.__remaining_time_text()
        
        match (self.color_phase.value):
            case (ColorPhase.GREEN.value):
                self.screen.blit(self.img_green,(self.x, self.y))
            
            case (ColorPhase.YELLOW.value):
                self.screen.blit(self.img_yellow,(self.x, self.y))
            
            case (ColorPhase.RED.value):
                self.screen.blit(self.img_red,(self.x, self.y))
        
    def __update_phase(self) -> None:
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
                self.countdown_start: int = self.green_phase # restart the countdown for the timer
                
            elif self.starting_color_phase == ColorPhase.GREEN:
                self.color_phase = ColorPhase.RED
                self.starting_color_phase = ColorPhase.RED
                self.countdown_start: int = self.red_phase # restart the countdown for the timer
            
            self.start_ticks = pygame.time.get_ticks()
            
    def get_phase(self) -> str:
        return self.color_phase.name

    def __remaining_time_text(self) -> None:
        time_left = str(self.remaining_time)
        
        self.text1 = self.my_font.render(time_left, True, Color.BLACK.value)
        self.screen.blit(self.text1,(self.x + 5, self.y+60))
    
    def __set_img(self) -> None:
        scale = (20, 56)
        
        self.img_green = self.__load_img('version_one/images/GreenTrafficLight.png', scale)
        self.img_yellow = self.__load_img('version_one/images/YellowTrafficLight.png', scale)
        self.img_red = self.__load_img('version_one/images/RedTrafficLight.png', scale)
    
    def __load_img(self, url: str, scale: tuple[int,int]) -> pygame.image:
        img = pygame.image.load(url)
        img = pygame.transform.scale(img, scale)
        return img
    
    @property
    def remaining_time(self) -> int:
        red = ColorPhase.RED.name
        green = ColorPhase.GREEN.name
        
        phase = self.get_phase()

        if phase == red or phase == green:
            return int(self.time_left - self.yellow_phase)
        else:        
            return int(self.time_left)
    
    @property  
    def get_location(self) -> tuple[int, int]:
        return (self.x, self.y) 
     