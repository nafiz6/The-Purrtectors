"""
Platformer Game
"""
import arcade
import math
from player import Player
from enemy import Enemy
from enemy import Turret
from enemy import Boss


# Constants
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Outcast Cat"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1.5
ENEMY_SCALING  = 0.5
TILE_SCALING = 5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 4
PLAYER_DASH_SPEED = 50
GRAVITY = 0
PLAYER_JUMP_SPEED = 20

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 350
RIGHT_VIEWPORT_MARGIN = 520
BOTTOM_VIEWPORT_MARGIN = 320
TOP_VIEWPORT_MARGIN = 320

RIGHT_FACING=0
LEFT_FACING=1

CUTSCENE_1 = 1
PLAYTHROUGH_1 = 2
PLAYTHROUGH_2 = 3
PLAYTHROUGH_3 = 4
PLAYTHROUGH_4 = 5
PLAYTHROUGH_5 = 6
PLAYTHROUGH_6 = 7
PLAYTHROUGH_7 = 8
CUTSCENE_2 = 9
CUTSCENE_3 = 10
PLAYTHROUGH_8 = 11

BLACK_BAR_HEIGHT = 150

TURRET = 1
RANGE = 2
MELEE = 3
BOSS = 4




# class Enemy:
#     def __init__(self):
#         self.sprite = None
#         self.health = 10

#     def setup(self):
#         image_source = "./tiles/5_enemies_1_idle_007.png"
#         self.direction = RIGHT_FACING
#         self.sprite = arcade.Sprite(image_source, ENEMY_SCALING)
#         self.sprite.initial_x = 900
#         self.sprite.center_x = 900
#         self.sprite.center_y = 1200
#         self.walk_range = 100

#     def move(self):
#         if self.sprite.change_x == 0:
#             if self.direction == LEFT_FACING:
#                 self.direction = RIGHT_FACING
#             else:
#                 self.direction = LEFT_FACING
        
#         if self.sprite.center_x > self.sprite.initial_x + self.walk_range:
#             self.direction = LEFT_FACING
#         elif self.sprite.center_x < self.sprite.initial_x - self.walk_range:
#             self.direction = RIGHT_FACING

#         if self.direction == LEFT_FACING:
#             self.sprite.change_x = -PLAYER_MOVEMENT_SPEED
#         else:
#             self.sprite.change_x = +PLAYER_MOVEMENT_SPEED


        


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,resizable=True)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.wall_list = None
        self.player_list = None
        self.enemy_list = None
        self.dashable_list=None
        self.blockable_list=None
        self.health_pickup_list=None
        self.health_sprite = None

        self.can_control = None

        self.plot_text = None
        self.in_start_screen = None

        # Separate variable that holds the player sprite
        self.player = None
        self.enemy = None

        # Our physics engine
        self.physics_engines = None
        self.enemy_physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        self.mouse_x = 160
        self.mouse_y = 0

        self.right_click = False


        #smooth camera
        self.view_target_left = self.view_left
        self.view_target_bottom = self.view_bottom

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.state = None

        self.cutscene_timer = None
        self.player_idx = None
        self.story_idx = None
        self.level_sound = None

        # --- Load in a map from the tiled editor ---
    def load_level(self,path_to_map,path_to_level_sound,map_width,map_height,tile_width,tile_height,tile_scale):
        """ Loads a level"""

        # Name of map file to load
        map_name = path_to_map
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Floor'
        platforms_wall_layer_name = 'Walls'
        platforms_dashable_layer_name='Dashable'
        platforms_props_layer_name = 'props'

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_wall_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        self.floor_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        self.props_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_props_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        self.dashable_list = arcade.tilemap.process_layer(map_object=my_map
                                                        ,layer_name=platforms_dashable_layer_name,
                                                        scaling=TILE_SCALING,
                                                        use_spatial_hash=True)

        self.level_width  = map_width*tile_width*tile_scale
        self.level_height = map_height*tile_height*tile_scale

        self.dashable_removed = None
        if self.level_sound == None:
            #self.level_sound = arcade.load_sound(path_to_level_sound)
            pass

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        self.help_text = None

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        self.help_text = ""

        
        self.state = CUTSCENE_1
        self.cutscene_timer = 0
        self.can_control = False
        self.in_start_screen = True

        self.dashable_removed = False

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.dashable_list = arcade.SpriteList()
        self.blockable_list = arcade.SpriteList()
        self.health_pickup_list = arcade.SpriteList()
        

        self.player_idx = 0
        self.story_idx = 0 

        self.load_level("./maps/level-1.tmx","sounds/scores/level-1.mp3",50,50,16,16,TILE_SCALING)
        arcade.play_sound(self.level_sound)
        # Set up the player, specifically placing it at these coordinates.
        self.player = Player(self)
        self.second_player = Player(self)
        self.player.setup("./characters/cat", CHARACTER_SCALING, 550, 1020, 1)
        self.second_player.setup("./characters/cat", CHARACTER_SCALING, 3000 , 3400, 2)
        #self.third_player.setup("./characters/cat", CHARACTER_SCALING, 350, 400, 3)
        #self.fourth_player.setup("./characters/cat", CHARACTER_SCALING*1.2, 350, 416, 4)
        self.player_list.append(self.player)
        #self.player_list.append(self.second_player)
        #self.player_list.append(self.third_player)
        #self.player_list.append(self.fourth_player)
        self.health_sprite = arcade.Sprite('./effects/256px-Paw-print.svg.png', 0.2)
    

        self.enemy = Turret(self)
        self.enemy.setup("./characters/enemies/turret/turret", CHARACTER_SCALING, 2800, 300, TURRET)
        self.enemy_list.append(self.enemy)
        print(self.enemy.dead)

        self.enemy_2 = Enemy(self)
        self.enemy_2.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 3000, 300, MELEE)
        self.enemy_list.append(self.enemy_2)


        self.enemy_3 = Enemy(self)
        self.enemy_3.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 2500, 1500, MELEE)
        self.enemy_list.append(self.enemy_3)


        self.enemy_3 = Enemy(self)
        self.enemy_3.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 3000, 1560, MELEE)
        self.enemy_list.append(self.enemy_3)

        self.enemy_4 = Turret(self)
        self.enemy_4.setup("./characters/enemies/turret/turret", CHARACTER_SCALING, 2800, 1660, TURRET)
        self.enemy_list.append(self.enemy_4)
        
        self.enemy_5 = Enemy(self)
        self.enemy_5.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 3000, 1560, MELEE)
        self.enemy_list.append(self.enemy_5)

        self.enemy_6 = Turret(self)
        self.enemy_6.setup("./characters/enemies/turret/turret", CHARACTER_SCALING, 2800, 1400, TURRET)
        self.enemy_list.append(self.enemy_6)
        
        for sprite in self.wall_list:
            self.blockable_list.append(sprite)
        for sprite in self.dashable_list:
            self.blockable_list.append(sprite)

        #health pickups
        health_1 = arcade.Sprite("./effects/hpa/hpa/hpa.png")
        health_2 = arcade.Sprite("./effects/hpa/hpa/hpa.png")
        health_1.center_x = 2700
        health_1.center_y = 1100
        self.health_pickup_list.append(health_1)

        health_2.center_x = 350
        health_2.center_y = 550
        self.health_pickup_list.append(health_2)

        for tile in self.floor_list:
            tile.color = [200, 200, 255]
        for tile in self.wall_list:
            tile.color = [200, 200, 255]
        for tile in self.wall_list:
            tile.color = [200, 200, 255]


        

        # Create the 'physics engine'
        self.physics_engines = []

        for player in self.player_list:
            if (player == self.player):
                self.physics_engines.append(
                        arcade.PhysicsEngineSimple(player, self.enemy_list,
                                                                 )
                                                    )

            else:
                self.physics_engines.append(
                        arcade.PhysicsEngineSimple(player, self.blockable_list,
                                                                 )
                                                    )
            


        for enemy in self.enemy_list:
            self.physics_engines.append(
                                arcade.PhysicsEngineSimple(enemy,
                                     self.blockable_list,
                                             ))
        """
        self.physics_engine = arcade.PhysicsEngineSimple(self.player,
                                                            self.enemy_list
                                                             )
        """
        #self.enemy.barrier_list.recalculate()

    def setup_2(self):
        self.cutscene_timer = 0
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.dashable_list = arcade.SpriteList()
        self.blockable_list = arcade.SpriteList()
        self.health_pickup_list = arcade.SpriteList()

        self.load_level("./maps/level-3.tmx","sounds/scores/level-1.mp3",50,50,16,16,TILE_SCALING)
        

        # Set up the player, specifically placing it at these coordinates.
        self.player = Player(self)
        self.second_player = Player(self)
        self.third_player = Player(self)
        self.fourth_player = Player(self)
        self.player.setup("./characters/cat", CHARACTER_SCALING, 2000, 200, 1)
        self.player.facing_dir = 'UP'
        self.second_player.setup("./characters/cat", CHARACTER_SCALING, 2200 , 300, 2)
        self.player.facing_dir = 'LEFT'
        self.third_player.setup("./characters/cat", CHARACTER_SCALING, 2200 , 100, 3)
        self.player.facing_dir = 'RIGHT'
        self.fourth_player.setup("./characters/cat", CHARACTER_SCALING * 1.2, 2000 , 400, 4)
        self.player.facing_dir = 'DOWN'

        self.state = CUTSCENE_3
        self.story_idx = 17
        #self.third_player.setup("./characters/cat", CHARACTER_SCALING, 350, 400, 3)
        #self.fourth_player.setup("./characters/cat", CHARACTER_SCALING*1.2, 350, 416, 4)
        self.player_list.append(self.player)
        self.player_list.append(self.second_player)
        self.player_list.append(self.third_player)
        self.player_list.append(self.fourth_player)

        self.health_sprite = arcade.Sprite('./effects/256px-Paw-print.svg.png', 0.2)

        for sprite in self.wall_list:
            self.blockable_list.append(sprite)

        for player in self.player_list:

            self.physics_engines.append(
                    arcade.PhysicsEngineSimple(player, self.blockable_list,
                                                             )
                                                )

    def level2Enemies1(self):
        self.enemy_1 = Enemy(self)
        self.enemy_1.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 2200, 1200, MELEE)
        self.enemy_list.append(self.enemy_1)

        self.enemy_2 = Enemy(self)
        self.enemy_2.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 1800, 1200, MELEE)
        self.enemy_list.append(self.enemy_2)

        self.enemy_3 = Enemy(self)
        self.enemy_3.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 2000, 1500, MELEE)
        self.enemy_list.append(self.enemy_3)

        self.enemy_4 = Enemy(self)
        self.enemy_4.setup("./characters/enemies/robo-1/robo", CHARACTER_SCALING, 2300, 1800, MELEE)
        self.enemy_list.append(self.enemy_4)
        
        self.enemy_5 = Turret(self)
        self.enemy_5.setup("./characters/enemies/turret/turret", CHARACTER_SCALING, 2000, 1300, TURRET)
        self.enemy_list.append(self.enemy_5)
        
        self.enemy_6 = Turret(self)
        self.enemy_6.setup("./characters/enemies/turret/turret", CHARACTER_SCALING, 2200, 1300, TURRET)
        self.enemy_list.append(self.enemy_6)
        
        self.enemy_7 = Turret(self)
        self.enemy_7.setup("./characters/enemies/turret/turret", CHARACTER_SCALING, 2100, 1600, TURRET)
        self.enemy_list.append(self.enemy_7)
        
        self.enemy_8 = Boss(self)
        self.enemy_8.setup("./characters/enemies/robotgunner/turrent", CHARACTER_SCALING, 2000, 1600, RANGE)
        self.enemy_list.append(self.enemy_8)
        
        self.enemy_9 = Boss(self)
        self.enemy_9.setup("./characters/enemies/robotgunner/turrent", CHARACTER_SCALING, 2400, 1600, RANGE)
        self.enemy_list.append(self.enemy_9)
        
        self.enemy_10 = Boss(self)
        self.enemy_10.setup("./characters/enemies/robotgunner/turrent", CHARACTER_SCALING, 2400, 2000, RANGE)
        self.enemy_list.append(self.enemy_10)
        
        for enemy in self.enemy_list:
            self.physics_engines.append(
                                arcade.PhysicsEngineSimple(enemy,
                                     self.blockable_list,
                                             ))


    




    def setup_post_cut_scene(self):
        self.physics_engines[self.player_idx] = arcade.PhysicsEngineSimple(self.player,
                                                             self.blockable_list
                                                             )
                                           

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Draw our sprites
        self.floor_list.draw()
        self.dashable_list.draw()
        self.wall_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.props_list.draw()
        self.health_pickup_list.draw()

        for enemy in self.enemy_list:
            enemy.bullet_list.draw()

        self.player.hud_sprite.left = self.view_left
        self.player.hud_sprite.bottom = self.view_bottom + BLACK_BAR_HEIGHT
        self.player.hud_sprite.draw()

        for player in self.player_list:
            player.bullet_list.draw()
            if (player.explosion_happening):
                player.explosion_index += .5
                if player.explosion_index >= len(player.explosion_sprites):
                    player.explosion_happening = False
                    player.explosion_index = 0
                else:
                    player.explosion_sprites[int(player.explosion_index)].draw()



        if self.player.melee_attacking:
            self.player.melee_list.draw()

        if self.player.projectile_state:
            arcade.draw_circle_filled(self.mouse_x + self.view_left,
                                self.mouse_y + self.view_bottom, 100,
                             	(100, 149, 237, 50))


        for i in range(self.player.health):
            self.health_sprite.left = self.view_left + 10 + i*(self.health_sprite.width + 10)
            self.health_sprite.bottom = self.view_bottom + SCREEN_HEIGHT - BLACK_BAR_HEIGHT - self.health_sprite.height - 10 
            self.health_sprite.draw()
        
        rect = arcade.create_rectangle_filled(self.view_left + SCREEN_WIDTH/2, 
                self.view_bottom + BLACK_BAR_HEIGHT/2, SCREEN_WIDTH, BLACK_BAR_HEIGHT,
                (0,0,0))
        rect_top = arcade.create_rectangle_filled(self.view_left + SCREEN_WIDTH/2, 
                self.view_bottom + SCREEN_HEIGHT - BLACK_BAR_HEIGHT/2, SCREEN_WIDTH, BLACK_BAR_HEIGHT,
                (0,0,0))
        """
        rect = arcade.create_rectangle_filled(self.player.center_x, 
                self.player.center_y, SCREEN_WIDTH, BLACK_BAR_HEIGHT,
                (0,0,0))
        """
        rect.draw()
        rect_top.draw()

        self.plot_text = ["The cats and the hoomans lived in harmony",
                 "But one sudden evening, something stranged happened!",
                 "Cat: I don't understand, why was I thrown out?",
                 "Cat: I'm weak. I need to find something to heal", 
                 "Cat: That's a lot better! I need to figure out what's going on.",
                 "Cat: Maybe I can dash over that hole \nPress Shift to Dash",
                 "",
                 "Cat: Oh no! Danger Ahead!\nRight click to scratch",
                 "I think I can salvage the robot's laser \nLeft click to shoot laser",
                 "Why are there so many robots?!",
                 "Cat Two: Wow! You seem to be good at this!",
                 "One: WHAT THE HECK IS GOING ON?!",
                 "TWO: Everyone hates us now",
                 "TWO: ...we have to fight for our lives",
                 "TWO: You coming with me?",
                 "ONE: umm...",
                 "TWO: Unless you wanna hide here forever..",
                 "ONE: ok...",
                 "TWO: ok, you're in for a treat...meet..",
                 "TWO: Heavy cat….he's the best with guns..and nobody \n has ever gone through his shield",
                 "TWO: Support cat….without him we we'd be dead somewhere, \nhe heals and throws bombs to get us to safety",
                 "TWO: Aaand yours truly, I can become invisible and sneak up\non enemies and take them out before they know what hit em",
                 "FOUR: so...what're you good at.?",
                 "ONE: NOTHING, I'm just a house cat! I still have no idea what's going on",
                 "ONE: well..there's been rumours that this weird guy's responsible for all this...",
                 "???: you've been causing a lot of trouble for me,\nand so you shall die, muahahahahahaha",
                 "THREE: Who was that? Lets check it out!\nPRESS SPACE TO SWITCH BETWEEN DIFFERENT CATS",
                 "",
                 "",
                 ]


        # Draw our health on the screen, scrolling it with the viewport
        health_text = f"{self.player.help_text}"
        arcade.draw_text(health_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 27, bold = True)
        arcade.draw_text(self.plot_text[self.story_idx], 10 + self.view_left, 80 + self.view_bottom,
                         arcade.csscolor.WHITE, 27, bold = True)




    def on_mouse_press(self, x, y, button, modifiers):
        if not self.can_control:
            return
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.melee()
        elif button == arcade.MOUSE_BUTTON_LEFT:
            if self.player.type == 1 or self.player.type == 4:
                self.player.range(x, y, self.view_left, self.view_bottom)
            elif self.player.type == 2:
                if (self.player.projectile_state):
                    self.player.range(x, y, self.view_left, self.view_bottom)
                else:
                    self.player.heal(x + self.view_left, y + self.view_bottom, self.player_list)
            elif self.player.type == 3:
                self.help_text = self.player.sneak_kill(x + self.view_left, y + self.view_bottom, self.enemy_list)

    def on_mouse_motion(self, x, y, dx, dy):
        #position of mouse relative to palyer
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.can_control:
            return
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_click = False
            self.player.change_x=0
            self.player.change_y=0

    def on_key_press(self, key, modifiers):
        if (not self.can_control and key!=32) or (self.player.dead and key!=32):
            return
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = self.player.movement_speed
            self.player.direction_y = self.player.movement_speed
            if self.player.change_x == 0:
                self.player.direction_x = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = -self.player.movement_speed
            self.player.direction_y = -self.player.movement_speed
            if self.player.change_x == 0:
                self.player.direction_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -self.player.movement_speed
            self.player.direction_x = -self.player.movement_speed
            if self.player.change_y == 0:
                self.player.direction_y = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = self.player.movement_speed
            self.player.direction_x = self.player.movement_speed
            if self.player.change_y == 0:
                self.player.direction_y = 0
        elif key == 65505: 
            """shift"""

            if (self.player.type == 1):

                if not self.dashable_removed:
                    for sprite in self.dashable_list:
                        self.blockable_list.remove(sprite)
                self.dashable_removed = True
                    

                dash = self.player.dash()
                #if(dash!=(self.player.center_x,self.player.center_y) and arcade.has_line_of_sight((self.player.center_x,self.player.center_y),dash,self.wall_list)):
                #        self.player.center_x,self.player.center_y = dash
                
            elif (self.player.type == 2):
                self.player.projectile_state = True

            elif self.player.type == 3:
                self.player.invisible()
                

        elif key == 32: #space
            if (self.state == CUTSCENE_2):
                if (self.story_idx < len(self.plot_text) -1 ):
                    self.story_idx += 1
            if (self.state == CUTSCENE_3):
                if (self.story_idx < len(self.plot_text) -1 ):
                    self.cutscene_timer+=3
            else:
                #stop motion
                self.player.change_x = 0
                self.player.change_y = 0

                #make selected
                self.player_idx += 1
                if self.player_idx >= len(self.player_list):
                    self.player_idx = 0
                self.player = self.player_list[self.player_idx]
            

    def on_key_release(self, key, modifiers):
        if not self.can_control:
            return
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = 0
            if self.player.change_y!=0:
                self.player.direction_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = 0
            if self.player.change_y!=0:
                self.player.direction_x = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = 0
            if self.player.change_x!=0:
                self.player.direction_y = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = 0
            if self.player.change_x!=0:
                self.player.direction_y = 0

    def update_scroll(self):
        changed_left = False
        changed_bottom = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player.left < left_boundary and left_boundary > 0:
            self.view_target_left = - left_boundary + self.player.left
            changed_left = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player.right > right_boundary and right_boundary<self.level_width-RIGHT_VIEWPORT_MARGIN:
            self.view_target_left = self.player.right - right_boundary
            changed_left = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN - BLACK_BAR_HEIGHT
        if self.player.top > top_boundary:
            self.view_target_bottom = self.player.top - top_boundary
            changed_bottom = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN + BLACK_BAR_HEIGHT
        if self.player.bottom < bottom_boundary:
            self.view_target_bottom = - bottom_boundary + self.player.bottom
            changed_bottom = True

        if changed_bottom == False:
            self.view_target_bottom = 0

        if changed_left == False:
            self.view_target_left = 0

        if self.view_target_bottom!=self.view_bottom or self.view_target_left!=self.view_left:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_left += self.view_target_left/10
            self.view_bottom += self.view_target_bottom/10

            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            self.view_left = max(0,self.view_left)
            self.view_left = min(self.view_left,self.level_width-SCREEN_WIDTH)

            self.view_bottom = max(-BLACK_BAR_HEIGHT ,self.view_bottom)
            self.view_bottom = min(self.view_bottom,self.level_height + 2*BLACK_BAR_HEIGHT - SCREEN_HEIGHT)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


    def animate_cutscene_1(self, delta_time):
        self.player.canRange = False
        self.cutscene_timer += delta_time 
        if (self.cutscene_timer == delta_time):
            self.player.set_brightness(0)
            self.player.health = 5
            self.player.movement_speed = 1


        if (self.cutscene_timer > 5):
            self.story_idx = 1

        if (self.cutscene_timer > 7):
            self.player.health = 2
            brightness = self.player.color[0]
            brightness += 10
            if (brightness > 255):
                brightness = 255
            self.player.set_brightness(brightness)
            self.player.change_angle = 4.9
            self.player.change_x  = -5
            self.player.change_y = 0

        if self.cutscene_timer > 8.2:
            self.player.change_angle = 0
            self.player.angle = 0
            self.player.change_y = 0
            self.player.change_x = 0

            self.can_control = True

            self.state = PLAYTHROUGH_1
            self.setup_post_cut_scene()
            self.cutscene_timer = 0
            self.story_idx = 2

    def playthrough_1(self, delta_time):
        self.cutscene_timer += delta_time
        if self.cutscene_timer > 6:
            self.story_idx = 3
            self.state = PLAYTHROUGH_2
            self.cutscene_timer = 0

    def playthrough_2(self, delta_time):
        if self.player.health == self.player.max_health:
            self.story_idx = 4
            self.state = PLAYTHROUGH_3
        self.playthrough_3(delta_time)

    def playthrough_3(self, delta_time):
        if self.player.center_x > 794:
            self.story_idx = 5
            self.state = PLAYTHROUGH_4


    def playthrough_4(self, delta_time):
        if self.player.center_x > 1159:
            self.story_idx = 6
            self.state = PLAYTHROUGH_5

    def playthrough_5(self, delta_time):
        if self.player.center_x > 1350:
            self.story_idx = 7
        pass

    def playthrough_7(self, delta_time):
        if self.player.center_x > 2700 and self.player.center_y > 2000:
            self.story_idx = 9
            self.state = CUTSCENE_2
        pass



    
    def animate_cutscene_2(self, delta_time):
        self.player.change_x = 0
        self.player.change_y = 0
        self.second_player.change_x = 0
        self.second_player.change_y = 0
        self.cutscene_timer += delta_time 
        self.can_control = False
        self.player_list.append(self.second_player)
        self.physics_engines.append(
                        arcade.PhysicsEngineSimple(self.second_player, self.blockable_list,
                                                                 )
                                                    )
        if self.second_player.center_x < self.player.left:
            self.second_player.change_x = PLAYER_MOVEMENT_SPEED
        elif self.second_player.center_x > self.player.left + self.player.width:
            self.second_player.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.second_player.change_x = 0

        if self.second_player.center_y > self.player.bottom + self.player.height * 3:
            self.second_player.change_y = -PLAYER_MOVEMENT_SPEED
        else:
            self.second_player.change_y = 0
        if (self.cutscene_timer > 3):
            self.story_idx = 10
        if (self.cutscene_timer > 5):
            self.story_idx = 11
        if (self.cutscene_timer > 8):
            self.story_idx = 12
        if (self.cutscene_timer > 11):
            self.story_idx = 13
        if (self.cutscene_timer > 14):
            self.story_idx = 14
        if (self.cutscene_timer > 17):
            self.story_idx = 15
        if (self.cutscene_timer > 20):
            self.story_idx = 16
        if (self.cutscene_timer > 23):
            self.story_idx = 17
        if self.cutscene_timer > 27:
            self.setup_2()
            self.cutscene_timer = 0
            self.state = CUTSCENE_3

    def animate_cutscene_3(self, delta_time):
        self.cutscene_timer += delta_time 
        self.can_control = False
        if (self.cutscene_timer > 3):
            self.story_idx = 18
        if (self.cutscene_timer > 6):
            self.story_idx = 19
        if (self.cutscene_timer > 9):
            self.story_idx = 20
        if (self.cutscene_timer > 13):
            self.story_idx = 21
        if (self.cutscene_timer > 17):
            self.story_idx = 22
        if (self.cutscene_timer > 21):
            self.story_idx = 23
        if (self.cutscene_timer > 25):
            self.story_idx = 24
        if (self.cutscene_timer > 29):
            self.second_player.explosion(SCREEN_WIDTH/3 , SCREEN_HEIGHT - BLACK_BAR_HEIGHT, self.view_left, self.view_bottom)
        if (self.cutscene_timer > 30):
            self.story_idx = 25
        if (self.cutscene_timer > 34):
            self.story_idx = 26
            self.state = PLAYTHROUGH_8
            self.can_control = True
            self.level2Enemies1()
    
    



    def on_update(self, delta_time):

        if (self.dashable_removed and self.player.dash_timer==0):
            self.dashable_removed = False
        
            for sprite in self.dashable_list:
                self.blockable_list.append(sprite)
        #print (self.player.center_x)


        self.update_scroll()
        for enemy in self.enemy_list:
            enemy.bullet_list.update()

        for player in self.player_list:
            player.update_animation()
            player.update()
            player.bullet_list.update()

          
        if (self.state == CUTSCENE_1):
            self.animate_cutscene_1(delta_time)
        elif (self.state == PLAYTHROUGH_1):
            self.playthrough_1(delta_time)
        elif (self.state == PLAYTHROUGH_2):
            self.playthrough_2(delta_time)
        elif (self.state == PLAYTHROUGH_3):
            self.playthrough_3(delta_time)
        elif (self.state == PLAYTHROUGH_4):
            self.playthrough_4(delta_time)
        elif (self.state == PLAYTHROUGH_5):
            self.playthrough_5(delta_time)
        elif (self.state == PLAYTHROUGH_7):
            self.playthrough_7(delta_time)
        elif (self.state == CUTSCENE_2):
            self.animate_cutscene_2(delta_time)
        elif (self.state == CUTSCENE_3):
            self.animate_cutscene_3(delta_time)

        # self.enemy.move()

        for player in self.player_list:
            for bullet in player.bullet_list:
                wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
                enemy_hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

                if len(wall_hit_list) > 0 or len(enemy_hit_list) > 0:
                    bullet.remove_from_sprite_lists()

                for enemy in enemy_hit_list:
                    enemy.getDamaged(bullet.center_x, bullet.center_y)

                if bullet.bottom > self.view_bottom + self.height or bullet.top < 0 or bullet.right < 0 or bullet.left > self.view_left + self.width:
                    bullet.remove_from_sprite_lists()

            if player.explosion_happening:
                enemy_hit_list = arcade.check_for_collision_with_list(player.explosion_sprites[int(player.explosion_index)],
                                                                self.enemy_list)
                for enemy in enemy_hit_list:
                    enemy.getDamaged(player.explosion_sprites[int(player.explosion_index)].center_x,
                            player.explosion_sprites[int(player.explosion_index)].center_y)


        
        for e in self.enemy_list:
            for bullet in e.bullet_list:
                wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
                enemy_hit_list = arcade.check_for_collision(bullet, self.player)

        for enemy in self.enemy_list:
            for bullet in enemy.bullet_list:
                wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
                enemy_hit_list = arcade.check_for_collision(bullet, self.player)

                if len(wall_hit_list) > 0 or enemy_hit_list:
                    bullet.remove_from_sprite_lists()

                if enemy_hit_list:
                    self.player.getDamaged(bullet.center_x, bullet.center_y)
                if len(wall_hit_list) > 0 or enemy_hit_list:
                    bullet.remove_from_sprite_lists()

                print(enemy_hit_list,bullet.position,self.player.position)
                if enemy_hit_list:
                    self.player.getDamaged(enemy.center_x, enemy.center_y)

                if bullet.bottom > self.view_bottom + self.height or bullet.top < 0 or bullet.right < 0 or bullet.left > self.view_left + self.width:
                    bullet.remove_from_sprite_lists()

        for health in self.health_pickup_list:
            pickup = arcade.check_for_collision(health, self.player)
            if pickup:
                health.remove_from_sprite_lists()
                self.player.health_pickup()

        hit_list = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        for enemy in hit_list:
            if enemy.path_traversal_state == 'ATTACK' or enemy.path_traversal_state=='SHOOT' or enemy.path_traversal_state=='MELEE':
                self.player.getDamaged(enemy.center_x, enemy.center_y)
                enemy.deagro()


        
        if self.player.melee_attacking:
            hit_list = arcade.check_for_collision_with_list(self.player.melee_sprite[self.player.melee_idx], self.enemy_list)

            for enemy in hit_list:
                enemy.getDamaged(self.player.center_x, self.player.center_y)
        

        """
        if(self.level_sound.is_complete()):
            arcade.play_sound(self.level_sound)
        """

        for physics_engine in self.physics_engines:
            physics_engine.update()
        #self.enemy_physics_engine.update()
        
        for enemy in self.enemy_list:
            if (self.player.center_x<enemy.range_x[1] 
            and self.player.center_x>enemy.range_x[0]
            and self.player.center_y<enemy.range_y[1]
            and self.player.center_y>enemy.range_y[0]):
                enemy.update()
                enemy.update_animation()



        
        #print(self.enemy.path)
        #print(self.player.center_x,self.player.center_y)




        

    def on_resize(self, width, height):
        """ This method is automatically called when the window is resized. """

        # Call the parent. Failing to do this will mess up the coordinates, and default to 0,0 at the center and the
        # edges being -1 to 1.
        super().on_resize(width, height)

        # global SCREEN_WIDTH
        # global SCREEN_HEIGHT
        
        # SCREEN_WIDTH, SCREEN_HEIGHT = width,height

        arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)
        print(f"Window resized to: {width}, {height}")


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    window.setup_2()
    arcade.run()


if __name__ == "__main__":
    main()
