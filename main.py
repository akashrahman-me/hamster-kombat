from classes.coord_interaction import CoordInteraction
resources = "resources/hamster/"
import time
import random

device = CoordInteraction(
   base_path = resources,
   device = "37e4014c"
)

def tab_press():
   device.tap_coord(random.randint(50, 700), random.randint(730, 1250))
   device.tap_coord(random.randint(50, 700), random.randint(730, 1250))
   device.tap_coord(random.randint(50, 700), random.randint(730, 1250))

print("Start successful")

limit = 1
while True:
   limit += 1
   tab_press()
   time.sleep(random.randint(3, 4))

   if limit % random.randint(20, 50) == 0:
      time.sleep(random.randint(5, 15))
      tab_press()
      tab_press()
      tab_press()
