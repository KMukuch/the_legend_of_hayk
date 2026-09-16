import json

from enum import Enum

from dataclasses import dataclass, field
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAP_FILE = os.path.join(BASE_DIR, "map.json")
ITEMS_FILE = os.path.join(BASE_DIR, "items.json")
NPCS_FILE = os.path.join(BASE_DIR, "npcs.json")
JOURNAL_FILE = os.path.join(BASE_DIR, "journal.json")

class ConditionType(Enum):
    TALK_TO = "talk to"
    GO_TO = "go to"
    TAKE_ITEM = "take item"
    DEFEAT_NPC = "defeat npc"
    SCRIPT = "script"

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

    def parse_map(self, filepathe):
        with open(filepathe, "r") as f:
            data = json.load(f)

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

@dataclass
class World:
    maps: dict[int, Map] = field(default_factory=dict)
    items: dict[int, Item] = field(default_factory=dict)
    npcs: dict[int, NPC] = field(default_factory=dict)
    journal: dict[int, Quest] = field(default_factory=dict)
    
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

@dataclass
class Player:
    name: str
    position: Position

@dataclass
class Game:
    name: str
    world: World
    player: Player

    def go_player(self):
        current = self.player.position.location

        print(f"\nYou are at {current.name}")

        print("You can go to:")
        for connection in current.connections:
            print(f"- {connection.name}")

        choice = input("> ")

        for connection in current.connections:
            if connection.name.lower() == choice.lower():
                destination = self.player.position.map.locations[connection.id]
                self.player.position.location = destination
                print(f"\nYou are at {self.player.position.location.name}")
                return

        print("You can't go there.")

    def take(self):
        current_location = self.player.position.location

        item_name = input("Take what? ").strip().lower()

        for item in self.world.items.values():
            if (item.position.location.id == current_location.id and item.name.lower() == item_name):
                print(f"You take the {item.name}.")

                # temporary: remove from location
                item.position.location = None

                return

        print("You don't see that here.")

    def talk(self):
        current_location = self.player.position.location

        npc_name = input("Talk to whom? ").strip().lower()

        for npc in self.world.npcs.values():
            if (npc.position.location.id == current_location.id and npc.name.lower() == npc_name):
                print(f"\n{npc.name}")

                for dialog in npc.dialog.values():
                    print(f"NPC: {dialog.content}")
                    input("(Press Enter to reply)")
                    print(f"You: {dialog.answer}")
                    input("(Press Enter to continue)")
                return

        print("Nobody by that name is here.")

    def look(self):
        current = self.player.position.location

        print(f"\n=== {current.name} ===")

        print("\nItems:")
        found_item = False

        for item in self.world.items.values():
            if (item.position.location is not None and item.position.location.id == current.id):
                print(f"- {item.name}")
                found_item = True

        if not found_item:
            print("- None")

        print("\nPeople:")
        found_npc = False

        for npc in self.world.npcs.values():
            if npc.position.location.id == current.id:
                print(f"- {npc.name}")
                found_npc = True

        if not found_npc:
            print("- Nobody")

        print("\nExits:")
        for connection in current.connections:
            print(f"- {connection.name}")

    def help(self):
        print("Commands:")
        print()
        print("- look")
        print("- go")
        print("- talk")
        print("- take")
        print("- help")
        print("- quit")

    def process_command(self, command):
        command = command.lower()

        if command == "go":
            self.go_player()

        elif command == "look":
            self.look()

        elif command == "take":
            self.take()

        elif command == "talk":
            self.talk()

        elif command == "help":
            self.help()

        elif command == "quit":
            return False

        else:
            print("Unknown command.")

        return True

    def game_loop(self):
        running = True

        while running:
            command = input("> ")
            running = self.process_command(command)

name = input("What's your name? ")

world = World()

game_map = Map(1, "World Map", {})
game_map.parse_map(MAP_FILE)

world.maps[game_map.id] = game_map

world.parse_items(ITEMS_FILE)
world.parse_npcs(NPCS_FILE)
world.parse_journal(JOURNAL_FILE)

player = Player(name, Position(game_map, game_map.locations[1]))

game = Game(name, world, player)

game.game_loop()