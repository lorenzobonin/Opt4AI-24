'''
In this lab session, we will leverage NEAT to make a car learn how to drive within a certain track.

The controller is based on a neural network taking 3 input values corresponding to the current distance from the grassy area
perceived by 3 different radar sensors.

We will use Pygame for the simulation environment.

'''

import pygame
import os
import math
import sys
import neat
import enum
import random

random.seed(5)

SCREEN_WIDTH = 1244
SCREEN_HEIGHT = 1016
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

TRACK = pygame.image.load(os.path.join("../pygame_assets", "track.png"))

directions = enum.Enum('directions', 'LEFT STRAIGHT RIGHT')


###############################################
################  CAR CLASS  ##################
###############################################

class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join("../pygame_assets", "car.png")) # we need it then for rotation
        self.image = pygame.transform.scale_by(self.original_image, 0.1) # current car image
        self.rect = self.image.get_rect(center=(490, 820)) # rectangle containing the car
        self.vel_vector = pygame.math.Vector2(0.8, 0) # car velocity vector
        self.angle = 0 # determines the steering of the car
        self.radar_angles = (-45, 0, 45) # angles of the redars
        self.rotation_vel = 5
        self.direction = directions.STRAIGHT
        self.alive = True # False if the car goes off the track
        self.radars = []

    def update(self):
        self.radars.clear()
        # to update the position of car you need to translate and rotate it
        self.translate()
        self.rotate()
        # get the distance from the grassy area from the sensors
        for radar_angle in self.radar_angles:
            self.radar(radar_angle)
        # detect whether the car went off the track
        self.collision()

    def translate(self):
        # we update the position of the car depending on the velocity vector
        self.rect.center += self.vel_vector * 6

    def collision(self):
        length = 40
        # the first collision point is located at the right headlight
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        # the first collision point is located at the left headlight
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        # die on collision (if one of the 2 collision points is on the grass)
        if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255):
            self.alive = False

        # draw collision points
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(SCREEN, (0, 255, 255, 0), collision_point_left, 4)

    def rotate(self):
        if self.direction == directions.RIGHT:
            #rotate clockwise
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == directions.LEFT:
            # rotate counterclockwise
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle):
        length = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        # the loop is responsible for extending the ray until it reaches a grassy area
        while not SCREEN.get_at((x, y)) == pygame.Color(2, 105, 31, 255) and length < 200:
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        # draw the ray
        pygame.draw.line(SCREEN, (255, 255, 255, 255), self.rect.center, (x, y), 1)
        pygame.draw.circle(SCREEN, (0, 255, 0, 0), (x, y), 3)

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                             + math.pow(self.rect.center[1] - y, 2)))

        self.radars.append([radar_angle, dist])

    def get_input(self):
        input = [0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input
    
###############################################
###############################################
###############################################


def eval_genomes(genomes, config):
    cars = []
    ge = []
    nets = []

    def remove(index):
        cars.pop(index)
        ge.pop(index)
        nets.pop(index)

    ###############
    ## CODE HERE ##
    ###############

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.blit(TRACK, (0, 0))

        ###############
        ## CODE HERE ##
        ###############

        pygame.display.update()


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    n_gen = 1 # change
    pop.run(eval_genomes, n_gen)