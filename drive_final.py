import os
import RPi.GPIO as GPIO
import sys
from time import sleep


# Vars
TIMEOUT_COUNT = 8000 # Time in ms before timeout during inactive sensors
MIN_STATE_COUNT = 10 # Minimum time in ms before switching state 
TURN_SEQUENCE_COUNT = 250 # Minimum time in ms before switching state when turning


state = "forward" # default state
destinationState = None # direction state to go when at a cross point
destinationCrossThreshold = 1500 # time in ms till turn intensity increases while crossing


crossed = False # Has crossed the first intersection
crossing = False # Is traversing the intersection
enginesOn = False

# Input pins for sensors
LeftSensor = 23
MiddleSensor = 25
RightSensor = 24

# Input pins for buttons
StartButtonPin = 21 # Start/Pause button
LeftButtonPin = 12 # Starbucks
ForwardButtonPin = 16 # Apple Store
RightButtonPin = 20 # Science Center

# TurnMotor pins, defines wheels
LeftWheel = [4, 17, 27, 22]
RightWheel = [26, 19, 13, 9]


# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup input sensors
allSensors = (LeftSensor, MiddleSensor, RightSensor)
GPIO.setup(allSensors, GPIO.IN)

# Setup button inputs
allButtons = (StartButtonPin,LeftButtonPin,RightButtonPin, ForwardButtonPin)
GPIO.setup(allButtons, GPIO.IN, GPIO.PUD_UP)


allWheels = LeftWheel + RightWheel
GPIO.setup(allWheels,GPIO.OUT)
GPIO.output(allWheels, False) # Disable engines at start

os.system('mpg321 -q -g 100 selectdestination.mp3 &')

stateCount = {
"forward": 0,
"left": 0,
"right": 0,
"softleft": 0,
"softright": 0
}


# Sequence variables
StepCounter = 0
StepCount = 8

# Forwards LeftWheel, Backwards RightWheel
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

# Backwards LeftWheel, Forwards RightWheel
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


# Define functions
def count():
    # Increments the step counter 
    global StepCounter
    StepCounter += 1
    
    # restart sequence at the end.
    if (StepCounter==StepCount):
        StepCounter = 0
    if (StepCounter<0):
        StepCounter = StepCount

def increaseStateCount(state):
    # Increments state count for selected state and resets the count other states
    global stateCount

    currentStateCount = stateCount[state] + 1
    for states in range(0, len(stateCount)):
        stateCount[state] = 0
    
    stateCount[state] = currentStateCount


def drive(state):
    # Executes a full movement sequence
    global StepCounter

    # go forward
    if (state == "forward"):
        for pin in range(0, 4): # Cycle through pins 0 to 3
            GPIO.output(LeftWheel[pin], Seq1[StepCounter][pin])
            GPIO.output(RightWheel[pin], Seq2[StepCounter][pin])
        count()
        sleep(0.001)

    # go hard left
    elif (state == "left"):
        for pin in range(0, 4):
            GPIO.output(LeftWheel[pin], Seq2[StepCounter][pin])
            GPIO.output(RightWheel[pin], Seq2[StepCounter][pin])            
        count()
        sleep(0.001)

    # go hard right
    elif (state == "right"):
        for pin in range(0, 4):
            GPIO.output(LeftWheel[pin], Seq1[StepCounter][pin])
            GPIO.output(RightWheel[pin], Seq1[StepCounter][pin])
        count()
        sleep(0.001)

    # go soft left
    elif (state == "softleft"):
        for pin in range(0, 4):
            GPIO.output(RightWheel[pin], Seq2[StepCounter][pin])
        count()
        sleep(0.001)

    # go soft right
    elif (state == "softright"):
        for pin in range(0, 4):
            GPIO.output(LeftWheel[pin], Seq1[StepCounter][pin])
        count()
        sleep(0.001)    


def checkStartButtonInput(input):
    # Handles input for the start/pause button
    global enginesOn

    # Check if button is pressed down
    if(input == 0): 
        if(destinationState == None):
            # Please select your destination
            os.system('mpg321 -q selectdestination.mp3 &') 
            sleep(1.5)
        else:
            enginesOn = not enginesOn
            #os.system('mpg321 -q -Z -g 10 pacman.mp3 &') # Seinfeld theme

def checkDestinationButtonsInput():
    # Handles input for destination buttons
    global destinationState

    buttonPressed = False
    if(GPIO.input(LeftButtonPin) == 0): 
        destinationState = "softleft"
        os.system('mpg321 -q starbucks.mp3 &')
        buttonPressed = True
    if(GPIO.input(ForwardButtonPin) == 0):
        destinationState = "forward"
        os.system('mpg321 -q applestore.mp3 &')
        buttonPressed = True
    if(GPIO.input(RightButtonPin) == 0):
        destinationState = "softright"
        os.system('mpg321 -q sciencecenter.mp3 &')
        buttonPressed = True

    if(buttonPressed):
        sleep(1.5)
        os.system('mpg321 -q power.mp3 &') # Press the power button


def soundToDestination(state):
    # Plays 'to destination' sound
    if(state == "softleft"): 
        os.system('mpg321 -q to_starbucks.mp3 &')
    if(state == "forward"):
        os.system('mpg321 -q to_applestore.mp3 &')
    if(state == "softright"):
        os.system('mpg321 -q to_sciencecenter.mp3 &')


def quit(msg):
    os.system("pkill -SIGSTOP mpg321") # Stop all sounds
    GPIO.cleanup()
    sys.exit(msg)

def reset():
    # reset variables & states
    crossed = False
    crossing = False
    GPIO.output(allWheels, False) # Disable engines
    os.system("pkill -SIGSTOP mpg321") # Stop all sounds

#Start main loop
try:
    while True:
        # Check button inputs
        checkStartButtonInput(GPIO.input(StartButtonPin)) # 0 = pressed
        checkDestinationButtonsInput()

        loop_index = 1
        while enginesOn:
            
            if loop_index > 1500: # 1500 x 0.001 sec delay for checking pause button input
                checkStartButtonInput(GPIO.input(StartButtonPin))
                if not enginesOn:
                    reset()
                    os.system('mpg321 -q tobecontinued.mp3 &') # Pause sound
                    sleep(1)
                    break;

            if loop_index == 1:
                StopCounter = 0

            # Check if no timeout has occured yet
            if StopCounter < TIMEOUT_COUNT: 

                # Middle sensor only -> go forward
                if GPIO.input(LeftSensor) and GPIO.input(RightSensor) and not GPIO.input(MiddleSensor):
                    increaseStateCount('forward')

                    # Check threshold in order to change state
                    if stateCount['forward'] > MIN_STATE_COUNT:
                        state = "forward"

                        # Check to see if previously crossing the intersection
                        if crossing:
                            crossed = True
                            print "Crossed!"

                        crossing = False

                    StopCounter = 0

                # Middle+Right sensor or Right sensor only -> go right
                elif GPIO.input(LeftSensor) and not GPIO.input(RightSensor) and not GPIO.input(MiddleSensor) or GPIO.input(LeftSensor) and not GPIO.input(RightSensor):
                    increaseStateCount('right')

                    # Check threshold in order to change state
                    if stateCount['right'] > MIN_STATE_COUNT and not crossing:
                        state = "right"

                        # Execute TURN_SEQUENCE_COUNT steps towards right
                        for i in range(0,TURN_SEQUENCE_COUNT): 
                            drive(state)

                    StopCounter = 0

                # Middle+Left sensor or Left sensor only -> go left
                elif not GPIO.input(LeftSensor) and GPIO.input(RightSensor) and not GPIO.input(MiddleSensor) or not GPIO.input(LeftSensor) and GPIO.input(RightSensor):
                    increaseStateCount('left')

                    # Check threshold in order to change state
                    if stateCount['left'] > MIN_STATE_COUNT and not crossing:
                        state = "left"

                        # Execute TURN_SEQUENCE_COUNT steps towards left
                        for i in range(0,TURN_SEQUENCE_COUNT):
                            drive(state)     

                    StopCounter = 0

                # All three sensors -> intersection (check destination)
                elif not GPIO.input(LeftSensor) and not GPIO.input(RightSensor) and not GPIO.input(MiddleSensor):
                    increaseStateCount(destinationState)

                    # Check threshold in order to change state
                    if stateCount[destinationState] > MIN_STATE_COUNT and not crossing:
                        state = destinationState # change state

                        # Only play sound at the first intersection
                        if not crossed:
                            soundToDestination(destinationState)

                        crossing = True
                        # Reach intersection state after having crossed -> arrival
                        if crossed: 
                            os.system('mpg321 -q arrival.mp3 &')
                            sleep(2.5)
                            quit("Pizza delivered.")

                        if state == "softleft" or state == "softright":
                            for i in range(0,destinationCrossThreshold):
                                drive(state)

                                      
                    StopCounter = 0

                # ALL three sensors disabled while crossing the intersection -> increase turn intensity
                elif crossing:
                    increaseStateCount(destinationState)

                    # Check threshold in order to change turbo state
                    if(stateCount[destinationState] > 10): # destinationCrossThreshold
                        print "crossing forward"
                        if(destinationState == "softleft"):
                            state = "left" # activate hard left
                        if(destinationState == "softright"):
                            state = "right" # activate hard right
                        if(destinationState == "forward"):
                            state = "forward"
                            crossed = True
                            crossing = False
                            for i in range(0,destinationCrossThreshold):
                                drive(state)                            

                    StopCounter = 0  

                # ALL three sensors disabled -> default to forward
                else:
                    StopCounter += 1
                    state = "forward"

                # drive with the current state.
                print "driving! state: " + str(state)  + " crossing? " + str(crossing) + " crossed? " + str(crossed)
                #print "driving! left: " + str(GPIO.input(LeftSensor)) + " middle: " + str(GPIO.input(MiddleSensor)) + " right: " + str(GPIO.input(RightSensor))
                drive(state)

            else:
                quit("Sorry boss, I somehow lost my way.")
                
            loop_index += 1

except KeyboardInterrupt:
    # Clean up
    os.system("pkill -SIGSTOP mpg321") # Stop all sounds
    GPIO.cleanup()
