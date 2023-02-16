import cv2 as cv
import numpy as np
import math
from dataclasses import dataclass
import time
from enum import Enum
import sys

video = cv.VideoCapture("badapple-qx7.mp4")
all_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
result_file = 'badapple.lua'

if len(sys.argv) > 1:
    result_file = sys.argv[1]

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

@dataclass
class Square:
    x: int
    y: int
    size: int

def areColorsDifferent(first, second):
    if first > second:
        return first - second > 100
    else:
        return second - first > 100

def do_overlap(rect1, rect2):
    return not (rect1.x1 > rect2.x2 or rect1.x2 < rect2.x1 or rect1.y1 > rect2.y2 or rect1.y2 < rect2.y1)

# bro chatgps is a goat, it has literatelly made 
# this function from my request and it's better
# than the stackoverflow variant

def get_adjacent_pixels(pixel: Pixel, allowlist):
    x = pixel.x 
    y = pixel.y
    adjacent_pixels = [Pixel(x-1, y), Pixel(x+1, y), Pixel(x, y-1), 
        Pixel(x, y+1), Pixel(x-1, y-1), Pixel(x+1, y-1), 
        Pixel(x-1, y+1), Pixel(x+1, y+1)]
    return [p for p in adjacent_pixels if p in allowlist]

# Combines supplied pixels into 2x2 squares. Canvas should be divisible by 2
def combine_in_squares(pixels, square_size = 2):
    # pixels_unused = pixels

    squares = []

    for p in pixels:
        if p.x % 2 == 0 and p.y % 2 == 0: # is on the top left of a rect
            adjacent = get_adjacent_pixels(p, pixels)

            pixel_set = {Pixel(p.x + 1, p.y), Pixel(p.x, p.y + 1), Pixel(p.x + 1, p.y + 1)}

            if pixel_set.issubset(adjacent):
                # print("Found pixel that can be made into a square: ", p)
                # squares.append(Rect(p.x, p.y, p.x + 1, p.y + 1))
                squares.append(Square(p.x, p.y, square_size))
                # pixels_unused = list(set(pixels_unused) - set(pixel_set))
    
    # print(pixels_unused)
    # print(squares)

    # for p in pixels_unused:
    #     squares.append(Square(p.x, p.y, square_size / 2))
    
    # print(squares)
    # print(square_size)

    # if len(squares) == 0: return [] # protection against infinite recursion

    # scale down everything
    # new_pixels = []
    # for sq in squares:
    #     new_pixels.append(Pixel(sq.x / 2, sq.y / 2))

    # time.sleep(2)
    
    # new_squares = combine_in_squares(new_pixels, square_size * 2)
    # if len(new_squares) == 0:
    #     return squares
    # else:
    #     return new_squares

    return squares

with open(result_file, 'w') as lua_file:
    lua_file.write("local video_data = {")

    # Converting video into an int table
    prev_frame = np.zeros((64,84), np.uint8)
    prev_frame[:] = 255

    # for _ in range(0, 1):
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

        squares = combine_in_squares(changed_pixels)

        print(squares)

        # TODO: Make converter from Rect to Square for further size reduction

        for sq in squares:
            lua_file.write("{")
            lua_file.write(f"{sq.x},{sq.y},{sq.size}")
            lua_file.write("},")

        prev_frame = frame

        lua_file.write("},")

    lua_file.write("}\n\n")

    print("Adding player...")
    
    with open("player.lua", "r") as display_file:
        lua_file.write(display_file.read())

print("Done.")

video.release()
cv.destroyAllWindows()
