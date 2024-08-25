from machine import Pin
import time
import network
from umqtt.simple import MQTTClient
import json
import _thread

# Define the GPIO pins for STEP, DIR, and the analog pin for the potentiometer
STEP_PIN = Pin(14, Pin.OUT)  # GPIO pin for STEP
DIR_PIN = Pin(12, Pin.OUT)   # GPIO pin for DIR
pinEnabled = Pin(4, Pin.OUT,value=0)

# Define the number of steps per revolution for your motor
STEPS_PER_REV = 200
# Define the step delay (in seconds)
STEP_DELAY = 0.001

current_position = 0
value = 0

# HiveMQ Broker details---------------
broker = "broker.hivemq.com"
client_id = "esp32_subscriber"
topic = "stepper01ktf"
#-------------------------------------

# Wi-Fi credentials-------------------
ssid = "Wokwi-GUEST"
password = ""
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    
    print("Connected to WiFi:", wlan.ifconfig())
#-------------------------------------

def step_motor_forward():
    #print("js",current_position)
    STEP_PIN.value(1)
    time.sleep(STEP_DELAY)
    STEP_PIN.value(0)
    time.sleep(STEP_DELAY)

def step_motor_back():
    #print("js",current_position)
    STEP_PIN.value(1)
    time.sleep(STEP_DELAY)
    STEP_PIN.value(0)
    time.sleep(STEP_DELAY)

#-------------mapping--------------------------------------
def map_value(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def rotate_to_angle_from_pot(pot_value):
    angle = map_value(pot_value, 0, 360, 0, 360)  #
    print("Rotating to:", angle, "degrees")
    steps = int(((angle / (360)) * STEPS_PER_REV)-1)
    print("Step Size:",steps)
    return steps
#----------------------------------------------------------

# Callback function for received messages------------------
def sub_cb(topic, msg):
    global value
    #Extract data from string into integer-----------------
    decoded_msg = msg.decode()
    #JSON string to a Python dictionary
    data = json.loads(decoded_msg)
    # Extracting the "value" and converting it to an integer
    value = int(data["value"])
    #------------------------------------------------------
    print("Received message:", value)
#----------------------------------------------------------

# MQTT subscribe function----------------------------------
def mqtt_subscribe():
    client = MQTTClient(client_id, broker)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic)
    
    print("Subscribed to topic:", topic)
    
    while True:
        client.wait_msg()  # Wait for a message
    
    client.disconnect()
#----------------------------------------------------------

# Start MQTT subscription in a new thread------------------
def start_mqtt_thread():
    _thread.start_new_thread(mqtt_subscribe, ())
#----------------------------------------------------------

# Main execution--------------------
connect_wifi()
start_mqtt_thread()
#-----------------------------------

while True:
    pot_value = value
    desired_position = rotate_to_angle_from_pot(pot_value)

    # Move the motor to the desired position
    if desired_position > current_position:
        DIR_PIN.value(1)  # Set direction forward
        while current_position < desired_position:
            step_motor_forward()
            current_position += 1
    elif desired_position < current_position:
        DIR_PIN.value(0)  # Set direction backward
        while current_position > desired_position:
            step_motor_back()
            current_position -= 1
    elif desired_position == current_position:
        pass

    time.sleep(0.1)  # Small delay to avoid excessive polling
    
