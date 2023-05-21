import time

import requests
import wiringpi as wip
import sys

print("start")

coil_A = 3
coil_B = 4
coil_C = 6
coil_D = 9

# stepper initialise
wip.wiringPiSetup()
wip.pinMode(coil_A, 1)
wip.pinMode(coil_B, 1)
wip.pinMode(coil_C, 1)
wip.pinMode(coil_D, 1)

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
    ubeac(1, triggercounter)
    while j:
        wip.digitalWrite(relayPin, 1)
        time.sleep(0.5)
        wip.digitalWrite(relayPin, 0)
        time.sleep(0.5)
        if wip.digitalRead(button2) == 0:
            reversed_stepper()
            ubeac(0, triggercounter)
            j = False


def stepper():
    start_time = time.time()
    while time.time() - start_time < 4:
        wip.digitalWrite(coil_D, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_D, 0)

        wip.digitalWrite(coil_C, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_C, 0)

        wip.digitalWrite(coil_B, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_B, 0)

        wip.digitalWrite(coil_A, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_A, 0)


def reversed_stepper():
    start_time = time.time()
    while time.time() - start_time < 4:
        wip.digitalWrite(coil_A, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_A, 0)

        wip.digitalWrite(coil_B, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_B, 0)

        wip.digitalWrite(coil_C, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_C, 0)

        wip.digitalWrite(coil_D, 1)
        time.sleep(0.01)
        wip.digitalWrite(coil_D, 0)
    time.sleep(10)


def ubeac(status, trigger_amount):
    data = {
        "uid": uid,
        "sensors": [
            {'id': 'status',
             'data': status},
            {"id": 'trigger_amount',
             'data': trigger_amount}
            ]
    }
    r = requests.post(url, verify=False, json=data)
    print(r.status_code)


trigcount = 0

while True:
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
    if distance < 5 or wip.digitalRead(button1) == 0:
        stepper()
        trigcount += 1
        relay_start(trigcount)
    time.sleep(0.5)
