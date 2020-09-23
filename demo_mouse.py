"""
Platformer Game
"""
import arcade
import math
from arcade.isometric import isometric_grid_to_screen

# Constants
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 10
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
PLAYER_DASH_SPEED = 50
GRAVITY = 0
PLAYER_JUMP_SPEED = 20
BULLET_SPEED = 15

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 350
RIGHT_VIEWPORT_MARGIN = 350
BOTTOM_VIEWPORT_MARGIN = 350
TOP_VIEWPORT_MARGIN = 350


def magnitude(x, y):
    return math.sqrt(x*x + y*y)


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coin_list = None
        self.wall_list = None
        self.bullet_list = None
        self.player_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        self.mouse_x = 160
        self.mouse_y = 0

        self.right_click = False

        self.direction_x = 1
        self.direction_y = 0

        #smooth camera
        self.view_target_left = self.view_left
        self.view_target_bottom = self.view_bottom

        self.shift_timer = 0


        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"

        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 350
        self.player_sprite.center_y = 350
        self.player_list.append(self.player_sprite)



        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = "./tiles/level1.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Floor'
        platforms_wall_layer_name = 'Walls'
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
        # -- Coins

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite,
                                                             self.wall_list,
                                                             )

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.floor_list.draw()
        self.player_list.draw()
        self.wall_list.draw()
        self.bullet_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)


    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_click = True
        elif button == arcade.MOUSE_BUTTON_LEFT:
            #create bullet
            bullet = arcade.Sprite("./tiles/ray.png", 1)

            #position at player
            bullet.center_x = self.player_sprite.center_x
            bullet.center_y = self.player_sprite.center_y

            x_diff = x - self.player_sprite.left + self.view_left - 30
            y_diff = y - self.player_sprite.bottom + self.view_bottom - 30

            angle = math.atan2(y_diff, x_diff)

            bullet.angle = math.degrees(angle) + 90

            bullet.change_x = math.cos(angle) * BULLET_SPEED
            bullet.change_y = math.sin(angle) * BULLET_SPEED

            self.bullet_list.append(bullet)
            
            #stop player motion
            self.right_click = False
            self.player_sprite.change_x=0
            self.player_sprite.change_y=0
            



    def on_mouse_motion(self, x, y, dx, dy):
        #position of mouse relative to palyer
        self.mouse_x = x
        self.mouse_y = y


    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.right_click = False
            self.player_sprite.change_x=0
            self.player_sprite.change_y=0


            

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        """
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            self.direction_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
            self.direction_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.direction_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.direction_x = PLAYER_MOVEMENT_SPEED
        """
        if key == 65505: 
            """shift"""
            self.shift_timer = 5
            

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
            if self.player_sprite.change_y!=0:
                self.direction_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0
            if self.player_sprite.change_y!=0:
                self.direction_x = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
            if self.player_sprite.change_x!=0:
                self.direction_y = 0
        elif key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
            if self.player_sprite.change_x!=0:
                self.direction_y = 0

    def on_update(self, delta_time):


        self.bullet_list.update()

        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)

            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if bullet.bottom > self.view_bottom + self.height or bullet.top < 0 or bullet.right < 0 or bullet.left > self.view_left + self.width:
                bullet.remove_from_sprite_lists()

        """ Movement and game logic """

        if self.shift_timer!=0 or self.right_click:
            relative_mouse_x = self.mouse_x - self.player_sprite.left + self.view_left - 30
            relative_mouse_y = self.mouse_y - self.player_sprite.bottom + self.view_bottom - 30
           
            relative_magnitude =  magnitude(relative_mouse_x, relative_mouse_y)

            relative_mouse_x /= relative_magnitude
            relative_mouse_y /= relative_magnitude

            if self.shift_timer==0 and self.right_click:

                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED*relative_mouse_x 
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED*relative_mouse_y
            
            if self.shift_timer!=0:
                self.shift_timer-=1
                if self.shift_timer!=0:
                    self.player_sprite.change_x = PLAYER_DASH_SPEED*relative_mouse_x 
                    self.player_sprite.change_y = PLAYER_DASH_SPEED*relative_mouse_y
                else:
                    self.player_sprite.change_x = 0
                    self.player_sprite.change_y = 0
                    
        



        self.physics_engine.update()

        # See if we hit any coins

        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed_left = False
        changed_bottom = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            #self.view_left -= left_boundary - self.player_sprite.left
            self.view_target_left = - left_boundary + self.player_sprite.left

            changed_left = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            #self.view_left += self.player_sprite.right - right_boundary
            self.view_target_left = self.player_sprite.right - right_boundary
            changed_left = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            #self.view_bottom += self.player_sprite.top - top_boundary
            self.view_target_bottom = self.player_sprite.top - top_boundary
            changed_bottom = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            #self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            self.view_target_bottom = - bottom_boundary + self.player_sprite.bottom
            changed_bottom = True

        if changed_bottom == False:
            self.view_target_bottom = 0

        if changed_left == False:
            self.view_target_left = 0

        if self.view_target_bottom!=self.view_bottom or self.view_target_left!=self.view_left:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_left += self.view_target_left/6
            self.view_bottom += self.view_target_bottom/6


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
