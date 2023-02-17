import cv2 as cv
import numpy as np
import math
import os
import shutil
from dataclasses import dataclass
import time

video = cv.VideoCapture("badapple-qx7.mp4")
all_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))
frame_chunk_size = 5 # frames per chunk

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
    print(squares)

    # for p in pixels_unused:
    #     squares.append(Square(p.x, p.y, square_size / 2))
    
    # print(squares)
    # print(square_size)

    # if len(squares) == 0: return [] # protection against infinite recursion

    # scale down everything
    new_pixels = []
    for sq in squares:
        new_pixels.append(Pixel(sq.x / 2, sq.y / 2))

    time.sleep(2)
    
    new_squares = combine_in_squares(new_pixels, square_size * 2)
    if len(new_squares) == 0:
        return squares
    else:
        return new_squares

video_data = []

# with open('badapple.lua', 'w') as lua_file:
# lua_file.write("local video_data = {")

# Converting video into an int table
prev_frame = np.zeros((64,128,1), np.uint8)
prev_frame[:] = 255

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

    for x in range(0, height):
        for y in range(0, width):
            if areColorsDifferent(prev_frame[x, y], frame[x, y]):
                encoded_frame.append(Pixel(x, y))
    
    squares = combine_in_squares(encoded_frame)

    print(squares)

    prev_frame = frame
    video_data.append(encoded_frame)

chunked_video_data = divide_chunks(video_data, frame_chunk_size)

try: 
    os.mkdir("bundle")
    os.mkdir("bundle/SCRIPTS")
    os.mkdir("bundle/SCRIPTS/TOOLS")
    os.mkdir("bundle/SCRIPTS/TOOLS/BADAPPLE")
except OSError as error: pass

for i, chunk in enumerate(chunked_video_data):
    with open(f"bundle/SCRIPTS/TOOLS/BADAPPLE/chunk{i + 1}.lua", "w") as file:
        print(f"Writing chunk {i + 1}")
        file.write("local chunk_data = {")
        for frame in chunk:
            file.write("{")
            for p in frame:
                file.write("{")
                file.write(f"{p.x},{p.y}")
                file.write("},")
            file.write("},")
        file.write("}\nreturn chunk_data")

shutil.copy2("badapple.lua", "bundle/SCRIPTS/TOOLS")

video.release()
cv.destroyAllWindows()

print("Done.")