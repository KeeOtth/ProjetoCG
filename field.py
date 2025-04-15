import math
import random
import threading
import time

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pygame.locals import *
from pygame.mixer import Sound

pygame.mixer.init()
tome = Sound("./tome.mp3")

class Ball:
    def __init__(self, x, y, texture_id):
        self.x = x
        self.y = y
        self.radius = 8.5
        self.theta_x = 0
        self.theta_y = 0
        self.texture_id = texture_id
        self.quad = gluNewQuadric()
        gluQuadricTexture(self.quad, GL_TRUE)
        gluQuadricNormals(self.quad, GLU_SMOOTH)

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        self.theta_x = self.theta_x % 360
        self.theta_y = self.theta_y % 360
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotate(self.theta_x, 1, 0, 0)
        glRotate(self.theta_y, 0, 1, 0)
        gluSphere(self.quad, self.radius, 50, 50)
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self, ax, ay):
        self.theta_x += ax
        self.theta_y += ay

    def erase(self):
        glDeleteTextures([self.texture_id])
        gluDeleteQuadric(self.quad)

    def get_aabb(self):
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
        )


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.half_width = 8
        self.half_height = 20
        self.direction = []
        self.diff = 1.5
        self.guard = 0

    def draw(self):
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(self.x + self.half_width, self.y + self.half_height, 0)
        glVertex3f(self.x - self.half_width, self.y + self.half_height, 0)
        glVertex3f(self.x - self.half_width, self.y - self.half_height, 0)
        glVertex3f(self.x + self.half_width, self.y - self.half_height, 0)
        glEnd()
        if self.x >= 400:
            glColor3f(0.0, 0.8, 1.0)
        elif self.x < 400:
            glColor3f(1.0, 0.0, 0.4)
        glBegin(GL_QUADS)
        glVertex3f(self.x + 9, self.y + 14, 0)
        glVertex3f(self.x - 9, self.y + 14, 0)
        glVertex3f(self.x - 9, self.y - 14, 0)
        glVertex3f(self.x + 9, self.y - 14, 0)
        glEnd()
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(self.x, self.y, 0)
        for i in range(51):
            angle = 2 * math.pi * i / 50
            cx = self.x + 8 * math.cos(angle)
            cy = self.y + 8 * math.sin(angle)
            glVertex3f(cx, cy, 0)
        glEnd()

    def update(self, bola: Ball):
        if abs(bola.x - self.x) > 100:
            if random.random() <= 0.02:
                self.diff *= -1
        else:
            if self.y != bola.y:
                if abs(self.y - bola.y) > 15:
                    self.diff = (
                        abs(self.diff)
                        * (abs(self.y - bola.y) / (self.y - bola.y))
                        * (-1)
                    )

        if random.random() <= 0.01:
            self.diff = (1 + random.random() * 1.5) * (abs(self.diff) / self.diff)

        self.y += self.diff
        if self.y + self.diff > 380:
            self.y = 379
            self.diff *= -1
        elif self.y + self.diff < 220:
            self.y = 221
            self.diff *= -1

    def get_aabb(self):
        return (
            self.x - self.half_width,
            self.y - self.half_height,
            self.x + self.half_width,
            self.y + self.half_height,
        )

    def aabb_collision(
        self, a_left, a_bottom, a_right, a_top, b_left, b_bottom, b_right, b_top
    ):
        return (
            a_left < b_right
            and a_right > b_left
            and a_bottom < b_top
            and a_top > b_bottom
        )

    def collision(self, ball):
        player_box = self.get_aabb()
        ball_box = ball.get_aabb()

        return self.aabb_collision(*player_box, *ball_box)


class Field:
    def __init__(self):
        self.points_a = 0
        self.points_b = 0
        self.gool_string = "ooOoOOoOOo"
        self.is_gol = False

    def plot(self, x, y):
        glBegin(GL_POINTS)
        glVertex3i(x, y, 0)
        glEnd()

    def bresenhamLine(self, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            self.plot(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def drawCircle(self, xc, yc, r):
        x = 0
        y = r
        d = 3 - 2 * r
        while y >= x:
            self.plot(xc + x, yc + y)
            self.plot(xc - x, yc + y)
            self.plot(xc + x, yc - y)
            self.plot(xc - x, yc - y)
            self.plot(xc + y, yc + x)
            self.plot(xc - y, yc + x)
            self.plot(xc + y, yc - x)
            self.plot(xc - y, yc - x)
            x += 1
            if d >= 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6

    def draw(self):
        # Definindo a faixa
        faixa_x = 100  # Começando a faixa a 200 unidades no eixo X (entre 100 e 700)

        glColor3f(0.1, 0.52, 0.1)
        # Desenhando o campo
        glBegin(GL_QUADS)  # Campo
        glTexCoord2f(0, 0)
        glVertex2f(100, 100)

        glTexCoord2f(1, 0)
        glVertex2f(700, 100)

        glTexCoord2f(1, 1)
        glVertex2f(700, 500)

        glTexCoord2f(0, 1)
        glVertex2f(100, 500)
        glEnd()

        faixa_largura = 50  # Aumentando a largura das faixas para 30
        glColor3f(0.1, 0.6, 0.1)  # Cor das faixas (branco)

        # Adiciona faixas a cada 100 unidades no eixo X
        while faixa_x < 700:
            glBegin(GL_QUADS)  # Faixa
            glVertex2f(faixa_x, 100)
            glVertex2f(faixa_x + faixa_largura, 100)
            glVertex2f(faixa_x + faixa_largura, 500)
            glVertex2f(faixa_x, 500)
            glEnd()

            faixa_x += 2 * faixa_largura  # Próxima faixa

        glColor3f(1, 1, 1)  # Cor das linhas

        # Linhas do campo
        self.bresenhamLine(100, 100, 700, 100)
        self.bresenhamLine(700, 100, 700, 500)
        self.bresenhamLine(700, 500, 100, 500)
        self.bresenhamLine(100, 500, 100, 100)

        # Linha central
        self.bresenhamLine(400, 100, 400, 500)

        # Círculo central
        self.drawCircle(400, 300, 50)

        # Área esquerda
        self.bresenhamLine(100, 200, 200, 200)
        self.bresenhamLine(200, 200, 200, 400)
        self.bresenhamLine(200, 400, 100, 400)

        # Área direita
        self.bresenhamLine(700, 200, 600, 200)
        self.bresenhamLine(600, 200, 600, 400)
        self.bresenhamLine(600, 400, 700, 400)

    def cyclic_shift(self):
        if self.is_gol:
            self.gool_string = self.gool_string[-1] + self.gool_string[:-1]
            threading.Timer(0.1, self.cyclic_shift).start()

    def display_score(self):
        string = (
            "Time A  " + str(self.points_a) + "   |   Time B  " + str(self.points_b)
        ).encode()
        glColor3f(1.0, 1.0, 1.0)
        glRasterPos(322, 550)
        for c in string:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, c)

        if self.is_gol:
            gool_string_enc = ("G" + self.gool_string + "L").encode()
            glColor3f(1.0, 1.0, 1.0)
            glRasterPos(340, 520)
            for c in gool_string_enc:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, c)

    def reset_after_goal(self):
        self.is_gol = False
        time.sleep(0.4)
        self.points_a = 0
        self.points_b = 0


class Game:
    def __init__(self):
        self.running = True
        self.key_state = [False] * 4  # [UP, DOWN, LEFT, RIGHT]
        self.field = Field()
        self.goleiro1 = Player(688, 300)
        self.goleiro2 = Player(112, 300)
        self.ball = Ball(400.0, 300.0, None)
        self.texture_id = None

    def load_texture(self, path):
        texture_surface = pygame.image.load(path)
        texture_data = pygame.image.tostring(texture_surface, "RGB", True)
        width, height = texture_surface.get_rect().size

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            width,
            height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            texture_data,
        )

        return texture_id

    def check_collision(self):
        if self.goleiro1.collision(self.ball):
            dx = self.ball.x - self.goleiro1.x
            dy = self.ball.y - self.goleiro1.y

            if dx == 0 and dy == 0:
                dx = 1

            length = (dx**2 + dy**2) ** 0.5
            dx /= length
            dy /= length

            bounce_distance = 15
            self.ball.move(dx * bounce_distance, dy * bounce_distance)

        if self.goleiro2.collision(self.ball):
            dx = self.ball.x - self.goleiro2.x
            dy = self.ball.y - self.goleiro2.y

            if dx == 0 and dy == 0:
                dx = 1

            length = (dx**2 + dy**2) ** 0.5
            dx /= length
            dy /= length

            bounce_distance = 15
            self.ball.move(dx * bounce_distance, dy * bounce_distance)

    def update(self):
        movement = 2
        angle = 5

        left_bound = 100 + self.ball.radius
        right_bound = 700 - self.ball.radius
        top_bound = 500 - self.ball.radius
        bottom_bound = 100 + self.ball.radius

        if self.key_state[0] and self.ball.y + movement <= top_bound:
            self.ball.move(0, movement)
            self.ball.rotate(-angle, 0)
        if self.key_state[1] and self.ball.y - movement >= bottom_bound:
            self.ball.move(0, -movement)
            self.ball.rotate(angle, 0)
        if self.key_state[2] and (
            self.ball.x - movement >= left_bound
            or (self.ball.y >= 200 and self.ball.y <= 400)
        ):
            self.ball.move(-movement, 0)
            self.ball.rotate(0, -angle)
        if self.key_state[3] and (
            self.ball.x + movement <= right_bound
            or (self.ball.y >= 200 and self.ball.y <= 400)
        ):
            self.ball.move(movement, 0)
            self.ball.rotate(0, angle)

        self.goleiro1.update(self.ball)
        self.goleiro2.update(self.ball)
        self.check_goal()
        self.check_collision()

    def check_goal(self):
        if self.ball.x <= 95:
            self.field.points_b += 1
            self.field.is_gol = True
            self.gol()
        elif self.ball.x >= 703:
            self.field.points_a += 1
            self.field.is_gol = True
            self.gol()

    def gol(self):
        tome.play()
        self.ball.x = 400.0
        self.ball.y = 20000.0
        self.field.is_gol = True
        self.field.cyclic_shift()
        threading.Timer(3, self.back_after_gol).start()

    def back_after_gol(self):
        self.field.is_gol = False
        time.sleep(0.1)
        self.ball.x = 400.0
        self.ball.y = 300.0

    def special_key_down(self, key):
        if key == pygame.K_UP:
            self.key_state[0] = True
        elif key == pygame.K_DOWN:
            self.key_state[1] = True
        elif key == pygame.K_LEFT:
            self.key_state[2] = True
        elif key == pygame.K_RIGHT:
            self.key_state[3] = True

    def special_key_up(self, key):
        if key == pygame.K_UP:
            self.key_state[0] = False
        elif key == pygame.K_DOWN:
            self.key_state[1] = False
        elif key == pygame.K_LEFT:
            self.key_state[2] = False
        elif key == pygame.K_RIGHT:
            self.key_state[3] = False

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.field.draw()
        self.ball.draw()
        self.goleiro1.draw()
        self.goleiro2.draw()
        self.field.display_score()
        pygame.display.flip()

    def init(self):
        glutInit()
        glMatrixMode(GL_PROJECTION)
        glPointSize(2.4)  # Espessura do ponto desenhado
        glLoadIdentity()
        glOrtho(0, 800, 0, 600, -50, 50)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glColor3f(1.0, 1.0, 1.0)  # Cor da linha
        glClearColor(0, 0.6, 0, 1)  # Cor do campo
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

    def main(self):
        pygame.init()
        pygame.display.set_mode((960, 525), pygame.DOUBLEBUF | pygame.OPENGL)
        self.init()

        self.texture_id = self.load_texture("./textures/ball_texture.jpg")
        self.ball.texture_id = self.texture_id
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self.special_key_down(event.key)
                    elif event.type == pygame.KEYUP:
                        self.special_key_up(event.key)

                self.update()
                self.display()
        finally:
            self.ball.erase()
            pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.main()
