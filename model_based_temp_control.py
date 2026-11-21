"""
عامل واکنشی مدل‌محور (Model-Based Reflex Agent)
مسئله: کنترل دمای محیط 2 خانه‌ای
  - دمای هدف: 20 درجه
  - دمای اولیه: خانه1 = 17 درجه ، خانه2 = 24 درجه

الگوریتم (6 مرحله در هر گام):
  1) PERCEIVE : حسِ دمای واقعی هر دو خانه
  2) PREDICT  : پیش‌بینی با مدل گذار   p̂ = state + model(last_action)
  3) UPDATE   : خطا = مشاهده − پیش‌بینی (تشخیص اختلال) و به‌روزرسانی state
  4) TEST     : آزمون پایان (هر دو خانه == 20)
  5) DECIDE   : قواعد شرط-عمل روی state + قانون پیش‌بینی یک‌قدمی
  6) ACT      : اعمال عمل روی محیط و ذخیره last_action

تفاوت با عامل ساده‌عکس‌العملی (simple_reflex_temp_control.py):
  - حالت داخلی (state) و مدل گذار دارد → نویز/اختلال محیط را تشخیص می‌دهد
  - تصمیم بر اساس state به‌روزشده گرفته می‌شود، نه دریافتی خام
"""

import sys

TARGET = 20.0          # دمای هدف
DELTA = 1.0            # مقدار تغییر دما در هر عمل
MAX_STEPS = 50         # سقف ایمنی تعداد گام‌ها


# =================================================================
# 1) محیط (Environment)
# =================================================================
class TemperatureEnvironment:
    """محیط 2 خانه‌ای با دمای هدف 20 درجه (با امکان اختلال)."""

    def __init__(self, initial=(17.0, 24.0), disturbances=None):
        self.temps = list(initial)      # دمای واقعی فعلی هر خانه
        self.goal = False               # آیا هر دو خانه به هدف رسیده‌اند؟
        self.step_no = 0                # شماره گام جاری
        # اختلال‌ها: {شماره گام: (افزایش خانه1, افزایش خانه2)}
        # مثال: باز شدن پنجره در گام 3 برای خانه 1 → {3: (-1.0, 0.0)}
        self.disturbances = disturbances or {}

    def percept(self):
        """دریافتی فعلی: دمای واقعی هر خانه."""
        return list(self.temps)

    def step(self, actions):
        """اعمال عمل هر خانه روی محیط + اختلال احتمالی همان گام."""
        self.step_no += 1
        for i, act in enumerate(actions):
            if act == "HEAT":
                self.temps[i] += DELTA
            elif act == "COOL":
                self.temps[i] -= DELTA
            # act == "NOOP" -> بدون تغییر
        # اعمال اختلال (اگر برای این گام تعریف شده باشد)
        d = self.disturbances.get(self.step_no)
        if d:
            for i in range(len(self.temps)):
                self.temps[i] += d[i]
        self.goal = all(t == TARGET for t in self.temps)

    def show(self):
        print(f"   [خانه 1: {self.temps[0]:.0f}C]     [خانه 2: {self.temps[1]:.0f}C]")


# =================================================================
# 2) عامل مدل‌محور (Model-Based Agent)
# =================================================================
class ModelBasedAgent:
    """
    عامل مدل‌محور:
      - model  : مدل گذار محیط (اثر هر عمل روی دما)
      - state  : حالت داخلی = دمای باورشده هر خانه
      - predict: پیش‌بینی دمای فعلی از state و last_action
      - update : ترکیب مشاهده با پیش‌بینی و محاسبه خطا (تشخیص اختلال)
      - decide : قواعد شرط-عمل روی state + قانون پیش‌بینی یک‌قدمی
    """

    def __init__(self, initial=(17.0, 24.0), target=TARGET):
        self.target = target
        self.model = {"HEAT": +1, "COOL": -1, "NOOP": 0}   # مدل گذار محیط
        self.state = list(initial)                          # حالت داخلی
        self.last_action = ["NOOP", "NOOP"]                 # عمل اعمال‌شده در گام قبل
        self.rules_fired = {"R1": 0, "R2": 0, "R3": 0}      # فقط برای گزارش

    # ---------- مرحله 2: پیش‌بینی با مدل ----------
    def predict(self):
        """p̂ = state + model(last_action)  (دمایی که مدل انتظار دارد)."""
        return [self.state[i] + self.model[self.last_action[i]]
                for i in range(len(self.state))]

    # ---------- مرحله 3: به‌روزرسانی حالت ----------
    def update(self, percept):
        """ترکیب مشاهده و مدل؛ خطا = مشاهده − پیش‌بینی."""
        predicted = self.predict()
        errors = [percept[i] - predicted[i] for i in range(len(percept))]
        self.state = list(percept)          # state ← مشاهده (اگر حسگر سالم بود)
        return predicted, errors

    # ---------- مرحله 5: تصمیم‌گیری ----------
    def decide(self, i):
        """انتخاب عمل خانه i بر اساس state (نه دریافتی خام)."""
        t = self.state[i]
        if t < self.target:                         # R1: سردتر از هدف
            action = "HEAT"
            self.rules_fired["R1"] += 1
        elif t > self.target:                       # R2: گرم‌تر از هدف
            action = "COOL"
            self.rules_fired["R2"] += 1
        else:                                       # R3: دقیقاً روی هدف
            action = "NOOP"
            self.rules_fired["R3"] += 1

        # قانون پیش‌بینی یک‌قدمی: اگر عمل، دما را از هدف دورتر کرد → NOOP
        nxt = t + self.model[action]
        if abs(nxt - self.target) > abs(t - self.target):
            action = "NOOP"
        return action

    # ---------- چرخه اصلی عامل: حس + پیش‌بینی + به‌روزرسانی + تصمیم ----------
    def act(self, percept):
        predicted, errors = self.update(percept)            # مراحل 2 و 3
        actions = [self.decide(i) for i in range(len(percept))]  # مرحله 5
        self.last_action = actions                          # مرحله 6 (ذخیره برای بعد)
        return actions, predicted, errors


# =================================================================
# 3) حلقه اجرا (Agent-Environment Loop)
# =================================================================
def run(initial=(17.0, 24.0), disturbances=None, title="اجرا"):
    env = TemperatureEnvironment(initial, disturbances)
    agent = ModelBasedAgent(initial)

    print("=" * 62)
    print(f"{title} | هدف: {TARGET:.0f}C | دمای اولیه: "
          f"خانه1={initial[0]:.0f}C ، خانه2={initial[1]:.0f}C")
    if disturbances:
        print(f"اختلال تعریف‌شده: {disturbances}")
    print("=" * 62)
    print("حالت اولیه:")
    env.show()

    step = 0
    while not env.goal and step < MAX_STEPS:
        p = env.percept()                                   # 1) PERCEIVE
        actions, predicted, errors = agent.act(p)           # 2,3,5,6)

        print(f"\nگام {step + 1}:")
        print(f"   دریافتی      = ({p[0]:.0f}C, {p[1]:.0f}C)")
        print(f"   پیش‌بینی مدل = ({predicted[0]:.0f}C, {predicted[1]:.0f}C)")
        err_txt = f"   خطا         = ({errors[0]:+.0f}, {errors[1]:+.0f})"
        if any(errors):
            err_txt += "   <<< اختلال شناسایی شد"
        print(err_txt)
        print(f"   state        = ({agent.state[0]:.0f}C, {agent.state[1]:.0f}C)"
              f"  ->  عمل‌ها = {actions}")

        env.step(actions)                                   # 4) TEST (داخل step)
        env.show()
        step += 1

    print("\n" + "=" * 62)
    if env.goal:
        print(f"نتیجه: هر دو خانه به {TARGET:.0f}C رسیدند ✔  (در {step} گام)")
    else:
        print("نتیجه: به سقف تعداد گام‌ها رسیدیم!")
    print(f"قاعد‌های اجراشده: R1(HEAT)={agent.rules_fired['R1']}, "
          f"R2(COOL)={agent.rules_fired['R2']}, R3(NOOP)={agent.rules_fired['R3']}")
    print("=" * 62)
    return step


if __name__ == "__main__":
    # نمایش درست متن فارسی در کنسول ویندوز
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # اجرای 1: شرایط عادی (بدون اختلال)
    run(initial=(17.0, 24.0), title="اجرای 1 — شرایط عادی")

    print("\n\n")

    # اجرای 2: اختلال محیطی (در گام 3 پنجره خانه 1 باز می‌شود: -1 درجه)
    run(initial=(17.0, 24.0),
        disturbances={3: (-1.0, 0.0)},
        title="اجرای 2 — با اختلال محیطی")
