import numpy as np
from PIL import ImageGrab, Image
import cv2
import time
from multiprocessing import Process
import pytesseract


def process_image(img):
    # matrix = (0, 0, 1, 0,
    #           0, 0, 1, 0,
    #           0, 0, 1, 0)
    # R, G, B = img.convert("RGB", matrix).split()
    R, G, B = img.convert("RGB").split()
    r = R.load()
    g = G.load()
    b = B.load()
    w, h = img.size
    threshold = 170
    threshold_two = 10
    for i in range(w):
        for j in range(h):
            if r[i, j] < threshold or g[i, j] < threshold or b[i, j] < threshold:
                r[i, j] = 0
            if abs(r[i, j] - g[i, j]) > threshold_two or abs(g[i, j] - b[i, j]) > threshold_two or abs(r[i, j] - b[i, j]) > threshold_two:
                r[i, j] = 0
            r[i, j] = 255 - r[i, j]
    img = Image.merge("RGB", (R, R, R))
    return img


def main():
    process = Process()
    while True:
        # in game
        # x = 842
        # y = 1026
        # offx = 100
        # offy = 22
        ####
        x = 830
        y = 1025
        offx = 150
        offy = 50
        ####
        # dev
        # x = 400
        # y = 400
        # offx = 87
        # offy = 20
        img = ImageGrab.grab(bbox=(x, y, x + offx, y + offy))
        img = process_image(img)
        img = np.array(img)
        cv2.imshow("window", img)
        time.sleep(0.025)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


main()
