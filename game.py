import math
import simplejson
import pygame, sys
import time
from random import randint
from pygame.locals import *
from hotqueue import HotQueue as hq

#===== THE STATES =======
# 0	This is the menu state, so before you start a game, where you can select the wining score etc
# 1	This is the game state, we are activly playing a game now
# 2	this is the pause state, we are are paused in the game.
# 3	this is the game-over state, show a nice little screen with information
state = 0

#===== SCREEN RESOLUTION =====
WIDTH = 700
HEIGHT = 400

HALF_WIDTH = WIDTH / 2


#===== COLORS ======
BLACK = ( 0 , 0 , 0 )
WHITE = ( 255 , 255 , 255 )
RED = ( 255 , 0 , 0 )
GREEN = ( 0 , 255 , 0)
BLUE = ( 0 , 0 , 255 )

#===== OTHER VARIABLES =====
SCORE_PLAYER_1 = 0
SCORE_PLAYER_2 = 0


#start Pygame
pygame.init()
font=pygame.font.Font(None,30)
pygame.mouse.set_visible(False)
DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

#============ Setup the message busses

busFromFPGA = hq("pong")

#============ setup the mainscreen ====================

#bar uptop
HEIGHT_BAR = 20
pygame.draw.rect(DISPLAYSURF , WHITE , (0,0,WIDTH,HEIGHT_BAR))

#bar bottom
pygame.draw.rect(DISPLAYSURF, WHITE, (0,(HEIGHT-HEIGHT_BAR),WIDTH,HEIGHT_BAR))

#squares
WIDTH_SQUARE_DIVIDER = 10
PLAYING_HEIGHT = HEIGHT - ( 2 * HEIGHT_BAR )
num_of_squares = PLAYING_HEIGHT / WIDTH_SQUARE_DIVIDER

x_coordinate_squares = HALF_WIDTH - (WIDTH_SQUARE_DIVIDER / 2)

for i in range(num_of_squares):
	 pygame.draw.rect(DISPLAYSURF, WHITE, (x_coordinate_squares, HEIGHT_BAR + ( i * 2 * WIDTH_SQUARE_DIVIDER), WIDTH_SQUARE_DIVIDER, WIDTH_SQUARE_DIVIDER))

#first score
WIDTH_SCORE_NUMBER = 50
HEIGHT_SCORE_NUMBER = 80

SCORE_DIVIDER = 10
WIDTH_BETWEEN_SQUARES_AND_SCORE = 10

x_coordinate_score_p1 = x_coordinate_squares - WIDTH_BETWEEN_SQUARES_AND_SCORE-WIDTH_SCORE_NUMBER
x_coordinate_score_p2 = x_coordinate_squares + WIDTH_SQUARE_DIVIDER + WIDTH_BETWEEN_SQUARES_AND_SCORE

RECT_SCORE_PLAYER_1 = pygame.draw.rect(DISPLAYSURF, WHITE, (x_coordinate_score_p1, HEIGHT_BAR + SCORE_DIVIDER, WIDTH_SCORE_NUMBER, HEIGHT_SCORE_NUMBER))
RECT_SCORE_PLAYER_2 = pygame.draw.rect(DISPLAYSURF, WHITE, (x_coordinate_score_p2, HEIGHT_BAR + SCORE_DIVIDER, WIDTH_SCORE_NUMBER, HEIGHT_SCORE_NUMBER))

#============= GAME ELEMENTS ====================
offset_controller = 20
width_controller = 10
height_controller = 80

ball_size = 20

ball = pygame.draw.rect(DISPLAYSURF, WHITE, ((WIDTH / 2)-(ball_size/2),(HEIGHT / 2)-(ball_size / 2) ,ball_size ,ball_size ))

controller_p1_y = (HEIGHT / 2) - (height_controller / 2)
controller_p2_y = controller_p1_y

controller_p1 = pygame.draw.rect(DISPLAYSURF, WHITE, (offset_controller,controller_p1_y, width_controller, height_controller)) 
controller_p2 = pygame.draw.rect(DISPLAYSURF, WHITE, (WIDTH - width_controller - offset_controller, controller_p2_y, width_controller, height_controller))

#============= SCORE DRAWING ====================
score_bar_size = 10 
matrix = [0]*15


def draw_matrix(rect, matrix, color):
#	print matrix
	if matrix[1] == 1:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left+score_bar_size, rect.top, rect.width-2*score_bar_size, score_bar_size)) #top bar
	if matrix[2]:	
		pygame.draw.rect(DISPLAYSURF, color, (rect.right - score_bar_size, rect.top, score_bar_size, score_bar_size)) #top right square
	if matrix[3]:	
		pygame.draw.rect(DISPLAYSURF, color, (rect.right - score_bar_size, rect.top + score_bar_size, score_bar_size, ((rect.height - 3*score_bar_size) / 2) )) #right top middle bar
	if matrix[4]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.right - score_bar_size, rect.top +  ((rect.height - (3*score_bar_size)) / 2) + score_bar_size, score_bar_size, score_bar_size)) #right middle square	
	if matrix[5]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.right - score_bar_size,  rect.top +  ((rect.height - (3*score_bar_size)) / 2) + 2*score_bar_size, score_bar_size, ((rect.height - 3*score_bar_size) / 2) )) #right bottom middle bar
	if matrix[6]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.right - score_bar_size, rect.bottom - score_bar_size, score_bar_size, score_bar_size)) #bottom right square
	if matrix[7]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left + score_bar_size, rect.bottom - score_bar_size, rect.width - 2*score_bar_size, score_bar_size)) #bottom bar
	if matrix[8]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left, rect.bottom - score_bar_size, score_bar_size, score_bar_size)) #bottom right square
	if matrix[9]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left,  rect.top +  ((rect.height - (3*score_bar_size)) / 2) + 2*score_bar_size, score_bar_size,((rect.height -3*score_bar_size) / 2) )) #left bottom middle bar
	if matrix[10]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left, rect.top +  ((rect.height - (3*score_bar_size)) / 2) + score_bar_size, score_bar_size, score_bar_size)) #left middle square
	if matrix[11]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left, rect.top + score_bar_size, score_bar_size, ((rect.height - 3*score_bar_size) / 2) )) #left top middle bar	
	if matrix[12]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left, rect.top, score_bar_size, score_bar_size)) #top left square
	if matrix[13]:
		pygame.draw.rect(DISPLAYSURF, color, (rect.left + score_bar_size ,rect.top +  ((rect.height - (3*score_bar_size)) / 2) + score_bar_size, rect.width-2*score_bar_size, score_bar_size)) #middle bar

def draw_zero(rect, color):
	for i in range(1, 13):
		matrix[i] = 1
	draw_matrix(rect, matrix, color)
#        pygame.draw.rect(DISPLAYSURF, WHITE, (rect.left, rect.top, rect.width, score_bar_size)) #top bar
#        pygame.draw.rect(DISPLAYSURF, WHITE, (rect.left, rect.bottom - score_bar_size , rect.width, score_bar_size)) #bottem bar
#        pygame.draw.rect(DISPLAYSURF, WHITE, (rect.left, rect.top + score_bar_size, score_bar_size, rect.height - 2 * score_bar_size)) #left bar
#        pygame.draw.rect(DISPLAYSURF, WHITE, (rect.right - score_bar_size, rect.top + score_bar_size, score_bar_size, rect.height - 2 * score_bar_size)) #right bar

def draw_one(rect, color):
	#pygame.draw.rect(DISPLAYSURF, WHITE, (rect.right-score_bar_size, rect.top, score_bar_size, rect.height)) #left bar
	for i in range(2,7):
		matrix[i] = 1
	draw_matrix(rect, matrix, color)
	
def draw_two(rect, color):
	for i in range(1, 14):
		if(i != 5 and i != 11) :
			matrix[i] = 1
	draw_matrix(rect, matrix, color)

#	pygame.draw.rect(DISPLAYSURF, WHITE, (rect.left, rect.top, rect.width, score_bar_size)) #topbar
#	pygame.draw.rect(DISPLAYSURF, WHITE, (rect.left,rect.top +  ((rect.height - (3*score_bar_size)) / 2) + score_bar_size, rect.width, score_bar_size)) #middle bar
#	pygame.draw.rect(DISPLAYSURF, WHITE, (rect.left, rect.bottom-score_bar_size, rect.width, score_bar_size)) #bottembar
#	pygame.draw.rect(DISPLAYSURF, WHITE, (rect.right - score_bar_size, rect.top + score_bar_size, score_bar_size, ((rect.height - 3*score_bar_size) / 2) )) #first middle part
#	pygame.draw.rect(DISPLAYSURF, WHITE, (rect.left, rect.top +  ((rect.height - (3*score_bar_size)) / 2) + 2*score_bar_size, score_bar_size, ((rect.height - 3*score_bar_size) / 2) )) #second middle part

def draw_three(rect, color):
	for i in range(1, 14):
                if(i != 11 and i != 9) :
                        matrix[i] = 1
        draw_matrix(rect, matrix, color)

def draw_four(rect, color):
	for i in range(1, 14):
                if(i != 7 and i != 8 and i != 9 and i != 1) :
                        matrix[i] = 1
        draw_matrix(rect, matrix, color)

def draw_five(rect, color):
	for i in range(1, 14):
                if(i != 3 and i != 9) :
                        matrix[i] = 1
        draw_matrix(rect, matrix, color)

def draw_six(rect, color):
	for i in range(1, 14):
                if(i != 3) :
                	matrix[i] = 1
        draw_matrix(rect, matrix, color)

def draw_seven(rect, color):
	matrix[12] = 1
	for i in range(1,7):
		matrix[i] = 1
	draw_matrix(rect, matrix, color)

def draw_eight(rect, color):
	for i in range(1, 14):
		matrix[i] = 1
	draw_matrix(rect, matrix, color)

def draw_nine(rect, color):
	for i in range(1, 14):
                if(i != 9) :
                        matrix[i] = 1
        draw_matrix(rect, matrix, color)


draw_options = {0 : draw_zero,
                1 : draw_one,
                2 : draw_two,
                3 : draw_three,
                4 : draw_four,
                5 : draw_five,
                6 : draw_six,
                7 : draw_seven,
                8 : draw_eight,
                9 : draw_nine
}

def draw_score(rect, score, color, backgroundcolor):
        pygame.draw.rect(DISPLAYSURF, backgroundcolor, rect)
#	print score
	for i in range(1,15):
		matrix[i]=0
	
        draw_options[score % 10](rect, color)

def draw_hud():
	#bar uptop
	HEIGHT_BAR = 20
	pygame.draw.rect(DISPLAYSURF , WHITE , (0,0,WIDTH,HEIGHT_BAR))

	#bar bottom
	pygame.draw.rect(DISPLAYSURF, WHITE, (0,(HEIGHT-HEIGHT_BAR),WIDTH,HEIGHT_BAR))

	#squares
	WIDTH_SQUARE_DIVIDER = 20
	PLAYING_HEIGHT = HEIGHT - ( 2 * HEIGHT_BAR )
	num_of_squares = PLAYING_HEIGHT / WIDTH_SQUARE_DIVIDER

	x_coordinate_squares = HALF_WIDTH - (WIDTH_SQUARE_DIVIDER / 2)

	for i in range(num_of_squares):
	         pygame.draw.rect(DISPLAYSURF, WHITE, (x_coordinate_squares, HEIGHT_BAR + ( i * 2 * WIDTH_SQUARE_DIVIDER), WIDTH_SQUARE_DIVIDER, WIDTH_SQUARE_DIVIDER))

def draw_game_elements():
	pygame.draw.rect(DISPLAYSURF, WHITE, controller_p1)
	pygame.draw.rect(DISPLAYSURF, WHITE, controller_p2)	
	pygame.draw.rect(DISPLAYSURF, WHITE, ball)

triangle_padding = 20
angle_increment = 120

def draw_triangle(rect, adjust):
	point_list = []
	
	center_x = rect.centerx
	center_y = rect.centery

#	center_x = WIDTH/2
#	center_y = HEIGHT/2
	
	radius = rect.height - 2*triangle_padding
#	radius = 200
	for i in range(0,3):
		angle = i * angle_increment
		angle -= adjust
		angle *= 3.14159 / 180
	
		extra = 0
#		if(angle == 0):
			#extra = radius

		x = center_x + int(math.cos(angle) * radius)
                y = center_y + int(math.sin(angle) * radius) + extra
                point_list.append((x, y))
	
	pygame.draw.polygon(DISPLAYSURF, RED, point_list)

menu_padding_y = 150 
menu_padding_x = 75

scorebutton_width = 100
scorebutton_height = 66

scorebutton_padding_from_side = 75
scorebutton_padding_from_top = 20

global score_up
global score_down
global scoreblock

winning_score = 0

def draw_menu():
	menubox = pygame.draw.rect(DISPLAYSURF, WHITE, (menu_padding_y, menu_padding_x, WIDTH - 2*menu_padding_y, HEIGHT - 2*menu_padding_x))
	global score_up
	global score_down	
	global scoreblock
	score_up = pygame.draw.rect(DISPLAYSURF, BLUE, ((WIDTH/2)-(scorebutton_width/2), menubox.top + scorebutton_padding_from_top, scorebutton_width, scorebutton_height))
	score_down = pygame.draw.rect(DISPLAYSURF, GREEN,((WIDTH/2)-(scorebutton_width/2), menubox.bottom -scorebutton_height - scorebutton_padding_from_top, scorebutton_width, scorebutton_height))
#0.625	
	h_sb = score_down.top - score_up.bottom

	scoreblock = pygame.Rect(score_up.centerx - (0.625*h_sb)/2, score_up.bottom, 0.625*h_sb, h_sb)

	draw_triangle(score_down, 270)
	draw_triangle(score_up, 90)
	draw_score(scoreblock, winning_score, BLACK, WHITE)
		
def draw_pause_screen():
	global pausebox
	pausebox = pygame.draw.rect(DISPLAYSURF, WHITE, (menu_padding_y, menu_padding_x, WIDTH - 2*menu_padding_y, HEIGHT - 2*menu_padding_x))
	label = font.render("Game is paused. Press to coninue",1, BLACK)
	DISPLAYSURF.blit(label,(pausebox.centerx - (label.get_width()/2),pausebox.top+20))			

while True: #main loop
	for event in pygame.event.get():
		if(event.type == QUIT):
			pygame.quit()
			sys.exit()
#		if(event.type is )
		if(event.type is MOUSEBUTTONDOWN):
  		        pos = pygame.mouse.get_pos()
           		print pos
        	elif(event.type is MOUSEBUTTONUP):
            		pos = pygame.mouse.get_pos()
            		print pos
          		x,y = pos
			if(state == 0):
				if(score_up.collidepoint(x,y)):
					print "score up"
					winning_score += 1
					winning_score = math.fabs(winning_score) % 10
				if(score_down.collidepoint(x,y)):
  					print "score down"
					winning_score -= 1
					winning_score = math.fabs(winning_score) % 10
				if(scoreblock.collidepoint(x,y)):
					print "starting game"
					#todo change
					#todo check if winningscore is not 0
					busFromFPGA.put({'identifier':1, 'data':[{'howmanyplayers': 2},{'winningScore':winning_score}]})
					time.sleep(1)
					state = 1
			elif(state==1):
				state = 2
				#TODO SENT TO FPGA
				print "paused"
			elif(state==2):
				if(pausebox.collidepoint(x,y)):
					state = 1
					#todo SENT TO FPGA
					print "continuing playing"
	DISPLAYSURF.fill(BLACK)
	
	if(state == 0):
		draw_menu()
		clock.tick(10)
	if(state == 1):
		draw_hud()	
		
		incommingData = busFromFPGA.get()
		if(incommingData is not None):
			id = incommingData['identifier']
			if (id == 1):
				data = incommingData['data']
				controllerY1 	= data[0]['controller1']
				controllerY2 	= data[1]['controller2']
				ballX 		= data[2]['ballx']
				ballY 		= data[3]['bally']
				SCORE_PLAYER_1	= data[4]['score1']
				SCORE_PLAYER_2 	= data[5]['score2']
				
				controller_p1 = controller_p1.move(0, controllerY1 - controller_p1.top)
				controller_p2 = controller_p2.move(0, controllerY2 - controller_p2.top)
				
				ball = ball.move(ballX - ball.left, ballY - ball.top)

		draw_game_elements()
		draw_score(RECT_SCORE_PLAYER_1, SCORE_PLAYER_1 % 10, WHITE, BLACK)
		draw_score(RECT_SCORE_PLAYER_2, SCORE_PLAYER_2 % 10, WHITE, BLACK)
		clock.tick(30)
	if(state == 2):
		draw_hud()
		draw_game_elements()
		draw_pause_screen()

	pygame.display.update()
