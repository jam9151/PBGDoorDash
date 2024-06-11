import time
import pyautogui
import os
from images import getConfidence
import random
from pyscreeze import Box

# SETTINGS
VERBOSE = True
DEFAULT_CONFIDENCE = 0.9
IMAGE_EXTENSION = "png"
pathToImages = os.path.join(os.getcwd(), "images")    #default path to images folder

# # TODO: uncomment this out in prod
pyautogui.FAILSAFE=False



class customInput:

    """
    safe_space: if false, mouse will not move back
                if given coordinates (x, y), mouse has option to move back to that spot after clicking automatically

    click_delay: if false, no click delay
                 if given a number, that is the seconds that each click will delay

    region:     if false, will search whole screen for images
                if given (x1, y1, x2, y2), will only search that part of the screen for images
    """
    def __init__(self, safe_space=False, click_delay=False, region=False, pathToImages=pathToImages):
        self.safe_space = safe_space
        self.click_delay = click_delay
        self.region = region
        self.pathToImages = pathToImages



    #waits until image is on screen or until max time limit is reached
    """
    description:    name of the image without the extension

    max:            maximum amount of time to wait before timing out
                    False means it will wait indefinitely

    wait:           amount of time to sleep before returning (surprisingly useful)

    visible:        True: waiting for the image to be visible
                    False: waiting for the image to not be visible
    """
    def wait_until(self, description, max=20, wait=0, visible=True):
        startTime = time.time()
        while True:
            test = self.find(description)

            if test and visible:
                break
            
            if not test and not visible:
                break

            if max and (time.time() - startTime) > max:
                if visible and VERBOSE: print(f"Couldn't find {description} after {max} seconds")
                if not visible and VERBOSE: print(f"{description} still found on screen after {max} seconds")
                return False
            time.sleep(0.5)
        
        if wait:
            time.sleep(wait)
        
        return test



    # takes a pyscreeze.Box and returns the center coordinates
    """
    object:     pyautogui object with format (x, y, length, width)
    """
    def locate(self, object):
        if type(object) != Box:
            print("ERROR: Trying to locate object which is not type pyscreeze.Box")
            return (0, 0)
        x = int(object[0] + object[2] / 2)
        y = int(object[1] + object[3] / 2)
        return x, y



    # moves the mouse back to the safe space
    def move_back(self):
        if self.safe_space:   
            pyautogui.moveTo(self.safe_space[0], self.safe_space[1])
            return True
        else:
            if VERBOSE:
                print("WARNING: Attempting to move mouse to safe_space when safe_space is not defined. ignoring...")
            return False



    #finds an image on the screen and returns a Box object (x, y, length, width) or False
    """
    description:    image name without the extension
    confidence:     specify how precise the image needs to match
    grayscale:      if true, can reduce precision but improve performance
    """
    def find(self, description, confidence=None, grayscale=False):
        imgPath = f"{os.path.join(self.pathToImages, description)}.{IMAGE_EXTENSION}"

        if not confidence:
            confidence = getConfidence(description)
            if confidence == "default":
                confidence = DEFAULT_CONFIDENCE

        try:
            if self.region:
                return pyautogui.locateOnScreen(imgPath, confidence=confidence, region=self.region, grayscale=grayscale)
            else:
                return pyautogui.locateOnScreen(imgPath, confidence=confidence, grayscale=grayscale)
        except pyautogui.ImageNotFoundException:
            return False
        


    #click an object on the screen. optionally, move back to safe_space
    """
    object:     1) a tuple (x, y) to click
                2) None (click at current position)
                3) the name of an image without the extension
                4) the pyautogui bounding box (x, y, length, width)

    button:     "left" or "right"

    wait:       how long to wait before returning

    back:       whether or not to move back to safe_space

    confidence: the degree to match object if it is an image
    """
    def click(self, object=None, button="left", wait=0, back=False, confidence=None):
        if VERBOSE: print(f"Attempting to click {object}")

        if object != None and not object:
            print("ERROR: could not find object to click")
            return False
        
        if type(object) == tuple:
            x, y = object
        elif object:
            if type(object) == str:
                object = self.find(object, confidence=confidence)
                if not object:
                    print("ERROR: could not find object to click")
                    return False
            x, y = self.locate(object)
        else:
            x, y = pyautogui.position()

        pyautogui.moveTo(x=x, y=y)
        time.sleep(self.click_delay)
        pyautogui.mouseDown(button=button)
        time.sleep(0.075 + random.random() / 50)    #average mouse click lasts 85ms, with Q3 = 95ms, Q1= 75ms;
        pyautogui.mouseUp(button=button)
        if back:
            self.move_back()
        if wait:
            time.sleep(wait)
        return True


    #moves to an object
    """
    object:     1) a tuple (x, y) to click
                2) the name of an image without the extension
                3) the pyautogui bounding box (x, y, length, width)

    duration:   how long it should take to perform the movement
    """
    def moveTo(self, object, duration=0):
        if not object:
            print(f"ERROR: cannot move to {object} - probably couldn't find object")
            return False
        if type(object) == tuple:
            x, y = object
        else:
            if type(object) == str:
                object = self.find(object)
                if not object:
                    return False
            x, y = self.locate(object)
        pyautogui.moveTo(x, y, duration=duration)
        return True


    #presses one key
    """
    key:        character to be pressed
    presses:    how many times
    interval:   time between presses
    """
    def press(self, key, presses=1, interval=0.1):
        for i in range(presses):
            if interval:
                time.sleep(interval)
            if key.isupper():
                self.hotkey('shift', key)
            else:
                self.hotkey(key)


    #presses a sequence of keys
    """
    message:    string to be written
    interval:   time between presses
    end:        special character to print at end, e.g. "enter"
    """
    def write(self, message, interval=0.1, end=""):
        for letter in message:
            self.press(letter, interval=interval)
        if end:
            self.press(end)


    #pushes keys down in a sequence and then up in a reverse sequence
    def hotkey(self, *keys):
        for key in keys:
            pyautogui.keyDown(key)

        if self.click_delay:
            time.sleep(0.1)

        for key in keys[::-1]:
            pyautogui.keyUp(key)


    #swipes from start to end
    """
    start:      (x, y) start coordinates
    end:        (x, y) end coordinates
    duration:   how long in seconds it takes
    back:       whether or not to move mouse back to safe_space when done
    """
    def swipe(self, start, end, duration=.25, back=False):
        pyautogui.moveTo(start)

        time.sleep(1)
        x, y = end
        pyautogui.dragTo(x, y, duration)
        if back:
            self.move_back()


    #scrolls a certain distance (somewhat unreliable)
    """
    direction:  "up" / "down"
    distance:   int, amount of scrolls to use
    min_interval:   time between scrolls
    """
    def scroll(self, direction, distance=1, min_interval=0.04):
        if direction == "up": direction = 100
        if direction == "down": direction = -100
        for i in range(distance):
            pyautogui.scroll(direction)
            time.sleep(min_interval + (random.random() * 0.02))
            
            
    def screenshot(self, region=False):
        if region:
            region = list(region)
            region[2] -= region[0]
            region[3] -= region[1]
            region = tuple(region)
        
            
            return pyautogui.screenshot(region=region)
        else:
            return pyautogui.screenshot()
        
        
    def locate_all(self, description, region, confidence=None, grayscale=False):
        imgPath = f"{os.path.join(self.pathToImages, description)}.{IMAGE_EXTENSION}"

        if not confidence:
            confidence = getConfidence(description)
            if confidence == "default":
                confidence = DEFAULT_CONFIDENCE

        try:
            return list(pyautogui.locateAllOnScreen(imgPath, confidence=confidence, region=region, grayscale=grayscale))
        except:
            return []


