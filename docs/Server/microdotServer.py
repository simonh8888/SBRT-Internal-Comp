# Run these on thonny
from microdot import Microdot
from microdot.websocket import with_websocket
from microdot.cors import CORS
from machine import Pin, PWM
import asyncio 
import network
import secrets
import time
import ujson

# Initialize PWM and direction pins
motor1_pwm = PWM(Pin(3, Pin.OUT), freq = 1000)
motor1_in1 = Pin(0, Pin.OUT)
motor1_in2 = Pin(10, Pin. OUT)

motor2_pwm = PWM(Pin(11, Pin.OUT), freq = 1000)
motor2_in1 = Pin(5, Pin. OUT)
motor2_in2 = Pin(9, Pin.OUT)

motor3_pwm = PWM(Pin(27, Pin.OUT), freq = 1000)
motor3_in1 = Pin(26, Pin. OUT)
motor3_in2 = Pin(22, Pin. OUT)

motor4_pwm = PWM (Pin(19, Pin.OUT), freq = 1000)
motor4_in1 = Pin(20, Pin.OUT)
motor4_in2 = Pin(21, Pin.OUT)

# Test LEDs
led = Pin(2, Pin.OUT)
led_connected = Pin(18, Pin.OUT)
led_wireless = Pin('LED', Pin.OUT)

led_wireless.value(1)  
time.sleep(1)
led_wireless.value(0)

# Function to stop all motors
def stop():
    motor1_in1.value(0)
    motor1_in2.value(0)
    motor2_in1.value(0)
    motor2_in2.value(0)
    motor3_in1.value(0)
    motor3_in2.value(0)
    motor4_in1.value(0)
    motor4_in2.value(0)
    
    motor1_pwm.duty_u16(0)
    motor2_pwm.duty_u16(0)
    motor3_pwm.duty_u16(0)
    motor4_pwm.duty_u16(0)

# Function to move forward
def move_forward(speed):
    motor1_in1.value(1)
    motor1_in2.value(0)
    motor2_in1.value(1)
    motor2_in2.value(0)
    motor3_in1.value(1)
    motor3_in2.value(0)
    motor4_in1.value(1)
    motor4_in2.value(0)

    motor1_pwm.duty_u16(speed)
    motor2_pwm.duty_u16(speed)
    motor3_pwm.duty_u16(speed)
    motor4_pwm.duty_u16(speed)

def move_backward(speed):
    motor1_in1.value(0)
    motor1_in2.value(1)
    motor2_in1.value(0)
    motor2_in2.value(1)
    motor3_in1.value(0)
    motor3_in2.value(1)
    motor4_in1.value(0)
    motor4_in2.value(1)

    motor1_pwm.duty_u16(speed)
    motor2_pwm.duty_u16(speed)
    motor3_pwm.duty_u16(speed)
    motor4_pwm.duty_u16(speed)

def turn_left(speed):
    # Turn off left motors
    motor1_in1.value(0)
    motor1_in2.value(0)
    motor3_in1.value(0)
    motor3_in2.value(0)
    
    # Run right motors forward
    motor2_in1.value(1)
    motor2_in2.value(0)
    motor4_in1.value(1)
    motor4_in2.value(0)
    
    motor1_pwm.duty_u16(0)        # Left motors off
    motor3_pwm.duty_u16(0)
    motor2_pwm.duty_u16(speed)    # Right motors on
    motor4_pwm.duty_u16(speed)

def turn_right(speed):
    # Turn off right motors
    motor2_in1.value(0)
    motor2_in2.value(0)
    motor4_in1.value(0)
    motor4_in2.value(0)
    
    # Run left motors forward
    motor1_in1.value(1)
    motor1_in2.value(0)
    motor3_in1.value(1)
    motor3_in2.value(0)

    motor2_pwm.duty_u16(0)        # Right motors off
    motor4_pwm.duty_u16(0)
    motor1_pwm.duty_u16(speed)    # Left motors on
    motor3_pwm.duty_u16(speed)

# Connect to Wi-Fi
time.sleep(2)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
time.sleep(2)

# Wait for connection
max_attempts = 10
attempt = 0

while not wlan.isconnected() and attempt < max_attempts:
    led_wireless.value(1)
    print(f"Trying to connect to {secrets.SSID} (Attempt {attempt + 1}/{max_attempts})...")
    time.sleep(10)
    attempt += 1
    led_wireless.value(0)
    time.sleep(1)
if wlan.isconnected():
    print("Connected to IP:", wlan.ifconfig()[0])
    led_connected.value(1)
    time.sleep(5)
    led_connected.value(0)
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
            print("Received data from client:", data)
            # Insert your logic here
            if data:
                # Parse the incoming data
                try:
                    json_data = ujson.loads(data)
                    direction = json_data['dir']
                    led_status = json_data['led']  # Handle LED control (on/off)
                    print(f"Joystick Position - Direction: {direction}, LED Status: {led_status}")

                    # Handle LED Control
                    if led_status == 1:
                        led.value(1)  # Turn the LED on
                    elif led_status == 0:
                        led.value(0)  # Turn the LED
                        
                    # Motor control
                    s = 65535
                    if direction == 'forward':
                        move_forward(s)  # Move forward when y > 0
                    elif direction == 'backward':
                        move_backward(s) # Move backward when y < 0
                    elif direction == 'right' and led_status == 1:
                        turn_right(s)    # Turn right when x > 0
                    elif direction == 'left':
                        turn_left(s)     # Turn left when x < 0
                    elif direction == 'right' and led_status == 0:
                        stop()
                except Exception as e:
                    print(f"Error parsing data: {e}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket connection closed")

app.run(port=80)