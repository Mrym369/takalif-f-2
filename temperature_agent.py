"""
عامل واکنشی ساده برای مسئله کنترل دما در محیط 2 خانه‌ای
دمای هدف: 20 درجه | دمای اولیه: خانه1=17 ، خانه2=24
معماری: Condition-Action Rules (فقط بر اساس percept فعلی)
"""

import random
from typing import List, Tuple

Pos = Tuple[int, int]
Percept = Tuple[Pos, float]         # (موقعیت عامل، دمای فعلی همان خانه)


# =================================================================
# 1) محیط (Environment)
# =================================================================
class TemperatureEnvironment:
    """محیط 2 خانه‌ای (یک ردیف از 2 خانه) با هدف دمایی 20 درجه."""
    ROWS = 1                    # تعداد سطرها
    COLS = 2                    # تعداد خانه‌ها در هر سطر
    TARGET = 20.0               # دمای هدف
    DELTA = 1.0                 # تغییر دما در هر عمل (درجه)
    MOVES = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    def __init__(self, initial: List[float] = None, agent_pos: Pos = (0, 0)):
        # دمای اولیه پیش‌فرض: 17 و 24
        if initial is None:
            initial = [17.0, 24.0]
        assert len(initial) == self.ROWS * self.COLS, "تعداد دماها باید برابر تعداد خانه‌ها باشد"
        self.temps = list(initial)
        self.agent_pos = agent_pos
        self.goal = False

    def _index(self, pos: Pos) -> int:
        r, c = pos
        return r * self.COLS + c

    # ---------- حسگرها ----------
    def percept(self) -> Percept:
        """دریافتی = (موقعیت، دمای خانهٔ فعلی)"""
        return self.agent_pos, self.temps[self._index(self.agent_pos)]

    # ---------- محرک‌ها ----------
    def step(self, action: str) -> None:
        """اعمال عمل عامل روی محیط (تأخیر یک گام)"""
        idx = self._index(self.agent_pos)

        if action == "HEAT":
            self.temps[idx] += self.DELTA
        elif action == "COOL":
            self.temps[idx] -= self.DELTA
        elif action in self.MOVES:
            dr, dc = self.MOVES[action]
            nr, nc = self.agent_pos[0] + dr, self.agent_pos[1] + dc
            # حرکت نامعتبر (بیرون از شبکه) = بدون تغییر
            if 0 <= nr < self.ROWS and 0 <= nc < self.COLS:
                self.agent_pos = (nr, nc)
        # action == "NOOP" -> هیچ تغییری روی محیط نمی‌دهد

        self.goal = self.all_at_target()    # آزمون هدف توسط محیط انجام می‌شود

    def all_at_target(self) -> bool:
        return all(abs(t - self.TARGET) < 1e-9 for t in self.temps)

    # ---------- نمایش ----------
    def show(self) -> None:
        rooms = []
        for r in range(self.ROWS):
            for c in range(self.COLS):
                label = f"{self.temps[self._index((r, c))]:.0f}C"
                rooms.append(f"[{label}]" if (r, c) == self.agent_pos else f" {label} ")
        print("   ".join(rooms))


# =================================================================
# 2) عامل واکنشی ساده (Simple Reflex Agent)
# =================================================================
class SimpleReflexAgent:
    """
    قواعد شرط-عمل (بر اساس percept فعلی، بدون حافظه تاریخچه):
      R1: IF دمای خانه فعلی < هدف     -> HEAT
      R2: IF دمای خانه فعلی > هدف     -> COOL
      R3: IF دمای خانه فعلی == هدف    -> حرکت به خانه بعدی مسیر ثابت
      R4: IF محیط گفت همه به هدف رسیدند -> NOOP
    """

    def __init__(self, rows: int = 1, cols: int = 2, target: float = 20.0):
        self.rows = rows
        self.cols = cols
        self.target = target
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
        """نگاشت هر خانه به حرکتی که به خانه بعدی مسیر می‌رساند (بازگشت حلقه‌ای به ابتدا)."""
        moves = {}
        pairs = list(zip(self.PATH, self.PATH[1:])) + [(self.PATH[-1], self.PATH[0])]
        for (r1, c1), (r2, c2) in pairs:
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
        pos, temp = percept

        # --- R4: پایان کار ---
        if goal:
            self.rules_fired += 1
            print("  >> قاعده R4: همه خانه‌ها به 20 درجه رسیدند -> NOOP (توقف)")
            return "NOOP"

        # --- R1: سردتر از هدف است؛ گرما بده ---
        if temp < self.target:
            self.rules_fired += 1
            print(f"  >> قاعده R1: دمای خانه {pos} = {temp:.0f}C (< 20) -> HEAT")
            return "HEAT"

        # --- R2: گرم‌تر از هدف است؛ سرد کن ---
        if temp > self.target:
            self.rules_fired += 1
            print(f"  >> قاعده R2: دمای خانه {pos} = {temp:.0f}C (> 20) -> COOL")
            return "COOL"

        # --- R3: به هدف رسید؛ به خانه بعدی مسیر برو ---
        self.rules_fired += 1
        move = self.NEXT_MOVE[pos]
        print(f"  >> قاعده R3: دمای خانه {pos} = {temp:.0f}C (== 20) -> {move}")
        return move


# =================================================================
# 3) عامل واکنشی با حالت داخلی (Reflex with State)
# =================================================================
class StatefulReflexAgent(SimpleReflexAgent):
    """عامل واکنشی با حالت: خودش می‌داند کی همه خانه‌ها را پوشش داده است."""

    def __init__(self, rows: int = 1, cols: int = 2, target: float = 20.0):
        super().__init__(rows, cols, target)
        self.visited = set()

    def act(self, percept: Percept, goal: bool = False) -> str:
        pos, temp = percept
        self.visited.add(pos)

        if temp < self.target:
            return "HEAT"                                         # R1
        if temp > self.target:
            return "COOL"                                         # R2
        # همه خانه‌ها یک بار بازدید شدند و به آخرین خانه مسیر رسیده‌ایم
        if len(self.visited) == self.rows * self.cols and pos == self.PATH[-1]:
            return "NOOP"                                         # R4
        return self.NEXT_MOVE[pos]                                # R3


# =================================================================
# 4) حلقه اجرا
# =================================================================
def run(initial: List[float] = None, max_steps: int = 20, agent=None) -> None:
    env = TemperatureEnvironment(initial=initial)
    if agent is None:
        agent = SimpleReflexAgent(rows=env.ROWS, cols=env.COLS, target=env.TARGET)

    print("=" * 46)
    print(f"حالت اولیه محیط {env.ROWS * env.COLS} خانه‌ای (هدف: {env.TARGET:.0f}C):")
    env.show()
    print("=" * 46)

    step = 0
    while not env.goal and step < max_steps:
        p = env.percept()
        print(f"\nگام {step + 1}: دریافتی = (موقعیت={p[0]}, دما={p[1]:.0f}C)")
        action = agent.act(p, goal=env.goal)
        env.step(action)
        print("وضعیت بعد از اعمال عمل:")
        env.show()
        step += 1

    print("\n" + "=" * 46)
    print("نتیجه:", "همه خانه‌ها به 20 درجه رسیدند ✔" if env.goal
          else "به سقف تعداد گام رسیدیم (بررسی کنید!)")
    print(f"تعداد کل قواعد اجراشده: {agent.rules_fired}")
    print("=" * 46)


if __name__ == "__main__":
    import sys

    # خروجی UTF-8 (برای نمایش درست متن فارسی در کنسول ویندوز)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # دمای اولیه: خانه1=17 ، خانه2=24 (طبق تمرین)
    run(initial=[17.0, 24.0])

    # اجرای نسخه بهبودیافته (عامل با حالت داخلی):
    # run(initial=[17.0, 24.0], agent=StatefulReflexAgent())
