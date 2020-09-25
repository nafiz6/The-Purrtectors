import arcade
import math

def magnitude(x, y):
    return math.sqrt(x*x + y*y)

class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.moving_textures = {}
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

        left = []
        for i in range(3):
            left.append(arcade.load_texture(f'{img_src}_{i}.png'))
        
        right = []
        for i in range(3):
            right.append(arcade.load_texture(f'{img_src}_{i}.png'))

        up = []
        for i in range(3):
            up.append(arcade.load_texture(f'{img_src}_{i}.png'))
        down = []
        for i in range(3):
            down.append(arcade.load_texture(f'{img_src}_{i}.png'))


        self.still_textures['LEFT'] = left
        self.still_textures['RIGHT'] = right
        self.still_textures['UP'] = up
        self.still_textures['DOWN'] = down

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

            self.left += 160*relative_x 
            self.bottom += 160*relative_y

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
            if(self.change_x == 0 and self.change_y==0):
                self.animation_timer = 0
                self.curr_idx+=1
                if(self.curr_idx==3):
                    self.curr_idx=0 
                self.texture = self.still_textures[self.facing_dir][self.curr_idx]
            else:
                self.curr_idx+=1
                if(self.curr_idx==3):
                    self.curr_idx=0
                self.texture=self.still_textures[self.facing_dir][self.curr_idx]



