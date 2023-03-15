from enum import Enum
import cv2 as cv
import numpy as np
import math
import os
import shutil
from dataclasses import dataclass
import sys

video = cv.VideoCapture("badapple-qx7.mp4")
all_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
title = "Bad Apple"
subtitle = "on EdgeTX"
author = "GGorAA"
video_chunk_size_kb = 7 # max size of a chunk in Kb
titlescreen_image_frame = 90 # frame of the video that would be extracted as the titlescreen image

@dataclass
class Point:
    x: int
    y: int

    def __hash__(self):
        return hash(repr(self))

@dataclass
class Rect:
    # x1 y1
    top_left: Point
    # x2 y2
    bottom_right: Point

@dataclass
class Square:
    x: int
    y: int
    size: int

class Direction(Enum):
    RIGHT = 0
    LEFT = 1
    TOP = 2
    BOTTOM = 3

def sizeof(obj): # idk it looks better that way
    return sys.getsizeof(obj)

def write_chunks(video, max_size_kb):
    frame_counter = 0
    chunk_counter = 1
    chunk_data = ""
    while frame_counter < len(video):
        frame = video[frame_counter]
        frame_data = "{"
        for data in frame:
            frame_data += "{"
            frame_data += encode_shape(data)
            frame_data += "},"
        frame_data += "},"
        if sizeof(chunk_data) + sizeof(frame_data) >= max_size_kb * 1000: # write a new chunk
            print(f"Writing chunk {chunk_counter}...")
            with open(f"bundle/SCRIPTS/BADAPPLE/chunk{chunk_counter}.lua", "w") as file:
                file.write("local chunk_data = {")
                file.write(chunk_data)
                file.write("}\nreturn chunk_data")
            chunk_data = "" # clear
            chunk_counter += 1
        else:
            chunk_data += frame_data
            frame_counter += 1

def are_colors_different(first, second):
    if first > second:
        return first - second > 100
    else:
        return second - first > 100

def do_overlap(rect1, rect2):
    return not (rect1.x1 > rect2.x2 or rect1.x2 < rect2.x1 or rect1.y1 > rect2.y2 or rect1.y2 < rect2.y1)

# bro chatgps is a goat, it has literatelly made 
# these three functions from my request and they work
# flawlessly

def find_closest_pixel(pixel: Point, pixel_list):
    closest_distance = float('inf') # Set initial closest distance to infinity
    closest_pixel = None
    
    for other_pixel in pixel_list:
        distance = math.sqrt((pixel.x - other_pixel.x)**2 + (pixel.y - other_pixel.y)**2) # Calculate Euclidean distance between the two pixels
        if distance < closest_distance:
            closest_distance = distance
            closest_pixel = other_pixel
    
    return closest_pixel

def get_pixels_in_rect(top_left, bottom_right):
    pixels = []
    x_min, y_min = top_left.x, top_left.y
    x_max, y_max = bottom_right.x, bottom_right.y

    for x in range(x_min, x_max+1):
        for y in range(y_min, y_max+1):
            pixels.append(Point(x,y))

    return pixels

def get_adjacent_pixels(pixel: Point, whitelist):
    x = pixel.x 
    y = pixel.y
    adjacent_pixels = [Point(x-1, y), Point(x+1, y), Point(x, y-1), 
        Point(x, y+1), Point(x-1, y-1), Point(x+1, y-1), 
        Point(x-1, y+1), Point(x+1, y+1)]
    return [p for p in adjacent_pixels if p in whitelist]

# Renders a supplied frame for usage by the Bad Apple player
def render_frame(frame, is_pixel_whitelisted):
    height, width = frame.shape
    center_pixel = Point(width / 2, height / 2)

    changed_pixels = []

    for x in range(0, width):
        for y in range(0, height):
            if is_pixel_whitelisted(frame[y, x], x, y):
                changed_pixels.append(Point(x, y))

    result = []

    while len(changed_pixels) > 0:
        closest = find_closest_pixel(center_pixel, changed_pixels)

        rect = Rect(closest, closest)
        
        hit_max_right = False
        hit_max_left = False
        hit_max_top = False
        hit_max_bottom = False

        currently_expanding_to = Direction.RIGHT

        while True:
            if hit_max_right and hit_max_left and hit_max_top and hit_max_bottom: # if there is nowhere to expand anymore
                break
            match currently_expanding_to:
                case Direction.RIGHT:
                    if not hit_max_right:
                        top_p = Point(rect.bottom_right.x + 1, rect.top_left.y)
                        bottom_p = Point(rect.bottom_right.x + 1, rect.bottom_right.y)
                        pixels = set(get_pixels_in_rect(top_p, bottom_p))

                        hit_max_right = not pixels.issubset(set(changed_pixels))

                        if not hit_max_right:
                            rect.bottom_right = Point(rect.bottom_right.x + 1, rect.bottom_right.y)
                    currently_expanding_to = Direction.LEFT
                case Direction.LEFT:
                    if not hit_max_left:
                        top_p = Point(rect.top_left.x - 1, rect.top_left.y)
                        bottom_p = Point(rect.top_left.x - 1, rect.bottom_right.y)
                        pixels = set(get_pixels_in_rect(top_p, bottom_p))

                        hit_max_left = not pixels.issubset(set(changed_pixels))

                        if not hit_max_left:
                            rect.top_left = Point(rect.top_left.x - 1, rect.top_left.y)
                    currently_expanding_to = Direction.TOP
                case Direction.TOP:
                    if not hit_max_top:
                        left_p = Point(rect.top_left.x, rect.top_left.y - 1)
                        right_p = Point(rect.bottom_right.x, rect.top_left.y - 1)
                        pixels = set(get_pixels_in_rect(left_p, right_p))

                        hit_max_top = not pixels.issubset(set(changed_pixels))

                        if not hit_max_top:
                            rect.top_left = Point(rect.top_left.x, rect.top_left.y - 1)
                    currently_expanding_to = Direction.BOTTOM
                case Direction.BOTTOM:
                    if not hit_max_bottom:
                        left_p = Point(rect.top_left.x, rect.bottom_right.y + 1)
                        right_p = Point(rect.bottom_right.x, rect.bottom_right.y + 1)
                        pixels = set(get_pixels_in_rect(left_p, right_p))

                        hit_max_bottom = not pixels.issubset(set(changed_pixels))

                        if not hit_max_bottom:
                            rect.bottom_right = Point(rect.bottom_right.x, rect.bottom_right.y + 1)
                    currently_expanding_to = Direction.RIGHT
        result.append(rect)
        pixels = get_pixels_in_rect(rect.top_left, rect.bottom_right)
        changed_pixels = list(set(changed_pixels) - set(pixels))

    # post-process the created data to further reduce it's size
    for i, rect in enumerate(result):
        if rect.top_left.x == rect.bottom_right.x and rect.top_left.y == rect.bottom_right.y: # can be just a pixel
            result[i] = Point(rect.top_left.x, rect.top_left.y)
            continue
        # TODO: Fix square generation
    #    if rect.bottom_right.x - rect.top_left.x == rect.bottom_right.y - rect.top_left.y: # two same sides, can be a square
    #        result[i] = Square(rect.top_left.x, rect.top_left.x, rect.bottom_right.x - rect.top_left.x)

    return result

def encode_shape(data):
    match data:
        case Point(x, y): return f"{x},{y}"
        case Square(x, y, size): return f"{x},{y},{size}"
        case Rect(top_left, bottom_right): return f"{top_left.x},{top_left.y},{bottom_right.x},{bottom_right.y}"

video_data = []

# an empty white frame (white because it's the default color on monochrome LCDs)
prev_frame = np.zeros((64,84), np.uint8)
prev_frame[:] = 255

titlescreen_image = []

# for _ in range(0, 0):
# for _ in range(0, 20):
# for _ in range(0, 120):    
# for _ in range(0, 240):    
# for _ in range(0, 500):    
# for _ in range(0, 700):    
while True:
    ret, frame = video.read()
    if not ret: break
    encoded_frame = []

    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    current_frame = int(video.get(cv.CAP_PROP_POS_FRAMES))
    print(f"Rendering frame {current_frame}/{all_frames} ({(current_frame / all_frames * 100):.2f}%)...")

    if current_frame == titlescreen_image_frame:
        titlescreen_image = render_frame(frame, lambda p, x, y: p < 100)

    encoded_frame = render_frame(frame, lambda p, x, y: are_colors_different(prev_frame[y, x], p))

    prev_frame = frame
    video_data.append(encoded_frame)

try:
    os.mkdir("bundle")
    os.mkdir("bundle/SCRIPTS")
    os.mkdir("bundle/SCRIPTS/TOOLS")
    os.mkdir("bundle/SCRIPTS/BADAPPLE")
    os.mkdir("bundle/SOUNDS")
except OSError as error: pass

write_chunks(video_data, video_chunk_size_kb)

print("Writing info...")

with open(f"bundle/SCRIPTS/BADAPPLE/info.lua", "w") as file:
    file.write(f"local title = \"{title}\"\n")
    file.write(f"local subtitle = \"{subtitle}\"\n")
    file.write(f"local author = \"{author}\"\n")
    file.write("local banner_image = {")
    for data in titlescreen_image:
        file.write("{")
        file.write(encode_shape(data))
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

print("Done!")
