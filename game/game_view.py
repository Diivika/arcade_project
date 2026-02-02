import arcade
from pyglet.graphics import Batch
from arcade.camera import Camera2D
from config import *
from hero import Hero
from particles.smoke import make_smoke_puff

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
            self.tile_map = arcade.load_tilemap("assets/map1.tmx", scaling=1.8)
        elif self.level == 2:
            self.tile_map = arcade.load_tilemap("assets/map2.tmx", scaling=1.8)
        elif self.level == 3:
            self.tile_map = arcade.load_tilemap("assets/map3.tmx", scaling=1.8)
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
                ladders=self.scene['ladders']
            )
        elif level == 3:
            self.engine = arcade.PhysicsEnginePlatformer(
                player_sprite=self.player,
                gravity_constant=GRAVITY,
                walls=self.scene['platforms'],
                ladders=self.scene['ladders']
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
            from views.lose_view import LoseView
            lose_view = LoseView(self.level)
            self.window.show_view(lose_view)
            self.score = 0
            arcade.stop_sound(self.back_player_1)
        exit = arcade.check_for_collision_with_list(self.player, self.scene['door'])
        if exit:
            from views.win_view import WinView
            win_view = WinView(self.level, self.score)
            self.window.show_view(win_view)
            self.score = 0
            arcade.stop_sound(self.back_player_1)
        emitters_copy = self.emitters.copy()
        for e in emitters_copy:
            e.update(delta_time)
        for e in emitters_copy:
            if e.can_reap():
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
            from views.pause_view import PauseView
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