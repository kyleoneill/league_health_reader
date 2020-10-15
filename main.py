import numpy as np
from PIL import ImageGrab, Image, ImageFilter
import cv2
import time
from multiprocessing import Process
import pytesseract
import requests
from dotenv import load_dotenv
import os
load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

server_address = os.getenv("ADDRESS")
server_port = os.getenv("PORT")


def change_color_request(rgb):
    (red, green, blue) = rgb
    res = requests.post(url=f"http://{server_address}:{server_port}/set_color?red={red}&green={green}&blue={blue}")


def handle_health_change(percent_health):
    green = round(255 * percent_health)
    red = 255 - green
    change_color_request((red, green, 0))


def ocr_image(img):
    raw_img = pytesseract.image_to_string(img, config="--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789/")
    # health = pytesseract.image_to_string(img, lang="symbols", config="--psm 6")
    # above line is for a custom data set where the lang is currently set to "symbols.traineddata"
    # in C:\Program Files\Tesseract-OCR\tessdata
    try:
        split = raw_img.split('\n')
        health = split[0].split('/')
        mana = split[1].split('/')
        percent_health = (int(health[0])/int(health[1]))
        percent_mana = (int(mana[0]) / int(mana[1]))
        print(f"Health: {health[0]}/{health[1]}: {round(percent_health * 100)}%", end=" ")
        print(f"Mana: {mana[0]}/{mana[1]}: {round(percent_mana * 100)}%", end='\r')
        handle_health_change(percent_health)
        time.sleep(0.5)
    except:
        print(raw_img, end='\r')


def process_image(img):
    # Resize image to 3x recorded size, tesseract just does better with a larger image
    w, h = img.size
    img = img.resize((w * 3, h * 3))

    # Split out R G B channels
    # Then converts red channel to black and white
    R, G, B = img.convert("RGB").split()
    r = R.load()
    g = G.load()
    b = B.load()
    w, h = img.size
    threshold = 170
    threshold_two = 10
    for i in range(w):
        for j in range(h):
            # if the pixel is too dark, it's background and is set to white
            if r[i, j] < threshold or g[i, j] < threshold or b[i, j] < threshold:
                r[i, j] = 255
            # if the pixel is too colorful (channels aren't balanced, not grayscale), then it's background and white
            elif abs(r[i, j] - g[i, j]) > threshold_two or abs(g[i, j] - b[i, j]) > threshold_two or abs(r[i, j] - b[i, j]) > threshold_two:
                r[i, j] = 255
            # otherwise pixel is foreground and black
            else:
                r[i, j] = 0
    # Turn red channel back into the image
    # Blue/Green aren't used because mana is blue and health is green
    img = Image.merge("RGB", (R, R, R))

    # Blur the image, tesseract just does better with a blurred image
    img = img.filter(ImageFilter.GaussianBlur(1))

    return img


def main():
    process = Process()
    while True:
        x = 830
        y = 1028
        offx = 150
        # offy = 20  # No mana
        offy = 40  # Mana included
        img = ImageGrab.grab(bbox=(x, y, x + offx, y + offy))
        img = process_image(img)
        img = np.array(img)
        cv2.imshow("window", img)
        ocr_image(img)
        time.sleep(0.025)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


main()
