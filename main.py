from pico2d import *
import random

import grass as grass_module
from boy import Boy

# Support grass modules that expose the class under a different name.
Grass = getattr(grass_module, 'Grass', None)
if Grass is None:
    Grass = next(
        (value for value in vars(grass_module).values()
         if isinstance(value, type) and callable(getattr(value, 'draw', None))),
        None
    )
    
if Grass is None:
    class Grass:
        def __init__(self):
            self.image = load_image('grass.png')

        def update(self):
            pass

        def draw(self):
            self.image.draw(400, 30)

# Game object class here

def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global world
    global boy

    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True

open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
# finalization code
close_canvas()
