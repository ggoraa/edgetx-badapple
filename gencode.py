import cv2 as cv
import numpy as np
import math

video = cv.VideoCapture("badapple-qx7.mp4")
all_frames = int(video.get(cv.CAP_PROP_FRAME_COUNT))

def pixelToBool(pixel):
    return int(pixel / 255)

def areColorsDifferent(first, second):
    if first > second:
        return first - second > 100
    else:
        return second - first > 100
    # value = math.sqrt(pow(first - second, 2))
    # return value > 200

with open('badapple.lua', 'w') as lua_file:
    lua_file.write("local video_data = {")

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
        lua_file.write("{")

        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        height, width = frame.shape

        current_frame = int(video.get(cv.CAP_PROP_POS_FRAMES))
        print(f"Rendering frame {current_frame}/{all_frames} ({(current_frame / all_frames * 100):.2f}%)...")

        for x in range(0, height):
            for y in range(0, width):
                # if pixelToBool(prev_frame[x, y]) != pixelToBool(frame[x , y]):
                if areColorsDifferent(prev_frame[x, y], frame[x, y]):
                    lua_file.write("{")
                    lua_file.write(f"{x},{y}")
                    lua_file.write("},")
        prev_frame = frame
        lua_file.write("},")

    lua_file.write("}\n\n")
    
    print("Adding player...")
    with open("player.lua", "r") as display_file:
        lua_file.write(display_file.read())

video.release()
cv.destroyAllWindows()

print("Done.")