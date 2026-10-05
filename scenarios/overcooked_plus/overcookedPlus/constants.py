DIRECTION = [(0, 1), (1, 0), (0, -1), (-1, 0)]

ITEMIDX = {
    "block": -1,
    "space": 0,
    "counter": 1,
    "agent": 2,
    "tomato": 3,
    "lettuce": 4,
    "plate": 5,
    "knife": 6,
    "delivery": 7,
    "onion": 8,
    "pan": 9,
    "steak": 10,
    "sink": 11,
    "trash_can": 12,
    "fish": 13,
    "ricecooker": 14,
    "rice": 15,
    "cheese": 16,
    "dough": 17,
    "oven": 18,
    "sushi": 19,
    "pizza": 20,
    "roastfish": 21,
}

AGENTCOLOR = ["blue", "magenta", "green", "yellow"]

TASKLIST = [
    "tomato salad",
    "lettuce salad",
    "onion salad",
    "lettuce-tomato salad",
    "onion-tomato salad",
    "lettuce-onion salad",
    "lettuce-onion-tomato salad",
    "steak",
    "steak with lettuce",
    "steak with tomato",
    "steak with onion",
    "steak with lettuce and tomato",
    "steak with lettuce and onion",
    "steak with tomato and onion",
    "steak with lettuce and tomato and onion",
]

INGLIST = [
    "tomato",
    "lettuce",
    "onion",
    "steak",
    "fish",
    "rice",
    "cheese",
    "dough",
    "sushi",
    "pizza",
    "roastfish",
]

from enum import Enum, IntEnum


class ActionType(str, Enum):
    MOVE = "move"
    COLLISION = "collision"
    PICKUP = "pickup"
    PICKUP_INTO_PLATE = "pickup_into_plate"
    PUTDOWN = "putdown"
    DUMP = "dump"
    DELIVER = "deliver"
    CHOP = "chop"
    WASH = "wash"
    NONE = "None"


class PrimitiveAction(IntEnum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3
    INTERACT = 4
