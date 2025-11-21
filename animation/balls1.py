import tkinter as tk
import json


class Ball:
    def __init__(self, simulation, x, y, r, m, color='pink2'):
        self.simulation = simulation
        self.config = simulation.config
        self.x = x
        self.y = y
        self.r = r
        self.m = m
        self.v = self.config['speeds']['initial_velocity']
        self.wr = self.config['behavior']['water_resistance']
        self.f_a = self.m * 0.02
        self.f_s = 0.05 * (self.v * 0.4 * 3.14 * self.r)
        self.color = color
        self.is_moving = True
        self.phase = 'falling'
        self.graphic_id = None


class Simulation:
    def __init__(self, config):
        self.config = config
        self.width = config['width']
        self.height = config['height']
        self.water_level = self.height // 2
        self.ground_level = self.height - 20
        self.balls = []

    def add_ball(self, x, y, r, m, color='pink2'):
        ball = Ball(self, x, y, r, m, color)
        self.balls.append(ball)
        return ball

    def update(self):
        for ball in self.balls:
            if not ball.is_moving:
                continue
            current_bottom = ball.y + ball.r
            if ball.phase == 'falling':
                self.update_falling(ball, current_bottom)
            elif ball.phase == 'water':
                self.update_water(ball, current_bottom)
            elif ball.phase == 'bounce1':
                self.update_bounce1(ball, current_bottom)
            elif ball.phase == 'bounce2':
                self.update_bounce2(ball, current_bottom)
            elif ball.phase == 'stopping':
                self.update_stopping(ball)

    def update_falling(self, ball, current_bottom):
        if current_bottom < self.water_level:
            ball.y += ball.v + ball.m * 0.005
        else:
            ball.phase = 'water'

    def update_water(self, ball, current_y):
        if current_y < self.ground_level:
            effective_weight = (ball.m * 0.5 + ball.r) * 0.05
            water_speed = ball.v - ball.wr - ball.f_a - ball.f_s * 0.0001
            ball.y += water_speed

            # if effective_weight > 1:
            #     ball.y += water_speed
            # else:
            #     while ball.y < self.water_level:
            #         ball.y -= min(water_speed, 0.3)
        else:
            ball.y = self.ground_level - ball.r
            ball.phase = 'bounce1'

    def update_bounce1(self, ball, current_bottom):
        bounce_height = ball.m * 0.003 * self.config['behavior']['bounce_height']
        if ball.y > self.ground_level - ball.r - bounce_height:
            # ball.y -= ball.v * 0.3
            ball.y -= ball.v - ball.wr - ball.f_a - ball.f_s * 0.0001
        else:
            ball.phase = 'bounce2'

    def update_bounce2(self, ball, current_bottom):
        if current_bottom < self.ground_level:
            ball.y += 0.2 * (ball.v * (1 - ball.wr * ball.m * 0.01) - ball.f_a * 0.001)
        else:
            ball.y = self.ground_level - ball.r
            ball.phase = 'stopping'

    def update_stopping(self, ball):
        if ball.y < self.ground_level - ball.r:
            ball.y += 0.1
        else:
            ball.y = self.ground_level - ball.r
            ball.is_moving = False


class Graphics:
    def __init__(self, root, simulation):
        self.root = root
        self.simulation = simulation
        config = simulation.config

        self.canv = tk.Canvas(root, width=config['width'], height=config['height'], bg=config['colors']['bg'])
        self.canv.pack()
        self.canv.create_rectangle(0, simulation.water_level, config['width'] + 2, config['height'] + 2,
                                   fill=config['colors']['water'], activefill=config['colors']['water_activefill'])
        self.ball_ids = []

    def draw(self):
        for ball_id in self.ball_ids:
            self.canv.delete(ball_id)
        self.ball_ids.clear()

        for ball in self.simulation.balls:
            x1 = ball.x - ball.r
            y1 = ball.y - ball.r
            x2 = ball.x + ball.r
            y2 = ball.y + ball.r

            ball_id = self.canv.create_oval(x1, y1, x2, y2, fill=ball.color,
                                            outline=self.simulation.config['colors']['oval_outline'], width=2)
            self.ball_ids.append(ball_id)


class Manager:
    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.root = tk.Tk()
        self.root.title('Balls on the water')
        self.simulation = Simulation(config)
        self.graphics = Graphics(self.root, self.simulation)

        self.simulation.add_ball(100, 20, 40, 10, color='pink2')
        self.simulation.add_ball(200, 20, 40, 120, color='pink1')
        self.root.bind('<Escape>', lambda e: self.escape())
        self.running = True
        self.game_loop()

    def game_loop(self):
        if self.running:
            self.simulation.update()
            self.graphics.draw()
            self.root.after(1000 // self.simulation.config['speeds']['animation'], self.game_loop)

    def escape(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    manager = Manager()
    manager.run()
