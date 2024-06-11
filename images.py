DC = "default"

images = {  
    "empty screen": 0.8,
    "required selection": 0.75,
    "required selection 2": 0.75
    #"circle": 0.8,
    #"plus": 0.8
}
"""
Ex:
    "purchase_search_x": DC,
    "receipt_detail_page": DC,
    "receipt_details_link": 0.8,    
    "search_your_purchases": DC,
"""

def getConfidence(image):
    try:
        return images[image]
    
    except KeyError:
        return DC
    
