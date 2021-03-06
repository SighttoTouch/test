import random
from datetime import datetime

from kivy.app import App
from kivy.graphics import Ellipse, Color
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock


class StartPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (20 / 255, 20 / 255, 20 / 255, 1)
        self.button = Button(text='Begin Tracking',
                             font_size='30',
                             size_hint=(.5, .5),
                             pos_hint={'center_x': .5, 'center_y': .5})
        self.add_widget(self.button)
        self.button.bind(on_release=self.on_release_button)

    def on_release_button(self, instance):
        app.screen_manager.current = "Dot"
        Clock.schedule_interval(app.dot_page.count_down, 1)


class DotPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instruction_label = Label(text='Follow the dot with your eyes',
                                       font_size='30',
                                       pos_hint={'center_x': 0.5, 'center_y': 0.65})
        self.add_widget(self.instruction_label)

        self.count = 3
        self.count_label = Label(text=str(self.count),
                                 font_size='50',
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.count_label)

        self.moving_dot = MovingDot()
        self.add_widget(self.moving_dot)

    def count_down(self, *args):
        self.count -= 1
        self.count_label.text = str(self.count)
        if self.count <= 0:  # end of count down
            self.remove_widget(self.count_label)
            self.remove_widget(self.instruction_label)
            self.count = 3
            self.count_label.text = str(self.count)
            app.dot_page.fob = open('./coordinates.txt', 'a+')
            Clock.schedule_interval(self.moving_dot.update, 1/30)

        # false will end the Clock.schedule_interval()
        return False if self.count == 3 else True


class MovingDot(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ball_size = dp(12)
        self.max_pos_x = Window.width - self.ball_size
        self.max_pos_y = Window.height - self.ball_size
        with self.canvas:
            Color(0, 150/255, 1, 1)
            self.ball = Ellipse(size=(self.ball_size, self.ball_size))

        self.new_starting_point()

    def new_starting_point(self, *args):
        # starting position is at the bottom of the screen, with a random x position
        self.ball.pos = (random.randrange(self.max_pos_x), 0)

    def update(self, *args):
        x, y = self.ball.pos
        x_center = int(x + self.ball_size/2)
        y_center = int(y + self.ball_size/2)
        # x and y coords are recorded in text file
        app.dot_page.fob.write('%s, %s\n' % (str(x_center), str(y_center)))
        # image is saved with name "image-Year-Month-Day-Hr-Min-Sec-xcoord-ycoord.png
        app.camObj.export_to_png("./imageFolder/image-" +
                                 datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-" +
                                 str(x_center) + "-" +
                                 str(y_center) + ".png")
        self.ball.pos = (x, y + 2)
        if y < self.max_pos_y:
            return True
        else:
            app.dot_page.fob.close()
            app.screen_manager.current = "Start"
            app.dot_page.add_widget(app.dot_page.count_label)
            app.dot_page.add_widget(app.dot_page.instruction_label)
            self.new_starting_point()
            return False


class MainApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        self.start_page = StartPage()
        screen = Screen(name="Start")
        screen.add_widget(self.start_page)
        self.screen_manager.add_widget(screen)

        self.dot_page = DotPage()
        screen = Screen(name="Dot")
        screen.add_widget(self.dot_page)
        self.screen_manager.add_widget(screen)

        app.screen_manager.current = "Start"

        self.fob = open('./coordinates.txt', 'a+')
        self.camObj = Camera(play=True,
                             resolution=(256, 256),
                             size=(256, 256))

        return self.screen_manager


if __name__ == '__main__':
    app = MainApp()
    app.run()
