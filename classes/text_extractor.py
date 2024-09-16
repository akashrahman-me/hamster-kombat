import pytesseract
from PIL import Image
from utils.get_screenshot import get_screenshot

class TextExtractor:
    def __init__(self, device):
        self.image = None
        self.text_data = None
        self.device = device

    def preprocess_image(self, screenshot):
        self.image = Image.open(screenshot)
        self.image = self.image.convert('L')
        self.image = self.image.point(lambda x: 0 if x < 180 else 255, 'L')

    def extract_text_data(self):
        conf = r'--oem 3'
        self.text_data = pytesseract.image_to_data(self.image, lang="eng", config=conf, output_type=pytesseract.Output.DICT)


    def list_of_words(self, text):
        self.preprocess_image(get_screenshot(self.device))
        self.extract_text_data()

        words = []
        for i, word in enumerate(self.text_data['text']):
            if word in text.split(" "):
                word_item = {
                    "wrd": word,
                    "w": self.text_data['width'][i],
                    "h": self.text_data['height'][i],
                    "x": self.text_data['left'][i],
                    "y": self.text_data['top'][i]
                }
                words.append(word_item)
        return words

    def is_next_word(self, screen_word, last_word):
        word_spacing = 1
        is_next_w = screen_word['x'] - (last_word["x"] + last_word["w"]) in range(0, round(last_word['h'] * word_spacing))
        is_same_y = screen_word['y'] - last_word["y"] in range(-round(last_word['h'] / 2), round(last_word['h'] / 2))
        return is_next_w and is_same_y

    def is_next_line(self, screen_word, last_word):
        line_height = 1.3
        is_next_line = screen_word['y'] - (last_word["y"] + last_word["h"]) in range(0, abs(round(last_word["h"] * line_height)))
        return is_next_line

    def words_to_sentence(self, text):
        screen_words = self.list_of_words(text)
        find_text = text.split()
        sentences = []
        for occ in [entry for entry in screen_words if entry['wrd'] == find_text[0]]:
            sentence = []
            for word in find_text:
                for screen_word in screen_words:
                    if screen_word['wrd'] == word:
                        if not sentence:
                            sentence.append(occ)
                            break
                        elif self.is_next_word(screen_word, sentence[-1]) or self.is_next_line(screen_word, sentence[-1]):
                            sentence.append(screen_word)
                            break
            is_complete = [a['wrd'] for a in sentence] == find_text
            if is_complete:
                sentences.append(sentence)
        return sentences

    def text_to_coordinate(self, text):
        sentences = self.words_to_sentence(text)

        if len(sentences) <= 0:
            return False

        coordinates = []
        for sentence in sentences:
            width = 0
            top = float('inf')
            left = float('inf')
            max_xw = 0
            for word in sentence:
                w = word["w"]
                x = word["x"]
                y = word["y"]
                max_xw = max(x + w, max_xw)
                top = min(y, top)
                left = min(x, left)

            height = (sentence[-1]["y"] - top) + sentence[-1]["h"]
            width = max_xw - left
            coordinates.append((left, top, width, height))
        return coordinates