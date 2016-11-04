import simplejson
from hotqueue import HotQueue as hq
import time
import random
import serial
import struct
from random import randint
import RPi.GPIO as GPIO                    #Import GPIO librar                                #Import time library

GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering 

TRIG = 23                                  #Associate pin 23 to TRIG
ECHO = 24                                  #Associate pin 24 to ECHO

print "Distance measurement in progress"

GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in

ser = serial.Serial(

port='/dev/serial0',
baudrate = 9600,
parity=serial.PARITY_NONE,
stopbits=serial.STOPBITS_ONE,
bytesize=serial.EIGHTBITS,
timeout=1

)



queue = hq("pong")
inputFromPi = hq("ping")

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
controller_modifiers = [4,-9]
ball_coordinates = [width/2 - ballSize/2, height/2 - ballSize/2]
ball_modifiers = [5,5]

score1 = 0
score2 = 0

#=== user input
howManyPlayers = 0
winningScore = 0

def distance():
        # set Trigger to HIGH
        GPIO.output(TRIG, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        StartTime = time.time()
        StopTime = time.time()

        # save StartTime
        while GPIO.input(ECHO) == 0:
                StartTime = time.time()

        # save time of arrival
        while GPIO.input(ECHO) == 1:
                StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2
	print distance
        return distance



def doMovement():
	global state, controller_modifiers, ball_modifiers, ball_coordinates, score1, score2

	controller_y[0] = controller_y[0] + controller_modifiers[0]
	controller_y[1] = controller_y[1] + controller_modifiers[1]	
	ball_coordinates[0] = ball_coordinates[0] + ball_modifiers[0]
	ball_coordinates[1] = ball_coordinates[1] + ball_modifiers[1]	
	
	controller_y[0] = controller_y[1] = (distance()-5) * (height/15)

	#controller
	if(controller_y[0] <= barsHeight or controller_y[0] >= height+barsHeight-controllerHeight):
		controller_modifiers[0] *= -1

	if(controller_y[1] <= barsHeight or controller_y[1] >= height+barsHeight-controllerHeight):
                controller_modifiers[1] *= -1
	
	#ball bounce
	if(ball_coordinates[1] <= barsHeight or ball_coordinates[1] >= height+barsHeight-ballSize):
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
                and ball_coordinates[0] >=  width - (20 +controllerWidth+ballSize) and ball_coordinates[0] <= width-20):
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
		global state
		state = 3
		print "game over"
	

def writeOverSerial(data):
	dataArray = data['data']
	if(data['identifier']==1):
#{identifier:1, data:[{controller1:_a_},{controller2:_b_},{ballX:_c_},{ballY:_d_},{score1:_e_},{score2:_f_}]}		
		toSent = bytearray([int(data['identifier']), int(dataArray[0]['controller1']), int(dataArray[1]['controller2']), int(dataArray[2]['ballx']),int(dataArray[3]['bally'])])
	elif(data['identifier']==2):
 
#	print "move"
try:
	while 1: 
		if(state == 0):
			a = inputFromPi.get()
			if(a is not None):
				#{identifier:1, data:[{howmanyplayers: _a_},{winningScore:_b_}]}
				if a['identifier'] == 1:
					print "starting"
					howManyPlayers = a['data'][0]['howmanyplayers']
					winningScore = a['data'][1]['winningScore']
					score1 = 0
					score2 = 0
					state = 1	
		if(state == 1):
#{identifier:1, data:[{controller1:_a_},{controller2:_b_},{ballX:_c_},{ballY:_d_},{score1:_e_},{score2:_f_}]}
			queue.put({'identifier':1, 'data':[{'controller1':controller_y[0]},{'controller2':controller_y[1]},{'ballx':ball_coordinates[0]},{'bally':ball_coordinates[1]},{'score1':score1},{'score2':score2}]})	
			doMovement()
			#check if paused
			inp = inputFromPi.get()
			if(inp is not None):
				id = inp['identifier']
				if id==2:
					#game is paused
					state = 2
		elif(state == 2):
			inp = inputFromPi.get()
			if(inp is not None):
                        	id = inp['identifier']
                        	if id==3:
                                	#game is unpaused
	                                state = 1

		elif(state == 3):
			if(score1 > score2):
				winner = 0
				loser = 1
			else:
				winner = 1
				loser = 0

			queue.put({'identifier':2, 'data':[{'winner':winner },{'loser':loser },{'score':score1 },{'score':score2}]})
			state = 0
		time.sleep(0.1)
except KeyboardInterrupt:
	print("exiting")
        GPIO.cleanup()
