import arcade
import math

BULLET_SPEED = 15

def magnitude(x, y):
    return math.sqrt(x*x + y*y)

DASH_AMOUNT = 200
ENEMY_SPEED = 5

class Enemy(arcade.Sprite):
    def __init__(self,window):
        super().__init__()
        self.window = window

        self.walk_textures = {}
        self.still_textures = {}
        
        self.facing_dir = None
        self.curr_idx = 0

        self.sprite = None
        self.health = None

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
        self.movement_speed = None
        
        self.dash_timer = 0

        self.grid_size=None
        self.frame_counter = 0


    def setup(self, img_src, scale, start_x, start_y):

        image_source = img_src

        self.center_x = start_x
        self.center_y = start_y

        self.direction_x = 0
        self.direction_y = 0

        self.movement_speed = 4

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

        self.health = 5


        self.grid_size = 40
        # Calculate the playing field size. We can't generate paths outside of
        # this.

        self.init_x = self.center_x
        self.init_y = self.center_y

        self.range_x = (max(self.init_x-500,0),min(self.init_x+500,self.window.level_width))
        self.range_y = (max(self.init_y-500,0),min(self.init_y+500,self.window.level_height))
        
        self.barrier_list = arcade.AStarBarrierList(self.window.player,
                                                    self.window.blockable_list,
                                                    self.grid_size,
                                                    0,
                                                    self.window.level_width,
                                                    0,
                                                    self.window.level_height)

        self.path_idx=0
        self.follow = None
        self.path=None
        self.path_traversal_state = 'ATTACK'    
        self.path_traversal_state_counter = 0    

    def health_pickup(self):
        self.health = 5
        self.movement_speed = 4

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

            self.dash_timer = 10
            if relative_x < 0:
                self.change_x -= 20
            elif relative_x > 0:
                self.change_x += 20
            if relative_y < 0:
                self.change_y -= 20
            elif relative_y > 0:
                self.change_y += 20

            
            return (self.center_x + DASH_AMOUNT*relative_x, self.center_y + DASH_AMOUNT*relative_y)
        return (self.center_x, self.center_y)

    def traverse_path(self):
        x,y = self.path[self.path_idx]
        dx=(x-self.center_x)
        dy=(y-self.center_y)
        m = magnitude(dx,dy)
        if(m<=ENEMY_SPEED):
            self.center_x = self.path[self.path_idx][0]
            self.center_y = self.path[self.path_idx][1]
            self.path_idx+=1
            if(len(self.path)>self.path_idx):
                self.traverse_path()
            return 

        self.change_x=dx/m*ENEMY_SPEED
        self.change_y=dy/m*ENEMY_SPEED

    def update(self):        
        dest = None
        new_follow=None

        if(self.path_traversal_state=='ATTACK' and 
        self.window.player.center_x<self.range_x[1] 
        and self.window.player.center_x>self.range_x[0]
        and self.window.player.center_y<self.range_y[1]
        and self.window.player.center_y>self.range_y[0]):
            dest = self.window.player.position
            new_follow = 'player'
        else:
            dest = (self.init_x,self.init_y)
            new_follow = 'init'

        if(new_follow==self.follow and self.path!=None and self.path_idx<len(self.path)
            and self.frame_counter<600):
            if((self.path!=None and len(self.path)>0) 
            and ((dest==self.window.player.position and len(self.path)<60) 
            or dest==(self.init_x,self.init_y))):
                self.traverse_path()
                if(self.collides_with_sprite(self.window.player)):
                    # self.on_counter=0
                    self.change_x=0
                    self.change_y=0
                    self.path_traversal_state='RETURN'
                    self.path_traversal_state_counter=0  
        else:
            self.path_idx=1
            self.frame_counter=0
            self.follow = new_follow
            self.path = arcade.astar_calculate_path((self.center_x,self.center_y),
                                                dest, 
                                                self.barrier_list,
                                                diagonal_movement=True)

        self.frame_counter+=1
        self.path_traversal_state_counter+=1
        if(self.path_traversal_state_counter>=120 and self.path_traversal_state=='RETURN'):
            self.path_traversal_state_counter=0
            self.path_traversal_state='ATTACK'
        # self.on_counter+=1
        #print(self.frame_counter)

        # if((self.path!=None and len(self.path)>0) 
        # and ((dest==self.window.player.position and len(self.path)<20) 
        # or dest==(self.init_x,self.init_y))):
        #     x,y = self.path[1]
        #     dx=(x-self.left)
        #     dy=(y-self.bottom)
        #     m = magnitude(dx,dy)
        #     print(self.position,self.window.player.position,dx/m*ENEMY_SPEED,dy/m*ENEMY_SPEED)
        #     self.change_x=dx/m*ENEMY_SPEED
        #     self.change_y=dy/m*ENEMY_SPEED
        # elif self.path!=None:
        #     print(len(self.path),"Hello")
        #     self.change_x=0
        #     self.change_y=0
        





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
        if (self.dash_timer>0):
            self.dash_timer-=1
            if (self.dash_timer < 5):
                self.color = [255, 150, 150]
            if self.dash_timer == 0:
                self.change_x = 0
                self.change_y = 0
                self.color = [255, 255, 255]


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



