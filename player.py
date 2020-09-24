import arcade
import math

def magnitude(x, y):
    return math.sqrt(x*x + y*y)

DASH_AMOUNT = 100

class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.walk_textures = {}
        self.still_textures = {}
        
        self.facing_dir = None
        self.curr_idx = 0

        self.sprite = None
        self.health = 10

        self.stamina_timer = 0
        self.stamina = 3

        self.direction_x = None
        self.direction_y = None

        self.texture = None
        self.scale = None

        self.animation_timer = None
 


    def setup(self, img_src, scale, start_x, start_y):

        image_source = img_src

        self.center_x = start_x
        self.center_y = start_y

        self.direction_x = 0
        self.direction_y = 0

        sprite_sheet = img_src

        self.scale = scale

        left_still = []
        right_still = []
        down_still = []
        up_still = []

        left_walk = []
        right_walk = []
        down_walk = []
        up_walk = []

        for i in range(4):
            left_still.append(arcade.load_texture(f'{img_src}-stand-horizontal-{i}.png'))
            left_walk.append(arcade.load_texture(f'{img_src}-walk-horizontal-{i}.png'))
        
        for i in range(4):
            right_still.append(arcade.load_texture(f'{img_src}-stand-horizontal-{i}.png', flipped_horizontally = True))
            right_walk.append(arcade.load_texture(f'{img_src}-walk-horizontal-{i}.png', flipped_horizontally = True))

        for i in range(4):
            up_still.append(arcade.load_texture(f'{img_src}-stand-up-{i}.png'))
            up_walk.append(arcade.load_texture(f'{img_src}-walk-up-{i}.png'))

        for i in range(4):
            down_still.append(arcade.load_texture(f'{img_src}-stand-down-{i}.png'))
            down_walk.append(arcade.load_texture(f'{img_src}-walk-down-{i}.png'))


        self.still_textures['LEFT'] = left_still
        self.still_textures['RIGHT'] = right_still
        self.still_textures['UP'] = up_still
        self.still_textures['DOWN'] = down_still

        self.walk_textures['LEFT'] = left_walk
        self.walk_textures['RIGHT'] = right_walk
        self.walk_textures['UP'] = up_walk
        self.walk_textures['DOWN'] = down_walk

        self.facing_dir = 'UP'

        self.texture = self.still_textures['UP'][self.curr_idx]

        self.animation_timer = 0


    def dash(self):
        if self.stamina > 0:
            self.stamina_timer = 100

            relative_x = self.direction_x
            relative_y = self.direction_y
            
            if relative_y==0 and relative_x==0:
                relative_x=1
           
            relative_magnitude =  magnitude(relative_x, relative_y)

            relative_x /= relative_magnitude
            relative_y /= relative_magnitude

            self.left += DASH_AMOUNT*relative_x 
            self.bottom += DASH_AMOUNT*relative_y

            self.stamina -= 1

    def update(self):
        if self.stamina < 3:
            self.stamina_timer-= 1
            if (self.stamina_timer == 0):
                self.stamina_timer = 100
                self.stamina += 1
            
    
    def update_animation(self,delta_time = 1/60):

        self.animation_timer += delta_time

        if self.change_x<0 and self.facing_dir != 'LEFT':
            self.facing_dir='LEFT'
        if self.change_x>0 and self.facing_dir != 'RIGHT':
            self.facing_dir='RIGHT'
        if self.change_y>0 and self.facing_dir != 'UP':
            self.facing_dir='UP'
        if self.change_y<0 and self.facing_dir != 'DOWN':
            self.facing_dir='DOWN'
        
        if (self.animation_timer > 0.1):
            self.animation_timer = 0
            self.curr_idx+=1
            if(self.curr_idx==4):
                self.curr_idx=0 

            if(self.change_x == 0 and self.change_y==0):
                self.texture = self.still_textures[self.facing_dir][self.curr_idx]
            else:
                self.texture=self.walk_textures[self.facing_dir][self.curr_idx]



