import simplejson
from hotqueue import HotQueue as hq
import time
import random
from random import randint

queue = hq("pong")

#SO this is the test to mimic the FPGA. so we first need to wait for the start signal
#we use states for that:
# 0	waiting for game start
# 1	in game
# 2 	game paused
# 3 	game over, directly go to state=0

state = 0

#=== Game vars
barsHeight = 20

width = 700
height = 400 - (2*barsHeight)
controllerHeight = 80
controllerWidth = 10
ballSize = 20

controller_y = [(height/2)-(controllerHeight/2), (height/2)-(controllerHeight/2)]
controller_x = 20
controller_modifiers = [9,-9]
ball_coordinates = [width/2 - ballSize/2, height/2 - ballSize/2]
ball_modifiers = [5,5]

score1 = 0
score2 = 0

#=== user input
howManyPlayers = 0
winningScore = 0

def doMovement():
	global controller_modifiers, ball_modifiers, ball_coordinates, score1, score2

	controller_y[0] = controller_y[0] + controller_modifiers[0]
	controller_y[1] = controller_y[1] + controller_modifiers[1]	
	ball_coordinates[0] = ball_coordinates[0] + ball_modifiers[0]
	ball_coordinates[1] = ball_coordinates[1] + ball_modifiers[1]	

	#controller
	if(controller_y[0] <= barsHeight or controller_y[0] >= height-controllerHeight):
		controller_modifiers[0] *= -1

	if(controller_y[1] <= barsHeight or controller_y[1] >= height-controllerHeight):
                controller_modifiers[1] *= -1
	
	#ball bounce
	if(ball_coordinates[1] <= barsHeight or ball_coordinates[1] >= height-ballSize):
		ball_modifiers[1] *= -1
		print "bounce wall"
	#bounce off controller1
	if(ball_coordinates[1] < controller_y[0]+controllerHeight and ball_coordinates[1] > controller_y[0]
		and ball_coordinates[0] <= 20 +controllerWidth and ball_coordinates[0] >= 20):
		ball_modifiers[0] *= -1
		ball_modifiers[1] *= -1
		print "bounce controller 1"	
	#controller2
	if(ball_coordinates[1] < controller_y[1]+controllerHeight and ball_coordinates[1] > controller_y[1]
                and ball_coordinates[0] >=  width - (20 +controllerWidth) and ball_coordinates[0] <= width-20):
                ball_modifiers[0] *= -1
                ball_modifiers[1] *= -1
		print "bounce controller 2"

	


	#scored
	if(ball_coordinates[0] <= 20 +controllerWidth and ball_coordinates[0] >= 20 and not
			 (ball_coordinates[1] < controller_y[0]+controllerHeight 
				and ball_coordinates[1] > controller_y[0])):
		#player 2 scored
		score2 += 1
		ball_modifiers[0] = randint(1,13)*random.choice(range(-1,0)+range(1,2))
		ball_modifiers[1] = randint(1,13)*random.choice(range(-1,0)+range(1,2))
		ball_coordinates = [width/2 - ballSize/2, height/2 - ballSize/2]
		print "Player 2 scored"
	
 	if(ball_coordinates[0] >= width-( 20 +controllerWidth) and ball_coordinates[0] <= width-20 and not 
                         (ball_coordinates[1] < controller_y[1]+controllerHeight 
                                and ball_coordinates[1] > controller_y[1])):
                #player 1 scored 
                score1 += 1
		ball_coordinates = [width/2 - ballSize/2, height/2 - ballSize/2]
		ball_modifiers[0] = randint(1,13)*random.choice(range(-1,0)+range(1,2))
		ball_modifiers[1] = randint(1,13)*random.choice(range(-1,0)+range(1,2))
		print "Player 1 scored"

	if(score1 == winningScore or score2 == winningScore):
		#game over => goto state3
		state = 3
		print "game over"
	
 
#	print "move"

while 1: 
	if(state == 0):
		a = queue.get()
		if(a is not None):
			#{identifier:1, data:[{howmanyplayers: _a_},{winningScore:_b_}]}
			if a['identifier'] == 1:
				print "starting"
				howManyPlayers = a['data'][0]['howmanyplayers']
				winningScore = a['data'][1]['winningScore']
				state = 1	
	if(state == 1):
		#{identifier:1, data:[{controller1:_a_},{controller2:_b_},{ballX:_c_},{ballY:_d_},{score1:_e_},{score2:_f_}]}
		queue.put({'identifier':1, 'data':[{'controller1':controller_y[0]},{'controller2':controller_y[1]},{'ballx':ball_coordinates[0]},{'bally':ball_coordinates[1]},{'score1':score1},{'score2':score2}]})	
		doMovement()
	time.sleep(0.1)

