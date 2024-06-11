from gpiozero import Button
button = Button(3)
button.wait_for_press()
print("PARTY TIME BABY")
