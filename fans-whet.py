import asyncio
import websockets
import json
import math
import time
import datetime

enable_GPIO = True
LED_MAX = 4095
MIN_LIGHT_AVG_TO_START = 20    #percentage of light to start fans
MIN_FAN_SPEED = 30              #slowest fans speed setting


try:
    import RPi.GPIO as GPIO
except:
    print("Unable to import GPIO - this probably isnt a Raspberry Pi")
    enable_GPIO = False


print("starting fan control")

async def handler_consumer():
    async with websockets.connect('ws://localhost:7999/chat/websocket') as websocket:
        while True:
            message = json.loads( await websocket.recv() )
            if 'status' in message:
                consumer(message)


def consumer(message):
    global fan_speed
    cnt = 0
    avg = 0
    for c in message['status']:
        avg += c['cur']
        cnt += 1
        
    pwm_avg = avg / cnt
    per_avg = math.ceil( (pwm_avg / 4095) * 100 )


    if per_avg > MIN_LIGHT_AVG_TO_START:
        fan_speed = max(per_avg, MIN_FAN_SPEED)
    else
        fan_speed = 0

    setFanSpeed(fan_speed)
    print('{:%H:%M:%S}: AVERAGE = {} | %AVG = {} | fan_speed = {}'.format(datetime.datetime.now(), pwm_avg, per_avg, fan_speed))

def createFan():
    if enable_GPIO:
        PIN = 12
        FREQ = 25
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PIN, GPIO.OUT)
        p = GPIO.PWM(PIN, FREQ)
        p.start(100)
        time.sleep(5)
        return p
    return 'No GPIO'



def setFanSpeed(speed):
    speed = min ( max(speed, 0) , 100)
    if enable_GPIO:
         p.ChangeDutyCycle(speed)


fan_speed = 0
p = createFan()
asyncio.get_event_loop().run_until_complete(handler_consumer())


p.stop()
GPIO.cleanup()
