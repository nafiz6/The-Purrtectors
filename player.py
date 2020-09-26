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
        self.health = None
        self.max_health = None

        self.stamina_timer = 0
        self.stamina = 3

        self.direction_x = None
        self.direction_y = None

        self.texture = None
        self.scale = None

        self.animation_timer = None
        self.melee_sprite = None
        self.melee_sprite_2 = None

        self.melee_timer = None
        self.melee_attacking = None
        self.melee_idx = None
        self.melee_list = None
 
        self.bullet_list = None
        self.movement_speed = None
        
        self.dash_timer = 0
        self.type = None

        self.healing_state = None
        self.projectile_state = None

        self.visibility = None
        self.visibility_timer = None
        self.invisible_cooldown = None
        
        self.health_regen_timer = None

        self.dead = None

        self.max_bullets = None
        self.rem_bullets = None
        self.bullet_regen_timer = None

        self.hud_sprite = None

    def setup(self, img_src, scale, start_x, start_y, cat_type):

        self.dead = False

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
        
        self.hud_sprite = arcade.Sprite(f'./effects/cat-{cat_type}-controls.png', 0.5)

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

        self.melee_sprite = [arcade.Sprite(f'{img_src}-melee-0.png' , 2), arcade.Sprite(f'{img_src}-melee-1.png', 2), arcade.Sprite(f'{img_src}-melee-0.png', 2) ]
        self.melee_sprite_2 = [arcade.Sprite(f'{img_src}-melee-0.png' , 2), arcade.Sprite(f'{img_src}-melee-1.png', 2), arcade.Sprite(f'{img_src}-melee-0.png', 2) ]
        self.melee_attacking = False 
        self.melee_idx = 0
        self.melee_list = arcade.SpriteList()

        self.type = cat_type
        self.health = 5
     
        self.max_health = 5


        self.healing_state = 0
        self.projectile_state = False

        self.visibility = True
        self.visibility_timer = 100

        self.health_regen_timer = 100

        self.melee_sound = arcade.load_sound('sounds/effects/knifeSlice.ogg')
    
        if cat_type == 1:
            self.max_bullets = 1
            self.rem_bullets = 1

        if cat_type == 4:
            self.max_health = 10
            self.movement_speed = 1.5
            self.max_bullets = 10
            self.rem_bullets = 10

        self.bullet_regen_timer = 0

        self.invisible_cooldown = 0

        self.explosion_sprites = []

        for i in range(1, 18):
            self.explosion_sprites.append( arcade.Sprite(f'./effects/explosion/{i}.png', 3))
        self.explosion_sprites.append( arcade.Sprite(f'./effects/explosion/17.png', 3))
        self.explosion_sprites.append( arcade.Sprite(f'./effects/explosion/17.png', 3))
        self.explosion_sprites.append( arcade.Sprite(f'./effects/explosion/16.png', 3))
        self.explosion_sprites.append( arcade.Sprite(f'./effects/explosion/16.png', 3))
        for i in range(1, 15):
            self.explosion_sprites.append( arcade.Sprite(f'./effects/explosion/{16-i}.png', 3))
        for sprite in self.explosion_sprites:
            sprite.alpha = 150

        self.explosion_happening = False
        self.explosion_index = 0

        self.melee_attacking_sound = arcade.load_sound('sounds/effects/knifeSlice.ogg')
        self.shooting_sound = arcade.load_sound('sounds/effects/laser2.ogg')



    def health_pickup(self):
        self.health = self.max_health
        if self.type == 1:
            self.movement_speed = 4

    def set_brightness(self, brightness):
        self.color = [brightness, brightness, brightness]

    def getDamaged(self, from_x, from_y):
        if self.dead:
            return
        x = 0
        y = 0
        if from_x > self.center_x:
            x -= 1
        else:
            x += 1
        if from_y > self.center_y:
            y -= 1
        else: 
            y += 1
        self.dash(x, y)
        self.health -= 1
        if self.health == 0:
            self.dead = True
            self.facing_dir = 'RIGHT'
            self.angle = 90
            self.change_x = 0
            self.change_y = 0

    def dash(self, x=0, y=0):
        if self.dead:
            return
        if self.stamina > 0 or (x!=0 and y!=0):
            self.stamina_timer = 100

            relative_x = self.direction_x
            relative_y = self.direction_y
            
            if relative_y==0 and relative_x==0:
                relative_x=1

            if x != 0 or y!= 0:
                relative_x = x
                relative_y = y
           
            relative_magnitude =  magnitude(relative_x, relative_y)

            relative_x /= relative_magnitude
            relative_y /= relative_magnitude

            self.stamina -= 1

            self.dash_timer = 7
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

    def heal(self, x, y, sprite_list):
        if self.dead:
            return
        if (self.healing_state > 0 ):
            return
        cat_to_heal = arcade.get_sprites_at_point((x, y), sprite_list)
        if len(cat_to_heal) > 0 and cat_to_heal[0].max_health > cat_to_heal[0].health:
            cat_to_heal[0].health = cat_to_heal[0].health + 1 
            self.healing_state = 100

        
    def sneak_kill(self, x, y, sprite_list):
        if self.dead:
            return ""
        if (self.healing_state > 0 ):
            return ""
        enemy_to_kill = arcade.get_sprites_at_point((x, y), sprite_list)
        print(len(enemy_to_kill))
        if len(enemy_to_kill) > 0 :
            if magnitude(self.center_x - enemy_to_kill[0].center_x, self.center_y - enemy_to_kill[0].center_y) < self.width * 2:
                enemy_to_kill[0].health = 0
                self.healing_state = 100
            else:
                return "NOT IN RANGE"

        

    def update(self):
        if self.dead:
            return
        if self.stamina < 3:
            self.stamina_timer-= 1
            if (self.stamina_timer == 0):
                self.stamina_timer = 100
                self.stamina += 1



    def melee_attack_animation(self):
        if self.dead:
            return
        if self.invisible:
            self.visible()
            self.invisible_cooldown = 500
        
        self.melee_list = arcade.SpriteList()
        self.melee_sprite[self.melee_idx].center_x = self.center_x
        self.melee_sprite[self.melee_idx].center_y = self.center_y
        self.melee_sprite_2[self.melee_idx].center_x = self.center_x
        self.melee_sprite_2[self.melee_idx].center_y = self.center_y

        if self.facing_dir == 'RIGHT':
            self.melee_sprite[self.melee_idx].center_x += self.width/2
            self.melee_sprite_2[self.melee_idx].center_x += self.width/2 + 10
            self.melee_sprite[self.melee_idx].angle = 0
            self.melee_sprite_2[self.melee_idx].angle = 0
            if (self.melee_idx == 0 or self.melee_idx == 2):
                self.angle = 15
            else:
                self.angle = 30
        elif self.facing_dir == 'LEFT':
            self.melee_sprite[self.melee_idx].center_x -= self.width/2
            self.melee_sprite_2[self.melee_idx].center_x -= self.width/2 + 10
            self.melee_sprite[self.melee_idx].angle = 180
            self.melee_sprite_2[self.melee_idx].angle = 180
            
            if (self.melee_idx == 0 or self.melee_idx == 2):
                self.angle = -15
            else:
                self.angle = -30
        elif self.facing_dir == 'DOWN':
            self.melee_sprite[self.melee_idx].center_y -= self.height/2
            self.melee_sprite_2[self.melee_idx].center_y -= self.height/2 + 10
            self.melee_sprite[self.melee_idx].angle = -90
            self.melee_sprite_2[self.melee_idx].angle = -90
            
        elif self.facing_dir == 'UP':
            self.melee_sprite[self.melee_idx].center_y += self.height/2
            self.melee_sprite_2[self.melee_idx].center_y += self.height/2 + 10
            self.melee_sprite[self.melee_idx].angle = 90
            self.melee_sprite_2[self.melee_idx].angle = 90
        
        
        
        self.melee_list.append(self.melee_sprite[self.melee_idx])
        


    def melee(self):
        if self.dead:
            return
        if self.melee_attacking == False:
            self.melee_timer = 0
            self.melee_attacking = True
            self.melee_attack_animation()
            arcade.play_sound(self.melee_sound)


    def range(self, x , y, view_left, view_bottom):
        if self.dead or self.bullet_regen_timer > 0:
            return

        if (self.type == 1 or self.type == 4):
            if self.rem_bullets == 0: 
                return
            
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
            self.rem_bullets -= 1
            if self.rem_bullets == 0:
                self.bullet_regen_timer = 75

        elif self.type == 2:
            self.explosion_happening = True   
            self.projectile_state = False
            for sprite in self.explosion_sprites:
                sprite.center_x = x + view_left
                sprite.center_y = y + view_bottom
            bullet_regen_timer = 500



    def invisible(self):
        if self.dead:
            return
        if self.invisible_cooldown > 0 :
            return
        self.invisible_cooldown = 500
        self.visibility = False
        self.visibility_timer = 250
        self.alpha = 150

            
    def visible(self):
        self.visibility = True
        self.alpha = 255
            
    
    def update_animation(self,delta_time = 1/60):
        if self.bullet_regen_timer > 0:
            self.bullet_regen_timer -= 1
            if self.bullet_regen_timer == 0:
                self.rem_bullets = self.max_bullets
        if self.dead:
            return
        if self.healing_state > 0:
            self.healing_state -= 1

        if self.invisible_cooldown > 0:
            self.invisible_cooldown -= 1

        if self.type == 4:
            if self.health < self.max_health:
                if self.health_regen_timer <= 0:
                    self.health_regen_timer = 300
                    self.health += 1
                self.health_regen_timer -= 1

                

        if self.visibility_timer > 0:
            self.visibility_timer -= 1
            if self.visibility_timer == 0:
                self.visible()

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



