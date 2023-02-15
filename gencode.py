import cv2 as cv
import numpy as np
import math
from dataclasses import dataclass
import time
from enum import Enum

video = cv.VideoCapture("badapple-qx7.mp4")
all_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))

@dataclass
class Pixel:
    x: int
    y: int

    def __hash__(self):
        return hash(repr(self))

@dataclass
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

def areColorsDifferent(first, second):
    if first > second:
        return first - second > 100
    else:
        return second - first > 100

# thank you https://stackoverflow.com/questions/62980280/finding-neighboring-pixels-python

def candidate_neighbors(pixel: Pixel):
    return ((pixel.x-1, pixel.y-1), (pixel.x-1, pixel.y), (pixel.x-1, pixel.y+1), (pixel.x, pixel.y-1), 
            (pixel.x, pixel.y+1), (pixel.x+1, pixel.y-1), (pixel.x+1, pixel.y), (pixel.x+1, pixel.y+1))

def neighboring_pixels(pixels):
    remain = set(pixels)
    while len(remain) > 0:
        visit = [remain.pop()]
        group = []
        while len(visit) > 0:
            pixel = visit.pop()
            group.append(pixel)
            for nb in candidate_neighbors(pixel):
                if nb in remain:
                    remain.remove(nb)
                    visit.append(nb)
        yield tuple(group)

# pixels = (Pixel(22, 23), Pixel(22, 24), Pixel(21, 23), Pixel(1, 5), Pixel(2, 6), Pixel(21, 22), Pixel(3, 5))

# print(tuple(neighboring_groups(pixels)))

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

        current_frame = int(video.get(cv.CAP_PROP_POS_FRAMES))
        print(f"Rendering frame {current_frame}/{all_frames} ({(current_frame / all_frames * 100):.2f}%)...")

        lua_file.write("{")

        changed_pixels = []
        rectangles = []

        for x in range(0, width):
            for y in range(0, height):
                if areColorsDifferent(prev_frame[y, x], frame[y, x]):
                    changed_pixels.append(Pixel(x, y))

        while len(changed_pixels) > 0: # search for squares that fully cover changed pixels
            for pixel in changed_pixels: 
                adjacent = neighboring_pixels(pixel)

        # for pixel in changed_pixels:
        #     x1 = pixel.x
        #     y1 = pixel.y
        #     x2 = 0
        #     y2 = 0
            
        #     # go left/right
        #     for xpixel in changed_pixels:
        #         if xpixel.y != pixel.y: continue
        #         if xpixel.x < x1: x1 = xpixel.x
        #         if xpixel.x > x2: x2 = xpixel.x

        #     # go top/bottom  
        #     for ypixel in changed_pixels:
        #         if ypixel.x != pixel.x: continue
        #         if ypixel.y < y1: y1 = ypixel.y
        #         if ypixel.y > y2: y2 = ypixel.y
        #     # print(x1, y1, x2, y2)

        #     overlap = False

        #     for rec in rectangles:
        #         if do_overlap(Rect(x1, y1, x2, y2), rec):
        #             # print("overlapping")
        #             overlap = True
        #             break
        #     if not overlap:
        #         rectangles.append(Rect(x1, y1, x2 - x1, y2 - y1))
        #         # print(rectangles)
        #         # time.sleep(1)
        #         lua_file.write("{")
        #         lua_file.write(f"{x1},{y1},{x2 - x1},{y2 - y1}")
        #         lua_file.write("},")
        

        prev_frame = frame

        lua_file.write("},")

    lua_file.write("}\n\n")

    print("Adding player...")
    
    with open("player.lua", "r") as display_file:
        lua_file.write(display_file.read())

print("Done.")

video.release()
cv.destroyAllWindows()
