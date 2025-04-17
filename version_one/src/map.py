from __future__ import annotations # To type hint car in the car class
import pygame
from abc import ABC
from constants import Color, ColorPhase, RoadDirections, LANE_WIDTH
from random import randint


class Road(ABC):
    def __init__(self, screen, start_x, start_y, lenght, width, directions: list[RoadDirections], lanes_amount=2):
        self.screen = screen
        self.x: float = start_x
        self.y: float = start_y
        self.length: float = lenght
        self.width: float = width
        self.lanes_amount: int = lanes_amount
        self.lane_width: float = LANE_WIDTH
        self._directions: list[RoadDirections] = directions

    def draw_rect(self, color, x: float, y: float, width:float , height: float) -> None:
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height))

    def draw(self) -> None:
        pass
    
    def create_seperator(self) -> None:
        pass

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
    def __init__(self, screen, start_x, start_y, lenght, width, directions, lanes_amount=2):
        super().__init__(screen, start_x, start_y, lenght, width, directions, lanes_amount) 
    
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


class VerticalRoad(Road):
    def __init__(self, screen, start_x, start_y, lenght, width, directions, lanes_amount=2):
        super().__init__(screen, start_x, start_y, lenght, width, directions, lanes_amount)

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
    
    
class Intersection(Road):
    def __init__(self, screen, start_x, start_y, side_length, directions):
        super().__init__(screen, start_x, start_y, side_length, side_length, directions)
        
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
     