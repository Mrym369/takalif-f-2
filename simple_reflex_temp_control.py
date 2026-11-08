"""
عامل واکنشی ساده (Simple Reflex Agent)
مسئله: کنترل دمای محیط 2 خانه‌ای
  - دمای هدف: 20 درجه
  - دمای اولیه: خانه1 = 17 درجه ، خانه2 = 24 درجه

معماری: قواعد شرط-عمل (Condition-Action Rules) - فقط بر اساس دریافتی فعلی
"""

TARGET = 20.0          # دمای هدف
DELTA = 1.0            # مقدار تغییر دما در هر عمل
MAX_STEPS = 50         # سقف ایمنی تعداد گام‌ها


# =================================================================
# 1) محیط (Environment)
# =================================================================
class TemperatureEnvironment:
    """محیط 2 خانه‌ای با دمای هدف 20 درجه."""

    def __init__(self, initial=(17.0, 24.0)):
        self.temps = list(initial)      # دمای فعلی هر خانه
        self.goal = False               # آیا هر دو خانه به هدف رسیده‌اند؟

    def percept(self):
        """دریافتی فعلی: دمای هر خانه."""
        return list(self.temps)

    def step(self, actions):
        """اعمال عمل هر خانه روی محیط (تغییر دما)."""
        for i, act in enumerate(actions):
            if act == "HEAT":
                self.temps[i] += DELTA
            elif act == "COOL":
                self.temps[i] -= DELTA
            # act == "NOOP" -> بدون تغییر
        self.goal = all(t == TARGET for t in self.temps)

    def show(self):
        print(f"   [خانه 1: {self.temps[0]:.0f}C]     [خانه 2: {self.temps[1]:.0f}C]")


# =================================================================
# 2) عامل واکنشی ساده (Simple Reflex Agent)
# =================================================================
class SimpleReflexAgent:
    """
    قواعد شرط-عمل (بدون حافظه، فقط بر اساس دریافتی فعلی):
      R1: IF دما < 20  -> HEAT
      R2: IF دما > 20  -> COOL
      R3: IF دما == 20 -> NOOP
    """

    def __init__(self, target=TARGET):
        self.target = target
        self.rules_fired = {"R1": 0, "R2": 0, "R3": 0}

    def decide(self, temp):
        """انتخاب عمل فقط از روی دمای فعلی یک خانه."""
        if temp < self.target:                 # R1
            self.rules_fired["R1"] += 1
            return "HEAT"
        elif temp > self.target:               # R2
            self.rules_fired["R2"] += 1
            return "COOL"
        else:                                  # R3
            self.rules_fired["R3"] += 1
            return "NOOP"

    def act(self, percepts):
        """ارائه عمل برای هر خانه بر اساس دریافتی فعلی."""
        return [self.decide(t) for t in percepts]


# =================================================================
# 3) حلقه اجرا (Agent-Environment Loop)
# =================================================================
def run(initial=(17.0, 24.0)):
    env = TemperatureEnvironment(initial)
    agent = SimpleReflexAgent()

    print("=" * 52)
    print(f"حالت اولیه محیط (هدف: {TARGET:.0f}C):")
    env.show()
    print("=" * 52)

    step = 0
    while not env.goal and step < MAX_STEPS:
        p = env.percept()                              # مرحله 3: حس کردن
        actions = agent.act(p)                         # مرحله 4: انتخاب عمل
        print(f"\nگام {step + 1}: دریافتی = ({p[0]:.0f}C, {p[1]:.0f}C)"
              f"  ->  عمل‌ها = {actions}")
        env.step(actions)                              # مرحله 5: اعمال عمل
        env.show()                                     # مرحله 6: آزمون پایان
        step += 1

    print("\n" + "=" * 52)
    if env.goal:
        print(f"نتیجه: هر دو خانه به {TARGET:.0f}C رسیدند ✔  (در {step} گام)")
    else:
        print("نتیجه: به سقف تعداد گام‌ها رسیدیم!")
    print(f"قاعد‌های اجراشده: R1(HEAT)={agent.rules_fired['R1']}, "
          f"R2(COOL)={agent.rules_fired['R2']}, R3(NOOP)={agent.rules_fired['R3']}")
    print("=" * 52)


if __name__ == "__main__":
    run(initial=(17.0, 24.0))
