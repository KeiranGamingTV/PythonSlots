import time
import random
import os
import sys
import json

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

# --- ALIGNMENT CONSTANTS ---
CONTENT_WIDTH = 52  
CELL_WIDTH = 16     

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_data():
    if not os.path.exists(SAVE_FILE): return 0, 0, 0, 0
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            return (data.get("spent", 0), 
                    data.get("earned", 0), 
                    data.get("high_score", 0),
                    data.get("streak", 0))
    except: return 0, 0, 0, 0

def save_data(spent, earned, high_score, streak):
    if earned > high_score: high_score = earned
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump({
                "spent": spent, 
                "earned": earned, 
                "high_score": high_score,
                "streak": streak
            }, f, indent=4)
    except: pass
    return high_score

def format_line(content):
    return f"||{content:^{CONTENT_WIDTH}}||"

def get_cell_text(key, is_win_row):
    symbol = SYMBOLS[key]
    raw_text = f"> {symbol} <" if is_win_row else f"  {symbol}  "
    return f"{raw_text:^{CELL_WIDTH}}"

def draw_machine(reels, stats, message=""):
    clear_screen()
    full_width = CONTENT_WIDTH + 4
    
    # 1. Header & Stats
    print("=" * full_width)
    print(format_line(f"BEST: ${stats['high_score']} | SPENT: ${stats['spent']} | EARNED: ${stats['earned']}"))
    
    # 2. Multiplier Info
    mult = max(1, stats['streak'] - 1) if stats['streak'] > 2 else 1
    streak_info = f"STREAK: {stats['streak']} | MULTIPLIER: x{mult}"
    print(format_line(streak_info))
    print("=" * full_width)
    
    center_idx = WINDOW_HEIGHT // 2
    spacer_content = f"{' ':^{CELL_WIDTH}}|{' ':^{CELL_WIDTH}}|{' ':^{CELL_WIDTH}}"
    spacer_row = format_line(spacer_content)

    # 3. Render Reels
    for row_idx in range(WINDOW_HEIGHT):
        offset = row_idx - center_idx
        row_cells = []
        for i in range(3):
            key_idx = (reels[i] + offset) % len(ITEM_KEYS)
            row_cells.append(get_cell_text(ITEM_KEYS[key_idx], row_idx == center_idx))
        
        print(spacer_row)
        print(format_line("|".join(row_cells)))

    print(spacer_row)
    print("=" * full_width)
    print(f"  {message}")

def spin_animation(current_reels, stats):
    stop_times = [25, 55, 90] 
    is_spinning = [True, True, True]
    ticks = 0
    while any(is_spinning):
        ticks += 1
        for i in range(3):
            if ticks > stop_times[i]: is_spinning[i] = False
            if is_spinning[i]: current_reels[i] += 1
        
        draw_machine(current_reels, stats, "SPINNING...")
        time.sleep(0.04 + (ticks / 1000))
    return current_reels

def main():
    spent, earned, high_score, streak = load_data()
    stats = {"spent": spent, "earned": earned, "high_score": high_score, "streak": streak}
    current_reels = [random.randint(0, 100) for _ in range(3)]
    last_msg = "Welcome! Press ENTER to spin."

    while True:
        draw_machine(current_reels, stats, last_msg)
        print("\n[Options] ENTER: Spin $1 | # : Bet | reset: Reset | q: Quit")
        user_input = input("> ").strip().lower()
        
        if user_input == 'q': break
        if user_input == 'reset':
            stats = {"spent": 0, "earned": 0, "high_score": 0, "streak": 0}
            save_data(0, 0, 0, 0)
            continue
            
        bet = int(user_input) if user_input.isdigit() else 1
        stats["spent"] += bet
        
        current_reels = spin_animation(current_reels, stats)
        
        # Win Logic
        final_keys = [ITEM_KEYS[current_reels[i] % len(ITEM_KEYS)] for i in range(3)]
        r1, r2, r3 = final_keys
        
        win_amount = 0
        if r1 == r2 == r3:
            stats["streak"] += 1
            mult = max(1, stats["streak"] - 1) if stats["streak"] > 2 else 1
            win_amount = (bet * PAYOUT_MULTIPLIERS[r1]) * mult
            last_msg = f"JACKPOT! {r1} (x{mult} Multiplier)! Won ${win_amount}"
        elif r1 == r2 or r2 == r3 or r1 == r3:
            stats["streak"] += 1
            mult = max(1, stats["streak"] - 1) if stats["streak"] > 2 else 1
            win_amount = (bet * 2) * mult
            last_msg = f"Double! (x{mult} Multiplier)! Won ${win_amount}"
        else:
            stats["streak"] = 0 
            last_msg = "No luck. Streak reset."
            
        stats["earned"] += win_amount
        stats["high_score"] = save_data(stats["spent"], stats["earned"], stats["high_score"], stats["streak"])

if __name__ == "__main__":
    main()
