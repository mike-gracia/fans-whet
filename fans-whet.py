import asyncio
import websockets
import json
import math
import time
import datetime

enable_GPIO = True              #auto sets to false if cant import gpio
LED_MAX = 4095                  #for converting to percentages
MIN_LIGHT_AVG_TO_SPIN = 15     #percentage of light to start fans
MIN_FAN_SPEED = 30              #slowest fans speed setting
PIN = 12                        #signal pin, must support pwm? Not sure if this is the only one by default
FREQ = 25                       #pwm freq

try:
    import RPi.GPIO as GPIO
except:
    print("Unable to import GPIO - this probably isnt a Raspberry Pi or you need to install it")
    enable_GPIO = False


print("starting fan control")

async def message_handler_async():
    async with websockets.connect('ws://localhost:7999/chat/websocket') as websocket:
        while True:
            message = json.loads( await websocket.recv() )
            if 'status' in message:
                consume_message(message)
                await websocket.send(create_message())


def consume_message(message):
    global fan_speed
    cnt = 0
    avg = 0
    for c in message['status']:
        avg += c['cur']
        cnt += 1
        
    pwm_avg = avg / cnt
    per_avg = math.ceil( (pwm_avg / 4095) * 100 )


    if per_avg > MIN_LIGHT_AVG_TO_SPIN:
        fan_speed = max(per_avg, MIN_FAN_SPEED)
    else:
        fan_speed = 0

    setFanSpeed(fan_speed)
    print('{:%H:%M:%S}: AVERAGE = {} | %AVG = {} | fan_speed = {}'.format(datetime.datetime.now(), pwm_avg, per_avg, fan_speed))

def create_message():
    msg = {}
    msg['value'] = fan_speed
    msg['active_at_perc'] = MIN_LIGHT_AVG_TO_SPIN
    msg['min_speed'] = MIN_FAN_SPEED
    msg['enabled'] = enable_GPIO

    msg_obj = {}
    msg_obj['FanContainer'] = []
    msg_obj['FanContainer'].append(msg)

    return json.dumps(msg_obj)



def createFan():
    if enable_GPIO:
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
asyncio.get_event_loop().run_until_complete(message_handler_async())


p.stop()
GPIO.cleanup()
