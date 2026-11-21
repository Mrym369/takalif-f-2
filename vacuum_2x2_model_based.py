"""
عامل واکنشی مدل‌محور (Model-Based Reflex Agent)
جاروبرقی در محیط ۲×۲ — هدف: تمیز کردن همهٔ خانه‌های کثیف

مراحل الگوریتم:
 ۱) مدل‌سازی: مدل داخلی از وضعیت ۴ خانه می‌سازیم (Dirty/Clean/Unknown)
 ۲) حس (Percept): وضعیت واقعی خانهٔ فعلی را می‌خوانیم
 ۳) به‌روزرسانی مدل با مشاهدهٔ جدید
 ۴) اعمال قواعد IF-THEN روی مدل برای انتخاب اقدام (قاعده ۱ تا ۴)
 ۵) اجرای اقدام روی محیط و تکرار ۲ تا ۴ تا تمیز شدن کل خانه

قواعد IF-THEN عامل مدل‌محور:
 قاعده ۱: IF خانهٔ فعلی کثیف است            THEN Suck (جارو کشیدن)
 قاعده ۲: IF خانهٔ کثیف شناخته‌شده‌ای هست   THEN حرکت به سمت نزدیک‌ترین آن (کوتاه‌ترین مسیر)
 قاعده ۳: IF خانهٔ ناشناسی وجود دارد       THEN کاوشِ نزدیک‌ترین خانهٔ ناشناس
 قاعده ۴: IF همهٔ خانه‌ها تمیز شناخته شدند THEN NoOp (پایان کار)
"""

from collections import deque
from itertools import combinations

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

# --- قواعد صریح IF-THEN (برای نمایش و ردیابی تصمیم‌ها) ---
RULES = {
    1: "IF خانهٔ فعلی Dirty است THEN Suck",
    2: "IF خانهٔ کثیف شناخته‌شده‌ای هست THEN حرکت به نزدیک‌ترین آن",
    3: "IF خانهٔ ناشناسی وجود دارد THEN کاوش نزدیک‌ترین خانهٔ ناشناس",
    4: "IF همهٔ خانه‌ها تمیزند THEN NoOp (پایان)",
}


# ============================================================
# محیط (جهان واقعی)
# ============================================================
class Environment:
    """محیط واقعی: وضعیت واقعی ۴ خانه را نگه می‌دارد."""

    def __init__(self, dirty_cells):
        # همه خانه‌ها تمیزند، مگر خانه‌های کثیف اولیه
        self.state = {(r, c): CLEAN for r in range(2) for c in range(2)}
        for cell in dirty_cells:
            if cell in self.state:
                self.state[cell] = DIRTY

    def percepts(self, position):
        """احساس (Percept): وضعیت واقعی خانه‌ای که عامل روی آن است."""
        return self.state[position]

    def execute(self, position, action):
        """اجرای اقدام روی محیط."""
        if action == "Suck":
            self.state[position] = CLEAN
        return self.state

    def is_all_clean(self):
        """آیا همهٔ خانه‌های محیط تمیز شده‌اند؟"""
        return all(v == CLEAN for v in self.state.values())


# ============================================================
# عامل واکنشی مدل‌محور
# ============================================================
class ModelBasedVacuumAgent:
    """
    عامل واکنشی مدل‌محور:
    - مدل داخلی (internal state) از وضعیت همهٔ خانه‌ها دارد
    - بر اساس مدل، قواعد IF-THEN را اعمال می‌کند
    - به سمت نزدیک‌ترین خانهٔ کثیف (یا ناشناس) برنامه‌ریزی می‌کند
    """

    def __init__(self, start_position=(0, 0)):
        self.position = start_position
        # مدل داخلی: ابتدا همه‌چیز «نامشخص» است
        self.model = {(r, c): UNKNOWN for r in range(2) for c in range(2)}
        self.last_rule = None  # شمارهٔ قاعدهٔ اعمال‌شده در آخرین تصمیم

    # ---------- به‌روزرسانی مدل ----------
    def update_model(self, percept):
        """مرحلهٔ ۳: مشاهده را در مدل داخلی لحاظ می‌کند."""
        self.model[self.position] = percept

    # ---------- تصمیم‌گیری با قواعد IF-THEN ----------
    def plan(self):
        """
        مرحلهٔ ۴: اعمال قواعد روی مدل داخلی.
        خروجی: (اقدام، شمارهٔ قاعدهٔ اعمال‌شده)
        """
        # قاعده ۱: IF خانهٔ فعلی کثیف است THEN Suck
        if self.model[self.position] == DIRTY:
            self.last_rule = 1
            return "Suck", 1

        # قاعده ۲: IF خانهٔ کثیف شناخته‌شده‌ای هست THEN حرکت به نزدیک‌ترین آن
        dirty = self.nearest_cell_with(DIRTY)
        if dirty is not None:
            self.last_rule = 2
            return self.first_step_towards(dirty), 2

        # قاعده ۳: IF خانهٔ ناشناسی وجود دارد THEN کاوش نزدیک‌ترین خانهٔ ناشناس
        unknown = self.nearest_cell_with(UNKNOWN)
        if unknown is not None:
            self.last_rule = 3
            return self.first_step_towards(unknown), 3

        # قاعده ۴: IF همهٔ خانه‌ها تمیز شناخته شدند THEN NoOp (پایان)
        self.last_rule = 4
        return "NoOp", 4

    # ---------- جستجوی مسیر روی مدل ----------
    def nearest_cell_with(self, status):
        """جستجوی سطح اول (BFS): نزدیک‌ترین خانه با وضعیت داده‌شده."""
        start = self.position
        visited = {start}
        queue = deque([start])

        while queue:
            cell = queue.popleft()
            if self.model.get(cell) == status and cell != start:
                return cell
            for dr, dc in MOVES.values():
                nxt = (cell[0] + dr, cell[1] + dc)
                if nxt not in visited and 0 <= nxt[0] < 2 and 0 <= nxt[1] < 2:
                    visited.add(nxt)
                    queue.append(nxt)
        return None

    def first_step_towards(self, target):
        """اولین حرکت کوتاه‌ترین مسیر از موقعیت فعلی به هدف (BFS)."""
        start = self.position
        if start == target:
            return "NoOp"
        visited = {start}
        queue = deque([(start, None)])  # (موقعیت، اولین حرکت مسیر)

        while queue:
            cell, first_move = queue.popleft()
            for dname, (dr, dc) in MOVES.items():
                nxt = (cell[0] + dr, cell[1] + dc)
                if nxt in visited or not (0 <= nxt[0] < 2 and 0 <= nxt[1] < 2):
                    continue
                move = dname if first_move is None else first_move
                if nxt == target:
                    return move
                visited.add(nxt)
                queue.append((nxt, move))
        return "NoOp"

    # ---------- چرخهٔ اصلی عامل ----------
    def act(self, percept):
        """حس + به‌روزرسانی مدل + تصمیم؛ خروجی: (اقدام، شمارهٔ قاعده)."""
        self.update_model(percept)  # مرحله ۳
        return self.plan()          # مرحله ۴

    def move(self, action):
        """اعمال اقدام حرکتی روی موقعیت عامل."""
        if action in MOVES:
            dr, dc = MOVES[action]
            nxt = (self.position[0] + dr, self.position[1] + dc)
            if 0 <= nxt[0] < 2 and 0 <= nxt[1] < 2:
                self.position = nxt

    def is_finished(self):
        """آیا مدل می‌گوید همهٔ خانه‌ها تمیز شده‌اند؟"""
        return all(v == CLEAN for v in self.model.values())


# ============================================================
# نمایش گرید ۲×۲
# ============================================================
def render(env, agent, step, action, rule_no):
    """نمایش بصری گرید ۲×۲ (وضعیت واقعی در برابر مدل داخلی)."""
    print(f"\nگام {step} | موقعیت {agent.position} | احساس: {env.percepts(agent.position)}")
    print(f"  قاعدهٔ {rule_no}: {RULES[rule_no]}")
    print(f"  اقدام: {action}")
    print("      واقعی            مدل داخلی")
    for r in range(2):
        real_row, model_row = [], []
        for c in range(2):
            mark = "*" if agent.position == (r, c) else " "
            real_row.append(env.state[(r, c)][0] + mark)        # D/C + علامت عامل
            model_row.append(agent.model[(r, c)][0] + mark)
        print(f"    [{' '.join(real_row)}]          [{' '.join(model_row)}]")
    print("  (D=کثیف  C=تمیز  U=نامشخص  *=موقعیت عامل)")


# ============================================================
# شبیه‌سازی
# ============================================================
def run_agent(dirty_cells, start=(0, 0), max_steps=20, verbose=True):
    """اجرای عامل روی یک پیکربندی؛ تعداد گام تا پایان را برمی‌گرداند (یا None)."""
    env = Environment(dirty_cells)
    agent = ModelBasedVacuumAgent(start)

    if verbose:
        print("=" * 60)
        print("شروع: خانه‌های کثیف =", dirty_cells)
        print(f"موقعیت شروع عامل: {start}")
        print("=" * 60)

    step = 0
    while step < max_steps:
        step += 1
        # ۱+۲) حس و به‌روزرسانی مدل / ۳) تصمیم با قواعد
        percept = env.percepts(agent.position)
        action, rule_no = agent.act(percept)

        # نمایش وضعیت قبل از اجرا
        if verbose:
            render(env, agent, step, action, rule_no)

        # ۴) اجرای اقدام
        env.execute(agent.position, action)
        agent.move(action)

        # ۵) شرط پایان: مدل بگوید همه تمیزند
        if agent.is_finished():
            if verbose:
                print("\n✔ همهٔ خانه‌ها تمیز شدند — عامل متوقف شد.")
                print("\nوضعیت نهایی محیط:")
                for r in range(2):
                    print("   ", " | ".join(env.state[(r, c)] for c in range(2)))
                print(f"تعداد گام‌ها: {step}")
            return step

    if verbose:
        print("\n⚠ به سقف گام‌ها رسید (عامل متوقف نشد).")
    return None


def all_dirty_configurations():
    """هر ۱۶ پیکربندی ممکن خانه‌های کثیف (هر زیرمجموعه از ۴ خانه)."""
    cells = [(r, c) for r in range(2) for c in range(2)]
    for k in range(len(cells) + 1):
        for combo in combinations(cells, k):
            yield list(combo)


def run_all_configurations():
    """اجرای عامل روی همهٔ حالت‌های ممکن و گزارش نتیجه."""
    print("\n" + "=" * 60)
    print("اجرای عامل روی هر ۱۶ پیکربندی ممکن خانه‌های کثیف")
    print("=" * 60)
    print(f"{'خانه‌های کثیف':<38} {'نتیجه':<10} {'گام‌ها'}")
    print("-" * 60)

    successes = 0
    total = 0
    for dirty in all_dirty_configurations():
        total += 1
        steps = run_agent(dirty, verbose=False)
        label = str(dirty) if dirty else "(هیچ خانهٔ کثیفی)"
        result = "موفق ✔" if steps is not None else "ناموفق ✘"
        if steps is not None:
            successes += 1
        print(f"{label:<38} {result:<10} {steps if steps is not None else '-'}")

    print("-" * 60)
    print(f"نتیجهٔ کلی: {successes} از {total} حالت موفق بود.")


if __name__ == "__main__":
    # مثال ۱: اجرای کامل با نمایش گام‌به‌گام (دو خانهٔ کثیف)
    run_agent(dirty_cells=[(0, 1), (1, 0)], start=(0, 0))

    # مثال ۲: آزمون همهٔ ۱۶ حالت ممکن
    run_all_configurations()
