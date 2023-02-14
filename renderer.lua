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
        -- lcd.clear()
        local time = getTime()
        for _, coords in ipairs(frames) do
            -- print(coords[1], coords[2], coords)
            lcd.drawPoint(coords[2] + 22, coords[1])
        end
        -- print(i)
        lcd.refresh()
        while (time + 10 > getTime()) do end
    end
    return 0
end

return { run=run, init=init }