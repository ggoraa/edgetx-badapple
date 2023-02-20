import cv2 as cv
import numpy as np
import math
import os
import shutil
from dataclasses import dataclass
import time

video = cv.VideoCapture("badapple-qx7.mp4")
all_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
title = "Bad Apple"
author = "GGorAA"
frame_chunk_size = 20 # frames per chunk
titlescreen_image_frame = 90 # frame of the video that would be extracted as the titlescreen image

def areColorsDifferent(first, second):
    if first > second:
        return first - second > 100
    else:
        return second - first > 100
    # value = math.sqrt(pow(first - second, 2))
    # return value > 200

# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

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

def get_adjacent_pixels(pixel: Pixel, whitelist):
    x = pixel.x 
    y = pixel.y
    adjacent_pixels = [Pixel(x-1, y), Pixel(x+1, y), Pixel(x, y-1), 
        Pixel(x, y+1), Pixel(x-1, y-1), Pixel(x+1, y-1), 
        Pixel(x-1, y+1), Pixel(x+1, y+1)]
    return [p for p in adjacent_pixels if p in whitelist]

# High level function over combine_in_squares.
# def combine_in_squares_hl(pixels):
#     squares = combine_in_squares()

# Combines supplied pixels into 2x2 squares. Canvas should be divisible by 2
def combine_in_squares(pixels, unused = None, square_size = 2):
    squares = []

    unused_pixels = pixels if unused is None else unused

    for p in pixels:
        if p.x % 2 == 0 and p.y % 2 == 0: # is on the top left of a rect
            adjacent = get_adjacent_pixels(p, pixels)

            pixel_set = {Pixel(p.x + 1, p.y), Pixel(p.x, p.y + 1), Pixel(p.x + 1, p.y + 1)}

            if pixel_set.issubset(adjacent):
                # print("Found pixel that can be made into a square: ", p)
                squares.append(Square(p.x, p.y, square_size))
                pixel_set.add(p)
                unused_pixels = list(set(unused_pixels) - pixel_set)

    # print(squares)
    # print(unused_pixels)
    # print(unused)

    if len(squares) == 0: return [] # protection against infinite recursion

    # scale down everything
    new_pixels = []
    for sq in squares:
        new_pixels.append(Pixel(sq.x / 2, sq.y / 2))

    new_squares = combine_in_squares(new_pixels, unused_pixels, square_size * 2)
    if len(new_squares) == 0:
        return squares
    else:
        return new_squares

video_data = []

# an empty white frame (white because it's the default color on monochrome LCDs)
prev_frame = np.zeros((64,84), np.uint8)
prev_frame[:] = 255

titlescreen_image = None

# for _ in range(0, 0):
# for _ in range(0, 20):
# for _ in range(0, 120):    
# for _ in range(0, 240):    
# for _ in range(0, 500):    
while True:
    ret, frame = video.read()
    if not ret: break
    encoded_frame = []

    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    height, width = frame.shape

    current_frame = int(video.get(cv.CAP_PROP_POS_FRAMES))
    print(f"Rendering frame {current_frame}/{all_frames} ({(current_frame / all_frames * 100):.2f}%)")

    if current_frame == titlescreen_image_frame:
        titlescreen_image = frame

    changed_pixels = []
    for x in range(0, width):
        for y in range(0, height):
            if areColorsDifferent(prev_frame[y, x], frame[y, x]):
                changed_pixels.append(Pixel(x, y))

    encoded_frame = combine_in_squares(changed_pixels)

    prev_frame = frame
    video_data.append(encoded_frame)

chunked_video_data = divide_chunks(video_data, frame_chunk_size)
titlescreen_image_data = []

# TODO: Optimise titlescreen image the same way any other frame is optimised
# if titlescreen_image is not None:
#     height, width = titlescreen_image.shape
#     for x in range(0, width):
#         for y in range(0, height):
#             if titlescreen_image[y, x] < 100:
#                 titlescreen_image_data.append(Pixel(x, y))

try:
    os.mkdir("bundle")
    os.mkdir("bundle/SCRIPTS")
    os.mkdir("bundle/SCRIPTS/TOOLS")
    os.mkdir("bundle/SCRIPTS/BADAPPLE")
    os.mkdir("bundle/SOUNDS")
except OSError as error: pass

for i, chunk in enumerate(chunked_video_data):
    with open(f"bundle/SCRIPTS/BADAPPLE/chunk{i + 1}.lua", "w") as file:
        print(f"Writing chunk {i + 1}")
        file.write("local chunk_data = {")
        for frame in chunk:
            file.write("{")
            for sq in frame:
                file.write("{")
                file.write(f"{sq.x},{sq.y},{sq.size}")
                file.write("},")
            file.write("},")
        file.write("}\nreturn chunk_data")

with open(f"bundle/SCRIPTS/BADAPPLE/info.lua", "w") as file:
    file.write(f"local titlescreen_title = \"{title}\"\n")
    file.write(f"local titlescreen_subtitle = \"by {author}\"\n")
    file.write("local titlescreen_image = {")
    for p in titlescreen_image_data:
        file.write("{")
        file.write(f"{p.x},{p.y}")
        file.write("},")
    file.write("}\n")
    width = video.get(cv.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv.CAP_PROP_FRAME_HEIGHT)
    file.write("local video_size = {")
    file.write(f"{width:.0f},{height:.0f}")
    file.write("}\n")
    file.write("return titlescreen_title, titlescreen_subtitle, titlescreen_image, video_size")


shutil.copy2("badapple.lua", "bundle/SCRIPTS/TOOLS")
shutil.copy2("badapple-qx7.wav", "bundle/SOUNDS/badapple.wav")

video.release()
cv.destroyAllWindows()

print("Done.")