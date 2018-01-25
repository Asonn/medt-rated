import os
import RPi.GPIO as GPIO
from time import sleep
import sys

GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

MAX_STOP = 8000
MIN_STATE_COUNT = 10

state = "forward"
destinationState = None
destinationCrossThreshold = 1000

crossed = False
crossing = False
enginesOn = False

# Input pins for Sensors
LeftSensor = 23
MiddleSensor = 25
RightSensor = 24

ButtonPin = 21 # button forward
LeftButtonPin = 21 # change to left button pin
RightButtonPin = 21 # change to right button pin
ForwardButtonPin = 21 # change to forward button pin

# TurnMotor pins, defines wheels
LeftWheel = [4, 17, 27, 22]
RightWheel = [26, 19, 13, 9]

#setup input sensors
GPIO.setup(LeftSensor, GPIO.IN)
GPIO.setup(MiddleSensor, GPIO.IN)
GPIO.setup(RightSensor, GPIO.IN)

allButtons = (ButtonPin,LeftButtonPin,RightButtonPin)
GPIO.setup(allButtons, GPIO.IN, GPIO.PUD_UP)

# setup pins for left and right Wheel
for pin in RightWheel+LeftWheel:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin, False)


# Definieer variabelen.
StepCounter = 0
StepCount = 8
stateCount = {
"forward": 0,
"left": 0,
"right": 0,
"softleft": 0,
"softright": 0
}


# "Vooruit LeftWheel"
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

# "Achteruit LeftWheel"
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

def increaseStateCount(state):
    global stateCount
    currentStateCount = stateCount[state] + 1
    for states in range(0, len(stateCount)):
        stateCount[state] = 0
    
    stateCount[state] = currentStateCount


def drive(direction):
    global StepCounter
    # go forward
    if (direction == "forward"):
        for pin in range(0, 4):
            GPIO.output(LeftWheel[pin], Seq1[StepCounter][pin])
            GPIO.output(RightWheel[pin], Seq2[StepCounter][pin])
        count()
        # Wait for the next sequence (lower = faster)
        sleep(.001)
    elif (direction == "left"):
        for pin in range(0, 4):
            GPIO.output(LeftWheel[pin], Seq2[StepCounter][pin])
            GPIO.output(RightWheel[pin], Seq2[StepCounter][pin])            
        count()
        # Wait for the next sequence (lower = faster)
        sleep(.001)
    elif (direction == "right"):
        for pin in range(0, 4):
            GPIO.output(LeftWheel[pin], Seq1[StepCounter][pin])
            GPIO.output(RightWheel[pin], Seq1[StepCounter][pin])
        count()
        # Wait for the next sequence (lower = faster)
        sleep(.001)
    elif (direction == "softright"):
        for pin in range(0, 4):
            GPIO.output(LeftWheel[pin], Seq1[StepCounter][pin])
        count()
        # Wait for the next sequence (lower = faster)
        sleep(.001)        
    elif (direction == "softleft"):
        for pin in range(0, 4):
            GPIO.output(RightWheel[pin], Seq2[StepCounter][pin])
        count()
        # Wait for the next sequence (lower = faster)
        sleep(.001)


def checkStartButtonInput(input):
    global enginesOn
    if(input == 0):
        if(destinationState == None):
            #Please select your destination, cunt.
            print "select destination"
        else:
            enginesOn = not enginesOn
            os.system('mpg321 -q seinfeld.mp3 &')

def checkDestinationButtonsInput():
    if(GPIO.input(LeftButtonPin) == 0): 
        destinationState = "softleft"
    if(GPIO.input(ForwardButtonPin) == 0):
        destinationState = "forward"
    if(GPIO.input(RightButtonPin) == 0):
        destinationState = "softright"

def quit(msg):
    os.system("pkill -SIGSTOP mpg321")
    GPIO.cleanup()
    sys.exit(msg)

try:
    while True:
        checkStartButtonInput(GPIO.input(ButtonPin)) # 0 = pressed
        #checkDestinationButtonsInput()
        destinationState = "softleft" # debug done without dest buttons
        # print("middle %s" % GPIO.input(MiddleSensor))
        loop_index = 1
        while enginesOn:
            
            if loop_index > 1500: # 1500 x 0.001 sec delay = 1.5 sec hardcoded delay
                checkStartButtonInput(GPIO.input(ButtonPin))
                if not enginesOn:
                    for pin in range(0, 4):
                        GPIO.output(RightWheel[pin], 0)
                        GPIO.output(LeftWheel[pin], 0)
                    crossed = False
                    crossing = False
                    os.system("pkill -SIGSTOP mpg321")
                    sleep(1)
                    break;

            if loop_index == 1:
                StopCounter = 0

            if StopCounter < MAX_STOP: # No timeout yet

                # if there is no light for the middle ONLY
                if GPIO.input(LeftSensor) and GPIO.input(RightSensor) and not GPIO.input(MiddleSensor):
                    # go forward
                    increaseStateCount('forward')
                    if stateCount['forward'] > MIN_STATE_COUNT:
                        state = "forward"
                        if crossing:
                            crossed = True
                            print "Crossed!"

                        crossing = False
                    StopCounter = 0

                elif GPIO.input(LeftSensor) and not GPIO.input(RightSensor) and not GPIO.input(MiddleSensor):
                    increaseStateCount('right')
                    if stateCount['right'] > MIN_STATE_COUNT and not crossing:
                        state = "right"
                    StopCounter = 0

                elif GPIO.input(LeftSensor) and not GPIO.input(RightSensor):
                    increaseStateCount('softright')
                    if stateCount['softright'] > MIN_STATE_COUNT and not crossing:
                        state = "softright"
                    StopCounter = 0


                elif not GPIO.input(LeftSensor) and GPIO.input(RightSensor) and not GPIO.input(MiddleSensor):
                    increaseStateCount('left')
                    if stateCount['left'] > MIN_STATE_COUNT and not crossing:
                        state = "left"
                    StopCounter = 0

                elif not GPIO.input(LeftSensor) and GPIO.input(RightSensor):
                    increaseStateCount('softleft')
                    if stateCount['softleft'] > MIN_STATE_COUNT and not crossing:
                        state = "softleft"
                    StopCounter = 0


                elif not GPIO.input(LeftSensor) and not GPIO.input(RightSensor) and not GPIO.input(MiddleSensor):
                    #keep driving the same direction.
                    #all three sensors triggered
                    print "cross-section"
                    increaseStateCount(destinationState)

                    if stateCount[destinationState] > MIN_STATE_COUNT and not crossing:
                        state = destinationState
                        crossing = True  
                        if crossed:
                            quit("Here's your pizza biatch.")
                                      
                    StopCounter = 0

                elif crossing:
                    increaseStateCount(destinationState)
                    print "stc dst" + str(stateCount[destinationState])
                    if(stateCount[destinationState] > destinationCrossThreshold):
                        if(destinationState == "softleft"):
                            state = "left"
                            print "TO LEFT STATE"
                        if(destinationState == "softright"):
                            state = "right"  
                            print "TO RIGHT STATE"    

                    StopCounter = 0  

                else:
                    StopCounter += 1

                # drive with the current state.
                print "driving! state: " + str(state)  + " crossing? " + str(crossing) + " crossed? " + str(crossed)
                #print "driving! left: " + str(GPIO.input(LeftSensor)) + " middle: " + str(GPIO.input(MiddleSensor)) + " right: " + str(GPIO.input(RightSensor))
                drive(state)

            else:
                quit("Sorry boss, I somehow lost my way.")
                
            loop_index += 1

except KeyboardInterrupt:
    # GPIO netjes afsluiten
    os.system("pkill -SIGSTOP mpg321")
    GPIO.cleanup()
