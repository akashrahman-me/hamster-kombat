import re
import pytesseract
from PIL import Image
from utils.get_screenshot import get_screenshot
import time

def extract_text(pattarn):
    time.sleep(1)
    image = Image.open(get_screenshot())

    text = pytesseract.image_to_string(image, lang="eng")
    match = re.findall(pattarn, text)
    result_text = match[0] if len(match) > 0 else ""
    print(f"scaned text: {result_text}")
    return result_text

_mail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
_url = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
_fb_id = r'id[=-](\d+)'