import os

MAP_FILE = "map.json"
ITEMS_FILE = "items.json"
NPCS_FILE = "npcs.json"
JOURNAL_FILE = "journal.json"

print(os.path.abspath(MAP_FILE))
print(os.path.exists(MAP_FILE))