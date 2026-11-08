"""
عامل واکنشی ساده برای عامل جاروبرقی (Vacuum World) در محیط 2*2
هدف: تمیز کردن همه خانه‌های کثیف
معماری: Condition-Action Rules (فقط بر اساس percept فعلی)
"""

import random
from typing import Tuple

Pos = Tuple[int, int]
Percept = Tuple[Pos, bool]          # (موقعیت عامل، آیا این خانه کثیف است؟)


# =================================================================
# 1) محیط (Environment)
# =================================================================
class VacuumEnvironment:
    """محیط 2*2 با چهار خانه که هر کدام ممکن است کثیف یا تمیز باشند."""
    ROWS = 2
    COLS = 2
    MOVES = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    def __init__(self, initial: list = None, agent_pos: Pos = (0, 0)):
        # True = کثیف (Dirty) ، False = تمیز (Clean)
        if initial is None:
            initial = [[random.choice([True, False]) for _ in range(self.COLS)]
                       for _ in range(self.ROWS)]
        self.dirt = [row[:] for row in initial]
        self.agent_pos = agent_pos
        self.goal = False

    # ---------- حسگرها ----------
    def percept(self) -> Percept:
        """دریافتی = (موقعیت، آیا خانهٔ فعلی کثیف است؟)"""
        r, c = self.agent_pos
        return self.agent_pos, self.dirt[r][c]

    # ---------- محرک‌ها ----------
    def step(self, action: str) -> None:
        """اعمال عمل عامل روی محیط (تأخیر یک گام)"""
        r, c = self.agent_pos

        if action == "SUCK":
            self.dirt[r][c] = False          # خانه تمیز شد
        elif action in self.MOVES:
            dr, dc = self.MOVES[action]
            nr, nc = r + dr, c + dc
            # حرکت نامعتبر (بیرون از شبکه) = بدون تغییر
            if 0 <= nr < self.ROWS and 0 <= nc < self.COLS:
                self.agent_pos = (nr, nc)
        # action == "NOOP" -> هیچ تغییری روی محیط نمی‌دهد

        self.goal = self.all_clean()        # آزمون هدف توسط محیط انجام می‌شود

    def all_clean(self) -> bool:
        return all(not cell for row in self.dirt for cell in row)

    # ---------- نمایش ----------
    def show(self) -> None:
        for r in range(self.ROWS):
            cells = []
            for c in range(self.COLS):
                room = "DIRT" if self.dirt[r][c] else "CLEAN"
                cells.append(f"[{room}]" if (r, c) == self.agent_pos else f" {room} ")
            print("   ".join(cells))


# =================================================================
# 2) عامل واکنشی ساده (Simple Reflex Agent)
# =================================================================
class SimpleReflexAgent:
    """
    قواعد شرط-عمل (بر اساس percept فعلی، بدون حافظه تاریخچه):
      R1: IF خانه فعلی کثیف است           -> SUCK
      R2: IF خانه فعلی تمیز است           -> حرکت به سمت خانه بعدی مسیر ثابت
      R3: IF محیط گفت همه خانه‌ها تمیز‌اند -> NOOP
    """

    def __init__(self, rows: int = 2, cols: int = 2):
        self.rows = rows
        self.cols = cols
        self.rules_fired = 0          # فقط برای گزارش
        # مسیر ثابت "مارپیچ ماری" (snake): هر خانه دقیقاً یک بار بازدید می‌شود
        self.PATH = self._build_snake_path()
        # از هر خانه، برای رسیدن به خانه بعدی مسیر، چه حرکتی لازم است؟
        self.NEXT_MOVE = self._build_next_move()

    def _build_snake_path(self):
        """مسیر ماری‌شکل: سطر زوج چپ→راست، سطر فرد راست→چپ."""
        path = []
        for r in range(self.rows):
            cols = range(self.cols) if r % 2 == 0 else range(self.cols - 1, -1, -1)
            path.extend((r, c) for c in cols)
        return path

    def _build_next_move(self):
        """نگاشت هر خانه به حرکتی که به خانه بعدی مسیر می‌رساند."""
        moves = {}
        for (r1, c1), (r2, c2) in zip(self.PATH, self.PATH[1:]):
            if r2 > r1:
                moves[(r1, c1)] = "DOWN"
            elif r2 < r1:
                moves[(r1, c1)] = "UP"
            elif c2 > c1:
                moves[(r1, c1)] = "RIGHT"
            else:
                moves[(r1, c1)] = "LEFT"
        return moves

    def act(self, percept: Percept, goal: bool = False) -> str:
        pos, dirty = percept

        # --- R3: پایان کار ---
        if goal:
            self.rules_fired += 1
            print("  >> قاعده R3: همه خانه‌ها تمیز است -> NOOP (توقف)")
            return "NOOP"

        # --- R1: اگر خانه کثیف است، مکش کن ---
        if dirty:
            self.rules_fired += 1
            print(f"  >> قاعده R1: خانه {pos} کثیف است -> SUCK")
            return "SUCK"

        # --- R2: تمیز است؛ به خانه بعدی مسیر برو ---
        self.rules_fired += 1
        move = self.NEXT_MOVE[pos]
        print(f"  >> قاعده R2: خانه {pos} تمیز است -> {move}")
        return move


# =================================================================
# 3) عامل واکنشی با حالت داخلی (Reflex with State)
# =================================================================
class StatefulReflexAgent(SimpleReflexAgent):
    """عامل واکنشی با حالت: خودش می‌داند کی همه خانه‌ها را پوشش داده است."""

    def __init__(self, rows: int = 2, cols: int = 2):
        super().__init__(rows, cols)
        self.visited = set()

    def act(self, percept: Percept, goal: bool = False) -> str:
        pos, dirty = percept
        self.visited.add(pos)

        if dirty:
            return "SUCK"                                         # R1
        # همه خانه‌ها یک بار بازدید شدند و به آخرین خانه مسیر رسیده‌ایم
        if len(self.visited) == self.rows * self.cols and pos == self.PATH[-1]:
            return "NOOP"                                         # R3
        return self.NEXT_MOVE[pos]                                # R2


# =================================================================
# 4) حلقه اجرا
# =================================================================
def run(initial: list = None, max_steps: int = 12, agent=None) -> None:
    env = VacuumEnvironment(initial=initial)
    if agent is None:
        agent = SimpleReflexAgent(rows=env.ROWS, cols=env.COLS)

    print("=" * 46)
    print(f"حالت اولیه محیط {env.ROWS}*{env.COLS}:")
    env.show()
    print("=" * 46)

    step = 0
    while not env.goal and step < max_steps:
        p = env.percept()
        print(f"\nگام {step + 1}: دریافتی = (موقعیت={p[0]}, کثیف={p[1]})")
        action = agent.act(p, goal=env.goal)
        env.step(action)
        print("وضعیت بعد از اعمال عمل:")
        env.show()
        step += 1

    print("\n" + "=" * 46)
    print("نتیجه:", "همه خانه‌ها تمیز شدند ✔" if env.goal
          else "به سقف تعداد گام رسیدیم (بررسی کنید!)")
    print(f"تعداد کل قواعد اجراشده: {agent.rules_fired}")
    print("=" * 46)


if __name__ == "__main__":
    import sys

    # خروجی UTF-8 (برای نمایش درست متن فارسی در کنسول ویندوز)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # برای نتیجه قابل تکرار می‌توانید initial را خودتان تعیین کنید،
    # مثلاً: initial = [[True, False], [True, False]]
    random.seed(7)
    run(initial=None)

    # اجرای نسخه بهبودیافته (عامل با حالت داخلی):
    # run(initial=None, agent=StatefulReflexAgent())