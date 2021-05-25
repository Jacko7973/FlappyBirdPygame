import sys
import os
import random
import json

import pygame
from pygame.locals import *


class FlappyBird:

    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.canvas = pygame.display.set_mode((500, 500))
        pygame.display.set_caption('Flappy Bird')
        
        icon = pygame.image.load(os.path.join('images', 'bird.png'))
        pygame.display.set_icon(icon)

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont('Arial', 30, 1)

        self.floor = pygame.image.load(os.path.join('images', 'floor.png'))
        self.floor = pygame.transform.scale(self.floor, (500, 100))

        self.bird_size = (40, 35)
        self.bird = pygame.image.load(os.path.join('images', 'bird.png'))
        self.bird = pygame.transform.scale(self.bird, self.bird_size)

        self.speed = 3

        self.data_file_path = 'flappy_bird_data.json'
        if os.path.exists(self.data_file_path):
            with open(self.data_file_path, 'r') as f:
                self.saved_data = json.load(f)
        else:
            self.saved_data = {'high_score': 0}
            with open(self.data_file_path, 'w') as f:
                json.dump(self.saved_data, f)

        self.high_score = self.saved_data.get('high_score', 0)

        self.setup_game()

        while True:
            self.update()


    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == 32 and self.alive:
                    self.bird_vel_y = -3

        if self.alive:
            self.draw()
        else:
            self.draw_death()

        pygame.display.update()
        self.clock.tick(60)
        self.frame += 1


    def draw(self):
        self.canvas.fill('#5ecfe0')

        self.canvas.blit(self.floor, (-(self.frame * self.speed % 500) , 400))
        self.canvas.blit(self.floor, (-(self.frame * self.speed % 500) + 500, 400))

        for pipe in self.pipes[:]:
            if pipe.x < -50:
                self.pipes.remove(pipe)
            else:
                if pipe.x == self.bird_pos[0]:
                    self.score += 1
                    if self.score > self.high_score:
                        self.high_score = self.score

                if pipe.check_collisions(self.bird_pos, self.bird_size):
                    self.trigger_death()

                pipe.draw(self.canvas)

        if self.bird_pos[1] + self.bird_size[1] > 400:
            self.trigger_death()

        self.render_bird()
        self.render_score()

        if self.frame % 100 == 0:
            self.pipes.append(
                PipeGroup(random.randint(10, 250), random.randint(100, 150), self.speed)
            )

    def setup_game(self):
        self.bird_pos = (50, 100)
        self.bird_vel_y = 0
        self.bird_acc_y = 0.1

        self.pipes = []
        self.alive = True
        self.score = 0

        self.frame = 0
        self.death_frame = 0

    def render_bird(self, rotation_coeficient=5):
        self.bird_vel_y += self.bird_acc_y
        self.bird_pos = (self.bird_pos[0], self.bird_pos[1] + self.bird_vel_y)
        bird_sprite = pygame.transform.rotate(self.bird, -rotation_coeficient*self.bird_vel_y)
        self.canvas.blit(bird_sprite, self.bird_pos)

    def render_score(self):
        score_text = self.font.render(str(self.score), False, '#e3e3e3')
        self.canvas.blit(score_text, (10, 10))

        high_score_text = self.font.render(f'High Score: {self.high_score}', False, '#e3e3e3')
        self.canvas.blit(high_score_text, (490 - high_score_text.get_width(), 10))


    def trigger_death(self):
        self.death_frame = self.frame
        self.bird_vel_y = -5
        self.bird_acc_y = 0.1
        self.alive = False

        if self.score > self.saved_data.get('high_score', 0):
            self.saved_data.update({'high_score': self.score})
            with open(self.data_file_path, 'w') as f:
                json.dump(self.saved_data, f)


    def draw_death(self):
        self.canvas.fill('#5ecfe0')

        self.canvas.blit(self.floor, (-(self.death_frame * self.speed % 500) , 400))
        self.canvas.blit(self.floor, (-(self.death_frame * self.speed % 500) + 500, 400))

        for pipe in self.pipes[:]:
            pipe.draw(self.canvas, move=False)

        self.render_bird(rotation_coeficient=10)
        self.render_score()

        if self.frame == self.death_frame + 240:
            self.setup_game()





class PipeGroup:

    def __init__(self, opening_offset, opening_height, speed):
        self.x = 500
        self.opening_offset = opening_offset
        self.opening_height = opening_height
        self.speed = speed

        default_pipe = pygame.image.load(os.path.join('images', 'pipe.png'))
        self.bottom_pipe = pygame.transform.scale(default_pipe, (50, 500))
        self.top_pipe = pygame.transform.flip(self.bottom_pipe, False, True)


    def draw(self, canvas, move=True):
        if move:
            self.x -= self.speed
        canvas.blit(self.bottom_pipe, (self.x, self.opening_offset + self.opening_height))
        canvas.blit(self.top_pipe, (self.x, self.opening_offset - 500))


    def check_collisions(self, bird_pos, bird_size):
        (bird_x, bird_y) = bird_pos
        (bird_w, bird_h) = bird_size

        if self.x - bird_w < bird_x < self.x + 50:
            if bird_y < self.opening_offset:
                return True
            if bird_y + bird_h > self.opening_height + self.opening_offset:
                return True

        return False






if __name__ == '__main__':
    game = FlappyBird()

