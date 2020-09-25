import arcade

VIEWPORT_MARGIN = 5
WIDTH = 25*16
HEIGHT = 10*16
TILE_SCALE = 1
SPRITE_SCALE = 1

SCREEN_WIDTH=WIDTH
SCREEN_HEIGHT=HEIGHT


class ZeldaPlayer(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.textures = {}
        sprite_sheet = 'images/zelda/gfx/character.png'
        left = []
        for i in range(4):
            left.append(arcade.load_texture(sprite_sheet,x=16*i,y=96,width=16,height=32))
        
        right = []
        for i in range(4):
            right.append(arcade.load_texture(sprite_sheet,x=16*i,y=32,width=16,height=32))

        up = []
        for i in range(4):
            up.append(arcade.load_texture(sprite_sheet,x=16*i,y=64,width=16,height=32))
        down = []
        for i in range(4):
            down.append(arcade.load_texture(sprite_sheet,x=16*i,y=0,width=16,height=32))


        self.textures['LEFT'] = left
        self.textures['RIGHT'] = right
        self.textures['UP'] = up
        self.textures['DOWN'] = down

        self.facing_dir = None
        self.curr_idx=0

    def update_animation(self,delta_time = 1/60):
        if self.change_x<0 and self.facing_dir != 'LEFT':
            self.facing_dir='LEFT'
        if self.change_x>0 and self.facing_dir != 'RIGHT':
            self.facing_dir='RIGHT'
        if self.change_y>0 and self.facing_dir != 'UP':
            self.facing_dir='UP'
        if self.change_y<0 and self.facing_dir != 'DOWN':
            self.facing_dir='DOWN'
        
        if(self.change_x == 0 and self.change_y==0):
            self.texture = self.textures[self.facing_dir][0]
            self.curr_idx=0
        else:
            self.curr_idx+=1
            if(self.curr_idx==len(self.textures[self.facing_dir])):
                self.curr_idx=0
            self.texture=self.textures[self.facing_dir][self.curr_idx]


class ZeldaWindow(arcade.Window):
    def __init__(self,width,height,title):
        super().__init__(width,height,title,resizable=True)
        arcade.set_background_color(arcade.color.WHITE)

        self.enemies_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.floor = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.player = None

        self.up_pressed = None
        self.down_pressed = None
        self.left_pressed = None
        self.right_pressed = None


        # Used in scrolling
        self.view_bottom = 0
        self.view_left = 0

    def setup(self):
        my_map = arcade.read_tmx("images/zelda.tmx")
        
        self.floor = arcade.process_layer(map_object=my_map,
                                        layer_name='Floor',
                                        scaling=1,
                                        use_spatial_hash=True)
        self.foundation = arcade.process_layer(map_object=my_map,
                                            layer_name='Foundations',
                                            scaling=1)

        self.carpet = arcade.process_layer(map_object=my_map,layer_name='Carpet',scaling=1)


        self.player = ZeldaPlayer()
        self.player.center_x = 20
        self.player.center_y = 20
        self.player.facing_dir = 'UP'
        self.player.curr_idx = 0
        self.player.texture = self.player.textures['UP'][self.player.curr_idx]
        
        self.player_list.append(self.player)

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        self.physics_engine = arcade.PhysicsEngineSimple(self.player,self.foundation)

    def on_draw(self):
        arcade.start_render()
        self.floor.draw()
        self.foundation.draw()
        self.carpet.draw()
        self.player_list.draw()

    def on_key_press(self, key, modifiers):
        if(key == arcade.key.UP):
            self.up_pressed=True
        elif(key == arcade.key.DOWN):
            self.down_pressed=True
        elif(key == arcade.key.LEFT):
            self.left_pressed=True
        elif(key == arcade.key.RIGHT):
            self.right_pressed=True

        self.process_keychange()
    
    def on_key_release(self, key, modifiers):
        if(key == arcade.key.UP):
            self.up_pressed=False
        elif(key == arcade.key.DOWN):
            self.down_pressed=False
        elif(key == arcade.key.LEFT):
            self.left_pressed=False
        elif(key == arcade.key.RIGHT):
            self.right_pressed=False
        
        self.process_keychange()


    def process_keychange(self):
        if self.left_pressed and not self.right_pressed:
            self.player.change_x=-1
        elif not self.left_pressed and self.right_pressed:
            self.player.change_x=1
        else:
            self.player.change_x=0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y=1
        elif not self.up_pressed and self.down_pressed:
            self.player.change_y=-1
        else:
            self.player.change_y=0

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
        
    def on_update(self, delta_time):
        self.player.update_animation()
        self.player_list.update()
        self.physics_engine.update()

        # --- Manage Scrolling ---

        # Keep track of if we changed the boundary. We don't want to call the
        # set_viewport command if we didn't change the view port.
        changed = False

        # Scroll left
        left_boundary = self.view_left + VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
            changed = True

        
        # Make sure our boundaries are integer values. While the view port does
        # support floating point numbers, for this application we want every pixel
        # in the view port to map directly onto a pixel on the screen. We don't want
        # any rounding errors.
        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)

        # If we changed the boundary values, update the view port to match
        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)



def main():
    """ Main method """
    window = ZeldaWindow(WIDTH,HEIGHT,'ZeldaWindow')
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
