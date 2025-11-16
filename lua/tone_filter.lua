-- tone_filter.lua
-- 声调过滤器：支持通过数字1234过滤带声调的候选词
-- 用法：输入拼音后，按1234选择对应声调的候选词

-- 从汉字的拼音中提取声调
local function get_tone_from_pinyin(pinyin)
    if not pinyin then return nil end

    -- 一声：ā ē ī ō ū ǖ ń ň ǹ
    if pinyin:find("[āēīōūǖńǸĀĒĪŌŪǕŃŇǸ]") then
        return "1"
    end

    -- 二声：á é í ó ú ǘ ń
    if pinyin:find("[áéíóúǘńÁÉÍÓÚǗŃ]") then
        return "2"
    end

    -- 三声：ǎ ě ǐ ǒ ǔ ǚ ň
    if pinyin:find("[ǎěǐǒǔǚňǍĚǏǑǓǙŇ]") then
        return "3"
    end

    -- 四声：à è ì ò ù ǜ ǹ
    if pinyin:find("[àèìòùǜǹÀÈÌÒÙǛǸ]") then
        return "4"
    end

    -- 轻声或无法识别
    return nil
end

local function tone_filter(input, env)
    local context = env.engine.context
    local input_code = context.input

    -- 检查输入码末尾是否有声调标记（1234）
    local tone_mark = input_code:match("(%d)$")

    if not tone_mark or tonumber(tone_mark) < 1 or tonumber(tone_mark) > 4 then
        -- 没有声调标记，直接输出所有候选词
        for cand in input:iter() do
            yield(cand)
        end
        return
    end

    -- 有声调标记，过滤候选词
    local has_output = false
    for cand in input:iter() do
        local comment = cand.comment or ""
        local preedit = cand.preedit or ""

        -- 从注释或预编辑文本中检测声调
        local tone = get_tone_from_pinyin(comment) or get_tone_from_pinyin(preedit)

        if tone == tone_mark then
            yield(cand)
            has_output = true
        end
    end

    -- 如果没有匹配的候选词，输出所有候选词（避免空白）
    if not has_output then
        for cand in input:iter() do
            yield(cand)
        end
    end
end

return tone_filter
