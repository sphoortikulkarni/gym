
%matplotlib notebook
import numpy as np
import matplotlib.pyplot as plt

from ipywidgets import widgets
from IPython.display import display

import gym

from matplotlib import animation
#from JSAnimation.IPython_display import display_animation
import pygame, random, sys ,os,time,math
from pygame.locals import *

from gym import spaces
#from gym.envs.box2d.car_dynamics import Car
from gym.utils import colorize, seeding
import pyglet
from pyglet import gl
from gym_foo.envs.__init__ import *

WINDOWWIDTH = 800
WINDOWHEIGHT = 600
TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (0, 0, 0)
FPS = 40
BADDIEMINSIZE = 10
BADDIEMAXSIZE = 40
BADDIEMINSPEED = 8
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 6
PLAYERMOVERATE = 5
count=3

SCALE       = 6.0        # Track scale
TRACK_RAD   = 900/SCALE  # Track is heavily morphed circle with this radius
PLAYFIELD   = 2000/SCALE # Game over boundary

# set up pygame, the window, and the mouse cursor
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('car race')
pygame.mouse.set_visible(False)

# fonts
font = pygame.font.SysFont(None, 30)

def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def waitForPlayerToPressKey(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.__terminate()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE: #escape quits
                        self.__terminate()
                    return

def playerHasHitBaddie(playerRect, baddies,baddieAddCounter):
    reward = 6.0
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            reward -= 1000.0/float(baddieAddCounter)
            print(reward)
            return True
        else: 
              reward = reward + 1000.0/float(baddieAddCounter)
              print(reward)
    return False
    
    
def terminate(self):    #__del__(self)
    self.pygame.quit()
    self.sys.exit()

    
def display_buttons():
    """ Display the buttons you can use to apply a force to the cart """
    left = widgets.Button(description="<")
    right = widgets.Button(description=">")
    display(left, right)
    
    left.on_click(leftclicked)
    right.on_click(rightclicked)

    

class CarEnv(gym.Env):
	metadata = {
			'render.modes': ['human', 'rgb_array', 'state_pixels'],
        'video.frames_per_second' : FPS
	}

	def __init__(self):
		self._seed()
		


		# images
		playerImage = pygame.image.load('car1.png')
		car3 = pygame.image.load('car3.png')
		car4 = pygame.image.load('car4.png')
		playerRect = playerImage.get_rect()
		baddieImage = pygame.image.load('car2.png')
		sample = [car3,car4,baddieImage]
		wallLeft = pygame.image.load('left.png')
		wallRight = pygame.image.load('right.png')
		self.reward = 0.0


	
	
	#def start(self):
		drawText('Press any key to start the game.',font, windowSurface, (WINDOWWIDTH / 3) - 30, (WINDOWHEIGHT / 3))
		drawText('And Enjoy', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3)+30)
		pygame.display.update()
		waitForPlayerToPressKey(self)
		pygame.display.update()
		zero=0
		if not os.path.exists("save.dat"):
		    f=open("save.dat",'w')
		    f.write(str(zero))
		    f.close()   
		v=open("save.dat",'r')
		topScore = int(v.readline())
		v.close()
		while (count>0):
                    # start of the game
                    baddies = []
                    score = 0
                    playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
                    moveLeft = moveRight = moveUp = moveDown = False
                    reverseCheat = slowCheat = False
                    baddieAddCounter = 0
                    #pygame.mixer.music.play(-1, 0.0)

                    while True: # the game loop
                        score += 1 # increase score
                        for event in pygame.event.get():    
                            if event.type == QUIT:
                                terminate()

                            if event.type == KEYDOWN:
                                if event.key == ord('z'):
                                    reverseCheat = True
                                if event.key == ord('x'):
                                   slowCheat = True
                                if event.key == K_LEFT or event.key == ord('a'):
                                    moveRight = False
                                    moveLeft = True
                                if event.key == K_RIGHT or event.key == ord('d'):
                                    moveLeft = False
                                    moveRight = True
                                if event.key == K_UP or event.key == ord('w'):
                                    moveDown = False
                                    moveUp = True
                                if event.key == K_DOWN or event.key == ord('s'):
                                    moveUp = False
                                    moveDown = True

                            if event.type == KEYUP:
                                if event.key == ord('z'):
                                    reverseCheat = False
                                    score = 0
                                if event.key == ord('x'):
                                    slowCheat = False
                                    score = 0
                                if event.key == K_ESCAPE:
                                    terminate(self)

			# Add new baddies at the top of the screen
                        if not reverseCheat and not slowCheat:
                            baddieAddCounter += 1
                        if baddieAddCounter == ADDNEWBADDIERATE:
                            baddieAddCounter = 1
                            baddieSize =30 
                            newBaddie = {'rect': pygame.Rect(random.randint(140, 485), 0 - baddieSize, 23, 47),
				        'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
				        'surface':pygame.transform.scale(random.choice(sample), (23, 47)),
				        }
                            baddies.append(newBaddie)
                            sideLeft= {'rect': pygame.Rect(0,0,126,600),
				       'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
				       'surface':pygame.transform.scale(wallLeft, (126, 599)),
				       }
                            baddies.append(sideLeft)
                            sideRight= {'rect': pygame.Rect(497,0,303,600),
				       'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
				       'surface':pygame.transform.scale(wallRight, (303, 599)),
				       }
                            baddies.append(sideRight)
			    
			    

			# Move the player around.
                        if moveLeft and playerRect.left > 0:
                            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
                        if moveRight and playerRect.right < WINDOWWIDTH:
                            playerRect.move_ip(PLAYERMOVERATE, 0)
                        if moveUp and playerRect.top > 0:
                            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
                        if moveDown and playerRect.bottom < WINDOWHEIGHT:
                            playerRect.move_ip(0, PLAYERMOVERATE)
		
                        for b in baddies:
                            if not reverseCheat and not slowCheat:
                                b['rect'].move_ip(0, b['speed'])
                            elif reverseCheat:
                                b['rect'].move_ip(0, -5)
                            elif slowCheat:
                                b['rect'].move_ip(0, 1)
                        #playerHasHitBaddie(playerRect, baddies,baddieAddCounter)
			 
                        for b in baddies[:]:
                            if b['rect'].top > WINDOWHEIGHT:
                               baddies.remove(b)

			# Draw the game world on the window.
                        windowSurface.fill(BACKGROUNDCOLOR)

			# Draw the score and top score.
                        drawText('Score: %s' % (score), font, windowSurface, 128, 0)
                        drawText('Top Score: %s' % (topScore), font, windowSurface,128, 20)
                        drawText('Rest Life: %s' % (count), font, windowSurface,128, 40)
		
                        windowSurface.blit(playerImage, playerRect)

		
                        for b in baddies:
                             windowSurface.blit(b['surface'], b['rect'])

                        pygame.display.update()

                        #playerHasHitBaddie(playerRect, baddies,baddieAddCounter) 
                        
                        if playerHasHitBaddie(playerRect, baddies,baddieAddCounter):
                            if score > topScore:
                                g=open("save.dat",'w')
                                g.write(str(score))
                                g.close()
                                topScore = score
                                self.env.reward += 1000.0/len(self.env.track)
                                print(reward)
                            break 

	def _seed(self, seed=None):
		self.np_random, seed = seeding.np_random(seed)
		return [seed]


if __name__ == '__main__':
    env = gym.make("gym_foo-v0")
    CarEnv(env)
	
    
    
# Create the environment and display the initial state
env = gym.make('Car-v0')
observation = env.reset()
firstframe = env.render(mode = 'rgb_array')
fig,ax = plt.subplots()
im = ax.imshow(firstframe) 

# Show the buttons to control the cart
display_buttons()


# Function that defines what happens when you click one of the buttons
frames = []
def onclick(action):
    global frames
    observation, reward, done, info = env.step(action)
    frame = env.render(mode = 'rgb_array')
    im.set_data(frame)
    frames.append(frame)
    if done:
        env.reset()

    
