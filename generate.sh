#!/usr/bin/env zsh

if [[ ! -f "badapple-qx7.mp4" ]]; then
    echo "Converting Bad Apple video to Q X7 resolution..."
    ffmpeg -i badapple.mp4 -filter:v scale=84:64 -c:a copy badapple-qx7-temp1.mp4
    ffmpeg -i badapple-qx7-temp1.mp4 -r 10 -y badapple-qx7-temp2.mp4
    ffmpeg -i badapple-qx7-temp2.mp4 -f lavfi -i color=gray:s=84x64 -f lavfi -i color=black:s=84x64 -f lavfi -i color=white:s=84x64 -filter_complex threshold badapple-qx7.mp4
    rm badapple-qx7-temp1.mp4 badapple-qx7-temp2.mp4
else 
    echo "Video already converted, skipping..."
fi

if [[ ! -f "badapple-qx7.wav" ]]; then
    echo "Extracting audio..."
    ffmpeg -i badapple-qx7.mp4 -q:a 0 -map a badapple-qx7-temp.mp3
    ffmpeg -i badapple-qx7-temp.mp3 -ar 8000 -map_channel 0.0.0 -c:v copy badapple-qx7.wav
    rm badapple-qx7-temp.mp3
else 
    echo "Audio already extracted, skipping..."
fi

echo "Running .lua generator..."
rm -rf bundle
mkdir bundle
mkdir bundle/SCRIPTS
mkdir bundle/SCRIPTS/TOOLS
mkdir bundle/SCRIPTS/BADAPPLE
mkdir bundle/SOUNDS
cargo run

echo "Finishing bundle..."
cp badapple-qx7.wav bundle/SOUNDS/badapple.wav
cp badapple.lua bundle/SCRIPTS/TOOLS/badapple.lua

# if [[ ! -d "lua" ]]; then
#     echo "Downloading Lua 5.2.2..."
#     curl -R -O "https://www.lua.org/ftp/lua-5.2.2.tar.gz"
#     tar zxf lua-5.2.2.tar.gz
#     rm lua-5.2.2.tar.gz
#     echo "Building Lua..."
#     mv lua-5.2.2 lua
#     cd lua
#     make macosx local
#     cd ..
# fi

# echo "Precompiling chunks..."
# for FILE in bundle/SCRIPTS/BADAPPLE/* ; do
#     ./lua/install/bin/luac -s -o ${FILE}c $FILE
#     rm $FILE
# done;
