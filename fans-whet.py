import asyncio
import websockets
import json
import math
import time

enable_GPIO = True
try:
    import RPi.GPIO as GPIO
except:
    print("Unable to import GPIO - this probably isnt a Raspberry Pi")
    enable_GPIO = False


fan_speed = 0
print("starting fan control")

async def handler_consumer():
    async with websockets.connect('ws://localhost:7999/chat/websocket') as websocket:
        while True:
            message = await websocket.recv()
            consumer(message)


def consumer(message):
    j = json.loads(message)
    
    if 'status' in j: 
        #print(json.dumps(j))
        cnt = 0
        avg = 0
        for c in j['status']:
            avg += c['cur']
            cnt += 1
            print("{} - {}".format(cnt, c['cur']))
        
        pwm_avg = avg / cnt
        per_avg = math.ceil( (pwm_avg / 4095) * 100 )
        fan_speed = per_avg if per_avg > 20 else 0
        print("AVERAGE = {} | %AVG = {} | fan_speed = {}".format(pwm_avg, per_avg, fan_speed))
        setFanSpeed(fan_speed)

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
     if enable_GPIO:
         p.ChangeDutyCycle(speed)



p = createFan()





asyncio.get_event_loop().run_until_complete(handler_consumer())


p.stop()
GPIO.cleanup()
