local toolName = "TNS|Bad Apple|TNE"

local function delay(time)
    local currentTime = getTime()
    while (currentTime + time > getTime()) do end
end
local chunk_count = 0

local current_chunk = 0
local current_chunk_data = nil

local function loadNextChunk()
    current_chunk = current_chunk + 1
    current_chunk_data = nil
    local script, err = loadScript(string.format("/SCRIPTS/TOOLS/BADAPPLE/chunk%d.lua", current_chunk))
    if (script == nil) then
        lcd.drawText(0, 0, string.format("chunk err: %s", err))
        lcd.refresh()
    else
        current_chunk_data = script()
    end
    collectgarbage()
end

local function init()
    for fname in dir("/SCRIPTS/TOOLS/BADAPPLE") do
        lcd.clear()
        chunk_count = chunk_count + 1
        lcd.drawText(0, 0, string.format("Compiling %s...", fname))
        lcd.drawText(0, 10, string.format("Total chunks: %d", chunk_count))
        lcd.refresh()
        loadScript(string.format("/SCRIPTS/TOOLS/BADAPPLE/%s", fname))
        collectgarbage()
    end
end


local function run(event, touchState)
    local framerate_time = getTime()
    local dynamic_frame_limiter_offset = 0
    -- lcd.clear()
    loadNextChunk()
    playFile("/SOUNDS/badapple.wav")

    ::RENDER::

    for _, frames in ipairs(current_chunk_data) do
        local time = getTime()

        lcd.drawText(0, 0, "FPS:")
        local time_delta = getTime() - framerate_time
        print("time_delta: ", time_delta)
        lcd.drawText(0, 10, string.format("%0.1f", 1 / time_delta * 100))
        dynamic_frame_limiter_offset = math.min((10 - time_delta) / 1, -0.1)
        print("dynamic_frame_limiter_offset: ", dynamic_frame_limiter_offset)
        framerate_time = getTime()

        for _, coords in ipairs(frames) do
            lcd.drawPoint(coords[2] + 22, coords[1])
        end
        lcd.refresh()
        print("frame limiter delay: ", 10 - dynamic_frame_limiter_offset)
        while (time + (10 + dynamic_frame_limiter_offset) > getTime()) do end
    end

    loadNextChunk()
    goto RENDER
end

return { run=run, init=init }