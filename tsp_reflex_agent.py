# -*- coding: utf-8 -*-
"""
جلسه مبانی هوش مصنوعی — عامل واکنشی هدف‌گر (Goal-based Reflex Agent)
پیاده‌سازی مسئله فروشنده دوره‌گرد (TSP)
سینتکس مطابق مثال‌های فایل reflex_agent_tasks.py

ساختار هر عامل دقیقاً مانند نمونه استاد:
    __init__         → مقداردهی اولیه محیط (ماتریس فاصله شهرها) و موقعیت عامل
    interpret_input  → دریافت ادراک (percept) از محیط: شهر فعلی + شهرهای بازدیدنشده
    rule_action      → قوانین شرط-عمل (condition-action) فقط بر اساس ادراک فعلی و هدف
    goal_reached     → شرط تحقق هدف: بازدید همه شهرها و بازگشت به شهر مبدأ

الگوریتم:
    1) حالت داخلی: شهر فعلی، شهرهای بازدیدشده، مسیر، مجموع هزینه
    2) ادراک: شهر فعلی و فهرست شهرهای بازدیدنشده به‌همراه فاصله‌شان
    3) قانون شرط-عمل:
         - اگر شهر بازدیدنشده‌ای هست → حرکت به نزدیک‌ترین شهر بازدیدنشده
         - اگر همه بازدید شدند و شهر فعلی ≠ مبدأ → حرکت به سمت شهر مبدأ
    4) هدف: همه شهرها یک‌بار بازدید شوند و عامل به شهر مبدأ برگردد
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# عامل واکنشی هدف‌گر: مسئله فروشنده دوره‌گرد (TSP)
# --------------------------------------------------------------------------- #
class TSPReflexAgent:
    def __init__(self):
        # محیط: 5 شهر با ماتریس فاصله (نمادها + ماتریس متناظر)
        self.cities = ['A', 'B', 'C', 'D', 'E']
        self.environment = [
            #  A   B   C   D   E
            [0, 10, 15, 20, 25],   # A
            [10, 0, 35, 25, 30],   # B
            [15, 35, 0, 30, 20],   # C
            [20, 25, 30, 0, 15],   # D
            [25, 30, 20, 15, 0],   # E
        ]
        self.start = 0            # شهر مبدأ (خانه عامل)
        self.location = 0         # percept: شهر فعلی که عامل در آن است
        # حالت داخلی عامل
        n = len(self.cities)
        self.visited = [False] * n
        self.visited[self.start] = True
        self.route = [self.start]
        self.cost = 0

    def interpret_input(self):
        # ادراک: شهر فعلی + فهرست شهرهای بازدیدنشده به‌همراه فاصله از شهر فعلی
        unvisited = [(j, self.environment[self.location][j])
                     for j in range(len(self.cities))
                     if not self.visited[j]]
        return (self.location, unvisited)  # percept

    def rule_action(self, percept):
        current, unvisited = percept
        if unvisited:
            # قانون 1: هنوز شهر بازدیدنشده هست → به نزدیک‌ترین شهر بازدیدنشده برو
            nearest, dist = min(unvisited, key=lambda x: x[1])
            print("From", self.cities[current], "move to nearest unvisited city",
                  self.cities[nearest], "| distance:", dist)
            self.location = nearest
            self.visited[nearest] = True
            self.route.append(nearest)
            self.cost += dist
        elif current != self.start:
            # قانون 2: همه بازدید شدند و شهر فعلی مبدأ نیست → به سمت مبدأ برگرد
            dist = self.environment[current][self.start]
            print("All cities visited -> return home to",
                  self.cities[self.start], "| distance:", dist)
            self.location = self.start
            self.route.append(self.start)
            self.cost += dist
        else:
            # قانون 3: همه بازدید شدند و در مبدأ هستیم → هیچ عملی لازم نیست
            print("Tour completed at", self.cities[self.start])

    def goal_reached(self):
        # معیار هدف: همه شهرها بازدید شده باشند و عامل در شهر مبدأ ایستاده باشد
        return (all(self.visited) and self.location == self.start
                and len(self.route) > 1)

    def print_result(self):
        path = " -> ".join(self.cities[c] for c in self.route)
        print("Route:", path)
        print("Total cost:", self.cost)


print("=" * 50)
print("Goal-based reflex agent: Travelling Salesman Problem (TSP)")
print("=" * 50)
agent = TSPReflexAgent()
print("Cities:", agent.cities)
print("Start city:", agent.cities[agent.start])
print("Initial location:", agent.cities[agent.location])
steps = 0
while not agent.goal_reached() and steps < 30:
    percept = agent.interpret_input()
    agent.rule_action(percept)
    steps += 1
print("Visited all cities:", all(agent.visited))
print("Final location:", agent.cities[agent.location])
print("Goal reached:", agent.goal_reached(), "| steps:", steps)
agent.print_result()
