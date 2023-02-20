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
subtitle = "on EdgeTX"
author = "GGorAA"
frame_chunk_size = 20 # frames per chunk
titlescreen_image_frame = 90 # frame of the video that would be extracted as the titlescreen image

@dataclass
class Pixel:
    x: int
    y: int

    def __hash__(self):
        return hash(repr(self))

@dataclass
class Rect:
    # x1 y1
    top_left: Pixel
    # x2 y2
    bottom_right: Pixel

@dataclass
class Square:
    x: int
    y: int
    size: int

# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def are_colors_different(first, second):
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

# Renders a supplied frame for usage by the Bad Apple player
def render_frame(frame, is_pixel_whitelisted):
    changed_pixels = []
    for x in range(0, width):
        for y in range(0, height):
            if is_pixel_whitelisted(frame[y, x], x, y):
                changed_pixels.append(Pixel(x, y))

    return []


video_data = []

# an empty white frame (white because it's the default color on monochrome LCDs)
prev_frame = np.zeros((64,84), np.uint8)
prev_frame[:] = 255

titlescreen_image = []

# for _ in range(0, 0):
# for _ in range(0, 20):
for _ in range(0, 120):    
# for _ in range(0, 240):    
# for _ in range(0, 500):    
# while True:
    ret, frame = video.read()
    if not ret: break
    encoded_frame = []

    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    height, width = frame.shape

    current_frame = int(video.get(cv.CAP_PROP_POS_FRAMES))
    print(f"Rendering frame {current_frame}/{all_frames} ({(current_frame / all_frames * 100):.2f}%)")

    if current_frame == titlescreen_image_frame:
        for x in range(0, width):
            for y in range(0, height):
                if frame[y, x] < 100:
                    titlescreen_image.append(Pixel(x, y))
    # titlescreen_image = render_frame(frame, lambda p, x, y: p < 100)

    encoded_frame = render_frame(frame, lambda p, x, y: are_colors_different(prev_frame[y, x], p))

    prev_frame = frame
    video_data.append(encoded_frame)

chunked_video_data = divide_chunks(video_data, frame_chunk_size)

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
            for data in frame:
                file.write("{")
                match data:
                    case Pixel(x, y): file.write(f"{x},{y}")
                    case Square(x, y, size): file.write(f"{x},{y},{size}")
                    case Rect(top_left, bottom_right): file.write(f"{top_left.x},{top_left.y},{bottom_right.x},{bottom_right.y}")
                    case default: pass # should never get here
                file.write("},")
            file.write("},")
        file.write("}\nreturn chunk_data")

with open(f"bundle/SCRIPTS/BADAPPLE/info.lua", "w") as file:
    file.write(f"local title = \"{title}\"\n")
    file.write(f"local subtitle = \"{subtitle}\"\n")
    file.write(f"local author = \"{author}\"\n")
    file.write("local banner_image = {")
    for p in titlescreen_image:
        file.write("{")
        file.write(f"{p.x},{p.y}")
        # file.write(f"{sq.x},{sq.y},{sq.size}")
        file.write("},")
    file.write("}\n")
    width = video.get(cv.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv.CAP_PROP_FRAME_HEIGHT)
    file.write("local video_size = {")
    file.write(f"{width:.0f},{height:.0f}")
    file.write("}\n")
    file.write("return title, subtitle, author, banner_image, video_size")


shutil.copy2("badapple.lua", "bundle/SCRIPTS/TOOLS")
shutil.copy2("badapple-qx7.wav", "bundle/SOUNDS/badapple.wav")

video.release()
cv.destroyAllWindows()

print("Done.")