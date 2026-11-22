# -*- coding: utf-8 -*-
"""
مسئله: برنامه‌ریزی مسیر (Route Planning) — عامل هدف‌گرا (Goal-based Agent)

الگوریتم: جستجوی A* در گراف وزن‌دار شهرها
    f(n) = g(n) + h(n)
    g(n) = هزینه واقعی مسیر از مبدأ تا گره n
    h(n) = برآورد هزینه از n تا هدف (heuristic قابل قبول / admissible)

مراحل الگوریتم:
    1. open ← صف اولویت‌دار از گره‌ها با کلید f
    2. برداشتن گره با کمترین f؛ اگر هدف باشد → مسیر برگردان (آزمون هدف)
    3. برای هر همسایه: اگر g جدید بهتر از بهترین g ثبت‌شده باشد، به‌روزرسانی و درج در open
    4. اگر open خالی شد و هدف نرسید → مسیری وجود ندارد

ساختار عامل دقیقاً مانند نمونه استاد:
    __init__         → مقداردهی اولیه محیط، مبدأ و هدف
    interpret_input  → دریافت ادراک (percept) از محیط
    rule_action      → قانون شرط-عمل هدف‌مند (برنامه‌ریزی A* + اجرای قدم بعدی)
    goal_reached     → آزمون هدف (goal test)

تفاوت با عامل واکنشی: عامل هدف‌گرا فقط با ادراک فعلی کار نمی‌کند؛ هدف را
می‌شناسد، برای رسیدن به آن جستجو (برنامه‌ریزی) می‌کند و سپس نقشه را اجرا می‌کند.
"""

import sys
import heapq

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# عامل هدف‌گرا: برنامه‌ریزی مسیر از مبدأ A تا هدف G با جستجوی A*
# --------------------------------------------------------------------------- #
class RouteAgent:
    def __init__(self):
        # محیط: گراف وزن‌دار 7 شهر (نام شهر -> {همسایه: هزینه مسیر})
        self.environment = {
            'A': {'B': 5, 'C': 2},
            'B': {'A': 5, 'D': 4, 'E': 12},
            'C': {'A': 2, 'D': 7, 'F': 8},
            'D': {'B': 4, 'C': 7, 'E': 3, 'G': 6},
            'E': {'B': 12, 'D': 3, 'G': 7},
            'F': {'C': 8, 'G': 4},
            'G': {'D': 6, 'E': 7, 'F': 4},
        }
        # برآورد هزینه تا هدف G (heuristic)؛ قابل قبول (admissible) یعنی
        # هرگز بیشتر از هزینه واقعی کوتاه‌ترین مسیر تا G نیست
        self.heuristic = {'A': 12, 'B': 9, 'C': 10, 'D': 6, 'E': 6, 'F': 4, 'G': 0}
        self.start = 'A'
        self.goal = 'G'
        self.location = self.start   # percept: موقعیت فعلی عامل
        self.route = []              # مسیر برنامه‌ریزی‌شده (شهرهای بعد از مبدأ)
        self.visited = [self.start]  # ترتیب واقعی طی‌شده
        self.cost = 0                # هزینه واقعی طی‌شده
        self.planned = False         # آیا تاکنون نقشه (plan) ساخته شده است؟
        self.failed = False          # آیا مسیری وجود ندارد؟

    def interpret_input(self):
        # ادراک: همسایه‌های مستقیم شهر فعلی به همراه هزینه یال و برآورد تا هدف
        return [(n, w, self.heuristic[n])
                for n, w in self.environment[self.location].items()]

    def plan(self):
        # جستجوی A* با صف اولویت (heap)؛ کلید مرتب‌سازی: f = g + h
        open_list = [(self.heuristic[self.start], 0, self.start, [self.start])]
        best_g = {self.start: 0}
        while open_list:
            f, g, city, path = heapq.heappop(open_list)
            if city == self.goal:                # آزمون هدف
                return path
            if g > best_g.get(city, float('inf')):
                continue                         # با هزینه بهتری دیده شده؛ نادیده بگیر
            for nxt, w in self.environment[city].items():
                ng = g + w
                if ng < best_g.get(nxt, float('inf')):
                    best_g[nxt] = ng
                    heapq.heappush(open_list, (ng + self.heuristic[nxt], ng, nxt, path + [nxt]))
        return []                                # مسیری به هدف وجود ندارد

    def rule_action(self, percept):
        # قانون شرط-عمل هدف‌مند
        neighbors = {n: w for n, w, _ in percept}

        if not self.planned:
            # شرط: اگر نقشه‌ای نداریم، اول برای رسیدن به هدف برنامه‌ریزی کن (A*)
            print("Percept at", self.location, ":", percept)
            path = self.plan()
            self.planned = True
            if not path:
                print("No route found to", self.goal)
                self.failed = True
                return
            print("Planned route:", " -> ".join(path))
            self.route = path[1:]               # شهرهای بعد از مبدأ

        # شرط: قدم بعدی مسیر برنامه‌ریزی‌شده را با توجه به ادراک همسایه‌ها اجرا کن
        next_city = self.route.pop(0)
        w = neighbors[next_city]                # هزینه حرکت از ادراک فعلی خوانده می‌شود
        print("Moving", self.location, "->", next_city, "| cost:", w)
        self.location = next_city
        self.visited.append(next_city)
        self.cost += w

    def goal_reached(self):
        # آزمون هدف: عامل به شهر مقصد رسیده باشد
        return self.location == self.goal


print("=" * 50)
print("Task: Goal-based route planning agent (A*)")
print("=" * 50)
agent = RouteAgent()
print("Start:", agent.start, "| Goal:", agent.goal)
print("Initial location:", agent.location)
steps = 0
while not agent.goal_reached() and not agent.failed and steps < 20:
    percept = agent.interpret_input()
    agent.rule_action(percept)
    steps += 1
print("Route taken:", " -> ".join(agent.visited))
print("Total cost:", agent.cost)
print("Goal reached:", agent.goal_reached(), "| steps:", steps)
