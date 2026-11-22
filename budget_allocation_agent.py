# -*- coding: utf-8 -*-
"""
عامل واکنشی هدف‌گرا — بهینه‌سازی تخصیص بودجه (Budget Allocation)
وزن منابع: 3، 8، 17   |   بودجه کل معین

ساختار عامل دقیقاً مانند نمونه استاد:
    __init__         → مقداردهی اولیه محیط (بودجه کل) و اشاره‌گر عامل
    interpret_input  → دریافت ادراک (percept) از محیط
    rule_action      → قوانین شرط-عمل (condition-action) فقط بر اساس ادراک فعلی
    goal_reached     → آزمون هدف (goal test)
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# عامل تخصیص بودجه: هر گام، بودجه را به منبعی با بیشترین کسری نسبت به
# سهم ایده‌آل (متناسب با وزن) اختصاص می‌دهد تا بودجه کاملاً و متناسب توزیع شود
# --------------------------------------------------------------------------- #
class BudgetAllocationAgent:
    WEIGHTS = [3, 8, 17]  # ارزش وزنی سه منبع

    def __init__(self, total_budget=280, step=10):
        self.weights = list(self.WEIGHTS)
        self.total_weight = sum(self.weights)      # 3 + 8 + 17 = 28
        self.budget = total_budget                 # بودجه کل معین
        self.remaining = total_budget              # بودجه باقی‌مانده (محیط)
        self.allocation = [0] * len(self.weights)  # تخصیص فعلی هر منبع
        # سهم ایده‌آل هر منبع: b_i = B * w_i / Σw
        self.targets = [total_budget * w / self.total_weight
                        for w in self.weights]
        self.step = step                           # حداکثر بودجه در هر گام
        self.location = 0                          # اشاره‌گر: منبع در حال بررسی

    def interpret_input(self):
        # ادراک: بودجه باقی‌مانده و کسری هر منبع نسبت به سهم ایده‌آل
        deficits = [t - a for t, a in zip(self.targets, self.allocation)]
        return self.remaining, deficits

    def rule_action(self, percept):
        remaining, deficits = percept
        if remaining <= 0:
            return
        # قانون شرط-عمل: اگر بودجه مانده، منبع دارای بیشترین کسری را انتخاب کن
        self.location = max(range(len(deficits)), key=lambda i: deficits[i])
        deficit = deficits[self.location]
        # حداقل ۱ واحد (تا بودجه‌ای باقی نماند)، حداکثر گام یا مقدار کسری
        amount = min(self.step, remaining, max(1, int(deficit)))
        print("Allocate", amount, "to source", self.location,
              "(weight", self.weights[self.location], ", deficit",
              round(deficit, 2), ")")
        self.allocation[self.location] += amount
        self.remaining -= amount

    def goal_reached(self):
        # هدف: بودجه کاملاً مصرف شود و هر منبع در فاصله کمتر از ۱ واحد
        # از سهم ایده‌آل خود باشد (کمینه انحراف ممکن با اعداد صحیح)
        return (self.remaining == 0 and
                all(abs(a - t) < 1.0
                    for a, t in zip(self.allocation, self.targets)))


# --------------------------------------------------------------------------- #
# Task 1: بودجه 280 (مضرب 28 → سهم‌ها صحیح: 30، 80، 170)
# --------------------------------------------------------------------------- #
print("=" * 50)
print("Task 1: Budget allocation agent (budget = 280, weights 3/8/17)")
print("=" * 50)
agent = BudgetAllocationAgent(total_budget=280, step=10)
print("Weights:", agent.weights, "| total weight:", agent.total_weight)
print("Ideal shares:", [round(t, 2) for t in agent.targets])
print("Initial allocation:", agent.allocation,
      "| remaining budget:", agent.remaining)
steps = 0
while not agent.goal_reached() and steps < 10000:
    percept = agent.interpret_input()
    agent.rule_action(percept)
    steps += 1
print("Final allocation:", agent.allocation)
print("Ideal shares    :", [round(t, 2) for t in agent.targets])
print("Deviation       :",
      [round(a - t, 2) for a, t in zip(agent.allocation, agent.targets)])
print("Goal reached:", agent.goal_reached(), "| steps:", steps)


# --------------------------------------------------------------------------- #
# Task 2: بودجه 100 (مضرب 28 نیست → اعداد صحیح نزدیک‌ترین سهم: رُند کردن)
# --------------------------------------------------------------------------- #
print()
print("=" * 50)
print("Task 2: Budget allocation agent (budget = 100, weights 3/8/17)")
print("=" * 50)
agent = BudgetAllocationAgent(total_budget=100, step=10)
print("Weights:", agent.weights, "| total weight:", agent.total_weight)
print("Ideal shares:", [round(t, 2) for t in agent.targets])
print("Initial allocation:", agent.allocation,
      "| remaining budget:", agent.remaining)
steps = 0
while not agent.goal_reached() and steps < 10000:
    percept = agent.interpret_input()
    agent.rule_action(percept)
    steps += 1
print("Final allocation:", agent.allocation)
print("Ideal shares    :", [round(t, 2) for t in agent.targets])
print("Deviation       :",
      [round(a - t, 2) for a, t in zip(agent.allocation, agent.targets)])
print("Goal reached:", agent.goal_reached(), "| steps:", steps)
