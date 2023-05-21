import time

import requests
import wiringpi as wip
import sys

# stepper initialise
print("start")

coil_A = 3
coil_B = 4
coil_C = 6
coil_D = 9

wip.wiringPiSetup()
wip.pinMode(coil_A, wip.OUTPUT)
wip.pinMode(coil_B, wip.OUTPUT)
wip.pinMode(coil_C, wip.OUTPUT)
wip.pinMode(coil_D, wip.OUTPUT)


# ultrasound sensor initialise
trgpin = 1
echopin = 2
wip.wiringPiSetup()
wip.pinMode(trgpin, 1)
wip.pinMode(echopin, 0)


# relay initialise
relayPin = 10
wip.wiringPiSetup()
wip.pinMode(relayPin, 1)
wip.digitalWrite(relayPin, 0)


# buttons initialise
button1 = 5
wip.wiringPiSetup()
wip.pinMode(button1, 0)
button2 = 7
wip.wiringPiSetup()
wip.pinMode(button2, 0)


# ubeac setup
url = "http://broombow.hub.ubeac.io/OPI"
uid = "OPI"


def relay_start(triggercounter):
    j = True
    # Sends new information to ubeac
    ubeac(100, triggercounter)
    # Makes the LED light blink, using the relay
    while j:
        wip.digitalWrite(relayPin, 1)
        time.sleep(0.5)
        wip.digitalWrite(relayPin, 0)
        time.sleep(0.5)
        # If the reset button is pressed
        if wip.digitalRead(button2) == 0:
            # opens the door using the stepper motor
            reversed_stepper()
            # Updates ubeac
            ubeac(0, triggercounter)
            # Exit this while loop
            j = False


def stepper():
    start_time = time.time()
    # makes sure the stepper motor is only active for 4 seconds
    while time.time() - start_time < 4:
        # makes the stepper motor turn by activating the coils in the correct pattern (wave drive)
        wip.digitalWrite(coil_D, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_D, wip.LOW)

        wip.digitalWrite(coil_C, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_C, wip.LOW)

        wip.digitalWrite(coil_B, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_B, wip.LOW)

        wip.digitalWrite(coil_A, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_A, wip.LOW)


def reversed_stepper():
    start_time = time.time()
    # makes sure the stepper motor is only active for 4 seconds
    while time.time() - start_time < 4:
        # makes the stepper motor turn by activating the coils in the correct pattern (wave drive)
        # activate coil
        wip.digitalWrite(coil_A, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_A, wip.LOW)

        wip.digitalWrite(coil_B, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_B, wip.LOW)

        wip.digitalWrite(coil_C, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_C, wip.LOW)

        wip.digitalWrite(coil_D, wip.HIGH)
        time.sleep(0.01)
        wip.digitalWrite(coil_D, wip.LOW)
    # Give people some time to remove the mouse before closing it again
    time.sleep(10)


def ubeac(status, trigger_amount):
    # make the json file to send to ubeac
    data = {
        "uid": uid,
        "sensors": [
            {'id': 'status',
             'data': status},
            {"id": 'trigger_amount',
             'data': trigger_amount}
            ]
    }
    # send the json file to ubeac
    r = requests.post(url, verify=False, json=data)
    print(r.status_code)


trigcount = 0

# Start of the main program, in a while loop to make it go on indefinitely
while True:
    # Measurement of the ultrasound sensor
    wip.digitalWrite(trgpin, 1)
    time.sleep(.000010)
    wip.digitalWrite(trgpin, 0)
    while wip.digitalRead(echopin) == 0:
        time.sleep(.000010)
    signal_high = time.time()
    while wip.digitalRead(echopin) == 1:
        time.sleep(.00001)
    signal_low = time.time()
    time_passed = signal_low - signal_high
    distance = time_passed * 17000
    # If distance is less than 5cm or the activate button is pressed
    if distance < 5 or wip.digitalRead(button1) == 0:
        # Close the door
        stepper()
        # Add 1 to amount of triggers
        trigcount += 1
        # Start the relay sequence
        relay_start(trigcount)
        # Measure distance every 5 seconds
    time.sleep(0.5)
