from classes.coord_interaction import CoordInteraction

interaction = CoordInteraction() 

def wait_element(text = None, image = None, second = 20):
    count = 0
    while True:
        print(f"wait for: {image}")
        el = interaction.is_exist_element(text, image)
        if el or count >= second:
            if el:
                return True
            else:
                return False
        count += 1
