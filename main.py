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


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Some tadpoles swimming randomly.")
    clock = pygame.time.Clock()

    space = pymunk.Space()
    # space.gravity = (0.0, -90.0)
    space.damping = 0.1


    for line_start, line_end in [((0, 0), (0, 600)),
                                 ((0, 600), (600, 600)),
                                 ((600, 600), (600, 0)),
                                 ((600, 0), (0, 0))]:
        add_wall(line_end, line_start, space)


    taddies = [add_ball(space) for _ in range(10)]
    policies = [renderer.RandomPolicy() for taddy in taddies]

    draw_options = pymunk.pygame_util.DrawOptions(screen)

    while True:
        for taddy, policy in zip(taddies, policies):
            force, rot = tuple(policy())
            force_vector = 300 * 1 * taddy.body.rotation_vector
            taddy.body.apply_force_at_local_point(force_vector, (0, 0))
            rot_force = 1000* rot * taddy.body.rotation_vector.rotated(np.pi/2) # orthogonal to the rot vector, magnitude rot
            rot_force_position = taddy.body.rotation_vector # unit distance in the direction of the rot vector
            taddy.body.apply_force_at_local_point(rot_force, rot_force_position)
            taddy.body.apply_force_at_local_point(-rot_force, -rot_force_position)


        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        screen.fill((255,255,255))

        space.debug_draw(draw_options)

        space.step(1/50.0)

        pygame.display.flip()
        clock.tick(50)



if __name__ == '__main__':
    main()