local toolName = "TNS|Bad Apple|TNE"

local function delay(time)
    local currentTime = getTime()
    while (currentTime + time > getTime()) do end
end

local cchunk = { -- current chunk
    index = -1,
    data = nil
}
local video_x_offset = 0
local video_y_offset = 0
local current_frame = 0

local function loadNextChunk()
    cchunk.index = cchunk.index + 1
    cchunk.data = nil
    local script, err = loadScript(string.format("/SCRIPTS/BADAPPLE/chunk%d.luac", cchunk.index), "bx")
    if script == nil then
        local temp = string.gsub(err, "loadScript%(\"/SCRIPTS/BADAPPLE/chunk", "")
        local temp2 = string.gsub(temp, ".luac\", \"bx\"%) error:", "")
        lcd.drawText(0, 0, temp2, SMLSIZE)
        lcd.refresh()
    else
        cchunk.data = script()
        script = nil
        err = nil
    end
    collectgarbage()
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
                shape[1] + 1 + shape[3], shape[2] + 1 + shape[3]
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

    local info = loadScript("/SCRIPTS/BADAPPLE/info.lua")()
    video_x_offset = (128 - info.video_size[1]) / 2
    video_y_offset = (64 - info.video_size[2]) / 2
    
    for i = 0, info.chunk_count do
        lcd.clear()
        lcd.drawText(2, 12, info.title, MIDSIZE)
        lcd.drawText(40, 24, info.subtitle, SMLSIZE)
        lcd.drawText(2, 36, string.format("by %s", info.author))
        lcd.drawText(2, 55, string.format("Chunk %d", i), SMLSIZE)
        renderFrame(info.banner_image, 50, 0)
        lcd.refresh()
        loadScript(string.format("/SCRIPTS/BADAPPLE/chunk%d.lua", i), "c")
        collectgarbage()
    end
    collectgarbage()
end

local function run(event, touchState)
    local dynamic_frame_limiter_offset = 0
    local show_debug_info = event == EVT_ENTER_LONG
    lcd.clear()
    loadNextChunk()
    local sound_start = getTime() - 50
    playFile("/SOUNDS/badapple.wav")

    ::RENDER::

    for _, frame in ipairs(cchunk.data) do
        local time = getTime()
        local time_delta = getTime() - (sound_start + current_frame * 10)
        dynamic_frame_limiter_offset = math.min((10 - time_delta) / 1, -0.1)

        if show_debug_info then
            lcd.drawText(0, 0, "FPS:", SMLSIZE)
            lcd.drawText(0, 8, string.format("%0.1f", 1 / time_delta * 100), SMLSIZE)
            lcd.drawText(0, 20, "MEM:", SMLSIZE)
            lcd.drawText(0, 28, string.format("%d", getAvailableMemory()), SMLSIZE)
            lcd.drawText(0, 40, "CNT:", SMLSIZE)
            lcd.drawText(0, 48, string.format("%d", cchunk.index), SMLSIZE)
            lcd.drawText(108, 0, "FRM:", SMLSIZE)
            lcd.drawText(108, 8, string.format("%d", current_frame), SMLSIZE)
            lcd.drawText(108, 20, "FLO:", SMLSIZE)
            lcd.drawText(108, 28, string.format("%d", dynamic_frame_limiter_offset), SMLSIZE)
            lcd.drawText(108, 40, "TDE:", SMLSIZE)
            lcd.drawText(108, 48, string.format("%d", time_delta), SMLSIZE)
        end

        renderFrame(frame, video_x_offset, video_y_offset)
        lcd.refresh()
        lcd.resetBacklightTimeout()
        current_frame = current_frame + 1
        while (time + (10 + dynamic_frame_limiter_offset) > getTime()) do end
    end

    loadNextChunk()
    goto RENDER
    return 0
end

return { run=run, init=init }