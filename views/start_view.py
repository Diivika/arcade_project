import arcade
import os
from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from config import SCREEN_WIDTH, SCREEN_HEIGHT

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_music = arcade.load_sound("music/Intro Theme.mp3")
        self.back_player = self.background_music.play(loop=True)
        self.manager = UIManager(self.window)
        self.manager.enable()
        self.box_layout = UIBoxLayout(vertical=True, align="center", space_between=10)
        self.create_txt()
        self.create_widgets()
        anchor = UIAnchorLayout()
        anchor.add(child=self.box_layout, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def create_widgets(self):
        title_label = UILabel(text="CloudHopper", font_size=32, text_color=arcade.color.WHITE)
        self.box_layout.add(title_label)
        self.box_layout.add(UILabel(text="", height=20))
        subtitle_label = UILabel(text="Select Level", font_size=20, text_color=arcade.color.LIGHT_GRAY)
        self.box_layout.add(subtitle_label)
        self.box_layout.add(UILabel(text="", height=20))
        level_layout = UIBoxLayout(vertical=False, align='center', space_between=20)
        for i in range(1, 4):
            level = UIBoxLayout(vertical=True, align='center', space_between=5)
            self.level_button = UIFlatButton(text=f'Level {i}', width=150, height=50)
            self.level_button.on_click = lambda event, level_num=i: self.on_level_select(level_num)
            with open(f'scores/score_map{i}.txt', 'r') as scores:
                scores = scores.readline()
            score_label = UILabel(text=f'Best score: {scores}', font_size=15, text_color=arcade.color.WHITE)
            level.add(self.level_button)
            level.add(score_label)
            level_layout.add(level)
        self.box_layout.add(level_layout)
        self.box_layout.add(UILabel(text="", height=30))
        self.exit_button = UIFlatButton(text="Exit", width=200, height=50)
        self.exit_button.on_click = self.on_exit_click
        self.box_layout.add(self.exit_button)
        self.box_layout.add(UILabel(text="", height=20))
        controls_label = UILabel(text="Controls: ← → to move, SPACE to jump", font_size=14,
                                 text_color=arcade.color.LIGHT_GRAY)
        self.box_layout.add(controls_label)

    def on_level_select(self, level):
        from game.game_view import MyGame
        game_view = MyGame(level)
        self.window.show_view(game_view)
        arcade.stop_sound(self.back_player)

    def on_exit_click(self, event):
        arcade.exit()

    def on_show(self):
        arcade.set_background_color(arcade.color.GRAY)
        self.manager.enable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def create_txt(self):
        os.makedirs("scores", exist_ok=True)
        for i in range(1, 4):
            try:
                with open(f'scores/score_map{i}.txt', 'x') as file:
                    file.write('0/20')
            except FileExistsError:
                pass