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
    local script, err = loadScript(string.format("/SCRIPTS/BADAPPLE/chunk%d.luac", current_chunk), "bx")
    if (script == nil) then
        lcd.drawText(0, 0, string.format("err: %s", err))
        lcd.refresh()
    else
        current_chunk_data = script()
        script = nil
        err = nil
    end
    collectgarbage("collect")
end

local function renderFrame(frame, x_offset, y_offset)
    for _, shape in ipairs(frame) do
        if #shape == 2 then -- pixel
            lcd.drawPoint(
                shape[1] + x_offset, shape[2] + y_offset
            )
        elseif #shape == 3 then -- square
            lcd.drawFilledRectangle(
                shape[1] + x_offset, shape[2] + y_offset,
                shape[1] + x_offset + shape[3], shape[2] + y_offset + shape[3]
            )
        elseif #shape == 4 then -- rect
            lcd.drawFilledRectangle(
                shape[1] + x_offset, shape[2] + y_offset,
                shape[3] - shape[1] + 1, shape[4] - shape[2] + 1
            )
        end
    end
end

local function init()
    lcd.clear()

    local title, subtitle, author, image, video_size = loadScript("/SCRIPTS/BADAPPLE/info.lua")()
    video_x_offset = (128 - video_size[1]) / 2
    video_y_offset = (64 - video_size[2]) / 2
    
    for fname in dir("/SCRIPTS/BADAPPLE") do
        if string.find(fname, ".luac") ~= nil or fname == "info.lua" then
            goto CONTINUE
        end
        lcd.clear()
        lcd.drawText(2, 12, title, MIDSIZE)
        lcd.drawText(40, 24, subtitle, SMLSIZE)
        lcd.drawText(2, 36, string.format("by %s", author))
        lcd.drawText(2, 55, fname, SMLSIZE)
        renderFrame(image, 50, 0)
        lcd.refresh()
        local temp = loadScript(string.format("/SCRIPTS/BADAPPLE/%s", fname), "c")
        temp = nil
        collectgarbage("collect")
        ::CONTINUE::
    end
    title = nil
    subtitle = nil
    image = nil
    collectgarbage("collect")
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
        -- lcd.clear()
        local time = getTime()

        lcd.drawText(0, 0, "FPS:", SMLSIZE)
        local time_delta = getTime() - framerate_time
        -- print("time_delta: ", time_delta)
        lcd.drawText(0, 10, string.format("%0.1f", 1 / time_delta * 100), SMLSIZE)
        lcd.drawText(0, 20, "MEM:", SMLSIZE)
        lcd.drawText(0, 30, string.format("%d", getAvailableMemory()), SMLSIZE)
        lcd.drawText(0, 40, "CHK:", SMLSIZE)
        lcd.drawText(0, 50, string.format("%d", current_chunk), SMLSIZE)
        dynamic_frame_limiter_offset = math.min((10 - time_delta) / 1, -0.1)
        -- print("dynamic_frame_limiter_offset: ", dynamic_frame_limiter_offset)
        framerate_time = getTime()

        renderFrame(frame, video_x_offset, video_y_offset)
        lcd.refresh()
        -- print("frame limiter delay: ", 10 - dynamic_frame_limiter_offset)
        lcd.resetBacklightTimeout()
        while (time + (10 + dynamic_frame_limiter_offset) > getTime()) do end
    end

    loadNextChunk()
    goto RENDER
end

return { run=run, init=init }