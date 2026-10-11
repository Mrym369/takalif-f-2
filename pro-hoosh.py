"""
عامل واکنشی ساده برای مسئله سوئیچ نور در محیط 2*2
هدف: خاموش کردن همه چراغ‌ها
معماری: Condition-Action Rules (فقط بر اساس percept فعلی)
"""

import random
from typing import Tuple

Pos = Tuple[int, int]
Percept = Tuple[Pos, bool]          # (موقعیت عامل، آیا چراغ همین خانه روشن است؟)


# =================================================================
# 1) محیط (Environment)
# =================================================================
class LightEnvironment:
    """محیط 2*2 با چراغ‌هایی که می‌توانند روشن/خاموش باشند."""
    SIZE = 2
    MOVES = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    def __init__(self, initial: list = None, agent_pos: Pos = (0, 0)):
        # True = روشن (ON) ، False = خاموش (OFF)
        if initial is None:
            initial = [[random.choice([True, False]) for _ in range(self.SIZE)]
                       for _ in range(self.SIZE)]
        self.lights = [row[:] for row in initial]
        self.agent_pos = agent_pos
        self.goal = False

    # ---------- حسگرها ----------
    def percept(self) -> Percept:
        """دریافتی = (موقعیت، وضعیت چراغ خانهٔ فعلی)"""
        r, c = self.agent_pos
        return self.agent_pos, self.lights[r][c]

    # ---------- محرک‌ها ----------
    def step(self, action: str) -> None:
        """اعمال عمل عامل روی محیط (تأخیر یک گام)"""
        if action == "TOGGLE":
            r, c = self.agent_pos
            self.lights[r][c] = not self.lights[r][c]
        elif action in self.MOVES:
            dr, dc = self.MOVES[action]
            nr, nc = self.agent_pos[0] + dr, self.agent_pos[1] + dc
            if 0 <= nr < self.SIZE and 0 <= nc < self.SIZE:   # حرکت نامعتبر = بدون تغییر
                self.agent_pos = (nr, nc)
        # action == "NOOP" -> هیچ تغییری روی محیط نمی‌دهد

        self.goal = self.all_off()      # آزمون هدف توسط محیط انجام می‌شود

    def all_off(self) -> bool:
        return all(not lamp for row in self.lights for lamp in row)

    # ---------- نمایش ----------
    def show(self) -> None:
        for r in range(self.SIZE):
            cells = []
            for c in range(self.SIZE):
                lamp = "ON " if self.lights[r][c] else "OFF"
                cells.append(f"[{lamp}]" if (r, c) == self.agent_pos else f" {lamp} ")
            print("   ".join(cells))


# =================================================================
# 2) عامل واکنشی ساده (Simple Reflex Agent)
# =================================================================
class SimpleReflexAgent:
    """
    قواعد شرط-عمل (بر اساس percept فعلی، بدون حافظه تاریخچه):
      R1: IF چراغ خانه فعلی روشن است        -> TOGGLE
      R2: IF چراغ خانه فعلی خاموش است        -> حرکت به سمت خانه بعدی مسیر ثابت
      R3: IF محیط گفت همه چراغ‌ها خاموش‌اند  -> NOOP
    """

    # مسیر ثابت مارپیچی: هر خانه دقیقاً یک بار بازدید می‌شود
    PATH = [(0, 0), (0, 1), (1, 1), (1, 0)]

    # از هر خانه، برای رسیدن به خانه بعدی مسیر، چه حرکتی لازم است؟
    # (این نقشه جزئی از قواعد عامل است؛ محیط کامل قابل مشاهده فرض شده)
    NEXT_MOVE = {
        (0, 0): "RIGHT",
        (0, 1): "DOWN",
        (1, 1): "LEFT",
        (1, 0): "UP",
    }

    def __init__(self):
        self.rules_fired = 0          # فقط برای گزارش

    def act(self, percept: Percept, goal: bool = False) -> str:
        pos, light_on = percept

        # --- R3: پایان کار ---
        if goal:
            self.rules_fired += 1
            print("  >> قاعده R3: همه چراغ‌ها خاموش است -> NOOP (توقف)")
            return "NOOP"

        # --- R1: اگر چراغ روشن است، خاموشش کن ---
        if light_on:
            self.rules_fired += 1
            print(f"  >> قاعده R1: چراغ خانه {pos} روشن است -> TOGGLE")
            return "TOGGLE"

        # --- R2: خاموش است؛ به خانه بعدی مسیر برو ---
        self.rules_fired += 1
        move = self.NEXT_MOVE[pos]
        print(f"  >> قاعده R2: چراغ خانه {pos} خاموش است -> {move}")
        return move


# =================================================================
# 3) عامل واکنشی با حالت داخلی (Reflex with State)
# =================================================================
class StatefulReflexAgent(SimpleReflexAgent):
    """عامل واکنشی با حالت: خودش می‌داند کی همه خانه‌ها را پوشش داده است."""

    def __init__(self):
        super().__init__()
        self.visited = set()

    def act(self, percept: Percept, goal: bool = False) -> str:
        pos, light_on = percept
        self.visited.add(pos)

        if light_on:
            return "TOGGLE"                                   # R1
        if len(self.visited) == 4 and pos == self.PATH[-1]:   # همه خانه‌ها یک بار بازدید شدند
            return "NOOP"                                     # R3: خودش پایان را تشخیص می‌دهد
        return self.NEXT_MOVE[pos]                            # R2


# =================================================================
# 4) حلقه اجرا
# =================================================================
def run(initial: list = None, max_steps: int = 12, agent=None) -> None:
    env = LightEnvironment(initial=initial)
    if agent is None:
        agent = SimpleReflexAgent()

    print("=" * 46)
    print("حالت اولیه محیط 2*2:")
    env.show()
    print("=" * 46)

    step = 0
    while not env.goal and step < max_steps:
        p = env.percept()
        print(f"\nگام {step + 1}: دریافتی = (موقعیت={p[0]}, روشن={p[1]})")
        action = agent.act(p, goal=env.goal)
        env.step(action)
        print("وضعیت بعد از اعمال عمل:")
        env.show()
        step += 1

    print("\n" + "=" * 46)
    print("نتیجه:", "همه چراغ‌ها خاموش شدند ✔" if env.goal
          else "به سقف تعداد گام رسیدیم (بررسی کنید!)")
    print(f"تعداد کل قواعد اجراشده: {agent.rules_fired}")
    print("=" * 46)


if __name__ == "__main__":
    import sys

    # خروجی UTF-8 (برای نمایش درست متن فارسی در کنسول ویندوز)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # برای نتیجه قابل تکرار می‌توانید initial را خودتان تعیین کنید،
    # مثلاً: initial = [[True, False], [True, True]]
    random.seed(4)
    run(initial=None)

    # اجرای نسخه بهبودیافته (عامل با حالت داخلی):
    # run(initial=None, agent=StatefulReflexAgent())
