"""
Platformer Game
"""
import arcade
import math
from player import Player
from enemy import Enemy

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
RIGHT_VIEWPORT_MARGIN = 350
BOTTOM_VIEWPORT_MARGIN = 250
TOP_VIEWPORT_MARGIN = 250

RIGHT_FACING=0
LEFT_FACING=1

CUTSCENE_1 = 1
PLAYTHROUGH_1 = 2
PLAYTHROUGH_2 = 3
PLAYTHROUGH_3 = 4
PLAYTHROUGH_4 = 5

BLACK_BAR_HEIGHT = 100




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

        # --- Load in a map from the tiled editor ---
    def load_level(self,path_to_map,map_width,map_height,tile_width,tile_height,tile_scale):
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


        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        self.state = CUTSCENE_1
        self.cutscene_timer = 0
        self.can_control = False

        self.dashable_removed = False

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.dashable_list = arcade.SpriteList()
        self.blockable_list = arcade.SpriteList()
        self.health_pickup_list = arcade.SpriteList()

        self.player_idx = 0
        self.story_idx = 0 

        self.load_level("./maps/level-1.tmx",50,50,16,16,TILE_SCALING)

        # Set up the player, specifically placing it at these coordinates.
        self.player = Player()
        self.second_player = Player()
        self.third_player = Player()
        self.fourth_player = Player()
        self.player.setup("./characters/cat", CHARACTER_SCALING, 550, 1020, 1)
        self.second_player.setup("./characters/cat", CHARACTER_SCALING, 350, 200, 2)
        self.third_player.setup("./characters/cat", CHARACTER_SCALING, 350, 400, 3)
        self.fourth_player.setup("./characters/cat", CHARACTER_SCALING*1.2, 350, 416, 4)
        self.player_list.append(self.player)
        self.player_list.append(self.second_player)
        self.player_list.append(self.third_player)
        self.player_list.append(self.fourth_player)
        self.health_sprite = arcade.Sprite('./effects/256px-Paw-print.svg.png', 0.2)

        self.enemy = Enemy(self)
        self.enemy.setup("./characters/cat", CHARACTER_SCALING, 1200, 300)
        self.enemy_list.append(self.enemy)

        for sprite in self.wall_list:
            self.blockable_list.append(sprite)
        for sprite in self.dashable_list:
            self.blockable_list.append(sprite)

        #health pickups
        health_1 = arcade.Sprite("./images/animals/PNG/Round/parrot.png", 0.4)
        health_1.center_x = 350
        health_1.center_y = 550
        self.health_pickup_list.append(health_1)

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
            


        self.physics_engine_second = arcade.PhysicsEngineSimple(self.second_player,
                                                             self.blockable_list,
                                                             )

        self.enemy_physics_engine = arcade.PhysicsEngineSimple(self.enemy,
                                                             self.blockable_list,
                                                             )
        """
        self.physics_engine = arcade.PhysicsEngineSimple(self.player,
                                                            self.enemy_list
                                                             )
        """


    def setup_post_cut_scene(self):
        self.physics_engines[self.player_idx] = arcade.PhysicsEngineSimple(self.player,
                                                             self.blockable_list
                                                             )
                                           
        self.enemy.barrier_list.recalculate()

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Draw our sprites
        self.floor_list.draw()
        self.player.bullet_list.draw()
        self.dashable_list.draw()
        self.wall_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.props_list.draw()
        self.health_pickup_list.draw()

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

        plot_text = ["The cats and the hoomans lived in harmony",
                 "But one sudden evening, something stranged happened!",
                 "Cat: I don't understand, why was I thrown out?",
                 "Cat: I'm weak. I need to find something to heal", 
                 "Cat: That's a lot better! I need to figure out what's going on.",
                 "Cat: Maybe I can dash over that hole \n Press Shift to Dash",
                 ""]


        # Draw our health on the screen, scrolling it with the viewport
        health_text = f"stamina: {self.player.stamina}"
        arcade.draw_text(health_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 27, bold = True)
        arcade.draw_text(plot_text[self.story_idx], 10 + self.view_left, 40 + self.view_bottom,
                         arcade.csscolor.WHITE, 27, bold = True)

        if(self.enemy.path!=None):
            arcade.draw_line_strip(self.enemy.path, arcade.color.BLACK, 2)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.can_control:
            return
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player.melee()
        elif button == arcade.MOUSE_BUTTON_LEFT:
            if self.player.type == 1:
                self.player.range(x, y, self.view_left, self.view_bottom)
            elif self.player.type == 2:
                if (self.player.projectile_state):
                    self.player.range(x, y, self.view_left, self.view_bottom)
                else:
                    self.player.heal(x + self.view_left, y + self.view_bottom, self.player_list)

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
        if not self.can_control:
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
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary and top_boundary<self.level_height-TOP_VIEWPORT_MARGIN:
            self.view_target_bottom = self.player.top - top_boundary
            changed_bottom = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary and bottom_boundary>BOTTOM_VIEWPORT_MARGIN:
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

            self.view_bottom = max(0 ,self.view_bottom)
            self.view_bottom = min(self.view_bottom,self.level_height + BLACK_BAR_HEIGHT - SCREEN_HEIGHT)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


    def animate_cutscene_1(self, delta_time):
        self.cutscene_timer += delta_time 
        if (self.cutscene_timer == delta_time):
            self.player.set_brightness(0)
            self.player.health = 2
            self.player.movement_speed = 1


        if (self.cutscene_timer > 5):
            self.story_idx = 1

        if (self.cutscene_timer > 7):
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
        pass
    


    def on_update(self, delta_time):

        if (self.dashable_removed and self.player.dash_timer==0):
            self.dashable_removed = False
        
            for sprite in self.dashable_list:
                self.blockable_list.append(sprite)
        #print (self.player.center_x)


        self.update_scroll()

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

        # self.enemy.move()

        for bullet in self.player.bullet_list:
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            enemy_hit_list = arcade.check_for_collision(bullet, self.enemy.sprite)

            if len(wall_hit_list) > 0 or enemy_hit_list:
                bullet.remove_from_sprite_lists()

            if enemy_hit_list:
                self.enemy.health -= 1

            if bullet.bottom > self.view_bottom + self.height or bullet.top < 0 or bullet.right < 0 or bullet.left > self.view_left + self.width:
                bullet.remove_from_sprite_lists()

        for health in self.health_pickup_list:
            pickup = arcade.check_for_collision(health, self.player)
            if pickup:
                health.remove_from_sprite_lists()
                self.player.health_pickup()

        hit_list = arcade.check_for_collision_with_list(self.player, self.enemy_list)
        for enemy in hit_list:

            self.player.health-=1

            if enemy.bottom > self.player.bottom:
                self.player.bottom -= 100
            elif enemy.bottom < self.player.bottom:
                self.player.bottom += 100

            if enemy.left > self.player.left:
                self.player.left -= 100
            elif enemy.left < self.player.left:
                self.player.left += 100

        
        if self.player.melee_attacking:
            hit_list = arcade.check_for_collision_with_list(self.player.melee_sprite[self.player.melee_idx], self.enemy_list)

            for enemy in hit_list:
                self.enemy.health -= 1
                if enemy.bottom > self.player.bottom:
                    enemy.bottom += 100
                elif enemy.bottom < self.player.bottom:
                    enemy.bottom -= 100

                if enemy.left > self.player.left:
                    enemy.left += 100
                elif enemy.left < self.player.left:
                    enemy.left -= 100
        



        for physics_engine in self.physics_engines:
            physics_engine.update()
        self.enemy_physics_engine.update()
        self.enemy.update()

        
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
    arcade.run()


if __name__ == "__main__":
    main()
