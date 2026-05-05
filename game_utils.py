import json
import os

SAVE_FILE = "game_saves.json"

def load_game(player_name):
    if not os.path.exists(SAVE_FILE):
        return None
    
    with open(SAVE_FILE, 'r') as f:
        saves = json.load(f)
    
    return saves.get(player_name)

def save_game(player_name, level, fuel, water, food, technology, location):
    saves = {}
    
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            saves = json.load(f)
    
    saves[player_name] = {
        'level': level,
        'fuel': fuel,
        'water': water,
        'food': food,
        'technology': technology,
        'location': location
    }
    
    with open(SAVE_FILE, 'w') as f:
        json.dump(saves, f, indent=2)

def delete_game(player_name):
    if not os.path.exists(SAVE_FILE):
        return
    
    with open(SAVE_FILE, 'r') as f:
        saves = json.load(f)
    
    if player_name in saves:
        del saves[player_name]
    
    with open(SAVE_FILE, 'w') as f:
        json.dump(saves, f, indent=2)