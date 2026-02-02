import arcade, random
from pyglet.graphics import Batch
from arcade.camera import Camera2D
from hero import Hero
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox  # Это разные виджеты
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout  # А это менеджеры компоновки, как в pyQT
import os
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitInterval, EmitMaintainCount

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
LADDER_SPEED = 5
SMOKE_TEX = arcade.make_soft_circle_texture(20, arcade.color.LIGHT_GRAY, 255, 80)


def smoke_mutator(p):  # Дым раздувается и плавно исчезает
    p.scale_x *= 1.02
    p.scale_y *= 1.02
    p.alpha = max(0, p.alpha - 2)


def make_smoke_puff(x, y):
    # Короткий «пых» дыма: медленно плывёт и распухает
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(12),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=SMOKE_TEX,
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 0.6),
            lifetime=random.uniform(1.5, 2.5),
            start_alpha=200, end_alpha=0,
            scale=random.uniform(0.6, 0.9),
            mutation_callback=smoke_mutator,
        ),
    )


class PauseView(arcade.View):
    def __init__(self, game_view, level):
        super().__init__()
        self.fl = True
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
        start_view = StartView()
        self.window.show_view(start_view)
        arcade.stop_sound(self.player)

    def next_level(self, event=None):
        game_view = MyGame(self.level + 1)
        self.window.show_view(game_view)

    def restart(self, event=None):
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
        game_view = MyGame(self.level)
        self.window.show_view(game_view)


class LoseView(arcade.View):
    def __init__(self, level):
        super().__init__()
        self.music = arcade.load_sound("music/Игра закончилась.mp3")
        self.player = arcade.play_sound(self.music)
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
        arcade.stop_sound(self.player)

    def restart(self, event=None):
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


class MyGame(arcade.View):
    def __init__(self, level):
        super().__init__()
        self.play = False
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
        if self.level == 1:
            self.tile_map = arcade.load_tilemap("map1.tmx", scaling=1.8)
        elif self.level == 2:
            self.tile_map = arcade.load_tilemap("map2.tmx", scaling=1.8)
        elif self.level == 3:
            self.tile_map = arcade.load_tilemap("map3.tmx", scaling=1.8)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.coin_list = self.scene['coins']
        self.score = 0
        self.batch = Batch()
        self.emitters = []

        if level == 1:
            self.engine = arcade.PhysicsEnginePlatformer(
                player_sprite=self.player,
                gravity_constant=GRAVITY,
                walls=self.scene['platforms'],
                ladders=self.scene['ladders']
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
            )

        self.jumps_left = MAX_JUMPS

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.scene.draw()
        self.player_spritelist.draw()
        for e in self.emitters:
            e.draw()
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
                self.emitters.append(make_smoke_puff(self.player.center_x, self.player.center_y))
                arcade.play_sound(self.jump_sound)

        on_ladders = arcade.check_for_collision_with_list(self.player, self.scene['ladders'])
        on_ladder = self.engine.is_on_ladder()

        if on_ladders:
            if self.up and not self.down:
                self.player.change_y = LADDER_SPEED
            elif self.down and not self.up:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0

        self.engine.update()
        for coin in arcade.check_for_collision_with_list(self.player, self.coin_list):
            coin.remove_from_sprite_lists()
            self.score += 1

        spikes_hit = arcade.check_for_collision_with_list(self.player, self.scene['spikes'])

        if spikes_hit:
            lose_view = LoseView(self.level)
            self.window.show_view(lose_view)
            self.score = 0
            arcade.stop_sound(self.back_player_1)

        exit = arcade.check_for_collision_with_list(self.player, self.scene['door'])

        if exit:
            win_view = WinView(self.level, self.score)
            self.window.show_view(win_view)
            self.score = 0
            arcade.stop_sound(self.back_player_1)

        emitters_copy = self.emitters.copy()  # Защищаемся от мутаций списка
        for e in emitters_copy:
            e.update(delta_time)
        for e in emitters_copy:
            if e.can_reap():  # Готов к уборке?
                self.emitters.remove(e)

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
        elif key == arcade.key.ESCAPE:
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
            self.play = True
        elif key == arcade.key.W:
            if self.play:
                self.back_player_1 = self.background_music_1.play(loop=True)
                self.play = False

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
