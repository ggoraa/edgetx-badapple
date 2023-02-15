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
        -- for _, coords in ipairs(frames) do
        --     lcd.drawPoint(coords[1] + 22, coords[2])
        -- end
        for _, coords in ipairs(frames) do
            lcd.drawFilledRectangle(coords[2] + 22, coords[1], coords[4] + 22, coords[3])
        end
        -- print(i)
        lcd.drawText(0, 0, string.format("%d", i))
        lcd.refresh()
        while (time + 10 > getTime()) do end
    end
    return 0
end

return { run=run, init=init }