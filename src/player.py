from world import *

from dataclasses import dataclass, field

@dataclass
class Player:
    name: str
    position: Position
    inventory: list[Item]
    journal: list[Quest]
    talked_to: list[NPC]