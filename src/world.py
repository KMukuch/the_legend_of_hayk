import os
import json

from enum import Enum

from dataclasses import dataclass, field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ConditionType(Enum):
    TALK_TO = "talk to"
    GO_TO = "go to"
    TAKE_ITEM = "take item"
    DEFEAT_NPC = "defeat npc"
    SCRIPT = "script"

class StatusType(Enum):
    IN_PROGRESS = "in progress"
    COMPLETED = "completed"

@dataclass
class Connection:
    id: int
    name: str
    distance: int

@dataclass
class Location:
    id: int
    name: str
    connections: list[Connection]

@dataclass
class Map:
    id: int
    name: str
    locations: dict[int, Location] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)

    def parse_map(self, filepathe):
        try:
            with open(filepathe, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Map file not found: {filepathe}")
            return

        for d in data:
            id = d["id"]
            name = d["name"]
            location = Location(id, name, [])

            self.locations[location.id] = location

        for d in data:
            location = self.locations[d["id"]]
            for c in d["connections"]:
                connection = Connection(c["id"], c["name"], c["distance"])
                location.connections.append(connection)

@dataclass
class Position:
    map: Map
    location: Location

@dataclass
class Item:
    id: int
    name: str
    position: Position

@dataclass
class Dialog:
    id: int
    content: str
    answer: str

@dataclass
class NPC:
    id: int
    name: str
    position: Position
    dialog: dict[int, Dialog] = field(default_factory=dict)

@dataclass
class Condition:
    type: ConditionType
    target_id: int

@dataclass
class Quest:
    id: int
    name: str
    content: str
    init: list[Condition]
    compl: list[Condition]
    status: StatusType = StatusType.IN_PROGRESS

@dataclass
class World:
    maps: dict[int, Map] = field(default_factory=dict)
    items: dict[int, Item] = field(default_factory=dict)
    npcs: dict[int, NPC] = field(default_factory=dict)
    journal: dict[int, Quest] = field(default_factory=dict)

    def parse_maps(self, filepathe):
        with open(filepathe, "r") as f:
            data = json.load(f)

        for d in data:
            id = d["id"]
            name = d["name"]
            map_ref = d["map_ref"]

            map = Map(id, name, {})
            map.parse_map(os.path.join(BASE_DIR, "data/", map_ref))

            self.maps[map.id] = map

        for d in data:
            map = self.maps[d["id"]]
            for c in d["connections"]:
                connection = Connection(c["id"], c["name"], c["distance"])
                map.connections.append(connection)
    
    def parse_items(self, filepathe):
        with open(filepathe, "r") as f:
            data = json.load(f)

        for d in data:
            id = d["id"]
            name = d["name"]

            map = self.maps[d["position"]["map"]["id"]]
            location = map.locations[d["position"]["location"]["id"]]

            position = Position(map, location)
            item = Item(id, name, position)

            self.items[item.id] = item

    def parse_npcs(self, filepathe):
        with open(filepathe, "r") as f:
            data = json.load(f)

        for d in data:
            map = self.maps[d["position"]["map"]["id"]]
            location = map.locations[d["position"]["location"]["id"]]
            position = Position(map, location)

            npc = NPC(d["id"], d["name"], position)

            for dlg in d["dialog"]:
                dialog = Dialog(dlg["id"], dlg["content"], dlg["answer"])

                npc.dialog[dialog.id] = dialog

            self.npcs[npc.id] = npc

    def parse_journal(self, filepathe):
        with open(filepathe, "r") as f:
            data = json.load(f)

        for d in data:
            init = []

            for c in d["init"]:
                init.append(Condition(ConditionType(c["type"]), c["target_id"]))

            compl = []

            for c in d["compl"]:
                compl.append(Condition(ConditionType(c["type"]), c["target_id"]))

            quest = Quest(d["id"], d["name"], d["content"], init, compl)

            self.journal[quest.id] = quest