from world import *
from player import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WORLD_FILE = os.path.join(BASE_DIR, "data/world.json")
ITEMS_FILE = os.path.join(BASE_DIR, "data/items.json")
NPCS_FILE = os.path.join(BASE_DIR, "data/npcs.json")
JOURNAL_FILE = os.path.join(BASE_DIR, "data/journal.json")

class Game:
    name: str
    world: World
    player: Player

    def __init__(self):
        self.world = World()

        self.world.parse_maps(WORLD_FILE)
        self.world.parse_items(ITEMS_FILE)
        self.world.parse_npcs(NPCS_FILE)
        self.world.parse_journal(JOURNAL_FILE)

        self.player = Player("", Position(self.world.maps[3], self.world.maps[3].locations[1]), [], [self.world.journal[1]], [])

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
            if (item.position.location is not None and item.position.location.id == current_location.id and item.name.lower() == item_name):
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
                if npc not in self.player.talked_to:
                    self.player.talked_to.append(npc)

                for dialog in npc.dialog.values():
                    print(f"NPC: {dialog.content}")
                    input("(Press Enter to reply)")
                    print(f"You: {dialog.answer}")
                    input("(Press Enter to continue)")
                return

        print("Nobody by that name is here.")

    def journal(self):
        for quest in self.player.journal:
            print(f"\n=== {quest.name} ===")

            print(f"\nInit:")

            if quest.init is not None:
                for cond in quest.init:

                    if cond.type is ConditionType.TALK_TO:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.npcs[cond.target_id].name}")

                    elif cond.type is ConditionType.GO_TO:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.maps[cond.target_id].name}")

                    elif cond.type is ConditionType.TAKE_ITEM:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.items[cond.target_id].name}")

                    elif cond.type is ConditionType.DEFEAT_NPC:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.npcs[cond.target_id].name}")

            print(f"\nCompletion:")

            if quest.compl is not None:
                for cond in quest.compl:

                    if cond.type is ConditionType.TALK_TO:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.npcs[cond.target_id].name}")

                    elif cond.type is ConditionType.GO_TO:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.maps[cond.target_id].name}")

                    elif cond.type is ConditionType.TAKE_ITEM:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.items[cond.target_id].name}")

                    elif cond.type is ConditionType.DEFEAT_NPC:
                        print(f"\n- {cond.type.value}")
                        print(f"  {self.world.npcs[cond.target_id].name}")

    def show(self):
        print(f"=== {self.player.position.map.name} ===")
        for location in self.player.position.map.locations.values():
            print(f"- {location.name}")

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
        print("- journal")
        print("- show")
        print("- take")
        print("- start")
        print("- load")
        print("- save")
        print("- help")
        print("- quit")

    def check_condition(self, cond):
        if cond.type == ConditionType.TALK_TO:
            return any(npc.id == cond.target_id for npc in self.player.talked_to)

        elif cond.type == ConditionType.GO_TO:
            return self.player.position.location.id == cond.target_id

        elif cond.type == ConditionType.TAKE_ITEM:
            return any(item.id == cond.target_id for item in self.player.inventory)

        elif cond.type == ConditionType.DEFEAT_NPC:
            # implement combat tracking later
            return False

        return False

    def check_init(self):
        for quest in self.world.journal.values():
            has_quest = quest in self.player.journal

            if not has_quest:
                conditions_met = True

                for cond in quest.init:
                    if not self.check_condition(cond):
                        conditions_met = False

                if conditions_met:
                    self.player.journal.append(quest)
                    print(f"New quest: {quest.name}")

    def check_compl(self):
        for quest in self.player.journal:
            if quest.status != StatusType.COMPLETED:
                conditions_met = True

                for cond in quest.compl:
                    if not self.check_condition(cond):
                        conditions_met = False

                if conditions_met:
                    quest.status = StatusType.COMPLETED
                    print(f"Quest completed: {quest.name}")

    def check_quest(self):
        for quest in self.player.journal:
            if quest.status != StatusType.COMPLETED:
                conditions_met = True

                for cond in quest.compl:
                    if not self.check_condition(cond):
                        conditions_met = False

                if conditions_met:
                    quest.status = StatusType.COMPLETED
                    print(f"Quest completed: {quest.name}")

    def start(self):
        self.player.name = input("What is your name? ")

    def load(self):
        with open("save.json", "r") as f:
            save_data = json.load(f)

        self.player.name = save_data["player_name"]

        map_id = save_data["current_map"]
        location_id = save_data["current_location"]

        self.player.position.map = self.world.maps[map_id]
        self.player.position.location = self.world.maps[map_id].locations[location_id]

        self.player.inventory = [
            self.world.items[item_id]
            for item_id in save_data["inventory"]
        ]

        for item in self.player.inventory:
            self.world.items.pop(item.id)

        self.player.talked_to = [
            self.world.npcs[npc_id]
            for npc_id in save_data["talked_to"]
        ]

        self.player.journal = []

        for q in save_data["quests"]:
            quest = self.world.journal[q["id"]]
            quest.status = StatusType(q["status"])
            self.player.journal.append(quest)

        print("Game loaded")

    def save(self):
        save_data = {
            "player_name": self.player.name,
            "current_map": self.player.position.map.id,
            "current_location": self.player.position.location.id,
            "inventory": [item.id for item in self.player.inventory],
            "talked_to": [npc.id for npc in self.player.talked_to],
            "quests": [
                {
                    "id": quest.id,
                    "status": quest.status.value
                }
                for quest in self.player.journal
            ]
        }

        with open("save.json", "w") as f:
            json.dump(save_data, f, indent=4)

    def process_command(self, command):
        command = command.lower()

        if command == "go":
            self.go_player()

        elif command == "look":
            self.look()

        elif command == "take":
            self.take()

        elif command == "journal":
            self.journal()
            
        elif command == "show":
            self.show()

        elif command == "talk":
            self.talk()

        elif command == "help":
            self.help()

        elif command == "start":
            self.start()
            
        elif command == "load":
            self.load()

        elif command == "save":
            self.save()

        elif command == "quit":
            return False

        else:
            print("Unknown command.")

        return True

    def game_loop(self):
        running = True

        self.help()
        
        while running:
            self.check_init()
            self.check_compl()

            command = input("> ")
            running = self.process_command(command)