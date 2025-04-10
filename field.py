import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Variáveis globais pra bugar tudo. :D (Se deus quiser)
ballX = 400.0
ballY = 300.0
keyState = [False] * 4  # [UP, DOWN, LEFT, RIGHT]

def plot(x, y):
    glBegin(GL_POINTS)
    glVertex3i(x, y, 0)
    glEnd()

def bresenhamLine(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        plot(x0, y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def drawCircle(xc, yc, r):
    x = 0
    y = r
    d = 3 - 2 * r
    while y >= x:
        plot(xc + x, yc + y)
        plot(xc - x, yc + y)
        plot(xc + x, yc - y)
        plot(xc - x, yc - y)
        plot(xc + y, yc + x)
        plot(xc - y, yc + x)
        plot(xc + y, yc - x)
        plot(xc - y, yc - x)
        x += 1
        if d >= 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6

def drawBall():
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(ballX, ballY, 5)
    glutWireSphere(10.0, 12, 20)
    glPopMatrix()

def drawField():
    glColor3f(1, 1, 1)  # Cor das linhas

    # Linhas do campo
    bresenhamLine(100, 100, 700, 100)
    bresenhamLine(700, 100, 700, 500)
    bresenhamLine(700, 500, 100, 500)
    bresenhamLine(100, 500, 100, 100)

    # Linha central
    bresenhamLine(400, 100, 400, 500)

    # Círculo central
    drawCircle(400, 300, 50)

    # Área esquerda
    bresenhamLine(100, 200, 200, 200)
    bresenhamLine(200, 200, 200, 400)
    bresenhamLine(200, 400, 100, 400)

    # Área direita
    bresenhamLine(700, 200, 600, 200)
    bresenhamLine(600, 200, 600, 400)
    bresenhamLine(600, 400, 700, 400)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    drawField()
    drawBall()
    pygame.display.flip()

def specialKeyDown(key):
    global keyState
    if key == pygame.K_UP:
        keyState[0] = True
    elif key == pygame.K_DOWN:
        keyState[1] = True
    elif key == pygame.K_LEFT:
        keyState[2] = True
    elif key == pygame.K_RIGHT:
        keyState[3] = True

def specialKeyUp(key):
    global keyState
    if key == pygame.K_UP:
        keyState[0] = False
    elif key == pygame.K_DOWN:
        keyState[1] = False
    elif key == pygame.K_LEFT:
        keyState[2] = False
    elif key == pygame.K_RIGHT:
        keyState[3] = False

def update():
    global ballX, ballY
    movement = 2

    left_bound = 100 + 10
    right_bound = 700 - 10
    top_bound = 500 - 10
    bottom_bound = 100 + 10

    if keyState[0] and ballY + movement <= top_bound:
        ballY += movement
    if keyState[1] and ballY - movement >= bottom_bound:
        ballY -= movement
    if keyState[2] and ballX - movement >= left_bound:
        ballX -= movement
    if keyState[3] and ballX + movement <= right_bound:
        ballX += movement

    display()

def init():
    glMatrixMode(GL_PROJECTION)
    glPointSize(2.4) # Espessura do ponto desenhado
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -50, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glColor3f(1.0, 1.0, 1.0)  # Cor da linha
    glClearColor(0, 0.6, 0, 1)  # Cor do campo

# Função principal
def main():
    glutInit()
    pygame.init()
    pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)

    init()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                specialKeyDown(event.key)
            elif event.type == pygame.KEYUP:
                specialKeyUp(event.key)

        update()

    pygame.quit()

if __name__ == "__main__":
    main()
