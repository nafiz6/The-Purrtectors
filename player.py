import arcade
import math

BULLET_SPEED = 15

def magnitude(x, y):
    return math.sqrt(x*x + y*y)

DASH_AMOUNT = 200

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
        self.melee_sprite = None

        self.melee_timer = None
        self.melee_attacking = None
        self.melee_idx = None
        self.melee_list = None
 
        self.bullet_list = None


    def setup(self, img_src, scale, start_x, start_y):

        image_source = img_src

        self.center_x = start_x
        self.center_y = start_y

        self.direction_x = 0
        self.direction_y = 0

        sprite_sheet = img_src

        self.scale = scale
        self.bullet_list = arcade.SpriteList()

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

        self.facing_dir = 'LEFT'

        self.texture = self.still_textures['UP'][self.curr_idx]

        self.animation_timer = 0

        self.melee_sprite = [arcade.Sprite(f'{img_src}-melee-0.png'), arcade.Sprite(f'{img_src}-melee-1.png'), arcade.Sprite(f'{img_src}-melee-0.png') ]
        self.melee_attacking = False 
        self.melee_idx = 0
        self.melee_list = arcade.SpriteList()

    def set_brightness(self, brightness):
        self.color = [brightness, brightness, brightness]



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

            self.stamina -= 1
            
            return (self.center_x + DASH_AMOUNT*relative_x, self.center_y + DASH_AMOUNT*relative_y)
        return (self.center_x, self.center_y)


    def update(self):
        if self.stamina < 3:
            self.stamina_timer-= 1
            if (self.stamina_timer == 0):
                self.stamina_timer = 100
                self.stamina += 1



    def melee_attack_animation(self):
        
        self.melee_list = arcade.SpriteList()
        self.melee_sprite[self.melee_idx].center_x = self.center_x
        self.melee_sprite[self.melee_idx].center_y = self.center_y

        if self.facing_dir == 'RIGHT':
            self.melee_sprite[self.melee_idx].center_x += self.width/2
            self.melee_sprite[self.melee_idx].angle = 0
            if (self.melee_idx == 0 or self.melee_idx == 2):
                self.angle = 15
            else:
                self.angle = 30
        elif self.facing_dir == 'LEFT':
            self.melee_sprite[self.melee_idx].center_x -= self.width/2
            self.melee_sprite[self.melee_idx].angle = 180
            
            if (self.melee_idx == 0 or self.melee_idx == 2):
                self.angle = -15
            else:
                self.angle = -30
        elif self.facing_dir == 'DOWN':
            self.melee_sprite[self.melee_idx].center_y -= self.height/2
            self.melee_sprite[self.melee_idx].angle = -90
            
        elif self.facing_dir == 'UP':
            self.melee_sprite[self.melee_idx].center_y += self.height/2
            self.melee_sprite[self.melee_idx].angle = 90
        
        
        self.melee_list.append(self.melee_sprite[self.melee_idx])
        


    def melee(self):
        if self.melee_attacking == False:
            self.melee_timer = 0
            self.melee_attacking = True
            self.melee_attack_animation()

    def range(self, x , y, view_left, view_bottom):

        #create bullet
        bullet = arcade.Sprite("./tiles/ray.png", 1)

        #position at player
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y

        x_diff = x - self.center_x + view_left 
        y_diff = y - self.center_y + view_bottom

        angle = math.atan2(y_diff, x_diff)

        bullet.angle = math.degrees(angle) + 90

        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        self.bullet_list.append(bullet)
        
        #stop player motion
        self.right_click = False
        self.change_x=0
        self.change_y=0
        





            
    
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

        if self.melee_attacking:
            self.change_x = 0
            self.change_y = 0
            self.melee_timer += delta_time
            if self.melee_timer > 0.11:
                self.melee_timer = 0

                self.melee_idx += 1
                if self.melee_idx == 3:
                    self.melee_attacking = False
                    self.melee_idx = 0 
                    self.melee_list = arcade.SpriteList()
                    self.angle = 0

                else:
                    self.melee_attack_animation()
        
        if (self.animation_timer > 0.2):
            self.animation_timer = 0
            self.curr_idx+=1
            if(self.curr_idx==4):
                self.curr_idx=0 

            if(self.change_x == 0 and self.change_y==0):
                self.texture = self.still_textures[self.facing_dir][self.curr_idx]
            else:
                self.texture=self.walk_textures[self.facing_dir][self.curr_idx]



