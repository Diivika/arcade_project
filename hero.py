import arcade

ANIMATION_SPEED = 0.12


class Hero(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("images/stay.png", scale=2.0)
        self.center_x, self.center_y = x, y
        self.textures_right = []
        self.textures_left = []
        for i in range(3, 5):
            self.textures_right.append(arcade.load_texture(f'images/walk_{i}.png'))
        for i in range(1, 3):
            self.textures_left.append(arcade.load_texture(f'images/walk_{i}.png'))
        self.stay_texture = arcade.load_texture('images/stay.png')
        self.animation_frame = 0
        self.is_moving_right = False
        self.is_moving_left = False
        self.animation_timer = 0

    def start_move_left(self):
        self.is_moving_left = True
        self.is_moving_right = False
        self.animation_frame = 0
        self.animation_timer = 0

    def start_move_right(self):
        self.is_moving_right = True
        self.is_moving_left = False
        self.animation_frame = 0
        self.animation_timer = 0

    def update(self, delta_time: float = 1 / 60):
        if not self.is_moving_left and not self.is_moving_right:
            self.texture = self.stay_texture
            self.animation_frame = 0
            self.animation_timer = 0
            return
        self.animation_timer += delta_time
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_frame += 1
            self.animation_timer = 0
            if self.is_moving_left:
                if self.animation_frame >= len(self.textures_left):
                    self.animation_frame = 0
                self.texture = self.textures_left[self.animation_frame]

            elif self.is_moving_right:
                if self.animation_frame >= len(self.textures_right):
                    self.animation_frame = 0
                self.texture = self.textures_right[self.animation_frame]

