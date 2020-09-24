"""
Platformer Game
"""
import arcade
import math
from player import Player

# Constants
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1.5
ENEMY_SCALING  = 0.5
TILE_SCALING = 5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
PLAYER_DASH_SPEED = 50
GRAVITY = 0
PLAYER_JUMP_SPEED = 20
BULLET_SPEED = 15

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 350
RIGHT_VIEWPORT_MARGIN = 350
BOTTOM_VIEWPORT_MARGIN = 250
TOP_VIEWPORT_MARGIN = 250

RIGHT_FACING=0
LEFT_FACING=1



def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

        



class Enemy:

    def __init__(self):
        self.sprite = None
        self.health = 10


    def setup(self):

        image_source = "./tiles/5_enemies_1_idle_007.png"

        self.direction = RIGHT_FACING

        self.sprite = arcade.Sprite(image_source, ENEMY_SCALING)
        self.sprite.initial_x = 900
        self.sprite.center_x = 900
        self.sprite.center_y = 1200
        self.walk_range = 100

    def move(self):

        if self.sprite.change_x == 0:
            if self.direction == LEFT_FACING:
                self.direction = RIGHT_FACING
            else:
                self.direction = LEFT_FACING
        
        if self.sprite.center_x > self.sprite.initial_x + self.walk_range:
            self.direction = LEFT_FACING
        elif self.sprite.center_x < self.sprite.initial_x - self.walk_range:
            self.direction = RIGHT_FACING

        if self.direction == LEFT_FACING:
            self.sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.sprite.change_x = +PLAYER_MOVEMENT_SPEED


        


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.wall_list = None
        self.bullet_list = None
        self.player_list = None
        self.enemy_list = None

        # Separate variable that holds the player sprite
        self.player = None
        self.enemy = None

        # Our physics engine
        self.physics_engine = None
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

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0


        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        self.player = Player()
        self.second_player = Player()
        self.player.setup("./characters/cat", CHARACTER_SCALING, 350, 350)
        self.second_player.setup("./characters/cat", CHARACTER_SCALING, 350, 200)
        self.player_list.append(self.player)
        self.player_list.append(self.second_player)

        self.enemy = Enemy()
        self.enemy.setup()
        self.enemy_list.append(self.enemy.sprite)



        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = "./maps/level-1.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Floor'
        platforms_wall_layer_name = 'Walls'
        platforms_props_layer_name = 'props'
        # Name of the layer that has items for pick-up

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

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(self.player,
                                                             self.wall_list,
                                                             )
        self.physics_engine_second = arcade.PhysicsEngineSimple(self.second_player,
                                                             self.wall_list,
                                                             )
        self.enemy_physics_engine = arcade.PhysicsEngineSimple(self.enemy.sprite,
                                                             self.wall_list,
                                                             )

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.floor_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.wall_list.draw()
        self.bullet_list.draw()
        self.props_list.draw()

        # Draw our health on the screen, scrolling it with the viewport
        health_text = f"health: {self.player.health} enemy: {self.enemy.health} stamina: {self.player.stamina}"
        arcade.draw_text(health_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)


    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_click = True
        elif button == arcade.MOUSE_BUTTON_LEFT:
            #create bullet
            bullet = arcade.Sprite("./tiles/ray.png", 1)

            #position at player
            bullet.center_x = self.player.center_x
            bullet.center_y = self.player.center_y

            x_diff = x - self.player.left + self.view_left - 30
            y_diff = y - self.player.bottom + self.view_bottom - 30

            angle = math.atan2(y_diff, x_diff)

            bullet.angle = math.degrees(angle) + 90

            bullet.change_x = math.cos(angle) * BULLET_SPEED
            bullet.change_y = math.sin(angle) * BULLET_SPEED

            self.bullet_list.append(bullet)
            
            #stop player motion
            self.right_click = False
            self.player.change_x=0
            self.player.change_y=0
            



    def on_mouse_motion(self, x, y, dx, dy):
        #position of mouse relative to palyer
        self.mouse_x = x
        self.mouse_y = y


    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_click = False
            self.player.change_x=0
            self.player.change_y=0


            

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player.change_y = PLAYER_MOVEMENT_SPEED
            self.player.direction_y = PLAYER_MOVEMENT_SPEED
            if self.player.change_x == 0:
                self.player.direction_x = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player.change_y = -PLAYER_MOVEMENT_SPEED
            self.player.direction_y = -PLAYER_MOVEMENT_SPEED
            if self.player.change_x == 0:
                self.player.direction_x = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
            self.player.direction_x = -PLAYER_MOVEMENT_SPEED
            if self.player.change_y == 0:
                self.player.direction_y = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
            self.player.direction_x = PLAYER_MOVEMENT_SPEED
            if self.player.change_y == 0:
                self.player.direction_y = 0
        elif key == 65505: 
            """shift"""
            self.player.dash()
            

        elif key == 32: #space
            #stop motion
            self.player.change_x = 0
            self.player.change_y = 0

            #make selected
            temp = self.player
            self.player = self.second_player
            self.second_player = temp

    def on_key_release(self, key, modifiers):
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

    def on_update(self, delta_time):

        self.player.update_animation()

        self.player.update()
        self.second_player.update()

        self.bullet_list.update()
        self.enemy.move()

        for bullet in self.bullet_list:
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            enemy_hit_list = arcade.check_for_collision(bullet, self.enemy.sprite)

            if len(wall_hit_list) > 0 or enemy_hit_list:
                bullet.remove_from_sprite_lists()

            if enemy_hit_list:
                self.enemy.health -= 1

            if bullet.bottom > self.view_bottom + self.height or bullet.top < 0 or bullet.right < 0 or bullet.left > self.view_left + self.width:
                bullet.remove_from_sprite_lists()


        for enemy in self.enemy_list:
            hit_list = arcade.check_for_collision(enemy, self.player)

            if hit_list:
                self.player.health-=1

                if enemy.bottom > self.player.bottom:
                    self.player.bottom -= 100
                elif enemy.bottom < self.player.bottom:
                    self.player.bottom += 100

                if enemy.left > self.player.left:
                    self.player.left -= 100
                elif enemy.left < self.player.left:
                    self.player.left += 100


        """ Movement and game logic """

        """"
        if self.shift_timer!=0 or self.right_click:
            relative_mouse_x = self.mouse_x - self.player.sprite.left + self.view_left - 30
            relative_mouse_y = self.mouse_y - self.player.sprite.bottom + self.view_bottom - 30
           
            relative_magnitude =  magnitude(relative_mouse_x, relative_mouse_y)

            relative_mouse_x /= relative_magnitude
            relative_mouse_y /= relative_magnitude

            if self.shift_timer==0 and self.right_click:

                self.player.sprite.change_x = PLAYER_MOVEMENT_SPEED*relative_mouse_x 
                self.player.sprite.change_y = PLAYER_MOVEMENT_SPEED*relative_mouse_y
            
            if self.shift_timer!=0:
                self.shift_timer-=1
                if self.shift_timer!=0:
                    self.player.sprite.change_x = PLAYER_DASH_SPEED*relative_mouse_x 
                    self.player.sprite.change_y = PLAYER_DASH_SPEED*relative_mouse_y
                else:
                    self.player.sprite.change_x = 0
                    self.player.sprite.change_y = 0
                    
        """

        



        self.physics_engine.update()
        self.physics_engine_second.update()
        self.enemy_physics_engine.update()


        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed_left = False
        changed_bottom = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            #self.view_left -= left_boundary - self.player.left
            self.view_target_left = - left_boundary + self.player.left

            changed_left = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            #self.view_left += self.player.right - right_boundary
            self.view_target_left = self.player.right - right_boundary
            changed_left = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            #self.view_bottom += self.player.top - top_boundary
            self.view_target_bottom = self.player.top - top_boundary
            changed_bottom = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            #self.view_bottom -= bottom_boundary - self.player.bottom
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

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
