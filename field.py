import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import threading
import time

# Variáveis globais pra bugar tudo. :D (Se deus quiser)
ballX = 400.0
ballY = 300.0
thetaY = 0
thetaX = 0
pointsA = 0
pointsB = 0
keyState = [False] * 4  # [UP, DOWN, LEFT, RIGHT]
isGol = False
running = True
texture_id = None
quad = gluNewQuadric()
gluQuadricTexture(quad, GL_TRUE)
gluQuadricNormals(quad, GLU_SMOOTH)


def plot(x, y):
    glBegin(GL_POINTS)
    glVertex3i(x, y, 0)
    glEnd()

goolString = "ooOoOOoOOo" 

def cyclic_shift():
    global goolString
    if running:
        goolString = goolString[-1]+goolString[:-1]
        threading.Timer(0.1, cyclic_shift).start()

def text():
    global pointsA, pointsB, goolString
    string = (
    'Time A  ' 
    + str(pointsA)
    + '   |   Time B  '
    + str(pointsB)
    )
    string = string.encode()

    glColor3f(1.0,1.0,1.0)
    glRasterPos(322, 550)
    for c in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18,c)

    if(isGol):
        goolStringEnc = ('G' +goolString+ "L").encode()
        glColor3f(0.0,0.0,0.0)
        glRasterPos(370, 300)
        for c in goolStringEnc :
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18,c)

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

def load_texture(path):
    texture_surface = pygame.image.load(path)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width, height = texture_surface.get_rect().size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0,
                 GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    
    return texture_id

def drawBall(texture_id):
    global ballX, ballY, thetaY, thetaX, quad
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    thetaX = thetaX%360
    thetaY = thetaY % 360
    glPushMatrix()
    glTranslatef(ballX, ballY, 0)
    glRotate(thetaX, 1, 0, 0)
    glRotate(thetaY, 0, 1, 0)
    gluSphere(quad, 7.0, 50, 50)
    glPopMatrix()

    glDisable(GL_TEXTURE_2D)

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
    global texture_id
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    drawField()
    drawBall(texture_id)
    text()
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

def back_after_gol():
    global ballX, ballY, isGol, thetaY, thetaX
    isGol = False
    time.sleep(0.4)
    thetaX = 0
    thetaY = 0
    ballX = 400.0
    ballY = 300

def gol():
    global ballX, ballY, isGol
    ballX = 400.0
    ballY = 20000.0

    isGol = True
    threading.Timer(3, back_after_gol).start()


def check_gol():
    global ballX, ballY, pointsA, pointsB

    if(ballX <= 95):
        pointsB+=1
        gol()

    if(ballX >= 703):
        pointsA+=1
        gol()

def update():
    global ballX, ballY, thetaY, thetaX
    movement = 2
    angle = 5

    left_bound = 100 + 10
    right_bound = 700 - 10
    top_bound = 500 - 10
    bottom_bound = 100 + 10

    if keyState[0] and ballY + movement <= top_bound:
        ballY += movement
        thetaX -= angle
    if keyState[1] and ballY - movement >= bottom_bound:
        ballY -= movement
        thetaX += angle

    if keyState[2] and (ballX - movement >= left_bound or (ballY>=200 and ballY<=400)):
        ballX -= movement
        thetaY -= angle
    if keyState[3] and (ballX + movement <= right_bound or (ballY>=200 and ballY<=400)):
        thetaY += angle
        ballX += movement

    check_gol()
    # thetaX = thetaX%(360)
    # thetaY = thetaY%(360)
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
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

def main():
    global running, quad, texture_id
    glutInit()
    pygame.init()
    pygame.display.set_mode((960, 525), pygame.DOUBLEBUF | pygame.OPENGL)

    init()

    texture_id = load_texture("./textures/ball_texture.jpg")

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    specialKeyDown(event.key)
                elif event.type == pygame.KEYUP:
                    specialKeyUp(event.key)

            update()

    finally:
        if texture_id:
            glDeleteTextures([texture_id])
        gluDeleteQuadric(quad)
        pygame.quit()

if __name__ == "__main__":
    cyclic_shift()
    main()
