import cv2 as cv
import numpy as np
import math
from dataclasses import dataclass
import time

video = cv.VideoCapture("badapple-qx7.mp4")

def areColorsDifferent(first, second):
    if first > second:
        return first - second > 100
    else:
        return second - first > 100

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

# def do_overlap(l1, r1, l2, r2):
#     return l1.x < r2.x and r1.x > l2.x and l1.y > r2.y and l2.y < l2.y

def do_overlap(rect1, rect2):
    return not (rect1.x1 > rect2.x2 or rect1.x2 < rect2.x1 or rect1.y1 > rect2.y2 or rect1.y2 < rect2.y1)
     

with open('badapple.lua', 'w') as lua_file:
    lua_file.write("local video_data = {")

    # Converting video into an int table
    prev_frame = np.zeros((64,84), np.uint8)
    prev_frame[:] = 255

    # for _ in range(0, 0):
    # for _ in range(0, 20):
    for _ in range(0, 120):    
    # for _ in range(0, 240):    
    # for _ in range(0, 500):    
    # while True:
        ret, frame = video.read()
        if not ret: break
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        height, width = frame.shape

        lua_file.write("{")

        changed_pixels = []
        rectangles = []

        for x in range(0, width):
            for y in range(0, height):
                if areColorsDifferent(prev_frame[y, x], frame[y, x]):
                    changed_pixels.append(Point(x, y))
                    # lua_file.write("{")
                    # lua_file.write(f"{y},{x}")
                    # lua_file.write("},")
        

        for pixel in changed_pixels:
            x1 = pixel.x
            y1 = pixel.y
            x2 = 0
            y2 = 0
            
            # go left/right
            for xpixel in changed_pixels:
                if xpixel.y != pixel.y: continue
                if xpixel.x < x1: x1 = xpixel.x
                if xpixel.x > x2: x2 = xpixel.x

            # go top/bottom  
            for ypixel in changed_pixels:
                if ypixel.x != pixel.x: continue
                if ypixel.y < y1: y1 = ypixel.y
                if ypixel.y > y2: y2 = ypixel.y
            print(x1, y1, x2, y2)

            overlap = False

            for rec in rectangles:
                if do_overlap(Rect(x1, y1, x2, y2), rec):
                    print("overlapping")
                    overlap = True
                    break
            if not overlap:
                rectangles.append(Rect(x1, y1, x2 - x1, y2 - y1))
                print(rectangles)
                time.sleep(1)
                lua_file.write("{")
                lua_file.write(f"{x1},{y1},{x2 - x1},{y2 - y1}")
                lua_file.write("},")
        

        prev_frame = frame

        lua_file.write("},")

    lua_file.write("}\n\n")
    
    with open("player.lua", "r") as display_file:
        lua_file.write(display_file.read())

video.release()
cv.destroyAllWindows()
