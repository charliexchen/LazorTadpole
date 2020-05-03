import itertools
import sys
import renderer
import numpy as np
import sys, random
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util

def add_ball(space):
    """Add a ball to the given space at a random position"""
    mass = 1
    radius = 14
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
    body = pymunk.Body(mass, inertia)
    x = random.randint(120,380)
    body.position = x, 550
    shape = pymunk.Circle(body, radius, (0,0))
    shape.collision_type = 0
    space.add(body, shape)
    return shape

def add_wall(line_end, line_start, space):
    line_point1 = pymunk.Vec2d(line_start)
    line_point2 = pymunk.Vec2d(line_end)
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, line_point1, line_point2, 0.0)
    shape.friction = 0.99
    space.add(shape)
    return shape


def add_food(pos, space):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = pos
    radius=14
    shape = pymunk.Circle(body, radius)
    shape.collision_type = 1
    space.add(body, shape)
    return shape

HEADLESS = False


def main():

    n_tadpoles = 10
    damping = 0.01
    screen_dims = (600, 600)
    policies = [renderer.RandomPolicy() for _ in range(n_tadpoles)]
    evaluate(n_tadpoles, damping, screen_dims, policies)


def evaluate(n_tadpoles, damping, screen_dims, policies):
    if not HEADLESS:
        pygame.init()
        screen = pygame.display.set_mode(screen_dims)
        pygame.display.set_caption("Some tadpoles swimming randomly.")
        clock = pygame.time.Clock()
        draw_options = pymunk.pygame_util.DrawOptions(screen)
    else:
        screen = None
        draw_options = None
        clock = None
    space = pymunk.Space()
    # space.gravity = (0.0, -90.0)
    space.damping = damping
    # Add walls.
    line_endpoints = []
    for line_start, line_end in [((0, 0), (0, 600)),
                                 ((0, 600), (600, 600)),
                                 ((600, 600), (600, 0)),
                                 ((600, 0), (0, 0))]:
        add_wall(line_end, line_start, space)
    # Add food.
    food_objects = []
    food_positions = itertools.product(range(100, 600, 100), range(100, 600, 100))
    for pos in food_positions:
        food_object = add_food(pos, space)
        food_objects.append(food_object)
    taddy_balls = [add_ball(space) for _ in range(n_tadpoles)]
    taddy_ball_mapping = {taddy_ball: i for i, taddy_ball in enumerate(taddy_balls)}

    # Initialize scores
    scores = {i: 0 for i in range(n_tadpoles)}
    # Add food-tadpole collision handler
    food_tadpole_handler = space.add_collision_handler(0, 1)

    def food_tadpole_handler_begin(arbiter, space, data):
        tadpole_ball, food = arbiter.shapes
        tadpole = taddy_ball_mapping[tadpole_ball]
        scores[tadpole] += 1
        space.remove(food)
        food_objects.remove(food)
        return False

    food_tadpole_handler.begin = food_tadpole_handler_begin
    # food_tadpole_handler.pre_solve = lambda arbiter, space, data: True
    # food_tadpole_handler.post_solve = lambda arbiter, space, data: print("post_solve")
    # food_tadpole_handler.separate = lambda arbiter, space, data: None
    while True:
        for taddy, policy in zip(taddy_balls, policies):
            force, rot = tuple(policy())
            force_vector = 300 * 1 * taddy.body.rotation_vector
            taddy.body.apply_force_at_local_point(force_vector, (0, 0))
            rot_force = 1000 * rot * taddy.body.rotation_vector.rotated(
                np.pi / 2)  # orthogonal to the rot vector, magnitude rot
            rot_force_position = taddy.body.rotation_vector  # unit distance in the direction of the rot vector
            taddy.body.apply_force_at_local_point(rot_force, rot_force_position)
            taddy.body.apply_force_at_local_point(-rot_force, -rot_force_position)

        if not food_objects:
            print(scores)
            sys.exit()

        if not HEADLESS:

            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit(0)

            screen.fill((255, 255, 255))

            space.debug_draw(draw_options)

            pygame.display.flip()
            clock.tick(50)

        space.step(1 / 50.0)


if __name__ == '__main__':
    main()