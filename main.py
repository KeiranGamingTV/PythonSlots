import time
import random
import os
import json
from datetime import datetime

# --- Configuration ---
SYMBOLS = {
    "CHERRY": "o^o",
    "LEMON": "(`_`)",
    "ORANGE": "( * )",
    "GRAPE": "`%o",
    "BELL": "/_\\",
    "BAR": "=[BAR]=",
    "777": "[[ 7 ]]",
    "DIAMOND": "~ V ~"
}

ITEM_KEYS = list(SYMBOLS.keys())
PAYOUT_MULTIPLIERS = {
    "CHERRY": 5, "LEMON": 10, "ORANGE": 15, "GRAPE": 20,
    "BELL": 50, "BAR": 100, "777": 500, "DIAMOND": 1000
}

WINDOW_HEIGHT = 7
SAVE_FILE = "slots_data.json"
CONTENT_WIDTH = 52  
CELL_WIDTH = 16

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_data():
    today = datetime.now().strftime("%Y-%m-%d")
    default = {
        "spent": 0, "earned": 0, "high_score": 0, "streak": 0, 
        "level": 1, "xp": 0, 
        "challenge_type": "LEMON", 
        "challenge_goal": 5, 
        "challenge_progress": 0,
        "challenge_completed": False,
        "last_date": today
    }
    
    if not os.path.exists(SAVE_FILE): 
        return default
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            # Ensure all keys exist
            for key, val in default.items():
                if key not in data: data[key] = val
            
            # --- Daily Reset Logic ---
            if data["last_date"] != today:
                data["last_date"] = today
                data["challenge_type"] = random.choice(["CHERRY", "LEMON", "ORANGE", "GRAPE", "BELL"])
                data["challenge_goal"] = random.randint(5, 15)
                data["challenge_progress"] = 0
                data["challenge_completed"] = False
            
            return data
    except: 
        return default

def save_data(stats):
    if stats["earned"] > stats["high_score"]:
        stats["high_score"] = stats["earned"]
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(stats, f, indent=4)
    except: pass

def get_xp_for_next_level(level):
    return int(100 * (level ** 1.5))

def level_up_animation(new_level):
    for _ in range(3):
        clear_screen()
        print("\n" * 5)
        print("*" * 58)
        print(f"** {'!!! LEVEL UP !!!':^52} **")
        print(f"** {'You reached Level ' + str(new_level):^52} **")
        print(f"** {'Winnings Bonus Increased!':^52} **")
        print("*" * 58)
        time.sleep(0.4)
        clear_screen()
        time.sleep(0.2)
    input("\nPress ENTER to claim your reward and continue...")

def add_xp(stats, amount):
    stats["xp"] += amount
    needed = get_xp_for_next_level(stats["level"])
    while stats["xp"] >= needed:
        stats["xp"] -= needed
        stats["level"] += 1
        level_up_animation(stats["level"])
        needed = get_xp_for_next_level(stats["level"])

def get_classic_cell(key, is_win_row):
    symbol = SYMBOLS[key]
    raw_text = f"> {symbol} <" if is_win_row else f"  {symbol}  "
    return f"{raw_text:^{CELL_WIDTH}}"

def draw_machine(reels, stats, message=""):
    clear_screen()
    full_width = CONTENT_WIDTH + 8
    print("=" * full_width)
    header = f"BEST: ${stats['high_score']} | SPENT: ${stats['spent']} | EARNED: ${stats['earned']}"
    print(f"|| {header:^{CONTENT_WIDTH + 2}} ||")
    
    xp_needed = get_xp_for_next_level(stats['level'])
    bar_width = 15
    filled = int((stats['xp'] / xp_needed) * bar_width)
    xp_bar = "[" + "=" * filled + "-" * (bar_width - filled) + "]"
    level_info = f"LVL {stats['level']} {xp_bar} XP: {stats['xp']}/{xp_needed}"
    print(f"|| {level_info:^{CONTENT_WIDTH + 2}} ||")
    
    # --- Challenge Header ---
    if stats["challenge_completed"]:
        chal_info = f"DAILY CHALLENGE: COMPLETED! (Check back tomorrow)"
    else:
        chal_info = f"DAILY CHALLENGE: Land {stats['challenge_goal']} {stats['challenge_type']}s ({stats['challenge_progress']}/{stats['challenge_goal']})"
    print(f"|| {chal_info:^{CONTENT_WIDTH + 2}} ||")
    
    s_mult = max(1, stats['streak'] - 1) if stats['streak'] > 2 else 1
    l_bonus = 1.0 + (stats['level'] - 1) * 0.1
    mult_info = f"STREAK: {stats['streak']} | MULT: x{s_mult} | LVL BONUS: x{l_bonus:.1f}"
    print(f"|| {mult_info:^{CONTENT_WIDTH + 2}} ||")
    print("=" * full_width)
    
    center_idx = WINDOW_HEIGHT // 2
    spacer = f"|| {' ' * CELL_WIDTH} | {' ' * CELL_WIDTH} | {' ' * CELL_WIDTH} ||"
    for row_idx in range(WINDOW_HEIGHT):
        offset = row_idx - center_idx
        row_cells = []
        for i in range(3):
            k_idx = (reels[i] + offset) % len(ITEM_KEYS)
            row_cells.append(get_classic_cell(ITEM_KEYS[k_idx], row_idx == center_idx))
        print(spacer)
        print(f"|| {row_cells[0]} | {row_cells[1]} | {row_cells[2]} ||")
    print(spacer)
    print("=" * full_width)
    print(f"  {message}")

def spin_animation(current_reels, stats):
    stops = [20, 45, 75] 
    spinning = [True, True, True]
    ticks = 0
    while any(spinning):
        ticks += 1
        for i in range(3):
            if ticks > stops[i]: spinning[i] = False
            if spinning[i]: current_reels[i] += 1
        draw_machine(current_reels, stats, "SPINNING...")
        time.sleep(0.05)
    return current_reels

def main():
    stats = load_data()
    current_reels = [random.randint(0, 100) for _ in range(3)]
    last_msg = "Welcome back! Press ENTER to spin."

    while True:
        draw_machine(current_reels, stats, last_msg)
        print(f"\nENTER: Spin $1 | # : Bet | reset: Reset | q: Quit")
        user_input = input("> ").strip().lower()
        
        if user_input == 'q': break
        if user_input == 'reset':
            today = datetime.now().strftime("%Y-%m-%d")
            stats = {"spent": 0, "earned": 0, "high_score": 0, "streak": 0, "level": 1, "xp": 0, "challenge_type": "LEMON", "challenge_goal": 5, "challenge_progress": 0, "challenge_completed": False, "last_date": today}
            save_data(stats); continue
            
        bet = int(user_input) if user_input.isdigit() else 1
        stats["spent"] += bet
        add_xp(stats, bet * 10) 
        
        current_reels = spin_animation(current_reels, stats)
        keys = [ITEM_KEYS[current_reels[i] % len(ITEM_KEYS)] for i in range(3)]
        
        # --- Update Challenge Progress (only if not already done) ---
        if not stats["challenge_completed"]:
            for k in keys:
                if k == stats["challenge_type"]: 
                    stats["challenge_progress"] += 1
        
        win_amount = 0
        s_mult = max(1, stats["streak"] - 1) if stats["streak"] > 2 else 1
        l_mult = 1.0 + (stats["level"] - 1) * 0.1
        
        if keys[0] == keys[1] == keys[2]:
            stats["streak"] += 1
            win_amount = int((bet * PAYOUT_MULTIPLIERS[keys[0]]) * s_mult * l_mult)
            last_msg = f"JACKPOT! {keys[0]} Won ${win_amount}"
        elif keys[0] == keys[1] or keys[1] == keys[2] or keys[0] == keys[2]:
            stats["streak"] += 1
            win_amount = int((bet * 2) * s_mult * l_mult)
            last_msg = f"Double! Won ${win_amount}"
        else:
            stats["streak"] = 0 
            last_msg = "No luck. Spin again!"
            
        # --- Handle Challenge Completion ---
        if not stats["challenge_completed"] and stats["challenge_progress"] >= stats["challenge_goal"]:
            stats["challenge_completed"] = True
            bonus_xp = stats["level"] * 500 # Bigger reward for daily
            add_xp(stats, bonus_xp)
            last_msg += f" | DAILY CHALLENGE DONE! +{bonus_xp} XP"
            
        stats["earned"] += win_amount
        save_data(stats)

if __name__ == "__main__":
    main()
