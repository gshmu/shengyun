-- tone_filter.lua
-- 声调过滤器：支持通过数字1234过滤带声调的候选词
-- 用法：输入拼音后，按1234选择对应声调的候选词

local function get_tone(text)
    -- 从汉字中提取声调信息
    -- 简化版：通过拼音注释获取声调
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

    -- 移除声调标记，获取纯拼音
    local pure_pinyin = input_code:sub(1, -2)

    -- 过滤候选词：只显示匹配声调的候选词
    for cand in input:iter() do
        -- 获取候选词的拼音注释
        local comment = cand.comment

        if comment then
            -- 检查拼音中的声调标记
            -- 一声：ā ō ē ī ū ǖ
            -- 二声：á ó é í ú ǘ
            -- 三声：ǎ ǒ ě ǐ ǔ ǚ
            -- 四声：à ò è ì ù ǜ
            local tone_chars = {
                ["1"] = "[āōēīūǖĀŌĒĪŪǕ]",
                ["2"] = "[áóéíúǘÁÓÉÍÚǗ]",
                ["3"] = "[ǎǒěǐǔǚǍǑĚǏǓǙ]",
                ["4"] = "[àòèìùǜÀÒÈÌÙǛ]"
            }

            if comment:find(tone_chars[tone_mark]) then
                yield(cand)
            end
        else
            -- 没有注释的候选词直接输出
            yield(cand)
        end
    end
end

return tone_filter
