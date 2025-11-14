-- SPDX-FileCopyrightText: 2025 Shengyun IME
-- SPDX-License-Identifier: GPL-3.0-or-later

local kRejected = 0
local kAccepted = 1
local kNoop = 2

local function processor(key, env)
  if key:release() or key:alt() then
    return kNoop
  end

  local ctx = env.engine.context
  local input = ctx.input

  -- 测试：输入b后切换到韵母层
  if input == "b" then
    ctx:set_option("_keyboard_shengyun_finals", true)
  end

  return kNoop
end

local function init(env)
  env.engine.context:set_option("_keyboard_shengyun_initials", true)
end

return { init = init, func = processor }
