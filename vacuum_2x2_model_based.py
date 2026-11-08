"""
عامل واکنشی مدل‌محور (Model-Based Reflex Agent)
جاروبرقی در محیط ۲×۲

مراحل الگوریتم:
۱) نگهداری مدل داخلی از وضعیت ۴ خانه (Dirty/Clean/Unknown)
۲) در هر گام: حس خانهٔ فعلی → به‌روزرسانی مدل
۳) اگر خانهٔ فعلی کثیف است → Suck
۴) اگر تمیز است → حرکت به سمت نزدیک‌ترین خانهٔ کثیف (طبق مدل)
۵) تکرار تا تمیز شدن همهٔ خانه‌ها → توقف
"""

import sys
from collections import deque

# کنسول ویندوز ممکن است UTF-8 نباشد (خطای UnicodeEncodeError)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- تعریف محیط ۲×۲ ---
# سلول‌ها: (row, col) با row, col ∈ {0,1}
DIRTY = "Dirty"
CLEAN = "Clean"
UNKNOWN = "Unknown"

# حرکت‌ها: بالا، پایین، چپ، راست
MOVES = {
    "Up": (-1, 0),
    "Down": (1, 0),
    "Left": (0, -1),
    "Right": (0, 1),
}


class Environment:
    """محیط واقعی (جهان): وضعیت واقعی خانه‌ها را نگه می‌دارد."""

    def __init__(self, dirty_cells):
        # همه خانه‌ها تمیزند، مگر خانه‌های کثیف اولیه
        self.state = {(r, c): CLEAN for r in range(2) for c in range(2)}
        for cell in dirty_cells:
            self.state[cell] = DIRTY

    def percepts(self, position):
        """احساس (Percept): وضعیت واقعی خانه‌ای که عامل روی آن است."""
        return self.state[position]

    def execute(self, position, action):
        """اجرای اقدام روی محیط؛ وضعیت جدید را برمی‌گرداند."""
        if action == "Suck":
            self.state[position] = CLEAN
        return self.state


class ModelBasedVacuumAgent:
    """
    عامل واکنشی مدل‌محور:
    - مدل داخلی (internal state) از وضعیت همهٔ خانه‌ها دارد
    - بر اساس مدل، به سمت نزدیک‌ترین خانهٔ کثیف برنامه‌ریزی می‌کند
    """

    def __init__(self, start_position=(0, 0)):
        self.position = start_position
        # مدل داخلی: ابتدا همه‌چیز «نامشخص» است
        self.model = {(r, c): UNKNOWN for r in range(2) for c in range(2)}

    # ---------- به‌روزرسانی مدل ----------
    def update_model(self, percept):
        """مرحلهٔ ۲: مشاهده را در مدل داخلی لحاظ می‌کند."""
        self.model[self.position] = percept

    # ---------- تصمیم‌گیری ----------
    def plan(self):
        """مرحلهٔ ۳: تصمیم بر اساس مدل داخلی (نه فقط حس فوری)."""
        # ۳.۱ اگر خانهٔ فعلی کثیف است → جارو بکش
        if self.model[self.position] == DIRTY:
            return "Suck"

        # ۳.۲ پیدا کردن نزدیک‌ترین خانهٔ کثیف با BFS روی مدل
        dirty = self.nearest_cell_with(DIRTY)
        if dirty is not None:
            # ۳.۳ اولین حرکت کوتاه‌ترین مسیر
            return self.first_step_towards(dirty)

        # ۳.۴ اگر خانهٔ کثیف شناخته‌شده‌ای نیست → کاوش خانه‌های ناشناس
        unknown = self.nearest_cell_with(UNKNOWN)
        if unknown is not None:
            return self.first_step_towards(unknown)

        # ۳.۵ همهٔ خانه‌ها تمیز شناخته شده‌اند → پایان
        return "NoOp"

    def nearest_cell_with(self, status):
        """جستجوی سطح اول (BFS) برای نزدیک‌ترین خانه با وضعیت داده‌شده."""
        start = self.position
        visited = {start}
        queue = deque([(start, [])])  # (موقعیت، مسیر تا اینجا)

        while queue:
            cell, path = queue.popleft()
            if self.model.get(cell) == status and cell != start:
                return cell
            for dname, (dr, dc) in MOVES.items():
                nxt = (cell[0] + dr, cell[1] + dc)
                if nxt not in visited and 0 <= nxt[0] < 2 and 0 <= nxt[1] < 2:
                    visited.add(nxt)
                    queue.append((nxt, path + [dname]))
        return None

    def first_step_towards(self, target):
        """اولین اقدام کوتاه‌ترین مسیر از موقعیت فعلی به هدف."""
        start = self.position
        visited = {start}
        queue = deque([(start, None)])  # (موقعیت، اولین حرکت)

        while queue:
            cell, first_move = queue.popleft()
            if cell == target:
                return first_move
            for dname, (dr, dc) in MOVES.items():
                nxt = (cell[0] + dr, cell[1] + dc)
                if nxt not in visited and 0 <= nxt[0] < 2 and 0 <= nxt[1] < 2:
                    visited.add(nxt)
                    queue.append(
                        (nxt, dname if first_move is None else first_move)
                    )
        return "NoOp"

    # ---------- چرخهٔ اصلی عامل ----------
    def act(self, percept):
        """مرحلهٔ ۲ (حس + مدل) و ۳ (تصمیم): اقدام را برمی‌گرداند."""
        self.update_model(percept)  # به‌روزرسانی مدل از مشاهده
        return self.plan()  # تصمیم بر اساس مدل

    def move(self, action):
        """اعمال اقدام حرکتی روی موقعیت عامل (در محیط)."""
        if action in MOVES:
            dr, dc = MOVES[action]
            nxt = (self.position[0] + dr, self.position[1] + dc)
            if 0 <= nxt[0] < 2 and 0 <= nxt[1] < 2:
                self.position = nxt


# ============================================================
# شبیه‌سازی (Simulation)
# ============================================================
def run_agent(dirty_cells, start=(0, 0), max_steps=20):
    env = Environment(dirty_cells)
    agent = ModelBasedVacuumAgent(start)

    print("=" * 55)
    print("شروع: خانه‌های کثیف =", dirty_cells)
    print(f"موقعیت شروع عامل: {start}")
    print("=" * 55)

    step = 0
    while step < max_steps:
        step += 1
        # ۱) حس
        percept = env.percepts(agent.position)
        print(f"\nگام {step} | موقعیت {agent.position} | احساس: {percept}")
        print("  مدل داخلی:", dict(sorted(agent.model.items())))

        # ۲+۳) به‌روزرسانی مدل و تصمیم‌گیری
        action = agent.act(percept)

        # ۴) اجرای اقدام
        print(f"  اقدام: {action}")
        env.execute(agent.position, action)
        agent.move(action)

        # ۵) شرط پایان: مدل بگوید همه تمیزند
        if all(v == CLEAN for v in agent.model.values()):
            print("\n✔ همهٔ خانه‌ها تمیز شدند — عامل متوقف شد.")
            break
    else:
        print("\n⚠ به سقف گام‌ها رسید.")

    print("\nوضعیت نهایی محیط:")
    for r in range(2):
        print("   ", " | ".join(env.state[(r, c)] for c in range(2)))
    print(f"تعداد گام‌ها: {step}")
    return step


if __name__ == "__main__":
    # مثال: دو خانهٔ کثیف
    run_agent(dirty_cells=[(0, 1), (1, 0)], start=(0, 0))
