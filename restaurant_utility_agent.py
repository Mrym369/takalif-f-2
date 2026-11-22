# -*- coding: utf-8 -*-
"""
عامل واکنشی مبتنی بر سودمندی — سیستم توصیه‌گر رستوران
(Utility-based Reflex Agent for Restaurant Recommendation)

ساختار هر عامل دقیقاً مانند نمونه استاد (reflex_agent_tasks.py):
    __init__         → مقداردهی اولیه محیط (لیست رستوران‌ها) و ترجیحات کاربر
    interpret_input  → دریافت ادراک (percept) از محیط
    rule_action      → محاسبه تابع سودمندی و قانون شرط-عمل فقط بر اساس ادراک فعلی
    goal_reached     → معیار پایان: همه رستوران‌ها ارزیابی شده‌اند؟

الگوریتم:
    U(r) = w_q * U_q(quality) + w_p * U_p(price) + w_l * U_l(distance)
    U_q = quality / 10
    U_p = clamp(1 - price / max_price, 0, 1)
    U_l = clamp(1 - distance / max_distance, 0, 1)
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# تمرین: عامل واکنشی مبتنی بر سودمندی — توصیه رستوران
# --------------------------------------------------------------------------- #
class RestaurantUtilityAgent:
    # آستانه سودمندی: زیر این مقدار، پیشنهادی داده نمی‌شود
    MIN_UTILITY = 0.3

    def __init__(self, restaurants, weights, max_price, max_distance):
        # محیط: لیست رستوران‌ها؛ هر رستوران: (نام، کیفیت 0..10، قیمت، فاصله)
        self.environment = restaurants
        # ترجیحات کاربر: وزن کیفیت، قیمت، موقعیت (مجموع باید 1 باشد)
        self.w_quality, self.w_price, self.w_location = weights
        self.max_price = max_price        # حداکثر قیمت قابل قبول کاربر
        self.max_distance = max_distance  # حداکثر فاصله قابل قبول کاربر
        # حالت داخلی عامل (کمینه حافظه برای نگه‌داشتن بهترین گزینه)
        self.index = 0                    # شاخص رستوران جاری
        self.best_utility = -1.0          # بهترین سودمندی تاکنون
        self.best_restaurant = None       # بهترین رستوران تاکنون

    def interpret_input(self):
        # ادراک: فقط ویژگی‌های رستورانی که هم‌اکنون جلوی عامل است
        return self.environment[self.index]  # percept

    # ------------------------- توابع سودمندی جزئی ------------------------- #
    def utility_quality(self, quality):
        # کیفیت بالاتر → سودمندی بیشتر (نرمال در بازه 0..1)
        return quality / 10.0

    def utility_price(self, price):
        # ارزان‌تر → سودمندی بیشتر؛ خارج از بودجه → 0
        return max(0.0, min(1.0, 1.0 - price / self.max_price))

    def utility_location(self, distance):
        # نزدیک‌تر → سودمندی بیشتر؛ خارج از محدوده → 0
        return max(0.0, min(1.0, 1.0 - distance / self.max_distance))

    def total_utility(self, percept):
        _name, quality, price, distance = percept
        # سودمندی کل = میانگین وزنی سودمندی‌های جزئی
        return (self.w_quality * self.utility_quality(quality)
                + self.w_price * self.utility_price(price)
                + self.w_location * self.utility_location(distance))

    def rule_action(self, percept):
        name, quality, price, distance = percept
        u = self.total_utility(percept)
        print("Percept:", name, "| quality =", quality, ", price =", price,
              ", distance =", distance, "-> U =", round(u, 3))
        # قانون شرط-عمل: اگر سودمندی این گزینه از بهترینِ تاکنون بیشتر است، جایگزین شود
        if u > self.best_utility:
            self.best_utility = u
            self.best_restaurant = percept
            print("   * new best ->", name, "| U =", round(u, 3))
        self.index += 1

    def goal_reached(self):
        # معیار کارایی: همه رستوران‌ها ارزیابی شده باشند
        return self.index >= len(self.environment)

    def recommend(self):
        if self.best_restaurant is None or self.best_utility < self.MIN_UTILITY:
            return "No suitable restaurant found (U_min = " + str(self.MIN_UTILITY) + ")"
        return (self.best_restaurant[0]
                + " (U = " + str(round(self.best_utility, 3)) + ")")


# ------------------------------ داده محیط ---------------------------------- #
# هر رستوران: (نام، کیفیت غذا 0..10، قیمت (هزار تومان)، فاصله (کیلومتر))
RESTAURANTS = [
    ("Kababi-ye Sadr",       9, 250, 2.0),
    ("Ghadim Sazan",         7, 120, 4.5),
    ("Shahrvand Restaurant", 8, 300, 1.0),
    ("Pizza Sazi",           6, 150, 0.8),
    ("Traditional Dizi",     8, 180, 6.0),
    ("Fast Food Mahdi",      5,  90, 3.0),
    ("Persian Rice & Kebab", 9, 350, 5.5),
    ("Cafe Nardan",          7, 200, 2.5),
]


print("=" * 50)
print("Task 1: Restaurant recommendation (quality-focused user)")
print("weights: quality=0.6, price=0.25, location=0.15")
print("=" * 50)
agent = RestaurantUtilityAgent(RESTAURANTS,
                               weights=(0.6, 0.25, 0.15),
                               max_price=400,
                               max_distance=8)
print("Initial restaurants:", len(agent.environment))
steps = 0
while not agent.goal_reached():
    percept = agent.interpret_input()
    agent.rule_action(percept)
    steps += 1
print("Recommendation:", agent.recommend(), "| steps:", steps)


print()
print("=" * 50)
print("Task 2: Restaurant recommendation (budget & near user)")
print("weights: quality=0.2, price=0.5, location=0.3")
print("=" * 50)
agent = RestaurantUtilityAgent(RESTAURANTS,
                               weights=(0.2, 0.5, 0.3),
                               max_price=200,
                               max_distance=3)
print("Initial restaurants:", len(agent.environment))
steps = 0
while not agent.goal_reached():
    percept = agent.interpret_input()
    agent.rule_action(percept)
    steps += 1
print("Recommendation:", agent.recommend(), "| steps:", steps)
