
"""
جلسه دوم مبانی هوش مصنوعی — عامل واکنشی ساده (Simple Reflex Agent)
تکلیف: مرتب‌سازی اقلام بر اساس وزن (از کوچک به بزرگ)
محیط: یک خط (خطی) با ۱۰ جرم مفروض

معماری عامل: فقط قواعد شرط-عمل (Condition-Action Rules) — بدون حافظه و بدون مدل
  ورودی : ادراک فعلی = (وزن خانه فعلی، وزن خانه بعدی یا None در انتهای خط)
  خروجی : یکی از عمل‌ها = GO_TO_START | SWAP | MOVE_RIGHT

الگوریتم: معادل مرتب‌سازی حبابی (Bubble Sort)
  - عامل از چپ به راست حرکت می‌کند و هر جفت مجاور را مقایسه می‌کند
  - اگر چپ > راست باشد، جابه‌جا می‌کند (SWAP)؛ جرم سنگین مثل «حباب» تا انتهای خط می‌رود
  - با رسیدن به انتهای خط، به خانه ۰ برمی‌گردد (GO_TO_START) و پیمایش بعدی شروع می‌شود
  - در هر پیمایش حداقل یک جرم سر جایش می‌نشیند ⇒ حداکثر n-1 = ۹ پیمایش
  - آزمون پایان توسط محیط (حلقه اجرا) انجام می‌شود، نه توسط عامل بی‌حافظه

پیچیدگی: O(n²) گام (بدترین حالت ~۹۰ گام برای n=10) و O(1) حافظه
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

N = 10          # تعداد جرم‌ها (محیط خطی ۱۰ تایی)
MAX_STEPS = 500 # سقف ایمنی تعداد گام‌ها


# =================================================================
# 1) محیط (Environment) — فقط ادراک می‌دهد و عمل‌ها را اعمال می‌کند
# =================================================================
class SortingEnvironment:
    """محیط خطی با N جرم؛ هیچ تصمیمی نمی‌گیرد."""

    def __init__(self, weights):
        if len(weights) != N:
            raise ValueError(f"محیط باید دقیقاً {N} جرم داشته باشد")
        self.weights = list(weights)
        self.swaps = 0   # شمارنده عمل‌های SWAP (فقط برای گزارش)

    def percept(self, pos):
        """ادراک فعلی عامل: (وزن خانه فعلی، وزن خانه بعدی یا None اگر انتهای خط باشد)."""
        cur = self.weights[pos]
        nxt = self.weights[pos + 1] if pos + 1 < N else None
        return cur, nxt

    def apply(self, action, pos):
        """اعمال عمل عامل روی محیط و بازگرداندن موقعیت جدید عامل."""
        if action == "SWAP":
            self.weights[pos], self.weights[pos + 1] = (
                self.weights[pos + 1], self.weights[pos])
            self.swaps += 1
            return pos                      # عامل سر جایش می‌ماند
        if action == "MOVE_RIGHT":
            return pos + 1                  # یک خانه به راست
        if action == "GO_TO_START":
            return 0                        # برگشت به ابتدای خط
        raise ValueError(f"عمل ناشناخته: {action}")

    def is_sorted(self):
        """آزمون پایان: همه جرم‌ها از کوچک به بزرگ چیده شده باشند."""
        return all(self.weights[i] <= self.weights[i + 1] for i in range(N - 1))

    def show(self, pos=0):
        """نمایش خط با اشاره‌گر موقعیت عامل."""
        line = "".join(f"[{w:2d}]" for w in self.weights)
        marker = " " * (4 * pos + 1) + "^"
        print(f"   {line}")
        print(f"   {marker}")


# =================================================================
# 2) عامل واکنشی ساده (Simple Reflex Agent)
# =================================================================
class SimpleReflexAgent:
    """
    قواعد شرط-عمل — فقط بر اساس ادراک فعلی (بدون حافظه، بدون مدل):
      R1: IF  انتهای خط است (nxt is None)  ->  GO_TO_START
      R2: IF  وزن فعلی > وزن بعدی          ->  SWAP
      R3: ELSE                              ->  MOVE_RIGHT
    """

    def __init__(self):
        self.location = 0                       # بخشی از ادراک (موقعیت فعلی)
        self.rules_fired = {"R1": 0, "R2": 0, "R3": 0}

    def decide(self, percept):
        """انتخاب عمل فقط از روی ادراک فعلی (تریگر اول برنده)."""
        cur, nxt = percept
        if nxt is None:                         # R1
            self.rules_fired["R1"] += 1
            return "GO_TO_START"
        if cur > nxt:                           # R2
            self.rules_fired["R2"] += 1
            return "SWAP"
        self.rules_fired["R3"] += 1             # R3
        return "MOVE_RIGHT"


# =================================================================
# 3) حلقه اجرا (Agent-Environment Loop)
# =================================================================
def run(weights, verbose=True):
    env = SortingEnvironment(weights)
    agent = SimpleReflexAgent()

    print("=" * 56)
    print("عامل واکنشی ساده — مرتب‌سازی ۱۰ جرم از کوچک به بزرگ")
    print("=" * 56)
    print("حالت اولیه محیط:")
    env.show(agent.location)

    steps = 0
    passes = 0
    while not env.is_sorted() and steps < MAX_STEPS:   # آزمون پایان: بر عهده محیط
        percept = env.percept(agent.location)          # مرحله ۱: حس کردن
        action = agent.decide(percept)                 # مرحله ۲: قواعد شرط-عمل
        if verbose:
            print(f"گام {steps + 1:3d} | موقعیت {agent.location} | "
                  f"ادراک {percept} -> {action}")
        agent.location = env.apply(action, agent.location)  # مرحله ۳: اعمال عمل
        if action == "GO_TO_START":
            passes += 1
            if verbose:
                print(f"   ---- پایان پیمایش {passes} ----")
                env.show(agent.location)
        steps += 1

    print("-" * 56)
    if env.is_sorted():
        print(f"نتیجه: مرتب شد ✔  (از کوچک به بزرگ) در {steps} گام و {passes} پیمایش")
    else:
        print("نتیجه: به سقف تعداد گام‌ها رسیدیم!")
    print(f"عمل‌های SWAP: {env.swaps} | "
          f"R1(GO_TO_START)={agent.rules_fired['R1']}, "
          f"R2(SWAP)={agent.rules_fired['R2']}, "
          f"R3(MOVE_RIGHT)={agent.rules_fired['R3']}")
    print("وضعیت نهایی محیط:")
    env.show(agent.location)
    print("=" * 56)
    return env.is_sorted()


if __name__ == "__main__":
    # محیط خطی با ۱۰ جرم مفروض (وزن‌ها از چپ به راست در خط چیده شده‌اند)
    initial_weights = [12, 5, 30, 8, 21, 3, 17, 9, 25, 14]
    run(initial_weights, verbose=True)
