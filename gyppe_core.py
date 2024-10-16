#!/usr/bin/python

import sys
import time
import threading
import importlib

from pytte_core.connection import PytteConnection
connection = PytteConnection("10.151.112.69:6388", "benjamin")

tcs_mock_path = "rigs:dhu3s:pi6:backend:track_1:network_1:tcs_mock_process"
shock_mock_path = "rigs:dhu3s:pi6:backend:track_1:network_1:shock_mock_process"

#Threads for performing two tasks simultaneuous
#load_thread = threading.Thread(target=load_event, daemon=True)
#drive_thread = threading.Thread(target=drive_event, daemon=True)
#Start threads

#drive_thread.start()
#load_thread.start()

#Event handling simultaneuous tasks (e.i lift and drive)
#drive_and_lift_event = threading.Event()
#drive_and_lift_event.clear()




#Main backend function
def update_tcs(tcs_state):
    print(tcs_state)
    connection.send_command(tcs_mock_path, "configure_tcs", {"values": tcs_state})

def set_driving_config(forward, backwards, speed):
    return {
        "driving_forwards": forward,
        "driving_backwards": backwards,
        "speed": speed
    }

def set_loading_config(lifting, lowering):
    return {
        "lifting": lifting,
        "lowering": lowering
    }

def set_config(forward, backward, speed, lifting, lowering):
    if forward and backward or lifting and lowering:
        print("Cant perform drive forward and backwards simultaneous")
    else:
        return {
            "driving_forwards": forward,
            "driving_backwards": backward,
            "speed": speed,
            "lifting": lifting,
            "lowering": lowering
        }

def stop():
    update_tcs(set_config(False, False, 0, False, False))

def drive(duration=1, repeat=1, interval=1, speed=5):
    for x in range(repeat):
        update_tcs(set_config(True, False, speed, False, False))
        time.sleep(duration)
        stop()
        time.sleep(interval)
    
def reverse(duration=1, repeat=1, interval=1, speed=-5):
    for x in range(repeat):
        update_tcs(set_config(False, True, speed, False, False))
        time.sleep(duration)
        stop()
        time.sleep(interval)
    
def lift(duration=1, interval=1, repeat=1,):
    for x in range(repeat):
        update_tcs(set_config(False, False, 0, True, False))
        time.sleep(duration)
        stop()
        time.sleep(interval)
    
def lower(duration=1, interval=1, repeat=1,):
    for x in range(repeat):
        update_tcs(set_config(False, False, 0, False, True))
        time.sleep(duration)
        stop()
        time.sleep(interval)

def drive_and_lift(duration=1, interval=1, repeat=1, speed=5):
    for x in range(repeat):
        update_tcs(set_config(True, False, speed, True, False))
        time.sleep(duration)
        stop()
        time.sleep(interval)

def drive_and_lower(duration=1, interval=1, repeat=1, speed=5):
    for x in range(repeat):
        update_tcs(set_config(True, False, speed, False, True))
        time.sleep(duration)
        stop()
        time.sleep(interval)

def reverse_and_lift(duration=1, interval=1, repeat=1, speed=-5):
    for x in range(repeat):
        update_tcs(set_config(False, True, speed, True, False))
        time.sleep(duration)
        stop()
        time.sleep(interval)

def reverse_and_lower(duration=1, interval=1, repeat=1, speed=-5):
    for x in range(repeat):
        update_tcs(set_config(False, True, speed, False, True))
        time.sleep(duration)
        stop()
        time.sleep(interval)

def shock(x=25, y=25, repeat=1, interval=1):
    payload = {
        "x_instant": x,
        "x_hold": x,
        "y_instant": y,
        "y_hold": y,
    }
    for x in range(repeat):
        connection.send_command(shock_mock_path, "set_shock", {"values": payload})
        #Maybe send a 0-set shock after?
        time.sleep(interval)
        

def wait(seconds):
    time.sleep(seconds)

def logon(pin):
    connection.send_command(keypad_mock_path, "logon", {"pin": pin})
    
def logoff(status=2):
    connection.send_command(keypad_mock_path, "logoff", {"status": status})