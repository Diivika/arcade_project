import arcade
from pyglet.graphics import Batch
from arcade.camera import Camera2D
from hero import Hero
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox  # Это разные виджеты
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout  # А это менеджеры компоновки, как в pyQT

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
SCREEN_TITLE = "CloudHopper"
GRAVITY = 2
MOVE_SPEED = 6
JUMP_SPEED = 40
COYOTE_TIME = 0.08
JUMP_BUFFER = 0.12
MAX_JUMPS = 1
CAMERA_LERP = 0.12

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
        start_view = StartView()
        self.window.show_view(start_view)

    def restart(self, event=None):
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


class WinView(arcade.View):
    def __init__(self, level):
        super().__init__()
        self.level = level
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
        level_layout = UIBoxLayout(vertical=False, align="center", space_between=20)
        self.back_to_main = UIFlatButton(text="Вернуться в главное меню", width=200, height=50)
        self.back_to_main.on_click = self.back_to_main_menu
        level_layout.add(self.back_to_main)
        self.restart_button = UIFlatButton(text="Начать сначала", width=150, height=50)
        self.restart_button.on_click = self.restart
        level_layout.add(self.restart_button)
        self.box_layout.add(level_layout)

    def back_to_main_menu(self, event=None):
        start_view = StartView()
        self.window.show_view(start_view)

    def restart(self, event=None):
        game_view = MyGame(self.level)
        self.window.show_view(game_view)

    def on_show(self):
        self.manager.enable()

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                          (0, 0, 0, 150))
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        game_view = MyGame(self.level)
        self.window.show_view(game_view)


class LoseView(arcade.View):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.manager = UIManager(self.window)
        self.manager.enable()
        self.box_layout = UIBoxLayout(vertical=True, align="center", space_between=10)
        self.create_widgets()
        anchor = UIAnchorLayout()
        anchor.add(child=self.box_layout, anchor_x="center", anchor_y="center")
        self.manager.add(anchor)

    def create_widgets(self):
        title_label = UILabel(text="You losed", font_size=40, text_color=arcade.color.WHITE)
        self.box_layout.add(title_label)
        level_layout = UIBoxLayout(vertical=False, align="center", space_between=20)
        self.back_to_main = UIFlatButton(text="Вернуться в главное меню", width=200, height=50)
        self.back_to_main.on_click = self.back_to_main_menu
        level_layout.add(self.back_to_main)
        self.restart_button = UIFlatButton(text="Начать сначала", width=150, height=50)
        self.restart_button.on_click = self.restart
        level_layout.add(self.restart_button)
        self.box_layout.add(level_layout)

    def back_to_main_menu(self, event=None):
        start_view = StartView()
        self.window.show_view(start_view)

    def restart(self, event=None):
        game_view = MyGame(self.level)
        self.window.show_view(game_view)

    def on_show(self):
        self.manager.enable()

    def on_draw(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                                          (0, 0, 0, 150))
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        game_view = MyGame(self.level)
        self.window.show_view(game_view)


class StartView(arcade.View):
    def __init__(self):

        super().__init__()
        self.background_music = arcade.load_sound("music/Intro Theme.mp3")
        self.back_player = self.background_music.play(loop=True)


        self.manager = UIManager(self.window)
        self.manager.enable()
        self.box_layout = UIBoxLayout(vertical=True, align="center", space_between=10)
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
        level_layout = UIBoxLayout(vertical=False, align="center", space_between=20)
        self.level1_button = UIFlatButton(text="Level 1", width=150, height=50)
        self.level1_button.on_click = lambda event: self.on_level_select(1)
        level_layout.add(self.level1_button)
        self.level2_button = UIFlatButton(text="Level 2", width=150, height=50)
        self.level2_button.on_click = lambda event: self.on_level_select(2)
        level_layout.add(self.level2_button)
        self.level3_button = UIFlatButton(text="Level 3", width=150, height=50)
        self.level3_button.on_click = lambda event: self.on_level_select(3)
        level_layout.add(self.level3_button)
        self.box_layout.add(level_layout)
        self.box_layout.add(UILabel(text="", height=30))
        self.exit_button = UIFlatButton(text="Exit", width=200, height=50)
        self.exit_button.on_click = self.on_exit_click
        self.box_layout.add(self.exit_button)
        self.box_layout.add(UILabel(text="", height=20))
        controls_label = UILabel(text="Controls: ← → to move, SPACE to jump",font_size=14,text_color=arcade.color.LIGHT_GRAY)
        self.box_layout.add(controls_label)

    def on_level_select(self, level):
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


class MyGame(arcade.View):
    def __init__(self, level):
        self.play = False
        super().__init__()
        self.jump_sound = arcade.load_sound(":resources:/sounds/jump1.wav")
        self.background_music_1 = arcade.load_sound("music/Mushroom Theme.mp3")
        self.background_music_2 = arcade.load_sound("music/Desert Theme.mp3")
        self.back_player_1 = self.background_music_1.play(loop=True)

        self.level = level
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.player = Hero(125, 125)
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)
        if level == 1:
            self.tile_map = arcade.load_tilemap("map1.tmx", scaling=1.8)
        elif level == 2:
            self.tile_map = arcade.load_tilemap("map2.tmx", scaling=1.8)
        elif level == 3:
            self.tile_map = arcade.load_tilemap("map3.tmx", scaling=1.8)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.coin_list = self.scene['coins']
        self.score = 0
        self.batch = Batch()

        if level == 1:
            self.engine = arcade.PhysicsEnginePlatformer(
                player_sprite=self.player,
                gravity_constant=GRAVITY,
                walls=self.scene['platforms'],
            )
        elif level == 2:
            self.engine = arcade.PhysicsEnginePlatformer(
                player_sprite=self.player,
                gravity_constant=GRAVITY,
                walls=self.scene['platforms'],
                platforms=self.scene['moving_platforms'],
            )
        elif level == 3:
            self.engine = arcade.PhysicsEnginePlatformer(
                player_sprite=self.player,
                gravity_constant=GRAVITY,
                walls=self.scene['platforms'],
                platforms=self.scene['moving_platforms'],
            )

        self.jumps_left = MAX_JUMPS

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.scene.draw()
        self.player_spritelist.draw()
        self.gui_camera.use()
        self.batch.draw()

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.player.change_y -= GRAVITY
        move = 0
        if self.left and not self.right:
            move = -MOVE_SPEED
            self.player.is_moving_left = True
            self.player.is_moving_right = False
        elif self.right and not self.left:
            move = MOVE_SPEED
            self.player.is_moving_left = False
            self.player.is_moving_right = True
        else:
            self.player.is_moving_left = False
            self.player.is_moving_right = False
        self.player.change_x = move
        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        world_w = 540
        world_h = 3240
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        self.text = arcade.Text(f'Score: {self.score}/20',
                                10, self.height - 30, arcade.color.BLACK,
                                24, batch=self.batch)

        grounded = self.engine.can_jump(y_distance=6)
        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

        if want_jump:
            can_coyote = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyote:
                self.engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0

        self.engine.update()
        for coin in arcade.check_for_collision_with_list(self.player, self.coin_list):
            coin.remove_from_sprite_lists()
            self.score += 1

        spikes_hit = arcade.check_for_collision_with_list(self.player, self.scene['spikes'])

        if spikes_hit:
            lose_view = LoseView(self.level)
            self.window.show_view(lose_view)
            self.score = 0

        exit = arcade.check_for_collision_with_list(self.player, self.scene['door'])

        if exit:
            win_view = WinView(self.level)
            self.window.show_view(win_view)
            self.score = 0

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT,):
            self.left = True
            self.player.start_move_left()
        elif key in (arcade.key.RIGHT,):
            self.right = True
            self.player.start_move_right()
        elif key in (arcade.key.UP,):
            self.up = True
        elif key in (arcade.key.DOWN,):
            self.down = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER
            arcade.play_sound(self.jump_sound)
        if key == arcade.key.ESCAPE:
            pause_view = PauseView(self, self.level)
            self.window.show_view(pause_view)

            arcade.stop_sound(self.back_player_1)
                


    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT,):
            self.left = False
            self.player.is_moving_left = False
        elif key in (arcade.key.RIGHT,):
            self.right = False
            self.player.is_moving_right = False
        elif key in (arcade.key.UP,):
            self.up = False
        elif key in (arcade.key.DOWN,):
            self.down = False
        elif key == arcade.key.SPACE:
            self.jump_pressed = False
            if self.player.change_y > 0:
                self.player.change_y *= 0.45
        elif key == arcade.key.ESCAPE:
            self.back_player_1 = self.background_music_1.play(loop=True)

    def reset_controls(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.player.is_moving_left = False
        self.player.is_moving_right = False
        self.player.change_x = 0
        self.player.change_y = 0



def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
