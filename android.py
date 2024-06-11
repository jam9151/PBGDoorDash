from customInput import customInput
import time
import random
import pytesseract

three_lines = (185, 904)
circle = (296, 908)
min_constraint = 0.1
max_constraint = 0.3

most_liked = [
    (200, 523),
    (390, 523),
    (200, 770),
    (390, 770)
]

with open("blocked_restaurants.txt", "r") as f:
    blocked_restaurants = [x.replace("\n", "") for x in f.readlines()]


def get_text_screenshot(coords, controller):
    screenshot = controller.screenshot(region=coords)
    screenshot.save("screenshot.png")
    text = pytesseract.image_to_string(screenshot)
    print(text)
    text = text.strip().replace("results", "").strip()
    
    return text

class Android:
    def __init__(self):
        self.controller = customInput(safe_space=(10, 10), click_delay=0.5, region=(102, 104, 493, 929))
        
    def start(self):
        if not self.controller.find("empty screen", grayscale=True):
            print("Did not find empty screen")
            return True
            
        else:
            self.controller.click(object=(200, 200), button="right", back=True, wait=0.5)
            self.controller.swipe((146, 752), (462, 299), back=True)
            time.sleep(1)
            
        if not self.controller.find("empty screen", grayscale=True):
            return True
        return False
        
    
    def get_to_doordash(self):
        self.controller.click(object=three_lines, back=True, wait=0.5)
        
        close_all = self.controller.wait_until("close all", max=5)
        if not close_all:
            self.controller.click(circle, back=True, wait=1)
        else:
            self.controller.click(close_all, back=True, wait=1)
        
        doordash_app = self.controller.wait_until("doordash app", max=5)
        if not doordash_app:
            return False
            
        self.controller.click(doordash_app, wait=5, back=True)
        
        if not self.controller.wait_until("fast food", max=5):
            return False
        return True
        
        
    def random_category(self):
        choices = [x for x in range(23) if x not in [0, 1, 8, 16]]
        choice = random.choice(choices)
        print(choice)
        
        self.controller.press("down", presses=2, interval=0.5)
        self.controller.press("right", presses=choice)
        time.sleep(1)  
        self.controller.press("enter")
        time.sleep(5)
        
    
    def random_restaurant(self):
        # 1: get the number
        text = get_text_screenshot((110, 535, 285, 585), self.controller)
        if text == '':
            print("shit")
        
        #hopefully text is a number
        print(f"{text} results!")
        
        num_results = int(text)
        lower_bound = int(num_results * min_constraint)
        upper_bound = int(num_results * max_constraint)
        
        choice = random.randint(lower_bound, upper_bound)
        print(f"chosen {choice}")
        
        self.controller.press("down", presses=choice+2-5, interval=0.2)
        # 2 extra for starting backwards
        # -5 Because we're going to enter an error handling loop
        
        most_ordered = False
        max_loop = 10
        while not most_ordered and max_loop > 0:
            self.controller.press("down", presses=4, interval=0.2)            
            time.sleep(1)
            self.controller.press("enter")
            time.sleep(5)
                
            
            #now scroll down and see if most ordered is there
            self.controller.swipe((376, 771), (370, 280), duration=1, back=True)
            
            most_ordered = self.controller.wait_until("most ordered", max=3)
            if not most_ordered:
                back = self.controller.find("back")
                if back:
                    self.controller.click(back)
                    continue
                    
            #now get restaurant name
            screenshot = self.controller.screenshot(region=(159, 173, 376, 201))
            restaurant_name = pytesseract.image_to_string(screenshot).strip().replace("...", "").replace("'", "")
            print(restaurant_name)
            for blocked_restaurant in blocked_restaurants:
                if blocked_restaurant.lower() in restaurant_name.lower():
                    back = self.controller.find("back")
                    if back:
                        self.controller.click(back, back=True)
                        most_ordered = False
                        break
                    
            max_loop -= 1
            
        if not most_ordered:
            return False
            
        time.sleep(0.5)
        self.controller.click(most_ordered, back=True, wait=1)
        
        if not self.controller.wait_until("most ordered big", max=5):
            return False
        
        return True
        
        
    def order_food(self):
        self.controller.click(random.choice(most_liked))
        
        required_selection = self.controller.wait_until("required selection", max=2)
        required_selection_2 = self.controller.wait_until("required selection 2", max=2)
        if not required_selection:
            required_selection = required_selection_2
            
        while required_selection:            
            self.controller.click(required_selection, back=True)
            required_tag = self.controller.wait_until("required tag", max=3)

            #determine if plus or circle
            top_left = (required_tag[0], required_tag[1] + required_tag[3])
            circle_region = (top_left[0], top_left[1], 169, 500)
            plus_region = (429, top_left[1], 493, 500)
            
            circles = self.controller.locate_all("circle", circle_region)
            plus = self.controller.locate_all("plus", plus_region)
            
            print(f"Circles: {circles}\nPlus: {plus}")
            non_empty_list = circles if circles else plus
            if not non_empty_list:
                print("Error with finding choices for food")
                return False
            
            self.controller.click(random.choice(non_empty_list), back=True)               
            save_options = self.controller.wait_until("save options", max=1)
            
            if save_options:
                self.controller.click(save_options, back=True, wait=1)
                
            required_selection = self.controller.wait_until("required selection", max=2)
            required_selection_2 = self.controller.wait_until("required selection 2", max=2)
            if not required_selection:
                required_selection = required_selection_2
                
        add_item = self.controller.wait_until("add item", max=1)
        if not add_item:
            print("Error with placing order")
            return False
            
        self.controller.click(add_item, back=True, wait=1)
        
        view_cart = self.controller.wait_until("view cart", max=10)
        if not view_cart:
            print("was able to add item to cart but not view cart")
            return False
            
        self.controller.click(view_cart, back=True, wait=1)
        
        continue_button = self.controller.wait_until("continue", max=10)
        if not continue_button:
            print("not able to continue to check out")
            return False
        self.controller.click(continue_button, back=True, wait=1)
            
        next_button = self.controller.wait_until("next", max=10)
        if next_button:
            self.controller.click(next_button, back=True, wait=1)
        
        place_order_button = self.controller.wait_until("place order", max=10)
        if not place_order_button:
            print("Not able to place order")
            return False
            
        self.controller.click(place_order_button, back=True)
        
        # don't know what happens after this
            
        
                
                
                
                
            
        
        
        
        
                
            
            
            
            
        
        
        
        
        
        
        
            
            
    
        
