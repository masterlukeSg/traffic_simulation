from enum import Enum

LANE_WIDTH = 5


class Color(Enum):
    BLACK = ( 0, 0, 0)
    WHITE = ( 255, 255, 255)
    GRAY = ( 128, 128, 128)


class ColorPhase(Enum):
    RED = ( 255, 0, 0)
    YELLOW = ( 238, 210, 2)
    GREEN = ( 0, 128, 0)


class RoadDirections(Enum):
    NORTH = "up"
    EAST = "right"
    SOUTH = "down"
    WEST = "left"
