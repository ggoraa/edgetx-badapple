local function delay(time)
    local currentTime = getTime()
    while (currentTime + time > getTime()) do end
end

local function init()
    lcd.clear()
    playFile("/SOUNDS/badapple.wav")
end

local function run(event, touchState)
    lcd.clear()
    for i, frames in ipairs(video_data) do
        local time = getTime()
        for _, coords in ipairs(frames) do
            -- print(string.format("Rectangle - x1: %d, x2: %d, y1: %d, y2: %d", coords[2], coords[1], coords[4], coords[3]))
            lcd.drawFilledRectangle(coords[2], coords[1], coords[4], coords[3])
        end
        print("frame: ", i)
        -- lcd.drawText(0, 0, string.format("%d", i))
        lcd.refresh()
        while (time + 10 > getTime()) do end
    end
    return 0
end

return { run=run, init=init }