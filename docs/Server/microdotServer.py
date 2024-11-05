# Run these on thonny
from microdot import Microdot
from microdot.websocket import with_websocket
from microdot.cors import CORS
from machine import Pin, PWM
import asyncio 
import network
import secrets
import time

# Initialize PWM and direction pins
PWM1 = PWM(Pin(3, Pin.OUT), freq=1000)
PWM2 = PWM(Pin(19, Pin.OUT), freq=1000)
left_wheel_pin1, left_wheel_pin2 = Pin(0, Pin.OUT), Pin(10, Pin.OUT)
right_wheel_pin1, right_wheel_pin2 = Pin(20, Pin.OUT), Pin(21, Pin.OUT)

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
time.sleep(5)

# Wait for connection
max_attempts = 10
attempt = 0

while not wlan.isconnected() and attempt < max_attempts:
    print(f"Trying to connect to {secrets.SSID} (Attempt {attempt + 1}/{max_attempts})...")
    time.sleep(10)
    attempt += 1

if wlan.isconnected():
    print("Connected to IP:", wlan.ifconfig()[0])
else:
    print("Failed to connect to Wi-Fi. Please check your SSID and password.")


app = Microdot()
CORS(app, allowed_origins = '*', allow_credentials = True)

@app.get('/test')
def index(request):
    return "hello world"

@app.get('/direction')
@with_websocket
async def index(request, ws): 
    try:
        while True:
            data = await ws.receive()
            ## Insert your logic here
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket connection closed")

app.run(port=80)