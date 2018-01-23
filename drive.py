import RPi.GPIO as GPIO
from time import sleep
import sys

GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

MAX_STOP = 500;
state = "forward"
# Input pins for Sensors
LeftSensor = 23
MiddleSensor = 25
RightSensor = 24
ButtonPin = 21

# TurnMotor pins, defines wheels
LeftWheel = [4, 17, 27, 22]
RightWheel = [26, 19, 13, 9]

#setup input sensors
GPIO.setup(LeftSensor, GPIO.IN)
GPIO.setup(MiddleSensor, GPIO.IN)
GPIO.setup(RightSensor, GPIO.IN)
GPIO.setup(ButtonPin, GPIO.IN, GPIO.PUD_UP)

# setup pins for left and right Wheel
for pin in RightWheel+LeftWheel:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)

# state default button
prev_state = 1

# Definieer variabelen.
StepCounter = 0
StepCount = 8

# "Vooruit"
Seq1 = []
Seq1 = range(0, StepCount)
Seq1[0] = [1,0,0,0]
Seq1[1] = [1,1,0,0]
Seq1[2] = [0,1,0,0]
Seq1[3] = [0,1,1,0]
Seq1[4] = [0,0,1,0]
Seq1[5] = [0,0,1,1]
Seq1[6] = [0,0,0,1]
Seq1[7] = [1,0,0,1]

# "Achteruit"
Seq2 = []
Seq2 = range(0, StepCount)
Seq2[0] = [0,0,0,1]
Seq2[1] = [0,0,1,1]
Seq2[2] = [0,0,1,0]
Seq2[3] = [0,1,1,0]
Seq2[4] = [0,1,0,0]
Seq2[5] = [1,1,0,0]
Seq2[6] = [1,0,0,0]
Seq2[7] = [1,0,0,1]

def count():
    global StepCounter
    StepCounter += 1

    # restart sequence at the end.
    if (StepCounter==StepCount):
        StepCounter = 0
    if (StepCounter<0):
        StepCounter = StepCount

def drive(direction):
    global StepCounter
    # go forward
    if (direction == "forward"):
        for pin in range(0, 4):
            xpin = RightWheel[pin]
            ypin = LeftWheel[pin]
            GPIO.output(xpin, Seq2[StepCounter][pin])
            GPIO.output(ypin, Seq1[StepCounter][pin])
        count()
            # Wait for the next sequence (lower = faster)
        sleep(.001)
    elif (direction == "left"):
        for pin in range(0, 4):
            xpin = RightWheel[pin]
            ypin = LeftWheel[pin]
            GPIO.output(xpin, Seq2[StepCounter][pin])
        count()
            # Wait for the next sequence (lower = faster)
        sleep(.001)
    else:
        for pin in range(0, 4):
            xpin = RightWheel[pin]
            ypin = LeftWheel[pin]
            GPIO.output(ypin, Seq2[StepCounter][pin])
        count()
            # Wait for the next sequence (lower = faster)
        sleep(.001)

try:
    while True:
        curr_state = GPIO.input(ButtonPin)
        # print("middle %s" % GPIO.input(MiddleSensor))
        loop_index = 1
        while (curr_state != prev_state):
            # once pressed set it back to previous state, for an infinite loop
            curr_state = 0
            if loop_index == 1:
                StopCounter = 0
            # if there is no light for the middle ONLY

            if GPIO.input(LeftSensor) and GPIO.input(RightSensor) and not GPIO.input(MiddleSensor) and StopCounter < MAX_STOP:
                # go forward
                state = "forward"
                StopCounter = 0
            elif GPIO.input(LeftSensor) and not GPIO.input(RightSensor) and not GPIO.input(MiddleSensor) or GPIO.input(LeftSensor) and not GPIO.input(RightSensor) and StopCounter < MAX_STOP:
                state = "right"
                StopCounter = 0
            elif not GPIO.input(LeftSensor) and GPIO.input(RightSensor) and not GPIO.input(MiddleSensor) or not GPIO.input(LeftSensor) and GPIO.input(RightSensor) and StopCounter < MAX_STOP:
                state = "left"
                StopCounter = 0
            elif not GPIO.input(LeftSensor) and not GPIO.input(RightSensor) and not GPIO.input(MiddleSensor) and StopCounter < MAX_STOP:
                #keep driving the same direction.
                StopCounter = 0
            else:
                StopCounter += 1

            # drive with the current state.
            if StopCounter < MAX_STOP:
                drive(state)
                print("driving...")
                print(StopCounter)

            if MAX_STOP == StopCounter:
                sys.exit("Sorry boss, I somehow lost my way.")

            loop_index += 1


except KeyboardInterrupt:
    # GPIO netjes afsluiten
    GPIO.cleanup()
