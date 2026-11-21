# -*- coding: utf-8 -*-
"""
جلسه دوم مبانی هوش مصنوعی — عامل‌های واکنشی ساده (اسلاید ۳۱)
سینتکس مطابق مثال ۱ اسلاید (VacuumAgent)

ساختار هر عامل دقیقاً مانند نمونه استاد:
    __init__         → مقداردهی اولیه محیط و موقعیت عامل
    interpret_input  → دریافت ادراک (percept) از محیط
    rule_action      → قوانین شرط-عمل (condition-action) فقط بر اساس ادراک فعلی
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# تمرین 1: عامل جاروبرقی در محیط 2*2
# --------------------------------------------------------------------------- #
class VacuumAgent2x2:
    def __init__(self):
        self.location = 0  # percept
        # محیط 2*2 با 4 خانه (شماره‌گذاری خطی 0 تا 3)
        self.environment = ['dirty', 'dirty', 'dirty', 'dirty']

    def interpret_input(self):
        return self.environment[self.location]  # action

    def rule_action(self, state):
        if state == 'dirty':
            print("Cleaning cell", self.location)
            self.environment[self.location] = 'clean'
        else:
            print("Moving to the next cell")
            self.location = (self.location + 1) % len(self.environment)

    def goal_reached(self):
        return all(cell == 'clean' for cell in self.environment)


print("=" * 50)
print("Task 1: Vacuum agent in a 2x2 environment")
print("=" * 50)
agent = VacuumAgent2x2()
print("Initial environment:", agent.environment)
steps = 0
while not agent.goal_reached() and steps < 20:
    state = agent.interpret_input()
    agent.rule_action(state)
    steps += 1
print("Final environment:", agent.environment)
print("Goal reached:", agent.goal_reached(), "| steps:", steps)


# --------------------------------------------------------------------------- #
# تمرین 2: عامل سوئیچ نور در محیط 2*2   (هدف: خاموش کردن همه خانه‌های روشن)
# --------------------------------------------------------------------------- #
class LightSwitchAgent:
    def __init__(self):
        self.location = 0  # percept
        # محیط 2*2 با 4 چراغ؛ هر کلید فقط چراغ همان خانه را عوض می‌کند
        self.environment = ['on', 'on', 'on', 'on']

    def interpret_input(self):
        return self.environment[self.location]  # action

    def rule_action(self, state):
        # قانون شرط-عمل: اگر چراغ روشن است، کلیدش را بزن وگرنه جابه‌جا شو
        if state == 'on':
            print("Turning OFF light", self.location)
            self.environment[self.location] = 'off'
        else:
            print("Moving to the next switch")
            self.location = (self.location + 1) % len(self.environment)

    def goal_reached(self):
        # معیار کارایی: همه خانه‌ها خاموش باشند
        return all(light == 'off' for light in self.environment)


print()
print("=" * 50)
print("Task 2: Light switch agent in a 2x2 environment")
print("=" * 50)
agent = LightSwitchAgent()
print("Initial environment:", agent.environment)
steps = 0
while not agent.goal_reached() and steps < 20:
    state = agent.interpret_input()
    agent.rule_action(state)
    steps += 1
print("Final environment:", agent.environment)
print("Goal reached:", agent.goal_reached(), "| steps:", steps)


# --------------------------------------------------------------------------- #
# تمرین 3: عامل کنترل دما — محیط 2 خانه، هدف 20 درجه، دمای اولیه 17 و 24
# --------------------------------------------------------------------------- #
class ThermostatAgent:
    TARGET = 20  # دمای مورد نظر بر اساس 20 درجه

    def __init__(self):
        self.location = 0  # percept
        self.environment = [17, 24]  # دمای اولیه دو خانه

    def interpret_input(self):
        return self.environment[self.location]  # action

    def rule_action(self, state):
        if state < self.TARGET:
            print("Heating room", self.location, ":", state, "->", state + 1)
            self.environment[self.location] = state + 1
        elif state > self.TARGET:
            print("Cooling room", self.location, ":", state, "->", state - 1)
            self.environment[self.location] = state - 1
        else:
            print("Room", self.location, "is already at", self.TARGET, "degrees")
        self.location = (self.location + 1) % len(self.environment)

    def goal_reached(self):
        return all(t == self.TARGET for t in self.environment)


print()
print("=" * 50)
print("Task 3: Thermostat agent (2 rooms, target 20 degrees)")
print("=" * 50)
agent = ThermostatAgent()
print("Initial environment:", agent.environment)
steps = 0
while not agent.goal_reached() and steps < 30:
    state = agent.interpret_input()
    agent.rule_action(state)
    steps += 1
print("Final environment:", agent.environment)
print("Goal reached:", agent.goal_reached(), "| steps:", steps)


# --------------------------------------------------------------------------- #
# تمرین 4: عامل مرتب‌سازی اقلام بر اساس وزن (کوچک به بزرگ)
#           محیط خطی با 10 جرم فرضی
# --------------------------------------------------------------------------- #
class SortAgent:
    def __init__(self):
        self.location = 0  # percept: اشاره‌گر به جفت همسایه‌ی فعلی
        # محیط خطی با 10 جرم فرضی
        self.environment = [12, 5, 30, 8, 21, 3, 17, 9, 25, 14]

    def interpret_input(self):
        # ادراک: جفت اقلام مجاور در موقعیت فعلی
        return (self.environment[self.location],
                self.environment[self.location + 1])  # action

    def rule_action(self, pair):
        # قانون شرط-عمل: اگر چپ بزرگ‌تر از راست است، جابه‌جا کن؛ وگرنه جلو برو
        if pair[0] > pair[1]:
            print("Swap", pair[0], "<->", pair[1])
            self.environment[self.location] = pair[1]
            self.environment[self.location + 1] = pair[0]
        self.location += 1
        if self.location >= len(self.environment) - 1:
            print("End of the line -> start a new pass")
            self.location = 0

    def goal_reached(self):
        # معیار کارایی: از کوچک به بزرگ مرتب شده باشد
        return all(self.environment[i] <= self.environment[i + 1]
                   for i in range(len(self.environment) - 1))


print()
print("=" * 50)
print("Task 4: Auto sorting agent (10 items, small to big)")
print("=" * 50)
agent = SortAgent()
print("Initial environment:", agent.environment)
steps = 0
while not agent.goal_reached() and steps < 300:
    pair = agent.interpret_input()
    agent.rule_action(pair)
    steps += 1
print("Final environment:", agent.environment)
print("Goal reached:", agent.goal_reached(), "| steps:", steps)
