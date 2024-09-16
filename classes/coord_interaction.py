from pyexpat.errors import messages

from classes.text_extractor import TextExtractor
import subprocess
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw
from utils.remove_duplicates import remove_duplicates
from utils.serialize_data import serialize_data
from utils.get_screenshot import get_screenshot
from plyer import notification


def is_device_connected(device):
    devices = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if device in devices.stdout:
       return True
    return False

class CoordInteraction(TextExtractor):

    def __init__(self, base_path, device):
        super().__init__(device)
        self.base_path = base_path
        self.device = device
        self.max_re_connect = 10

        while not is_device_connected(self.device):
            self.max_re_connect -= 1

            if self.max_re_connect % (self.max_re_connect / 3) == 0:
                notification.notify(
                    title="Fiverr Reminder.",
                    message="Specific device isn't connected to the USB cable."
                )
            if self.max_re_connect <= 0:
                exit()
            time.sleep(10)

    def adb_execute(self, command, shell = True):
        adb_input_command = f'adb {f"-s {self.device} shell " if shell else "" }{command}'

        subprocess.run(adb_input_command, shell=True)

    def adb_swipe(self, x1, y1, x2, y2, duration):
        adb_command = f"adb -s {self.device} shell input swipe {x1} {y1} {x2} {y2} {duration}"
        subprocess.call(adb_command, shell=True)

    def write(self, text, delay = 0.5 ):
        time.sleep(delay)

        def escape_text(input_text):
            special_chars = [' ', '"', "'", "&", "<", ">", "|", '$', '#', '@', '%']
            escaped_text = input_text if input_text != "" else " "

            for char in special_chars:
                escaped_text = escaped_text.replace(char, "\\" + char)

            return escaped_text

        self.adb_execute(f'input text "{escape_text(text)}"')

    def visible_coord(self, text = None, image = None, coord = False):
        is_el = coord if coord else self.is_exist_element(text = text, image = image)
        if not is_el:
            print("The element is not visible")
            return
        x, y, w, h = is_el

        image = Image.open(get_screenshot(self.device))
        outline_color = (255, 100, 100, 255)
        draw = ImageDraw.Draw(image)
        draw.rectangle((x, y, x + w, y + h), outline=outline_color, width=4)
        image.show()

    def get_screen_dimensions(self):
        adb_command = f"adb -s {self.device} shell wm size"
        result = subprocess.check_output(adb_command, shell=True).decode("utf-8")
        lines = result.strip().split("\n")
        
        # Extract width and height from the last line
        last_line = lines[-1]
        width, height = map(int, last_line.split("Physical size: ")[1].split("x"))

        return width, height
    
    def swipe(self, x = 0, y = None , duration=300):
        screen_width, screen_height = self.get_screen_dimensions()
        
        if y is None:
            y = -screen_height / 3

        middle_x = screen_width / 2
        middle_y = screen_height / 2

        # Calculate the start and end points for the swipe
        start_x = middle_x
        start_y = middle_y
        end_x = middle_x + x
        end_y = middle_y + y

        # Perform the swipe using ADB
        self.adb_swipe(start_x, start_y, end_x, end_y, duration)
        print(f"swipe: {start_x}, {start_y}, {end_x}, {end_y}")
        time.sleep((duration + 100) / 1000)

    def element_by_image(self, image):
        screenshot = cv2.imread(get_screenshot(self.device))
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        target_icon = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(screenshot_gray, target_icon, cv2.TM_CCOEFF_NORMED)
        locations = []

        while True:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= 0.97:
                x, y = max_loc
                sy, sx = target_icon.shape
                locations.append((x, y, sx, sy))
                result[y:y+sy, x:x+sx] = -1.0
            else:
                break
        locations = serialize_data(remove_duplicates(locations))

        return locations

    def is_exist_element(self, text=None, image=None, delay=1):
        if not text and not image:
            raise ValueError("Invalid arguments. They should be strings or lists.")

        text = [text] if isinstance(text, str) else text
        image = [image] if isinstance(image, str) else image

        for _ in range(delay):
            if image:
                for img in image:
                    coords = self.element_by_image(f"{self.base_path}{img}")
                    if coords:
                        return coords[0]

            if text:
                for txt in text:
                    coords = self.text_to_coordinate(txt)
                    if coords:
                        return coords[0]

        return False
    
    def awaitfor_element(self, text=None, image=None, timeout=5):
        if not text and not image:
            raise ValueError("Invalid arguments. They should be strings or lists.")

        for _ in range(timeout): 
            if self.is_exist_element(text = text, image = image):
                print (f"Element found: {text if text else image}")
                return True
            print(f"Waiting for element: {text if text else image}")
            time.sleep(timeout)

        return False

    def tap_coord(self, x, y, x_offset = 0, y_offset= 0, double_tap=None):
        command = f"input tap {round(x + x_offset)} {round(y + y_offset)}"
        self.adb_execute(command)
        if double_tap:
            self.adb_execute(command)
            
    @staticmethod
    def print_press_msg(self, text, image):
        print(f"pressed: {image[0] if image else text[0]}")


    def find_coord(self, text, image):
        for i in image if image else text:
            coord = self.is_exist_element(image=i if image else None, text=i if text else None)
            if coord:
                return coord

    def touch(self, text=None, image=None, x_offset=None, y_offset=None, wait=True, double_tap=False):
        
        text = [text] if isinstance(text, str) else text
        image = [image] if isinstance(image, str) else image

        coord = False
        if wait:
            while wait:
                coord = self.find_coord(text, image)
                if coord:
                    break
        else:
            coord = self.find_coord(text, image)

        if coord:
            x, y, w, h = coord
            x_offset = x_offset if x_offset is not None else w / 2
            y_offset = y_offset if y_offset is not None else h / 2
            self.print_press_msg(text, image)
            self.tap_coord(x, y, x_offset, y_offset, double_tap)
            return coord

        return False
    
    def check_screen_state(self):
        """Checks if the Android device screen is on or off using ADB."""
        output = subprocess.check_output(f"adb -s {self.device} shell dumpsys power", shell=True)
        for line in output.decode().splitlines():
            if 'Display Power: state=' in line:
                state = line.split('=')[1].strip()
                return state
        return "OFF"
    

    def press(self, name):
        if name == 'home':
            self.adb_execute("input keyevent 3")

        elif name == 'back':
            self.adb_execute("input keyevent 4")

        elif name == 'recent':
            self.adb_execute("input keyevent 187")

        elif name == 'tab':
            self.adb_execute("input keyevent 61")

        elif name == 'menu':
            self.adb_execute("input keyevent 82")

        elif name == 'search':
            self.adb_execute("input keyevent 84")

        elif name == 'volume_up':
            self.adb_execute("input keyevent 24")

        elif name == 'volume_down':
            self.adb_execute("input keyevent 25")

        elif name == 'volume_mute':
            self.adb_execute("input keyevent 164")

        elif name == 'power_on':
            if self.check_screen_state() == 'OFF':
                print("Screen turn on")
                self.adb_execute("input keyevent 26")
    
        elif name == 'power_off':
            if self.check_screen_state() == 'ON':
                print("Screen turn off")
                self.adb_execute("input keyevent 26")

        elif name == 'paste':
            self.adb_execute('input keyevent 279')
        
        else:
            raise ValueError(f"Invalid button: {name}")

       