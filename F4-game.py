import curses
import time
import random

def safe_addch(win, y, x, char):
    try:
        h, w = win.getmaxyx()
        if 0 <= y < h and 0 <= x < w:
            win.addch(y, x, char)
    except curses.error:
        pass

def safe_addstr(win, y, x, text):
    try:
        h, w = win.getmaxyx()
        if 0 <= y < h and 0 <= x + len(text) < w:
            win.addstr(y, x, text)
    except curses.error:
        pass

def collision(bx, by, ex, ey):
    if int(bx) == int(ex):
        return abs(by - ey) <= 1.5
    return False

class Tower():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heat = 0
        self.overheated = False

def draw_menu(win):
    win.clear()
    win.box()
    win.addstr(5, 30, "ДОБРО ПОЖАЛОВАТЬ В ИГРУ F4")
    win.addstr(8, 20, "H — башни (защитные сооружения)")
    win.addstr(10, 20, "m — это вы (могущественный маг по имени Карл)")
    win.addstr(12, 20, "E — враги (злые сущности)")
    win.addstr(14, 20, "# — стены вашего королевства")
    win.addstr(28, 30, "НАЖМИТЕ ЛЮБУЮ КЛАВИШУ ДЛЯ СТАРТА...")
    win.refresh()
    win.nodelay(False) 
    win.getch()
    win.clear() 
    win.nodelay(True) 

def main(stdscr):
    term_h, term_w = stdscr.getmaxyx()
    win_h, win_w = 35, 100
    start_y = max(0, (term_h - win_h) // 2)
    start_x = max(0, (term_w - win_w) // 2)
    
    win = curses.newwin(win_h, win_w, start_y, start_x)
    win.nodelay(True)
    win.keypad(True)
    curses.curs_set(0)
    curses.noecho()
    draw_menu(win)

    lanes = [5, 11, 17, 23, 29]
    towers = [Tower(lane, 20) for lane in lanes]

    mage = {"x": 10, "y": 10, "char": "m"}
    state = "GROUND"
    fire_bolls = []
    fire_points = 10
    enemies = []
    spawn_timer = 0 
    space_pressed = False
    kills = 0
    gold = 0
    current_tower = None
    game_over = False
    max_heat = 100
    cooling_rate = 0.1
    enemy_speed = 0.2
    difficulty_timer = 30  
    frame_counter = 0

    while not game_over:
        key = win.getch()
        if key == ord("q"):
            break

        frame_counter += 1

        if state == "SHOP":
            win.box()
            safe_addstr(win, 10, 35, "=== МАГАЗИН МАГИИ ===")
            safe_addstr(win, 12, 35, f"ЗОЛОТО: {gold}")
            safe_addstr(win, 15, 30, "1. Купить жидкость с маной (-100 золота + 10 зарядов маны)")
            safe_addstr(win, 17, 30, "2. Купить охлаждающие руны (-50 нагрев -100 золото)")
            safe_addstr(win, 19, 30, "3. Купить охлаждающий артефакт (скорость охлаждение X2 -200 золото)")
            safe_addstr(win, 25, 30, "X. Вернуться в бой")

            if key == ord("x"):
                state = "GROUND"
                win.clear()
            elif key == ord("1") and gold >= 100:
                fire_points += 10
                gold -= 100
                state = "GROUND"
                win.clear()
            elif key == ord("2") and gold >= 100:
                for t in towers:
                    t.heat = max(0, t.heat - 50)
                    if t.heat < max_heat: t.overheated = False
                gold -= 100
                state = "GROUND"
                win.clear()
            elif key == ord("3") and gold >= 200:
                cooling_rate = 0.2
                gold -= 200
                state = "GROUND"
                win.clear()
        else:
            total_seconds = frame_counter // 20
            minutes = total_seconds // 60
            seconds = total_seconds % 60

            if gold >= 100:
                safe_addstr(win, 30, 60, "Нажми 'B' для входа в магазин")
                if key == ord("b"):
                    state = "SHOP"
                    win.clear()
                    continue

            for t in towers:
                if t.heat > 0:
                    t.heat -= cooling_rate
                    if t.heat <= 0:
                        t.heat = 0
                        t.overheated = False

            safe_addch(win, int(mage["x"]), int(mage["y"]), " ")
            for b in fire_bolls:
                safe_addch(win, int(b["x"]), int(b["y"]), " ")
            for e in enemies:
                safe_addch(win, int(e["x"]), int(e["y"]), " ")

            if state == "GROUND":
                if key == ord("w") and mage["x"] > 1: mage["x"] -= 1
                elif key == ord("s") and mage["x"] < 33: mage["x"] += 1
                elif key == ord("a") and mage["y"] > 1: mage["y"] -= 1
                elif key == ord("d") and mage["y"] < 98: mage["y"] += 1
                
                for t in towers:
                    if int(mage["x"]) == t.x and int(mage["y"]) == t.y:
                        current_tower = t
                        state = "TOWER"

            elif state == "TOWER":
                safe_addstr(win, 33, 5, f"МАГ В БАШНЕ | УБИТО: {kills} | ЗОЛОТО: {gold} | МАНА {fire_points} | ВЫХОД: 'x'")
                
                if current_tower.overheated:
                    safe_addstr(win, 10, 40, "!!! ПЕРЕГРЕВ !!!")
                else:
                    safe_addstr(win, 10, 40, f"Нагрев башни: {int(current_tower.heat)}/100")
                    
                if key == ord("x"):
                    state = "GROUND"
                    mage["y"] -= 2 
                    win.clear()
                    current_tower = None
                
                if key == ord(" ") and not space_pressed and not (current_tower and current_tower.overheated):
                    if fire_points > 0:
                        fire_bolls.append({"x": mage["x"], "y": float(mage["y"] + 1), "active": True})
                        space_pressed = True
                        current_tower.heat += 20
                        fire_points -= 1
                        if current_tower.heat >= max_heat:
                            current_tower.overheated = True
                    else:
                        safe_addstr(win, 23, 40, "Нет маны!")
                elif key != ord(" "):
                    space_pressed = False

            spawn_timer += 1
            if spawn_timer > difficulty_timer:
                enemy_lane = random.choice(lanes)
                enemies.append({"x": float(enemy_lane), "y": 95.0, "char": "E", "active": True})
                spawn_timer = 0

            if frame_counter % 500 == 0 and difficulty_timer > 5:
                difficulty_timer -= 2
            
            if frame_counter % 1000 == 0:
                enemy_speed += 0.01

            for b in fire_bolls:
                if b["active"]:
                    b["y"] += 2.0
                    if b["y"] >= 98: b["active"] = False
                    for e in enemies:
                        if e["active"] and collision(b["x"], b["y"], e["x"], e["y"]):
                            e["active"] = False
                            b["active"] = False
                            kills += 1
                            gold += 20
                            break

            fire_bolls = [b for b in fire_bolls if b["active"]]
            for b in fire_bolls:
                safe_addch(win, int(b["x"]), int(b["y"]), "*")

            new_enemies = []
            for e in enemies:
                if e["active"]:
                    e["y"] -= enemy_speed
                    if e["y"] <= 6: game_over = True
                    safe_addch(win, int(e["x"]), int(e["y"]), e["char"])
                    new_enemies.append(e)
            enemies = new_enemies

            win.box()
            for row in range(1, 34): safe_addch(win, row, 6, "#")
            for t in towers: safe_addch(win, t.x, t.y, "H")
            safe_addch(win, int(mage["x"]), int(mage["y"]), mage["char"])
            safe_addstr(win, 1, 75, f"ВРЕМЯ: {minutes:02d}:{seconds:02d}")
        
        win.refresh()
        time.sleep(0.05)

    win.nodelay(False)
    win.clear()
    win.box()
    final_msg = f" КОРОЛЕВСТВО ПАЛО! СЧЕТ: {kills} | ЗОЛОТО: {gold}"
    safe_addstr(win, 15, 50 - len(final_msg)//2, final_msg)
    win.refresh()
    win.getch()

if __name__ == "__main__":
    curses.wrapper(main)
