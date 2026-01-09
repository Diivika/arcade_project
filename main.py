import arcade
from pyglet.graphics import Batch
from arcade.camera import Camera2D
from hero import Hero

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


class StartView(arcade.View):
    def on_show(self):
        """Настройка начального экрана"""
        arcade.set_background_color(arcade.color.BLUE)

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        # Батч для текста
        self.batch = Batch()
        start_text = arcade.Text("CloudHopper", self.window.width / 2, self.window.height / 2,
                                 arcade.color.WHITE, font_size=50, anchor_x="center", batch=self.batch)
        any_key_text = arcade.Text("Any key to start",
                                   self.window.width / 2, self.window.height / 2 - 75,
                                   arcade.color.GRAY, font_size=20, anchor_x="center", batch=self.batch)
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        """Начало игры при нажатии клавиши"""
        game_view = MyGame()
        self.window.show_view(game_view)


class MyGame(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLUE)

        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.player = Hero(125, 125)
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.tile_map = arcade.load_tilemap("map1.tmx", scaling=1.8)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        self.coin_list = self.scene['coins']
        self.score = 0
        self.batch = Batch()

        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.scene['platforms']
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


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
