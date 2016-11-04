import RPi.GPIO as GPIO                    #Import GPIO library
import time                                #Import time library
GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering 

TRIG = 23                                  #Associate pin 23 to TRIG
ECHO = 24                                  #Associate pin 24 to ECHO

print "Distance measurement in progress"

GPIO.setup(TRIG,GPIO.OUT)                  #Set pin as GPIO out
GPIO.setup(ECHO,GPIO.IN)                   #Set pin as GPIO in

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

	return distance

if __name__ == '__main__':
	try:
		while True:
			dist = distance()
			print ("Measured Distance = %.1f cm" % dist)
			time.sleep(0.1)

		# Reset by pressing CTRL + C
	except KeyboardInterrupt:
		print("Measurement stopped by User")
		GPIO.cleanup()
