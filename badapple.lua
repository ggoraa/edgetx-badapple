local toolName = "TNS|Bad Apple|TNE"

local function delay(time)
    local currentTime = getTime()
    while (currentTime + time > getTime()) do end
end
local current_chunk = 0
local current_chunk_data = nil
local video_x_offset = 0
local video_y_offset = 0

local function loadNextChunk()
    current_chunk = current_chunk + 1
    current_chunk_data = nil
    local script, err = loadScript(string.format("/SCRIPTS/BADAPPLE/chunk%d.lua", current_chunk))
    if (script == nil) then
        lcd.drawText(0, 0, string.format("chunk err: %s", err))
        lcd.refresh()
    else
        current_chunk_data = script()
    end
    collectgarbage()
end

local function renderFrame(frame, use_offsets)
    use_offsets = use_offsets or true
    for _, sq in ipairs(frame) do
        if use_offsets then
            lcd.drawFilledRectangle(
                sq[1] + video_x_offset, sq[2] + video_y_offset,
                sq[1] + video_x_offset + sq[3], sq[2] + video_y_offset + sq[3]
            )
        else
            lcd.drawFilledRectangle(
                sq[1], sq[2],
                sq[1] + sq[3], sq[2] + sq[3]
            )
        end
    end
end

local function init()
    lcd.clear()

    local title, subtitle, image, video_size = loadScript("/SCRIPTS/BADAPPLE/info.lua")()
    video_x_offset = (128 - video_size[1]) / 2
    video_y_offset = (64 - video_size[2]) / 2
    
    for fname in dir("/SCRIPTS/BADAPPLE") do
        if fname == "info.lua" then goto CONTINUE end
        lcd.clear()
        lcd.drawText(2, 15, title, MIDSIZE)
        lcd.drawText(2, 35, subtitle)
        lcd.drawText(0, 54, fname)
        renderFrame(image, false)
        lcd.refresh()
        loadScript(string.format("/SCRIPTS/BADAPPLE/%s", fname), SMLSIZE)
        collectgarbage()
        ::CONTINUE::
    end
    title = nil
    subtitle = nil
    image = nil
    lcd.clear()
end


local function run(event, touchState)
    local framerate_time = getTime()
    local dynamic_frame_limiter_offset = 0
    -- lcd.clear()
    loadNextChunk()
    playFile("/SOUNDS/badapple.wav")

    ::RENDER::

    for _, frame in ipairs(current_chunk_data) do
        local time = getTime()

        lcd.drawText(0, 0, "FPS:")
        local time_delta = getTime() - framerate_time
        print("time_delta: ", time_delta)
        lcd.drawText(0, 10, string.format("%0.1f", 1 / time_delta * 100))
        dynamic_frame_limiter_offset = math.min((10 - time_delta) / 1, -0.1)
        print("dynamic_frame_limiter_offset: ", dynamic_frame_limiter_offset)
        framerate_time = getTime()

        renderFrame(frame)
        lcd.refresh()
        print("frame limiter delay: ", 10 - dynamic_frame_limiter_offset)
        lcd.resetBacklightTimeout()
        while (time + (10 + dynamic_frame_limiter_offset) > getTime()) do end
    end

    loadNextChunk()
    goto RENDER
end

return { run=run, init=init }