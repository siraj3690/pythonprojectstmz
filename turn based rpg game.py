import random
import time
import sys
import os
import json
import sqlite3
from datetime import datetime


#  COLORAMA SETUP  (bonus feature — graceful fallback)

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS = True
except ImportError:
    COLORS = False
    class _Dummy:
        def __getattr__(self, _): return ""
    Fore = Back = Style = _Dummy()

def c(text, color=""):
    return f"{color}{text}{Style.RESET_ALL}" if COLORS else text

#  GAME CONSTANTS
GAME_TITLE = "LEGENDS OF THE FORGOTTEN REALM"
VERSION    = "1.0"
SAVE_DIR   = os.path.dirname(os.path.abspath(__file__))


#  WEAPON DATA   (20+ weapons, 7 rarities)

# rarity: (label, dmg_mult, crit_bonus, color)
RARITIES = {
    "Common":     ("Common",     1.0,  0,    Fore.WHITE),
    "Uncommon":   ("Uncommon",   1.1,  2,    Fore.GREEN),
    "Rare":       ("Rare",       1.3,  5,    Fore.BLUE),
    "Super Rare": ("Super Rare", 1.5,  8,    Fore.MAGENTA),
    "Epic":       ("Epic",       1.8, 12,    Fore.YELLOW),
    "Mythical":   ("Mythical",   2.2, 18,    Fore.RED),
    "Legendary":  ("Legendary",  2.8, 25,    Fore.CYAN),
}

WEAPONS = [
    # ── Common ──────────────────────────────────────────────────────────────
    {"name": "Wooden Sword",      "rarity": "Common",     "damage": 8,  "price": 50,   "req_level": 1},
    {"name": "Rusty Axe",         "rarity": "Common",     "damage": 9,  "price": 60,   "req_level": 1},
    {"name": "Training Bow",      "rarity": "Common",     "damage": 7,  "price": 45,   "req_level": 1},
    {"name": "Old Dagger",        "rarity": "Common",     "damage": 6,  "price": 40,   "req_level": 1},
    # ── Uncommon ────────────────────────────────────────────────────────────
    {"name": "Hunter's Bow",      "rarity": "Uncommon",   "damage": 13, "price": 150,  "req_level": 5},
    {"name": "Iron Mace",         "rarity": "Uncommon",   "damage": 14, "price": 160,  "req_level": 5},
    # ── Rare ────────────────────────────────────────────────────────────────
    {"name": "Iron Sword",        "rarity": "Rare",       "damage": 20, "price": 400,  "req_level": 11},
    {"name": "Steel Axe",         "rarity": "Rare",       "damage": 22, "price": 450,  "req_level": 11},
    {"name": "Long Bow",          "rarity": "Rare",       "damage": 18, "price": 380,  "req_level": 11},
    {"name": "Elvish Blade",      "rarity": "Rare",       "damage": 21, "price": 420,  "req_level": 15},
    # ── Super Rare ──────────────────────────────────────────────────────────
    {"name": "Crystal Blade",     "rarity": "Super Rare", "damage": 32, "price": 900,  "req_level": 21},
    {"name": "Shadow Dagger",     "rarity": "Super Rare", "damage": 30, "price": 850,  "req_level": 21},
    {"name": "Lightning Bow",     "rarity": "Super Rare", "damage": 28, "price": 800,  "req_level": 25},
    # ── Epic ────────────────────────────────────────────────────────────────
    {"name": "Flame Sword",       "rarity": "Epic",       "damage": 48, "price": 2000, "req_level": 31},
    {"name": "Ice Spear",         "rarity": "Epic",       "damage": 46, "price": 1900, "req_level": 35},
    {"name": "Thunder Hammer",    "rarity": "Epic",       "damage": 50, "price": 2100, "req_level": 40},
    # ── Mythical ────────────────────────────────────────────────────────────
    {"name": "Phoenix Blade",     "rarity": "Mythical",   "damage": 70, "price": 5000, "req_level": 51},
    {"name": "Demon Slayer",      "rarity": "Mythical",   "damage": 75, "price": 5500, "req_level": 60},
    {"name": "Celestial Staff",   "rarity": "Mythical",   "damage": 68, "price": 4800, "req_level": 55},
    # ── Legendary ───────────────────────────────────────────────────────────
    {"name": "Dragon King's Sword","rarity": "Legendary", "damage": 110,"price": 15000,"req_level": 71},
    {"name": "Blade of Eternity", "rarity": "Legendary",  "damage": 120,"price": 18000,"req_level": 81},
    {"name": "Bow of the Gods",   "rarity": "Legendary",  "damage": 105,"price": 14000,"req_level": 75},
]

# Apply rarity multipliers to weapon damage
for _w in WEAPONS:
    _mult = RARITIES[_w["rarity"]][1]
    _w["damage"] = int(_w["damage"] * _mult)
    _w["crit_bonus"] = RARITIES[_w["rarity"]][2]


#  ARMOR DATA   (12+ sets, 6 rarities)

ARMORS = [
    # ── Common ──────────────────────────────────────────────────────────────
    {"name": "Cloth Tunic",       "rarity": "Common",     "defense": 3,  "hp_bonus": 10,  "mana_bonus": 0,  "crit_res": 0,  "price": 60,   "req_level": 1},
    {"name": "Leather Vest",      "rarity": "Common",     "defense": 5,  "hp_bonus": 15,  "mana_bonus": 0,  "crit_res": 1,  "price": 80,   "req_level": 1},
    # ── Rare ────────────────────────────────────────────────────────────────
    {"name": "Chain Mail",        "rarity": "Rare",       "defense": 12, "hp_bonus": 40,  "mana_bonus": 10, "crit_res": 3,  "price": 500,  "req_level": 11},
    {"name": "Scale Armor",       "rarity": "Rare",       "defense": 14, "hp_bonus": 50,  "mana_bonus": 5,  "crit_res": 4,  "price": 580,  "req_level": 15},
    {"name": "Steel Plate",       "rarity": "Rare",       "defense": 16, "hp_bonus": 60,  "mana_bonus": 0,  "crit_res": 5,  "price": 650,  "req_level": 18},
    # ── Super Rare ──────────────────────────────────────────────────────────
    {"name": "Shadow Cloak",      "rarity": "Super Rare", "defense": 20, "hp_bonus": 70,  "mana_bonus": 30, "crit_res": 6,  "price": 1200, "req_level": 21},
    {"name": "Crystal Shield",    "rarity": "Super Rare", "defense": 25, "hp_bonus": 80,  "mana_bonus": 20, "crit_res": 8,  "price": 1500, "req_level": 26},
    # ── Epic ────────────────────────────────────────────────────────────────
    {"name": "Dragonscale Armor", "rarity": "Epic",       "defense": 38, "hp_bonus": 120, "mana_bonus": 40, "crit_res": 12, "price": 3500, "req_level": 31},
    {"name": "Arcane Robes",      "rarity": "Epic",       "defense": 28, "hp_bonus": 80,  "mana_bonus": 90, "crit_res": 10, "price": 3000, "req_level": 35},
    # ── Mythical ────────────────────────────────────────────────────────────
    {"name": "Phoenix Mail",      "rarity": "Mythical",   "defense": 55, "hp_bonus": 180, "mana_bonus": 60, "crit_res": 18, "price": 8000, "req_level": 51},
    {"name": "Demon Guard",       "rarity": "Mythical",   "defense": 60, "hp_bonus": 200, "mana_bonus": 50, "crit_res": 20, "price": 9000, "req_level": 61},
    # ── Legendary ───────────────────────────────────────────────────────────
    {"name": "Celestial Plate",   "rarity": "Legendary",  "defense": 85, "hp_bonus": 300, "mana_bonus": 100,"crit_res": 30, "price": 20000,"req_level": 71},
    {"name": "Eternal Mantle",    "rarity": "Legendary",  "defense": 90, "hp_bonus": 280, "mana_bonus": 150,"crit_res": 35, "price": 22000,"req_level": 81},
]

# ─────────────────────────────────────────────
#  POTION DATA  (15+ types)
# ─────────────────────────────────────────────
POTIONS = [
    # Health potions
    {"name": "Small Health Potion",   "type": "health", "hp": 50,  "mana": 0,   "buff": None, "price": 30,  "desc": "Restores 50 HP"},
    {"name": "Medium Health Potion",  "type": "health", "hp": 100, "mana": 0,   "buff": None, "price": 60,  "desc": "Restores 100 HP"},
    {"name": "Large Health Potion",   "type": "health", "hp": 250, "mana": 0,   "buff": None, "price": 130, "desc": "Restores 250 HP"},
    {"name": "Giant Health Potion",   "type": "health", "hp": 500, "mana": 0,   "buff": None, "price": 250, "desc": "Restores 500 HP"},
    {"name": "Ultimate Health Potion","type": "health", "hp": 9999,"mana": 0,   "buff": None, "price": 600, "desc": "Restores full HP"},
    # Mana potions
    {"name": "Small Mana Potion",     "type": "mana",   "hp": 0,   "mana": 30,  "buff": None, "price": 25,  "desc": "Restores 30 Mana"},
    {"name": "Medium Mana Potion",    "type": "mana",   "hp": 0,   "mana": 75,  "buff": None, "price": 55,  "desc": "Restores 75 Mana"},
    {"name": "Large Mana Potion",     "type": "mana",   "hp": 0,   "mana": 150, "buff": None, "price": 110, "desc": "Restores 150 Mana"},
    {"name": "Giant Mana Potion",     "type": "mana",   "hp": 0,   "mana": 300, "buff": None, "price": 220, "desc": "Restores 300 Mana"},
    {"name": "Ultimate Mana Potion",  "type": "mana",   "hp": 0,   "mana": 9999,"buff": None, "price": 500, "desc": "Restores full Mana"},
    # Mixed potions
    {"name": "Elixir of Life",        "type": "mixed",  "hp": 100, "mana": 50,  "buff": None, "price": 120, "desc": "Restores 100 HP and 50 Mana"},
    {"name": "Grand Elixir",          "type": "mixed",  "hp": 250, "mana": 100, "buff": None, "price": 280, "desc": "Restores 250 HP and 100 Mana"},
    {"name": "Celestial Elixir",      "type": "mixed",  "hp": 9999,"mana": 9999,"buff": None, "price": 1500,"desc": "Fully restores HP and Mana"},
    # Buff potions (3-turn effect)
    {"name": "Rage Potion",           "type": "buff",   "hp": 0,   "mana": 0,   "buff": ("attack", 20), "price": 200, "desc": "+20 Attack for 3 turns"},
    {"name": "Iron Skin Potion",      "type": "buff",   "hp": 0,   "mana": 0,   "buff": ("defense", 15),"price": 180, "desc": "+15 Defense for 3 turns"},
    {"name": "Swiftness Potion",      "type": "buff",   "hp": 0,   "mana": 0,   "buff": ("crit", 15),   "price": 220, "desc": "+15% Crit Chance for 3 turns"},
]

# ─────────────────────────────────────────────
#  ENEMY DATA  (25+ enemies, grouped by level)
# ─────────────────────────────────────────────
# Format: (name, base_hp, base_atk, base_def, base_exp, base_gold, skill_list)
ENEMY_POOL = {
    # Level  1–10: Village / Forest
    "early": [
        ("Goblin",           40,  8,  2,  20,  10, []),
        ("Wolf",             45, 10,  2,  22,  12, []),
        ("Slime",            35,  7,  1,  15,   8, []),
        ("Zombie",           55,  9,  3,  25,  14, []),
        ("Skeleton",         50, 11,  3,  28,  16, []),
    ],
    # Level 11–20: Forest / Cave
    "mid_early": [
        ("Orc",              80, 15,  5,  50,  30, ["Heavy Smash"]),
        ("Bandit",           75, 17,  4,  55,  35, ["Cheap Shot"]),
        ("Troll",           100, 14,  7,  60,  40, ["Regenerate"]),
        ("Dark Archer",      70, 18,  3,  58,  32, ["Volley"]),
        ("Giant Spider",     85, 13,  6,  52,  28, ["Poison Bite"]),
    ],
    # Level 21–30: Cave / Desert
    "mid": [
        ("Vampire",         130, 24,  8,  90,  60, ["Life Drain"]),
        ("Werewolf",        150, 28,  9, 100,  65, ["Feral Strike"]),
        ("Necromancer",     120, 22, 10,  85,  70, ["Bone Spear","Summon Dead"]),
        ("Ice Golem",       180, 20, 14,  95,  55, ["Frost Nova"]),
        ("Fire Demon",      160, 30,  8, 110,  75, ["Flame Burst"]),
    ],
    # Level 31–40: Ruins / Castle
    "mid_late": [
        ("Sand Wraith",     200, 35, 10, 140,  90, ["Mirage","Sand Storm"]),
        ("Stone Colossus",  250, 30, 18, 150,  80, ["Quake","Rock Smash"]),
        ("Ruin Specter",    180, 38,  8, 160, 100, ["Shadow Bolt"]),
        ("Castle Knight",   220, 32, 15, 145,  95, ["Lance Charge"]),
        ("Dark Paladin",    210, 36, 12, 155, 105, ["Holy Smite","Dark Barrier"]),
    ],
    # Level 41–60: Volcano / Frozen Mountain
    "late": [
        ("Lava Titan",      350, 48, 18, 220, 140, ["Eruption","Magma Fist"]),
        ("Frost Drake",     320, 45, 20, 210, 130, ["Blizzard","Freeze"]),
        ("Inferno Demon",   300, 52, 15, 230, 150, ["Hellfire"]),
        ("Glacial Wraith",  280, 42, 22, 200, 120, ["Ice Lance"]),
        ("Volcano Golem",   400, 40, 25, 240, 145, ["Meltdown"]),
    ],
    # Level 61–100: Sky Temple / Demon Realm
    "endgame": [
        ("Sky Sentinel",    500, 65, 28, 350, 200, ["Divine Strike","Aerial Slam"]),
        ("Void Demon",      550, 72, 25, 400, 220, ["Void Rift","Soul Drain"]),
        ("Chaos Hydra",     600, 68, 22, 420, 240, ["Multi-Bite","Poison Cloud"]),
        ("Shadow Wraith",   480, 78, 20, 380, 210, ["Nightmare","Phase Shift"]),
        ("Demon Lord's Guard",650,75,30, 460, 260, ["Demonic Slash","Dark Pulse"]),
    ],
}

# ─────────────────────────────────────────────
#  BOSS DATA  (one per 10 levels)
# ─────────────────────────────────────────────
BOSSES = [
    {
        "name": "Goblin King",        "level": 10,
        "hp": 500,  "attack": 28, "defense": 8,
        "exp": 500, "gold": 300,
        "skills": ["Royal Slam","Goblin Rally","Battle Cry"],
        "special": "Calls in Goblin reinforcements!",
        "desc": "The cunning leader of the Goblin clan, armed with a stolen crown and fury."
    },
    {
        "name": "Forest Guardian",    "level": 20,
        "hp": 1000, "attack": 42, "defense": 14,
        "exp": 1000, "gold": 600,
        "skills": ["Vine Whip","Nature's Wrath","Rooted"],
        "special": "Heals 80 HP from the forest energy!",
        "desc": "An ancient spirit bound to protect the forest. Powerful and relentless."
    },
    {
        "name": "Ancient Golem",      "level": 30,
        "hp": 1800, "attack": 58, "defense": 22,
        "exp": 1800, "gold": 1000,
        "skills": ["Stone Fist","Earthquake","Iron Skin"],
        "special": "Activates Iron Skin, halving all damage for 1 turn!",
        "desc": "A colossal construct of ancient magic, near-indestructible."
    },
    {
        "name": "Vampire Lord",       "level": 40,
        "hp": 2800, "attack": 72, "defense": 25,
        "exp": 2800, "gold": 1600,
        "skills": ["Blood Drain","Bat Storm","Crimson Curse"],
        "special": "Drains 100 HP from you and heals himself!",
        "desc": "An immortal lord of darkness. He feeds on the living."
    },
    {
        "name": "Dragon Rider",       "level": 50,
        "hp": 4000, "attack": 90, "defense": 30,
        "exp": 4000, "gold": 2400,
        "skills": ["Dragon Breath","Lance Dive","Inferno Wing"],
        "special": "Commands dragon to breathe fire for massive damage!",
        "desc": "A warlord who tamed the mightiest dragon. An unstoppable duo."
    },
    {
        "name": "Demon General",      "level": 60,
        "hp": 5500, "attack": 110,"defense": 38,
        "exp": 5500, "gold": 3200,
        "skills": ["Hellfire Rain","Demonic Charge","Soul Rend"],
        "special": "Unleashes Hellfire Rain on all your senses!",
        "desc": "A general of the demon army, ruthless and battle-hardened."
    },
    {
        "name": "Ice Titan",          "level": 70,
        "hp": 7500, "attack": 132,"defense": 48,
        "exp": 7500, "gold": 4500,
        "skills": ["Glacial Storm","Frozen Prison","Absolute Zero"],
        "special": "Absolute Zero — massive ice damage and stun!",
        "desc": "A towering titan of ancient ice. His breath can freeze mountains."
    },
    {
        "name": "Shadow Emperor",     "level": 80,
        "hp": 10000,"attack": 158,"defense": 58,
        "exp": 10000,"gold": 6000,
        "skills": ["Shadow Nova","Eclipse","Soul Erasure"],
        "special": "Shadow Nova explodes from all sides!",
        "desc": "The emperor of the shadow realm. Reality bends to his will."
    },
    {
        "name": "Celestial Dragon",   "level": 90,
        "hp": 14000,"attack": 185,"defense": 70,
        "exp": 14000,"gold": 8000,
        "skills": ["Star Cannon","Celestial Storm","Divine Breath"],
        "special": "Fires the Star Cannon, dealing colossal celestial damage!",
        "desc": "A dragon born from the stars. Defeating it means you are worthy."
    },
    {
        "name": "Ancient Demon King", "level": 100,
        "hp": 20000,"attack": 220,"defense": 85,
        "exp": 50000,"gold": 15000,
        "skills": ["Apocalypse","Dark Matter","Void Collapse","Demonic Resurrection"],
        "special": "Demonic Resurrection — rises from 1 HP at half life once!",
        "desc": "The source of all darkness. The final evil. The Demon King."
    },
]

# ─────────────────────────────────────────────
#  WORLD MAP  (10 regions)
# ─────────────────────────────────────────────
REGIONS = [
    {"name": "Village",         "min_level": 1,  "max_level": 10,  "boss_level": 10,  "pool": "early",    "emoji": "🏘️"},
    {"name": "Forest",          "min_level": 11, "max_level": 20,  "boss_level": 20,  "pool": "mid_early","emoji": "🌲"},
    {"name": "Cave",            "min_level": 21, "max_level": 30,  "boss_level": 30,  "pool": "mid",      "emoji": "🕳️"},
    {"name": "Desert",          "min_level": 31, "max_level": 40,  "boss_level": 40,  "pool": "mid_late", "emoji": "🏜️"},
    {"name": "Ruins",           "min_level": 41, "max_level": 50,  "boss_level": 50,  "pool": "late",     "emoji": "🏚️"},
    {"name": "Castle",          "min_level": 51, "max_level": 60,  "boss_level": 60,  "pool": "late",     "emoji": "🏰"},
    {"name": "Volcano",         "min_level": 61, "max_level": 70,  "boss_level": 70,  "pool": "endgame",  "emoji": "🌋"},
    {"name": "Frozen Mountain", "min_level": 71, "max_level": 80,  "boss_level": 80,  "pool": "endgame",  "emoji": "🏔️"},
    {"name": "Sky Temple",      "min_level": 81, "max_level": 90,  "boss_level": 90,  "pool": "endgame",  "emoji": "☁️"},
    {"name": "Demon Realm",     "min_level": 91, "max_level": 100, "boss_level": 100, "pool": "endgame",  "emoji": "😈"},
]

# ─────────────────────────────────────────────
#  CLASS DEFINITIONS  (base stats + skills)
# ─────────────────────────────────────────────
CLASSES = {
    "Warrior": {
        "emoji": "⚔️",
        "hp": 150, "mana": 40, "attack": 22, "defense": 14,
        "crit_chance": 8, "crit_damage": 150,
        "desc": "High HP, High Defense. A tank who thrives in close combat.",
        "skills": [
            {"name": "Slash",       "mana": 10, "dmg_mult": 1.5,  "effect": None,          "desc": "A powerful slash dealing 1.5× damage"},
            {"name": "Shield Bash", "mana": 15, "dmg_mult": 1.2,  "effect": "stun",        "desc": "Bash with shield; chance to stun enemy"},
            {"name": "Rage",        "mana": 20, "dmg_mult": 2.0,  "effect": "rage",        "desc": "Enter rage: deal 2× damage this turn"},
            {"name": "Earthquake",  "mana": 30, "dmg_mult": 2.5,  "effect": "aoe",         "desc": "Massive AOE slam, 2.5× damage"},
        ]
    },
    "Mage": {
        "emoji": "🔮",
        "hp": 100, "mana": 120, "attack": 28, "defense": 6,
        "crit_chance": 15, "crit_damage": 175,
        "desc": "High Magic Damage, Low Defense. Uses powerful spells.",
        "skills": [
            {"name": "Fireball",      "mana": 15, "dmg_mult": 1.8,  "effect": "burn",        "desc": "Launches a fireball; may burn the enemy"},
            {"name": "Ice Blast",     "mana": 20, "dmg_mult": 1.6,  "effect": "freeze",      "desc": "Blasts with ice; may freeze the enemy"},
            {"name": "Thunder Strike","mana": 25, "dmg_mult": 2.2,  "effect": "paralyze",    "desc": "Strikes with lightning; may paralyze"},
            {"name": "Meteor",        "mana": 40, "dmg_mult": 3.0,  "effect": "burn",        "desc": "Summons a meteor for massive damage"},
        ]
    },
    "Archer": {
        "emoji": "🏹",
        "hp": 110, "mana": 70, "attack": 20, "defense": 10,
        "crit_chance": 22, "crit_damage": 185,
        "desc": "High Crit Chance, Balanced stats. Excels at picking enemies off.",
        "skills": [
            {"name": "Multi Shot",     "mana": 12, "dmg_mult": 1.3,  "effect": "multi",      "desc": "Fire multiple arrows; 3 hits at 0.5× each"},
            {"name": "Poison Arrow",   "mana": 18, "dmg_mult": 1.2,  "effect": "poison",     "desc": "Poison-tipped arrow; enemy bleeds each turn"},
            {"name": "Explosive Arrow","mana": 25, "dmg_mult": 2.0,  "effect": "burn",       "desc": "Explosive tip; high damage + burn"},
            {"name": "Sniper Shot",    "mana": 35, "dmg_mult": 3.5,  "effect": None,         "desc": "Pinpoint sniper shot; extremely high damage"},
        ]
    },
    "Assassin": {
        "emoji": "🗡️",
        "hp": 90, "mana": 80, "attack": 26, "defense": 7,
        "crit_chance": 30, "crit_damage": 220,
        "desc": "Very High Crit, High Attack, Low Defense. Kills fast or dies fast.",
        "skills": [
            {"name": "Backstab",      "mana": 14, "dmg_mult": 2.0,  "effect": None,         "desc": "Strike from the shadows for 2× damage"},
            {"name": "Smoke Bomb",    "mana": 18, "dmg_mult": 0,    "effect": "blind",      "desc": "Blind the enemy; they miss next turn"},
            {"name": "Shadow Strike", "mana": 25, "dmg_mult": 2.8,  "effect": None,         "desc": "Lightning-fast shadow strike for 2.8× dmg"},
            {"name": "Instant Kill",  "mana": 40, "dmg_mult": 1.0,  "effect": "instakill",  "desc": "5% chance to instantly kill; otherwise 1× atk"},
        ]
    },
}

# Loot rarity drop table
LOOT_TABLE = [
    ("Common",     0.50),
    ("Uncommon",   0.25),
    ("Rare",       0.15),
    ("Super Rare", 0.06),
    ("Epic",       0.03),
    ("Mythical",   0.009),
    ("Legendary",  0.001),
]

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────
def print_slow(text, delay=0.015, color="", newline=True):
    sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if COLORS: sys.stdout.write(Style.RESET_ALL)
    if newline: print()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def draw_bar(current, maximum, length=20, color_full=Fore.GREEN, color_half=Fore.YELLOW, color_low=Fore.RED):
    if maximum == 0: maximum = 1
    pct = current / maximum
    filled = int(length * pct)
    empty = length - filled
    
    color = color_full
    if pct <= 0.25: color = color_low
    elif pct <= 0.5: color = color_half
        
    bar = f"{color}█" * filled + f"{Fore.WHITE}░" * empty + (Style.RESET_ALL if COLORS else "")
    return bar

# ─────────────────────────────────────────────
#  CLASSES
# ─────────────────────────────────────────────
class Character:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.buffs = {"attack": 0, "defense": 0, "crit": 0, "duration": 0}
        self.status = {} # e.g. {"burn": 2, "poison": 3}
        self.is_defending = False

    def get_attack(self):
        return self.attack + self.buffs["attack"]

    def get_defense(self):
        return self.defense + self.buffs["defense"]

    def take_damage(self, damage, source=""):
        actual_defense = self.get_defense()
        if self.is_defending:
            actual_defense *= 2
            damage //= 2
            
        final_damage = max(1, damage - actual_defense // 2)
        self.hp = max(0, self.hp - final_damage)
        return final_damage

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def process_turn_end(self):
        # Handle buffs
        if self.buffs["duration"] > 0:
            self.buffs["duration"] -= 1
            if self.buffs["duration"] == 0:
                self.buffs.update({"attack": 0, "defense": 0, "crit": 0})
                print_slow(f"  > {self.name}'s buffs wore off.", color=Fore.YELLOW)
        
        self.is_defending = False

        # Handle status effects
        status_damage = 0
        if "burn" in self.status and self.status["burn"] > 0:
            dmg = int(self.max_hp * 0.05) + 5
            self.hp -= dmg
            self.status["burn"] -= 1
            print_slow(f"  > {self.name} takes {dmg} burn damage!", color=Fore.RED)
            status_damage += dmg
            
        if "poison" in self.status and self.status["poison"] > 0:
            dmg = int(self.max_hp * 0.03) + 3
            self.hp -= dmg
            self.status["poison"] -= 1
            print_slow(f"  > {self.name} takes {dmg} poison damage!", color=Fore.GREEN)
            status_damage += dmg
            
        self.hp = max(0, self.hp)
        return status_damage

    def draw_hp_bar(self):
        return f"HP: {draw_bar(self.hp, self.max_hp)} {self.hp}/{self.max_hp}"

class Player(Character):
    def __init__(self, name, p_class):
        base = CLASSES[p_class]
        super().__init__(name, base["hp"], base["attack"], base["defense"])
        self.p_class = p_class
        self.emoji = base["emoji"]
        self.max_mana = base["mana"]
        self.mana = self.max_mana
        
        self.level = 1
        self.exp = 0
        self.exp_needed = 50
        self.gold = 100
        
        self.base_crit = base["crit_chance"]
        self.crit_damage = base["crit_damage"]
        
        self.inventory = [] 
        self.equipped_weapon = None
        self.equipped_armor = None
        
        # Give starting gear based on common tier 1 items
        starter_pots = [p for p in POTIONS if p["name"] in ["Small Health Potion", "Small Health Potion", "Small Mana Potion"]]
        self.inventory.extend(starter_pots)
        
        self.skills = [base["skills"][0]] # start with 1 skill
        
        self.bosses_defeated = []
        self.enemies_defeated = 0
        self.start_time = time.time()
        self.total_playtime = 0

    def draw_mp_bar(self):
        return f"MP: {draw_bar(self.mana, self.max_mana, color_full=Fore.CYAN, color_half=Fore.BLUE, color_low=Fore.MAGENTA)} {self.mana}/{self.max_mana}"

    def get_crit_chance(self):
        w_crit = self.equipped_weapon["crit_bonus"] if self.equipped_weapon else 0
        return self.base_crit + w_crit + self.buffs["crit"]

    def gain_exp(self, amount):
        self.exp += amount
        print_slow(f"  + Received {amount} EXP!", color=Fore.CYAN)
        while self.exp >= self.exp_needed and self.level < 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_needed
        self.exp_needed = int(50 * (1.5 ** (self.level - 1)))
        
        # Stat boosts
        self.max_hp += 15
        self.hp = self.max_hp
        self.max_mana += 10
        self.mana = self.max_mana
        self.attack += 4
        self.defense += 2
        
        print_slow(f"\n{Style.BRIGHT}{Fore.YELLOW}*** LEVEL UP! ***")
        print_slow(f"{self.name} is now Level {self.level}!")
        print_slow(f"Stats increased! HP and Mana restored.")
        
        # Skill unlock every 5 levels
        base_skills = CLASSES[self.p_class]["skills"]
        skill_idx = self.level // 5
        if self.level % 5 == 0 and skill_idx < len(base_skills):
            new_skill = base_skills[skill_idx]
            if new_skill not in self.skills:
                self.skills.append(new_skill)
                print_slow(f"{Fore.MAGENTA}Unlocked new skill: {new_skill['name']}!{Style.RESET_ALL}")

    def to_dict(self):
        self.total_playtime += (time.time() - self.start_time)
        self.start_time = time.time()
        return {
            "name": self.name,
            "p_class": self.p_class,
            "level": self.level,
            "exp": self.exp,
            "exp_needed": self.exp_needed,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "attack": self.attack,
            "defense": self.defense,
            "gold": self.gold,
            "inventory": self.inventory,
            "equipped_weapon": self.equipped_weapon,
            "equipped_armor": self.equipped_armor,
            "skills": self.skills,
            "bosses_defeated": self.bosses_defeated,
            "enemies_defeated": self.enemies_defeated,
            "playtime": self.total_playtime
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data["name"], data["p_class"])
        for k, v in data.items():
            if k == "playtime":
                p.total_playtime = v
            elif hasattr(p, k):
                setattr(p, k, v)
        p.start_time = time.time()
        return p

class Enemy(Character):
    def __init__(self, name, hp, attack, defense, exp, gold, skills):
        super().__init__(name, hp, attack, defense)
        self.exp_reward = exp
        self.gold_reward = gold
        self.skills = skills

class Boss(Enemy):
    def __init__(self, data, player_level):
        super().__init__(data["name"], data["hp"], data["attack"], data["defense"], data["exp"], data["gold"], data["skills"])
        self.special = data["special"]
        self.desc = data["desc"]
        self.turn_counter = 0
        
        # Scale slightly to player level if over leveled
        if player_level > data["level"]:
            diff = player_level - data["level"]
            self.max_hp += diff * 50
            self.hp = self.max_hp
            self.attack += diff * 5
            self.defense += diff * 3

# ─────────────────────────────────────────────
#  COMBAT SYSTEM
# ─────────────────────────────────────────────
def battle(player, enemy, is_boss=False):
    clear_screen()
    print_slow(f"\n{Style.BRIGHT}{Fore.RED}>>> BATTLE START <<<")
    print_slow(f"A wild {enemy.name} appeared!" if not is_boss else f"{Fore.MAGENTA}BOSS BATTLE: {enemy.name} approaches!")
    
    turn = 1
    while player.hp > 0 and enemy.hp > 0:
        print(f"\n{Style.BRIGHT}--- Turn {turn} ---{Style.RESET_ALL}")
        print(player.draw_hp_bar())
        print(player.draw_mp_bar())
        print(f"Enemy {enemy.name} {enemy.draw_hp_bar()}")
        
        # Player Turn
        print("\n[1] Attack   [2] Skills   [3] Heal      [4] Potion")
        print("[5] Defend   [6] Items    [7] Stats     [8] Run")
        
        action = input("Choose action: ").strip()
        
        while action not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            action = input("Invalid choice! Choose [1-8]: ").strip()
            
        if action == "7":
            # View stats, doesn't take a turn
            print(f"\n{Style.BRIGHT}--- Player Stats ---{Style.RESET_ALL}")
            print(f"Level: {player.level} ({player.exp}/{player.exp_needed} EXP)")
            print(f"Attack: {player.get_attack()} | Defense: {player.get_defense()} | Crit: {player.get_crit_chance()}%")
            print(f"Weapon: {player.equipped_weapon['name'] if player.equipped_weapon else 'None'}")
            print(f"Armor: {player.equipped_armor['name'] if player.equipped_armor else 'None'}")
            continue
            
        elif action == "6":
            # Inventory (can't equip in battle, just view)
            print("Inventory:")
            for item in player.inventory:
                print(f"- {item['name']} ({item.get('rarity', 'Item')})")
            print("You cannot equip items during battle.")
            continue
            
        elif action == "8":
            if is_boss:
                print_slow("You cannot run from a boss!", color=Fore.RED)
                continue
            run_chance = random.random()
            if run_chance > 0.5:
                print_slow("You successfully ran away!", color=Fore.YELLOW)
                return False
            else:
                print_slow("You failed to run away!", color=Fore.RED)
                
        elif action == "5":
            player.is_defending = True
            print_slow(f"{player.name} is defending! Damage taken next turn will be reduced.")
            
        elif action == "4":
            potions = [p for p in player.inventory if "hp" in p or "buff" in p]
            if not potions:
                print_slow("You have no potions!", color=Fore.RED)
                continue
            print("Select a potion to use:")
            for idx, p in enumerate(potions):
                print(f"[{idx+1}] {p['name']} ({p.get('desc', '')})")
            print("[0] Cancel")
            try:
                p_choice = int(input("Choice: "))
                if p_choice == 0: continue
                if 1 <= p_choice <= len(potions):
                    potion = potions[p_choice-1]
                    # Apply potion
                    if potion.get("hp", 0) > 0:
                        player.heal(potion["hp"])
                        print_slow(f"Healed for {potion['hp']} HP!", color=Fore.GREEN)
                    if potion.get("mana", 0) > 0:
                        player.mana = min(player.max_mana, player.mana + potion["mana"])
                        print_slow(f"Restored {potion['mana']} Mana!", color=Fore.CYAN)
                    if potion.get("buff"):
                        b_type, val = potion["buff"]
                        player.buffs[b_type] += val
                        player.buffs["duration"] = 3
                        print_slow(f"Gained {b_type} +{val} for 3 turns!", color=Fore.YELLOW)
                    player.inventory.remove(potion)
                else:
                    print("Invalid choice.")
                    continue
            except ValueError:
                continue
                
        elif action == "3":
            if player.mana >= 20:
                player.mana -= 20
                heal_amt = int(player.max_hp * 0.3)
                player.heal(heal_amt)
                print_slow(f"{player.name} used basic heal and recovered {heal_amt} HP!", color=Fore.GREEN)
            else:
                print_slow("Not enough mana (Need 20)!", color=Fore.RED)
                continue
                
        elif action == "2":
            if not player.skills:
                print_slow("You have no skills!", color=Fore.RED)
                continue
            print("Select a skill:")
            for idx, s in enumerate(player.skills):
                print(f"[{idx+1}] {s['name']} (Mana: {s['mana']}) - {s['desc']}")
            print("[0] Cancel")
            try:
                s_choice = int(input("Choice: "))
                if s_choice == 0: continue
                if 1 <= s_choice <= len(player.skills):
                    skill = player.skills[s_choice-1]
                    if player.mana < skill["mana"]:
                        print_slow("Not enough mana!", color=Fore.RED)
                        continue
                    else:
                        player.mana -= skill["mana"]
                        dmg = int(player.get_attack() * skill["dmg_mult"])
                        
                        is_crit = random.randint(1, 100) <= player.get_crit_chance()
                        if is_crit:
                            dmg = int(dmg * (player.crit_damage / 100.0))
                            print_slow("CRITICAL STRIKE!", color=Fore.YELLOW)
                        
                        dealt = enemy.take_damage(dmg)
                        print_slow(f"{player.name} used {skill['name']}! Dealt {dealt} damage to {enemy.name}.")
                        
                        # Apply effect
                        eff = skill["effect"]
                        if eff == "burn":
                            enemy.status["burn"] = 3
                            print_slow(f"{enemy.name} is burning!", color=Fore.RED)
                        elif eff == "poison":
                            enemy.status["poison"] = 3
                            print_slow(f"{enemy.name} is poisoned!", color=Fore.GREEN)
                        elif eff == "stun":
                            if random.random() < 0.5:
                                enemy.status["stun"] = 1
                                print_slow(f"{enemy.name} is stunned!", color=Fore.YELLOW)
                        elif eff == "rage":
                            player.buffs["attack"] += int(player.attack * 0.5)
                            player.buffs["duration"] = 2
                        elif eff == "blind":
                            enemy.status["blind"] = 1
                            print_slow(f"{enemy.name} is blinded!", color=Fore.MAGENTA)
                        elif eff == "instakill":
                            if random.random() < 0.05:
                                print_slow("INSTANT KILL PURGE!", color=Fore.RED)
                                enemy.hp = 0
                            
                else:
                    print("Invalid choice.")
                    continue
            except ValueError:
                continue

        elif action == "1":
            # Attack
            dmg = player.get_attack()
            is_crit = random.randint(1, 100) <= player.get_crit_chance()
            if is_crit:
                dmg = int(dmg * (player.crit_damage / 100.0))
                print_slow("CRITICAL HIT!", color=Fore.YELLOW)
            
            dealt = enemy.take_damage(dmg)
            print_slow(f"{player.name} slashed {enemy.name} for {dealt} damage!")

        if enemy.hp <= 0:
            break

        # Enemy Turn
        time.sleep(0.5)
        print(f"\n{Style.BRIGHT}--- Enemy Turn ---{Style.RESET_ALL}")
        
        if "stun" in enemy.status and enemy.status["stun"] > 0:
            print_slow(f"{enemy.name} is stunned and cannot move!")
            enemy.status["stun"] -= 1
        elif "blind" in enemy.status and enemy.status["blind"] > 0:
            print_slow(f"{enemy.name} is blinded and missed their attack!")
            enemy.status["blind"] -= 1
        else:
            # Enemy AI logic
            e_action = random.random()
            
            if is_boss and enemy.turn_counter % 3 == 2:
                # Boss special every 3 turns
                print_slow(f"{enemy.name} uses Special: {enemy.special}", color=Fore.MAGENTA)
                # Hardcode special effects
                if "Heals" in enemy.special:
                    enemy.hp = min(enemy.max_hp, enemy.hp + 80)
                elif "Iron Skin" in enemy.special:
                    enemy.is_defending = True
                elif "Drains 100" in enemy.special:
                    dealt = player.take_damage(100)
                    enemy.heal(dealt)
                else:
                    dmg = int(enemy.get_attack() * 1.5)
                    dealt = player.take_damage(dmg)
                    print_slow(f"{enemy.name} dealt {dealt} massive damage!", color=Fore.RED)
            
            elif e_action > 0.6 and enemy.skills:
                # Use skill
                s_name = random.choice(enemy.skills)
                dmg = int(enemy.get_attack() * 1.2)
                dealt = player.take_damage(dmg)
                print_slow(f"{enemy.name} uses {s_name}! Dealt {dealt} damage to you.", color=Fore.RED)
            elif is_boss and e_action < 0.2 and enemy.hp < enemy.max_hp * 0.3:
                # Boss heal
                heal_amt = int(enemy.max_hp * 0.1)
                enemy.heal(heal_amt)
                print_slow(f"{enemy.name} healed for {heal_amt} HP!", color=Fore.GREEN)
            else:
                # Normal attack
                dmg = enemy.get_attack()
                dealt = player.take_damage(dmg)
                print_slow(f"{enemy.name} attacks! Dealt {dealt} damage to you.")
                
        if is_boss: enemy.turn_counter += 1

        # Turn End Processing
        player_s_dmg = player.process_turn_end()
        enemy_s_dmg = enemy.process_turn_end()
        
        turn += 1
        time.sleep(1)

    # End of battle
    if player.hp <= 0:
        print_slow(f"\n{Style.BRIGHT}{Fore.RED}YOU DIED!")
        return False
    else:
        print_slow(f"\n{Style.BRIGHT}{Fore.GREEN}VICTORY!")
        player.gain_exp(enemy.exp_reward)
        player.gold += enemy.gold_reward
        player.enemies_defeated += 1
        print_slow(f"Found {enemy.gold_reward} Gold!", color=Fore.YELLOW)
        
        if is_boss:
            player.bosses_defeated.append(enemy.name)
            
        # Loot Drop (30% chance)
        if random.random() < 0.3 or is_boss:
            roll = random.random()
            dropped_rarity = "Common"
            accum = 0
            for rarity, prob in LOOT_TABLE:
                accum += prob
                if roll < accum:
                    dropped_rarity = rarity
                    break
            
            # Select random item of this rarity (Weapon, Armor, or Potion)
            pool = []
            pool.extend([w for w in WEAPONS if w["rarity"] == dropped_rarity])
            pool.extend([a for a in ARMORS if a["rarity"] == dropped_rarity])
            # If no gear in this rarity (e.g. Common potions)
            if not pool: pool.extend([p for p in POTIONS]) 
            
            if pool:
                drop = random.choice(pool)
                print_slow(f"Enemy dropped: {drop['name']}!", color=Fore.MAGENTA)
                player.inventory.append(drop)
        return True

# ─────────────────────────────────────────────
#  INVENTORY, SHOP, SAVE/LOAD
# ─────────────────────────────────────────────
def manage_inventory(player):
    while True:
        clear_screen()
        print_slow(f"\n{Style.BRIGHT}{Fore.CYAN}=== INVENTORY ===")
        print(f"Gold: {player.gold}")
        print(f"Equipped Weapon: {player.equipped_weapon['name'] if player.equipped_weapon else 'None'}")
        print(f"Equipped Armor: {player.equipped_armor['name'] if player.equipped_armor else 'None'}")
        print("\nItems:")
        if not player.inventory:
            print("  (Empty)")
        else:
            for i, item in enumerate(player.inventory):
                print(f"[{i+1}] {item['name']} ({item.get('rarity', 'Item')})")
        print("\n[1] Equip Item   [2] Use Potion   [3] Drop Item   [0] Back")
        
        choice = input("Choice: ").strip().lower()
        if choice == '0' or choice == 'esc' or choice == '':
            break
        elif choice == '1':
            try:
                idx = int(input("Item number to equip: ")) - 1
                if 0 <= idx < len(player.inventory):
                    item = player.inventory[idx]
                    if "damage" in item:
                        if player.level >= item["req_level"]:
                            if player.equipped_weapon:
                                player.inventory.append(player.equipped_weapon)
                            player.equipped_weapon = item
                            player.inventory.pop(idx)
                            print_slow(f"Equipped {item['name']}!", color=Fore.GREEN)
                        else:
                            print_slow(f"Level {item['req_level']} required!", color=Fore.RED)
                    elif "defense" in item:
                        if player.level >= item["req_level"]:
                            if player.equipped_armor:
                                player.inventory.append(player.equipped_armor)
                                player.max_hp -= player.equipped_armor["hp_bonus"]
                                player.max_mana -= player.equipped_armor["mana_bonus"]
                            player.equipped_armor = item
                            player.max_hp += item["hp_bonus"] 
                            player.max_mana += item["mana_bonus"]
                            player.inventory.pop(idx)
                            print_slow(f"Equipped {item['name']}!", color=Fore.GREEN)
                        else:
                            print_slow(f"Level {item['req_level']} required!", color=Fore.RED)
                    else:
                        print_slow("Cannot equip this item!", color=Fore.RED)
            except ValueError: pass
            time.sleep(1)
        elif choice == '2':
            print("Potions can be used in battle.")
            time.sleep(1)
        elif choice == '3':
            try:
                idx = int(input("Item number to drop: ")) - 1
                if 0 <= idx < len(player.inventory):
                    item = player.inventory.pop(idx)
                    print_slow(f"Dropped {item['name']}.", color=Fore.YELLOW)
            except ValueError: pass
            time.sleep(1)

def shop(player):
    while True:
        clear_screen()
        print_slow(f"\n{Style.BRIGHT}{Fore.YELLOW}=== SHOP ===")
        print(f"Your Gold: {player.gold}")
        print("\n[1] Buy Weapons")
        print("[2] Buy Armor")
        print("[3] Buy Potions")
        print("[4] Sell Items")
        print("[5] Leave")
        
        choice = input("Choice: ").strip()
        if choice == "5":
            break
        elif choice == "1":
            # Buy Weapons - generate 5 random weapons near player level
            stock = [w for w in WEAPONS if w["req_level"] <= player.level + 5]
            if len(stock) > 5: stock = random.sample(stock, 5)
            print("\n--- Weapons for Sale ---")
            for i, w in enumerate(stock):
                print(f"[{i+1}] {w['name']} (Dmg: {w['damage']}, Rarity: {w['rarity']}) - {w['price']} Gold")
            print("[0] Cancel")
            try:
                c = int(input("Buy: "))
                if 1 <= c <= len(stock):
                    item = stock[c-1]
                    if player.gold >= item["price"]:
                        player.gold -= item["price"]
                        player.inventory.append(item.copy())
                        print_slow(f"Bought {item['name']}!", color=Fore.GREEN)
                    else:
                        print_slow("Not enough gold!", color=Fore.RED)
            except ValueError: pass
            time.sleep(1)
        
        elif choice == "2":
            stock = [a for a in ARMORS if a["req_level"] <= player.level + 5]
            if len(stock) > 5: stock = random.sample(stock, 5)
            print("\n--- Armor for Sale ---")
            for i, a in enumerate(stock):
                print(f"[{i+1}] {a['name']} (Def: {a['defense']}, HP+: {a['hp_bonus']}) - {a['price']} Gold")
            print("[0] Cancel")
            try:
                c = int(input("Buy: "))
                if 1 <= c <= len(stock):
                    item = stock[c-1]
                    if player.gold >= item["price"]:
                        player.gold -= item["price"]
                        player.inventory.append(item.copy())
                        print_slow(f"Bought {item['name']}!", color=Fore.GREEN)
                    else:
                        print_slow("Not enough gold!", color=Fore.RED)
            except ValueError: pass
            time.sleep(1)
            
        elif choice == "3":
            stock = random.sample(POTIONS, min(5, len(POTIONS)))
            print("\n--- Potions for Sale ---")
            for i, p in enumerate(stock):
                print(f"[{i+1}] {p['name']} - {p['price']} Gold ({p['desc']})")
            print("[0] Cancel")
            try:
                c = int(input("Buy: "))
                if 1 <= c <= len(stock):
                    item = stock[c-1]
                    if player.gold >= item["price"]:
                        player.gold -= item["price"]
                        player.inventory.append(item.copy())
                        print_slow(f"Bought {item['name']}!", color=Fore.GREEN)
                    else:
                        print_slow("Not enough gold!", color=Fore.RED)
            except ValueError: pass
            time.sleep(1)
            
        elif choice == "4":
            print("\n--- Sell Items ---")
            if not player.inventory:
                print("Inventory empty.")
            else:
                for i, item in enumerate(player.inventory):
                    sell_price = item.get("price", 10) // 2
                    print(f"[{i+1}] {item['name']} - Sell for {sell_price} Gold")
                print("[0] Cancel")
                try:
                    c = int(input("Sell: "))
                    if 1 <= c <= len(player.inventory):
                        item = player.inventory.pop(c-1)
                        sell_price = item.get("price", 10) // 2
                        player.gold += sell_price
                        print_slow(f"Sold {item['name']} for {sell_price} Gold!", color=Fore.GREEN)
                except ValueError: pass
            time.sleep(1)

def get_db_connection():
    db_path = os.path.join(SAVE_DIR, "userdata.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS saves (slot INTEGER PRIMARY KEY, data TEXT)")
    return conn

def migrate_json_to_sqlite():
    for slot in range(4): # 0 (autosave), 1, 2, 3
        filepath = os.path.join(SAVE_DIR, f"save_slot_{slot}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                with get_db_connection() as conn:
                    conn.execute("INSERT OR IGNORE INTO saves (slot, data) VALUES (?, ?)", (slot, json.dumps(data)))
                os.rename(filepath, filepath + ".bak")
                print(f"Migrated Slot {slot} to userdata.db")
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to migrate Slot {slot}! Error: {e}")

def save_game(player, slot):
    try:
        data_str = json.dumps(player.to_dict())
        with get_db_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO saves (slot, data) VALUES (?, ?)", (slot, data_str))
        print_slow(f"Game saved to Slot {slot}!", color=Fore.GREEN)
    except Exception as e:
        print_slow(f"Failed to save! Error: {e}", color=Fore.RED)

def load_game(slot):
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT data FROM saves WHERE slot = ?", (slot,))
            row = cursor.fetchone()
            
        if not row:
            print_slow(f"Save Slot {slot} is empty!", color=Fore.RED)
            return None
            
        data = json.loads(row[0])
        player = Player.from_dict(data)
        print_slow(f"Game loaded from Slot {slot}!", color=Fore.GREEN)
        return player
    except Exception as e:
        print_slow(f"Failed to load! Error: {e}", color=Fore.RED)
        return None

# ─────────────────────────────────────────────
#  MAIN LOOP & WORLD MAP
# ─────────────────────────────────────────────
def town_menu(player, region):
    while True:
        clear_screen()
        print_slow(f"\n{Style.BRIGHT}{Fore.YELLOW}=== {region['emoji']} {region['name']} ===")
        print(player.draw_hp_bar())
        print(player.draw_mp_bar())
        print(f"Level: {player.level} | Gold: {player.gold}")
        
        print("\n[1] Explore (Battle)")
        print("[2] Boss Battle")
        print("[3] View Shop")
        print("[4] Inventory")
        print("[5] Rest (Heal completely - 50 Gold)")
        print("[6] View Stats")
        print("[7] Save Game")
        print("[0] Return to World Map")
        
        choice = input("Choice: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            pool_name = region["pool"]
            enemy_data = random.choice(ENEMY_POOL[pool_name])
            enemy = Enemy(enemy_data[0], enemy_data[1], enemy_data[2], enemy_data[3], enemy_data[4], enemy_data[5], enemy_data[6])
            
            # Scale slightly based on player level range for region
            scaling = (player.level - region["min_level"]) / 10.0
            if scaling > 0:
                enemy.max_hp += int(enemy.max_hp * scaling * 0.5)
                enemy.hp = enemy.max_hp
                enemy.attack += int(enemy.attack * scaling * 0.5)
                enemy.defense += int(enemy.defense * scaling * 0.5)
                
            battle(player, enemy)
            # Autosave option
            if player.hp > 0: save_game(player, 0) # Auto slot
        elif choice == "2":
            # Check boss requirement
            if player.level < region["boss_level"]:
                print_slow(f"You must be Level {region['boss_level']} to face the boss!", color=Fore.RED)
                time.sleep(1.5)
                continue
            boss_data = next((b for b in BOSSES if b["level"] == region["boss_level"]), None)
            if not boss_data:
                print_slow("No boss available here.", color=Fore.RED)
                time.sleep(1)
                continue
            if boss_data["name"] in player.bosses_defeated:
                print_slow("You already defeated this boss, but they have returned for a rematch!", color=Fore.YELLOW)
                time.sleep(1)
                
            boss = Boss(boss_data, player.level)
            won = battle(player, boss, is_boss=True)
            if won:
                print_slow(f"You defeated the {boss.name}! You can now progress to the next region.")
                save_game(player, 0)
                if boss.name == "Ancient Demon King":
                    print_slow("\n" + "="*40, color=Fore.YELLOW)
                    print_slow(f"🎉 CONGRATULATIONS {player.name}! You beat the game! 🎉", color=Fore.CYAN)
                    print_slow("="*40, color=Fore.YELLOW)
                    sys.exit(0)
            time.sleep(2)
        elif choice == "3":
            shop(player)
        elif choice == "4":
            manage_inventory(player)
        elif choice == "5":
            if player.gold >= 50:
                player.gold -= 50
                player.hp = player.max_hp
                player.mana = player.max_mana
                print_slow("You rested well. HP and Mana fully restored!", color=Fore.GREEN)
            else:
                print_slow("Not enough gold to rest (Need 50).", color=Fore.RED)
            time.sleep(1.5)
        elif choice == "6":
            print(f"\n{Style.BRIGHT}--- Player Stats ---{Style.RESET_ALL}")
            print(f"Name: {player.name} ({player.p_class} {player.emoji})")
            print(f"Level: {player.level} | EXP: {player.exp}/{player.exp_needed}")
            print(f"Attack: {player.get_attack()} | Defense: {player.get_defense()} | Crit: {player.get_crit_chance()}%")
            print(f"HP: {player.hp}/{player.max_hp} | Mana: {player.mana}/{player.max_mana}")
            w_name = player.equipped_weapon['name'] if player.equipped_weapon else 'None'
            a_name = player.equipped_armor['name'] if player.equipped_armor else 'None'
            print(f"Weapon: {w_name} | Armor: {a_name}")
            print(f"Bosses Defeated: {len(player.bosses_defeated)}/10")
            input("Press Enter to continue...")
        elif choice == "7":
            print("Select Save Slot (1-3):")
            try:
                slot = int(input("> "))
                if 1 <= slot <= 3:
                    save_game(player, slot)
            except: pass
            time.sleep(1)
            
        if player.hp <= 0:
            break

def world_map(player):
    while True:
        if player.hp <= 0:
            print_slow("\nGAME OVER", color=Fore.RED)
            return
            
        clear_screen()
        print_slow(f"\n{Style.BRIGHT}{Fore.CYAN}=== WORLD MAP ===")
        print("Select a region to travel to:")
        
        highest_unlocked = 0
        for b in player.bosses_defeated:
            for i, r in enumerate(REGIONS):
                if b == next((boss["name"] for boss in BOSSES if boss["level"] == r["boss_level"]), ""):
                    highest_unlocked = max(highest_unlocked, i + 1)
        
        highest_unlocked = min(9, highest_unlocked) # Max index 9
        
        for i, region in enumerate(REGIONS):
            if i <= highest_unlocked:
                print(f"[{i+1}] {region['emoji']} {region['name']} (Lv {region['min_level']}-{region['max_level']})")
            else:
                print(f"[{i+1}] 🔒 Unknown Region (Defeat previous boss to unlock)")
                
        print("\n[0] Save and Quit to Main Menu")
        choice = input("Choice: ").strip()
        
        if choice == "0":
            save_game(player, 0)
            break
            
        try:
            c = int(choice) - 1
            if 0 <= c <= highest_unlocked:
                town_menu(player, REGIONS[c])
            elif c > highest_unlocked and c < 10:
                print_slow("This region is locked!", color=Fore.RED)
                time.sleep(1)
        except: pass

def main():
    migrate_json_to_sqlite()
    clear_screen()
    while True:
        clear_screen()
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("=====================================================")
        print(f"           {GAME_TITLE} (v{VERSION})")
        print("=====================================================")
        print(Style.RESET_ALL)
        print("[1] New Game")
        print("[2] Continue (Load Game)")
        print("[3] Instructions")
        print("[4] Exit")
        
        choice = input("> ").strip()
        
        if choice == "4":
            print_slow("Farewell, hero.")
            sys.exit(0)
            
        elif choice == "3":
            print("\n--- Instructions ---")
            print("1. Choose a class (Warrior, Mage, Archer, Assassin).")
            print("2. Explore regions to fight enemies, gain EXP and Gold.")
            print("3. Level up to get stronger and unlock new skills.")
            print("4. Use Gold in the Shop to buy Weapons, Armor, and Potions.")
            print("5. Defeat the Boss in each region to unlock the next.")
            print("6. Save your progress often (slot 0 is Autosave).")
            print("7. Defeat the Ancient Demon King at Level 100 to win!")
            input("\nPress Enter to return...")
            
        elif choice == "2":
            print("\nLoad from slot [1-3] or [0] for Autosave:")
            try:
                slot = int(input("> "))
                player = load_game(slot)
                if player:
                    world_map(player)
                else:
                    time.sleep(1)
            except: pass
            
        elif choice == "1":
            print("\nEnter your hero's name:")
            name = input("> ").strip()
            if not name: name = "Hero"
            
            print("\nChoose your class:")
            for i, (c_name, c_data) in enumerate(CLASSES.items()):
                print(f"[{i+1}] {c_name} {c_data['emoji']} - {c_data['desc']}")
                
            c_choice = 0
            while c_choice not in [1, 2, 3, 4]:
                try:
                    c_choice = int(input("> "))
                except: pass
                
            classes_list = list(CLASSES.keys())
            player_class = classes_list[c_choice-1]
            
            player = Player(name, player_class)
            print_slow(f"\nWelcome to the Forgotten Realm, {player.name} the {player_class}!", color=Fore.GREEN)
            time.sleep(1.5)
            world_map(player)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame aborted by user.")
        sys.exit(0)


