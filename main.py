#!/usr/bin/.env python3
from customInput import customInput
import subprocess
import time
import android
from gpiozero import Button, LED

# push the button here
for i in range(2):
    led    = LED(2)
    led.toggle()
    button = Button(3)                                                                   
    button.wait_for_press()
    print("Its Party TIME BABAYYYYYYY")
    led.toggle()


    process = subprocess.Popen(["scrcpy", "--video-bit-rate", "1M", "--max-size", "800", "--always-on-top", "--window-x", "100", "--window-y", "100"])

    # scrcpy --video-bit-rate 1M --max-size 800 --always-on-top --window-x 100 --window-y 100 

    time.sleep(10)    
        
    a = android.Android()
    a.start()
    a.get_to_doordash()
    a.random_category()
    a.random_restaurant()
    a.order_food()
        
    process.terminate()
    led.toggle()

