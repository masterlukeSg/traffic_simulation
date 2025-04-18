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
        self.road_type:RoadType = road_type

    def draw_rect(self, color, x: float, y: float, width:float , height: float) -> None:
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height))

    def draw(self) -> None:
        pass
    
    def create_seperator(self) -> None:
        pass

    def street_end(self, direction: RoadDirections.value) -> tuple[int, int]:
        match (direction):
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
        if self.road_type != RoadType.INTERSECTION:
            return None
        
        self.connected_roads = {}

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
    
    def draw(self) -> None:
        black = Color.BLACK.value
        white = Color.WHITE.value
        
        # Road : Black lane
        self.draw_rect(black, self.x, self.y, self.length, self.lane_width)
        self.draw_rect(black, self.x, self.y+self.width, self.length, self.lane_width)
        
        # Innerroad : White space
        self.draw_rect(white, self.x, self.y+self.lane_width, self.length, self.width-self.lane_width)

        # Road seperator : Black 
        self.create_seperator()
    
    def create_seperator(self) -> None:
        # Road separator (middle dashed line)
        separator_width = 10
        separator_height = 5
        separator_gap = 10

        # Middle y-position for the separator
        for i in range(self.x, self.x + self.length, separator_width + separator_gap):
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(i, self.middle_y, separator_width, separator_height))

    def street_end(self, direction: RoadDirections.value) -> tuple[int, int] | None:
        if direction is RoadDirections.NORTH.value or direction is RoadDirections.SOUTH.value:
            direction = None
        
        return super().street_end(direction)
        
class VerticalRoad(Road):
    def __init__(self, screen, road_type: RoadType, start_x, start_y, lenght, width, directions):
        super().__init__(screen,road_type, start_x, start_y, lenght, width, directions)

    def draw(self) -> None:
        black = Color.BLACK.value
        white = Color.WHITE.value
        
        # Road : Black lane
        self.draw_rect(black, self.x, self.y+self.lane_width, self.lane_width, self.length)
        self.draw_rect(black,self.x+self.width, self.y+self.lane_width, self.lane_width, self.length)
                
        # Innerroad : White space
        self.draw_rect(white,self.x+self.lane_width, self.y+self.lane_width, self.width-self.lane_width, self.length)
        
        # Road seperator : Black 
        self.create_seperator()        

    def create_seperator(self) -> None:
        # Road separator (middle dashed line)
        separator_width = 10
        separator_height = 5
        separator_gap = 10

        # Middle y-position for the separator
        for i in range(self.y+self.lane_width, self.y + self.length, separator_width + separator_gap):
            pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(self.middle_x, i,  separator_height, separator_width))
    
    def street_end(self, direction: RoadDirections.value) -> tuple[int, int] | None:
        if direction is RoadDirections.EAST.value or direction is RoadDirections.WEST.value:
            direction = None
        
        return super().street_end(direction)
   
    
class Intersection(Road):
    def __init__(self, screen, road_type: RoadType, start_x: float, start_y: float, side_length: float, directions: list[RoadDirections]):
        super().__init__(screen, road_type, start_x, start_y, side_length, side_length, directions)
        
        reduced_side = side_length - self.lane_width
        
        self.side_length = reduced_side
        self.width = reduced_side
        self.length = reduced_side  # falls du das auch benutzt

    def draw(self) -> None:
        white = Color.WHITE.value
        self.draw_rect(white,self.x, self.y, self.side_length, self.side_length)
        
        self.create_boundries()
        self.draw_turn_markers()
    
    def draw_corner_pixel(self, x, y, w, h):
        pygame.draw.rect(self.screen, Color.BLACK.value, pygame.Rect(x, y, w, h))
    
    def create_boundries(self) -> None:
        lane = self.lane_width
        size = self.side_length
        max_x = self.x + size
        max_y = self.y + size
        corner_size = LANE_WIDTH


        # Side boundaries
        if RoadDirections.EAST not in self.directions:
            self.draw_corner_pixel(max_x, self.y, lane, size)

        if RoadDirections.WEST not in self.directions:
            self.draw_corner_pixel(self.x, self.y, lane, size )

        if RoadDirections.NORTH not in self.directions:
            self.draw_corner_pixel(self.x, self.y - lane, size , lane)

        if RoadDirections.SOUTH not in self.directions:
            self.draw_corner_pixel(self.x, self.y+ size, size , lane)


        # Draw corners
        corners = [
            (self.x - corner_size, self.y - corner_size),       # Top Left
            (max_x, self.y - corner_size),                      # Top Right
            (self.x - corner_size, max_y),                      # Bottom Left
            (max_x, max_y),                                      # Bottom Right
        ]
        
        for cx, cy in corners:
            self.draw_corner_pixel(cx, cy, corner_size, corner_size)
    
    def draw_turn_markers(self) -> None:
        black = Color.BLACK.value
    
        # middle
        self.draw_rect(black, self.middle_x, self.middle_y, LANE_WIDTH, LANE_WIDTH)
        
        # upper left & right
        self.draw_rect(black, self.upper_left_middle[0], self.upper_left_middle[1], LANE_WIDTH, LANE_WIDTH)
        self.draw_rect(black, self.upper_right_middle[0], self.upper_right_middle[1], LANE_WIDTH, LANE_WIDTH)
        
        # lower left & right
        self.draw_rect(black, self.lower_left_middle[0], self.lower_left_middle[1], LANE_WIDTH, LANE_WIDTH)
        self.draw_rect(black, self.lower_right_middle[0], self.lower_right_middle[1], LANE_WIDTH, LANE_WIDTH)
    
    
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
        self.green_red_phase = randint (4,9)
        self.yellow_phase = 2
              
        self.countdown_start: int = self.green_red_phase
        self.start_ticks = pygame.time.get_ticks()
        self.time_left = self.countdown_start
        
        self.my_font = pygame.font.SysFont('Freeroad', 20)
        self.img_green, self.img_red, self.img_yellow = None, None, None  
        self.set_img()
    
    def draw(self) -> None:
        self.update_phase()
        self.remaining_time_text()
        
        match (self.color_phase.value):
            case (ColorPhase.GREEN.value):
                self.screen.blit(self.img_green,(self.x, self.y))
            
            case (ColorPhase.YELLOW.value):
                self.screen.blit(self.img_yellow,(self.x, self.y))
            
            case (ColorPhase.RED.value):
                self.screen.blit(self.img_red,(self.x, self.y))
        
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
    
    def remaining_time_text(self) -> None:
        time_left = str(self.remaining_time)
        
        self.text1 = self.my_font.render(time_left, True, Color.BLACK.value)
        self.screen.blit(self.text1,(self.x + 5, self.y+60))
    
    def set_img(self) -> None:
        scale = (20, 56)
        
        self.img_green = self.load_img('version_one/images/GreenTrafficLight.png', scale)
        self.img_yellow = self.load_img('version_one/images/YellowTrafficLight.png', scale)
        self.img_red = self.load_img('version_one/images/RedTrafficLight.png', scale)
    
    def load_img(self, url: str, scale: tuple[int,int]) -> pygame.image:
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
     
