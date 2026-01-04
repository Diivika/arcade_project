import arcade
from pyglet.graphics import Batch
from arcade.camera import Camera2D
from hero import Hero

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Real Jump"
GRAVITY = 2
MOVE_SPEED = 6
JUMP_SPEED = 40
COYOTE_TIME = 0.08
JUMP_BUFFER = 0.12
MAX_JUMPS = 1
CAMERA_LERP = 0.12


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()
        self.left = self.right = self.up = self.down = self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.player = Hero(125, 125)
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.tile_map = arcade.load_tilemap("map.tmx", scaling=1.8)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

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
        self.player_spritelist.draw()
        self.scene.draw()
        self.gui_camera.use()
        self.batch.draw()

    def on_update(self, delta_time):
        self.player.update(delta_time)
        self.player.change_y -= GRAVITY

        move = 0
        if self.left and not self.right:
            move = -MOVE_SPEED
        elif self.right and not self.left:
            move = MOVE_SPEED
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
        world_w = 2000
        world_h = 900
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # self.text = arcade.Text(f'Score: {self.score}',
        #                        10, self.height - 30, arcade.color.WHITE,
        #                        24, batch=self.batch)

        grounded = self.engine.can_jump(y_distance=6)
        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

        if want_jump:
            can_coyote = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyote:
                self.engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0

        self.engine.update()

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


def setup_game(width=1220, height=850, title="Аркадный Бегун"):
    game = MyGame(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
