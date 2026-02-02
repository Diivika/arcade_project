import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class WinView(arcade.View):
    def __init__(self, level, score):
        super().__init__()
        self.music = arcade.load_sound("music/Вы пришли первым.mp3")
        self.player = arcade.play_sound(self.music)
        self.level = level
        self.score = score
        self.manager = UIManager(self.window)
        self.manager.enable()
        self.box_layout = UIBoxLayout(vertical=True, align="center", space_between=10)
        self.create_widgets()
        anchor = UIAnchorLayout()
        anchor.add(child=self.box_layout, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def create_widgets(self):
        title_label = UILabel(text="You win", font_size=40, text_color=arcade.color.WHITE)
        self.box_layout.add(title_label)
        with open(f'scores/score_map{self.level}.txt', 'r') as f:
            last_score = int(f.readline().split('/')[0])
            if last_score < self.score:
                with open(f'scores/score_map{self.level}.txt', 'w') as w:
                    w.write(f'{str(self.score)}/20')
                    record = UILabel(text='NEW RECORD!!!', font_size=40, text_color=arcade.color.WHITE)
                    self.box_layout.add(record)
        score_label = UILabel(text=f'Your score: {self.score}/20', font_size=40, text_color=arcade.color.WHITE)
        self.box_layout.add(score_label)
        level_layout = UIBoxLayout(vertical=False, align="center", space_between=20)
        self.back_to_main = UIFlatButton(text="Вернуться в главное меню", width=200, height=50)
        self.back_to_main.on_click = self.back_to_main_menu
        level_layout.add(self.back_to_main)
        self.restart_button = UIFlatButton(text="Начать сначала", width=150, height=50)
        self.restart_button.on_click = self.restart
        level_layout.add(self.restart_button)
        if self.level != 3:
            self.next_level_button = UIFlatButton(text='Следующий уровень', width=160, height=50)
            self.next_level_button.on_click = self.next_level
            level_layout.add(self.next_level_button)
        self.box_layout.add(level_layout)

    def back_to_main_menu(self, event=None):
        from views.start_view import StartView
        start_view = StartView()
        self.window.show_view(start_view)
        arcade.stop_sound(self.player)

    def next_level(self, event=None):
        from game.game_view import MyGame
        game_view = MyGame(self.level + 1)
        self.window.show_view(game_view)

    def restart(self, event=None):
        from game.game_view import MyGame
        game_view = MyGame(self.level)
        self.window.show_view(game_view)
        arcade.stop_sound(self.player)

    def on_show(self):
        self.manager.enable()

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                          (0, 0, 0, 150))
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        from game.game_view import MyGame
        game_view = MyGame(self.level)
        self.window.show_view(game_view)