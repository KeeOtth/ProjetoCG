import pygame as pg
from OpenGL.GL import *  # noqa: F403
from OpenGL.GLU import *  # noqa: F403

class App:

    def __init__(self):

        pg.init()
        pg.display.set_mode((800,500), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        glClearColor(0.1,0.2,0.2,0.1)
        self.mainLoop()

    def mainLoop(self):
        
        running = True
        while(running):
            for event in pg.event.get():
                if(event.type == pg.QUIT):
                    running = False

            glClear(GL_COLOR_BUFFER_BIT) 
            pg.display.flip() #A ideia aqui é atualizar o display trocando os buffers de cor, forçando a atualização dos elementos na tela durante o Loop.

            self.clock.tick(60) #A ideia do clock é ter um set e um controle de frames.
        self.quit()
    
    def quit(self):
        
        pg.QUIT

if __name__ == "__main__":
    myApp = App()