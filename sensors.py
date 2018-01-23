import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

# Input pins for Sensors
LeftSensor = 23
MiddleSensor = 25
RightSensor = 24
ButtonPin = 21

# TurnMotor pins, defines wheels
LeftWheel = [4,17,27,22]
RightWheel = [26,19,13,9]

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

# "Vooruit"
StepCount1 = 8
Seq1 = []
Seq1 = range(0, StepCount1)
Seq1[0] = [1,0,0,0]
Seq1[1] = [1,1,0,0]
Seq1[2] = [0,1,0,0]
Seq1[3] = [0,1,1,0]
Seq1[4] = [0,0,1,0]
Seq1[5] = [0,0,1,1]
Seq1[6] = [0,0,0,1]
Seq1[7] = [1,0,0,1]

# "Achteruit"
StepCount2 = 8
Seq2 = []
Seq2 = range(0, StepCount2)
Seq2[0] = [0,0,0,1]
Seq2[1] = [0,0,1,1]
Seq2[2] = [0,0,1,0]
Seq2[3] = [0,1,1,0]
Seq2[4] = [0,1,0,0]
Seq2[5] = [1,1,0,0]
Seq2[6] = [1,0,0,0]
Seq2[7] = [1,0,0,1]

# Welke stappenvolgorde gaan we hanteren?
# Seq1 = Seq3
# Seq2 = Seq2

StepCount = StepCount1


try:
    while True:
        curr_state = GPIO.input(ButtonPin)

        # print("middle %s" % GPIO.input(MiddleSensor))

        while (curr_state != prev_state):
            # once pressed set it back to previous state, for an infinite loop
            curr_state = 0
            StopCounter = 0

            # if there is no light for the middle ONLY
            if GPIO.input(LeftSensor) and GPIO.input(RightSensor) and not GPIO.input(MiddleSensor):
                # go forward
                for pin in range(0, 4):
                  xpin = RightWheel[pin]
                  ypin = LeftWheel[pin]
                  GPIO.output(xpin, Seq2[StepCounter][pin])
                  GPIO.output(ypin, Seq1[StepCounter][pin])
                    # GPIO.output(xpin, False)
                    # GPIO.output(ypin, False)
                StepCounter += 1

                # Als we aan het einde van de stappenvolgorde zijn beland start dan opnieuw
                if (StepCounter==StepCount): StepCounter = 0
                if (StepCounter<0): StepCounter = StepCount

                # Wacht voor de volgende stap (lager = snellere draaisnelheid)
                sleep(.001)

                print("Middle")
                # if GPIO.input(ButtonPin) == 0:
                #     curr_state = GPIO.input(ButtonPin)
                StopCounter = 0

            if GPIO.input(LeftSensor) and GPIO.input(RightSensor) and GPIO.input(MiddleSensor) and StopCounter < 1000:
                for pin in range(0, 4):
                  xpin = RightWheel[pin]
                  ypin = LeftWheel[pin]
                  GPIO.output(xpin, Seq2[StepCounter][pin])
                  GPIO.output(ypin, Seq1[StepCounter][pin])
                    # GPIO.output(xpin, False)
                    # GPIO.output(ypin, False)
                StepCounter += 1

                # Als we aan het einde van de stappenvolgorde zijn beland start dan opnieuw
                if (StepCounter==StepCount): StepCounter = 0
                if (StepCounter<0): StepCounter = StepCount

                # Wacht voor de volgende stap (lager = snellere draaisnelheid)
                sleep(.001)
                StopCounter += 1



            if GPIO.input(LeftSensor) and not GPIO.input(RightSensor):
                # go right
                for pin in range(0, 4):
                  xpin = RightWheel[pin]
                  ypin = LeftWheel[pin]
                  GPIO.output(xpin, Seq1[StepCounter][pin])
                  GPIO.output(ypin, Seq1[StepCounter][pin])
                    # GPIO.output(xpin, False)
                    # GPIO.output(ypin, False)
                StepCounter += 1

                # Als we aan het einde van de stappenvolgorde zijn beland start dan opnieuw
                if (StepCounter==StepCount): StepCounter = 0
                if (StepCounter<0): StepCounter = StepCount

                # Wacht voor de volgende stap (lager = snellere draaisnelheid)
                sleep(.001)

                StopCounter = 0

            if GPIO.input(RightSensor) and not GPIO.input(LeftSensor):
                # go left
                for pin in range(0, 4):
                  xpin = RightWheel[pin]
                  ypin = LeftWheel[pin]
                  GPIO.output(xpin, Seq2[StepCounter][pin])
                  GPIO.output(ypin, Seq2[StepCounter][pin])
                    # GPIO.output(xpin, False)
                    # GPIO.output(ypin, False)
                StepCounter += 1

                # Als we aan het einde van de stappenvolgorde zijn beland start dan opnieuw
                if (StepCounter==StepCount): StepCounter = 0
                if (StepCounter<0): StepCounter = StepCount

                # Wacht voor de volgende stap (lager = snellere draaisnelheid)
                sleep(.001)

                StopCounter = 0

            # if GPIO.input(MiddleSensor) == True:
            #     print("Middle")
            #     sleep(.5)
            #
            # if GPIO.input(RightSensor) == True:
            #     print("Right")
            #     sleep(.5)

except KeyboardInterrupt:
  # GPIO netjes afsluiten
  GPIO.cleanup()
