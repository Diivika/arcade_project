import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from config import SCREEN_WIDTH, SCREEN_HEIGHT


class PauseView(arcade.View):
    def __init__(self, game_view, level):
        super().__init__()
        self.level = level
        self.game_view = game_view
        self.manager = UIManager(self.window)
        self.manager.enable()

        self.box_layout = UIBoxLayout(vertical=True, align="center", space_between=10)
        self.create_widgets()

        anchor = UIAnchorLayout()
        anchor.add(child=self.box_layout, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def create_widgets(self):
        title_label = UILabel(text="PAUSED", font_size=40, text_color=arcade.color.WHITE)
        self.box_layout.add(title_label)

        level_layout = UIBoxLayout(vertical=False, align="center", space_between=20)

        self.continue_button = UIFlatButton(text="Продолжить", width=150, height=50)
        self.continue_button.on_click = self.continue_gaming
        level_layout.add(self.continue_button)

        self.back_to_main = UIFlatButton(text="Вернуться в главное меню", width=200, height=50)
        self.back_to_main.on_click = self.back_to_main_menu
        level_layout.add(self.back_to_main)

        self.restart_button = UIFlatButton(text="Начать сначала", width=150, height=50)
        self.restart_button.on_click = self.restart
        level_layout.add(self.restart_button)

        self.box_layout.add(level_layout)

    def continue_gaming(self, event=None):
        self.window.show_view(self.game_view)
        self.game_view.reset_controls()

    def back_to_main_menu(self, event=None):
        from views.start_view import StartView
        start_view = StartView()
        self.window.show_view(start_view)

    def restart(self, event=None):
        from game.game_view import MyGame
        game_view = MyGame(self.level)
        self.window.show_view(game_view)

    def on_show(self):
        self.manager.enable()

    def on_draw(self):
        self.game_view.on_draw()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                          (0, 0, 0, 150))
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.continue_gaming()