local function delay(time)
    local currentTime = getTime()
    while (currentTime + time > getTime()) do end
end

local function run(event, touchState)
    lcd.clear()
    local framerate_time = getTime()
    local dynamic_frame_limiter_offset = 0
    playFile("/SOUNDS/badapple.wav")

    for i, frames in ipairs(video_data) do
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
    return 0
end

return { run=run }