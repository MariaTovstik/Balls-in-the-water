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
        self.v = 0  # Начинаем с нулевой скорости
        self.a = 0  # Ускорение
        self.g = self.config['speeds']['gravity']  # Добавьте в config
        self.water_resistance_coef = self.config['behavior']['water_resistance']
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
        self.ground_level = self.height - 2
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
                self.update_bounce1(ball)
            elif ball.phase == 'bounce2':
                self.update_bounce2(ball, current_bottom)
            elif ball.phase == 'stopping':
                self.update_stopping(ball)

    def update_falling(self, ball, current_bottom):
        ''' Фаза падения шара в воду'''
        if current_bottom < self.water_level:
            # F = ma, ускорение постоянно
            ball.a = ball.g
            ball.v += ball.a * self.config['speeds']['time_step'] 
            ball.y += ball.v
        else:
            ball.phase = 'water'

    def update_water(self, ball, current_y):
        '''Фаза прохождения шара через воду. Функция изменяет координаты шара учтиывая действие силы сопротивления и силы тяжести'''
        if current_y < self.ground_level:
            ball.v+=ball.g*0.1
            if ball.r<20:
                water_resistance = ball.water_resistance_coef * ball.m * ball.r
            else:
                water_resistance= ball.water_resistance_coef*ball.m*ball.r*0.5
            if ball.v > 0:
                ball.v -= water_resistance*0.001
            else:
                ball.v += water_resistance * 0.005
            ball.y += ball.v
        else:
            ball.y = self.ground_level - ball.r
            ball.phase = 'bounce1'

    def update_bounce1(self, ball):
        '''Функция изменяет координаты шара при касании дна и отскоке, переводит анимацию в фазу повторного падения'''
        bounce_height = ball.m * 0.003 * self.config['behavior']['bounce_height']
        if ball.y > self.ground_level - ball.r - bounce_height:
            ball.v = -ball.v * self.config['behavior']['bounce_coef']*0.5  # Коэффициент отскока
            ball.y += ball.v
        else:
            ball.phase = 'bounce2'

    def update_bounce2(self, ball, current_bottom):
        '''Функция моделирует повторное падение на дно и переводит анимацию в фазу остановки движения'''
        if current_bottom < self.ground_level:
            ball.v += ball.g*0.05
            ball.y += ball.v
        else:
            ball.y = self.ground_level - ball.r
            ball.phase = 'stopping'

    def update_stopping(self, ball):
        '''Фаза завершения движения'''
        if ball.y < self.ground_level - ball.r:
            ball.y += 0.1
        else:
            ball.y = self.ground_level - ball.r
            ball.is_moving = False


    def all_balls_stopped(self):
        '''Проверяет, все ли шары остановили движение'''
        return all(not ball.is_moving for ball in self.balls)


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
        '''Графическое изображение шаров'''
        for ball_id in self.ball_ids:
            self.canv.delete(ball_id)
        self.ball_ids.clear()

        for ball in self.simulation.balls:
            x1 = ball.x - ball.r
            y1 = ball.y - ball.r
            x2 = ball.x + ball.r
            y2 = ball.y + ball.r

            ball_id = self.canv.create_oval(x1, y1, x2, y2, fill=ball.color,
                                            outline=self.simulation.config['colors']['oval_outline'], activefill=self.simulation.config['colors']['oval_activeclick'], width=2)
            self.ball_ids.append(ball_id)


class Manager:
    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
        self.root = tk.Tk()
        self.root.title('Balls on the water')
        self.simulation = Simulation(config)
        self.graphics = Graphics(self.root, self.simulation)

        self.simulation.add_ball(100, 20, 10, 0.1, color='pink2')
        self.simulation.add_ball(200, 20, 10, 120, color='pink2')
        self.simulation.add_ball(300, 20, 20, 3, color='pink2')
        self.simulation.add_ball(350, 20, 10, 100, color='pink2')
        self.simulation.add_ball(100, 20, 30, 10, color='pink2')
        self.simulation.add_ball(370, 10, 50, 10, color='pink2')
        self.root.bind('<Escape>', lambda e: self.escape())
        self.running = True
        self.game_loop()

    def game_loop(self):
        '''Запуск анимации и завершение'''
        if self.running and not self.simulation.all_balls_stopped():
            self.simulation.update()
            self.graphics.draw()
            self.root.after(1000 // self.simulation.config['speeds']['animation'], self.game_loop)
        elif not self.running:
            self.root.destroy()

    def escape(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    manager = Manager()
    manager.run()


