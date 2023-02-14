#!/usr/bin/env zsh

if [[ ! -f "badapple-qx7.mp4" ]]; then
    echo "Converting Bad Apple video to Q X7 resolution..."
    ffmpeg -i badapple.mp4 -filter:v scale="trunc(oh*a/2)*2:64" -c:a copy badapple-qx7-temp1.mp4
    ffmpeg -i badapple-qx7-temp1.mp4 -filter:v fps=10 -c:a copy badapple-qx7-temp2.mp4
    ffmpeg -i badapple-qx7-temp2.mp4 -f lavfi -i color=gray:s=84x64 -f lavfi -i color=black:s=84x64 -f lavfi -i color=white:s=84x64 -filter_complex threshold badapple-qx7.mp4
    rm badapple-qx7-temp1.mp4 badapple-qx7-temp2.mp4
else 
    echo "Video already converted, skipping..."
fi

echo "Running .lua generator..."
rm badapple.lua
python3 gencode.py