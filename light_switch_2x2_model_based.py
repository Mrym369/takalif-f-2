"""
تمرین 6: عامل واکنشی مدل‌گرا (Model-based Reflex Agent)
مسئله: سوئیچ نور در محیط 2*2 — هدف: خاموش کردن همه خانه‌های روشن
سینتکس مطابق مثال 2 (عامل جاروبرقی مدل‌گرا) داخل جزوه
"""


class LightSwitchAgent:
    def __init__(self):
        self.environment = ['on', 'on', 'on', 'on']  # محیط 2*2 = 4 چراغ
        self.position = 0
        self.model = {}                                # نقشه ذنی عامل از محیط

    def perceive(self):
        return self.environment[self.position]

    def update_model(self, perception):
        self.model[self.position] = perception

    def predict_future_state(self):
        if self.model.get(self.position) == 'on':
            # If the current light is on, predict it will remain on
            return 'on'
        else:
            # Otherwise, predict it will stay off
            return 'off'

    def decide_action(self):
        perception = self.perceive()
        self.update_model(perception)
        if perception == 'on':
            return 'turn_off'
        else:
            future_state = self.predict_future_state()
            if future_state == 'on':
                return 'turn_off'
            else:
                return 'move'

    def act(self, action):
        if action == 'turn_off':
            self.environment[self.position] = 'off'
        elif action == 'move':
            self.position = (self.position + 1) % len(self.environment)


agent = LightSwitchAgent()
print("Initial Environment:", agent.environment)
for _ in range(7):
    action = agent.decide_action()
    agent.act(action)
    print(f"Position: {agent.position}, Action: {action}, "
          f"Environment: {agent.environment}, Model: {agent.model}")

if all(light == 'off' for light in agent.environment):
    print("All lights are OFF - Goal reached!")
else:
    print("Goal not reached yet!")
