from dataclasses import dataclass
from typing import Tuple, Union
# from menu import *

import random
import sys

import pygame
from pygame.locals import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

POWER_2 = [2 ** _ for _ in range(1, 6)]
POWER_3 = [3 ** _ for _ in range(1, 6)]
POWER_5 = [5 ** _ for _ in range(1, 6)]

ALL_POWERS = [POWER_2, POWER_3, POWER_5]


@dataclass
class ValueAndPosition:
    value: int
    x: int
    y: int


class Board:
    def __init__(self, game, copied=False):
        self.board = [['.', '.', '.', '.'],
                      ['.', '.', '.', '.'],
                      ['.', '.', '.', '.'],
                      ['.', '.', '.', '.']]
        for i in range(4):
            for k in range(4):
                self.board[i][k] = random.choice(random.choice(ALL_POWERS))
        self.game = game
        self.copied = copied
        self.block_size_y = 100
        self.block_size_x = 100
        self.gap_size = 10
        self.selected_value = ValueAndPosition(0, 0, 0)

    def get_empty(self):
        empty = []
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == '.':
                    empty.append((i, j))
        return empty

    def create_random(self):
        empty = self.get_empty()
        if empty:
            i, j = random.choice(empty)
            value = random.choice([2] * 9 + [4])
            self.board[i][j] = value

    def get_block_value(self, position: Tuple[int, int]) -> Union[None, Tuple[int, int]]:
        x, y = position
        if max(x, y) > 480 or min(x, y) < 50:
            return None
        else:
            x -= 50
            y -= 50
            block_x = x // (self.block_size_x + self.gap_size)
            block_y = y // (self.block_size_y + self.gap_size)
            return block_y, block_x

    def set_new_val(self, pos: Tuple[int, int]):
        x, y = self.get_block_value(pos)
        self.selected_value.x = x
        self.selected_value.y = y
        self.selected_value.value = self.board[x][y]

    def change_two_blocks(self, pos: Tuple[int, int]):
        x, y = self.get_block_value(pos)
        new_val = ValueAndPosition(self.board[x][y], x, y)
        if all((new_val.value == self.selected_value, new_val == 1)):
            self.board[new_val.x][new_val.y] = -3
            self.board[self.selected_value.x][self.selected_value.y] = (-3, -3)
        elif any((new_val == self.selected_value, new_val.value == 1, self.selected_value == 1)):
            return None
        else:
            if ((self.selected_value.value % new_val.value == 0)):
                self.board[new_val.x][new_val.y] = 1
                self.board[self.selected_value.x][self.selected_value.y] = \
                    max(new_val.value, self.selected_value.value) // min(new_val.value, self.selected_value.value)
                self.selected_value = ValueAndPosition(0, 0, 0)
                return 1
            elif ((new_val.value % self.selected_value.value == 0)):
                self.board[self.selected_value.x][self.selected_value.y] = 1
                self.board[new_val.x][new_val.y] = \
                    max(new_val.value, self.selected_value.value) // min(new_val.value, self.selected_value.value)
                self.selected_value = ValueAndPosition(0, 0, 0)
                return 1
            else:
                self.selected_value = new_val
                return -1


class Cell(pygame.sprite.Sprite):
    colors = {1: Color(0, 33, 55), 2: Color(102, 0, 255), 4: Color(128, 0, 255), 8: Color(112, 0, 204), 16: Color(139, 0, 255),
              32: Color(138, 43, 226), 3: Color(148, 0, 211), 9: Color(153, 50, 204), 27: Color(116, 66, 200),
              81: Color(123, 104, 238), 243: Color(106, 90, 208),
              5: Color(147, 112, 216), 25: Color(153, 102, 204), 125: Color(120, 81, 169), 625: Color(115, 102, 189),
              3125: Color(93, 118, 203), -3: Color(0, 0, 0)}

    def __init__(self, pos, width=100, height=100, value=2):
        Font = pygame.font.Font('8-BIT WONDERmini.TTF', 24)
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.value = value
        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = pos
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(Color(self.colors[self.value]))

        self.label = Font.render(str(self.value), 1, BLACK)
        self.labelrect = self.label.get_rect()
        self.imagerect = self.image.get_rect()
        self.labelrect.center = self.imagerect.center
        if self.value != '.':
            self.image.blit(self.label, self.labelrect)

    def update(self, direction):
        pass

class GameMain:
    done = False
    color_bg = Color(0, 33, 55)

    def __init__(self, width=550, height=550):
        pygame.init()
        self.game_over = False
        self.font = pygame.font.Font('8-BIT WONDERmini.TTF', 24)
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.board = Board(self)
        self.score = 0

    def draw_board(self):
        self.cells = pygame.sprite.Group()
        cur_x, cur_y = 100, 100
        for row in self.board.board:
            for square in row:
                new_cell = Cell((cur_x, cur_y), value=square)
                self.cells.add(new_cell)
                cur_x += 110
            cur_y += 110
            cur_x = 100
        self.cells.draw(self.screen)

    def main_loop(self):
        while not self.done:
            self.handle_events()
            self.draw()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

    def draw(self):
        self.screen.fill(self.color_bg)
        self.draw_board()
        self.score_label = self.font.render("Score: %d" % (self.score), 1, WHITE)
        self.screen.blit(self.score_label, (50, 10))
        pygame.display.update()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == KEYDOWN and not self.game_over:
                if event.key == K_ESCAPE:
                    self.done = True
            elif event.type == MOUSEBUTTONDOWN:
                if self.board.selected_value == ValueAndPosition(0, 0, 0):
                    self.board.set_new_val(pygame.mouse.get_pos())
                else:
                    result = self.board.change_two_blocks(pygame.mouse.get_pos())
                    if result == 1:
                        self.score += 1

#
if __name__ == "__main__":
    game = GameMain()
    game.main_loop()