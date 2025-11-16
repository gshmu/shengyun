#!/bin/bash
# 部署声韵输入法到 Android 设备并测试

set -e

echo "================================"
echo "声韵输入法自动部署脚本 v1.0.1"
echo "================================"
echo ""

# 检查设备连接
if ! adb devices | grep -q "device$"; then
  echo "❌ 错误：未检测到 Android 设备"
  echo "请检查："
  echo "  1. USB 调试是否已启用"
  echo "  2. 设备是否已连接"
  echo "  3. adb devices 是否显示设备"
  exit 1
fi

echo "✅ 检测到 Android 设备"
echo ""

# 1. 强制停止 Trime（清除缓存）

# 2. 清除旧的编译缓存
echo "🗑️  步骤 2/5: 清除编译缓存..."
adb shell rm -rf /sdcard/rime/build/* 2>/dev/null || true
echo "   ✅ 完成"
echo ""

# 3. 推送配置文件
echo "📤 步骤 3/5: 推送配置文件到设备..."

files=(
  "shengyun.schema.yaml"
  "shengyun.trime.yaml"
  "default.custom.yaml"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "   - 推送 $file"
    adb push "$file" /sdcard/rime/ > /dev/null 2>&1
  else
    echo "   ⚠️  警告：文件 $file 不存在"
  fi
done

echo "   ✅ 完成"
echo ""

# 4. 触发重新部署
echo "🔧 步骤 4/5: 触发 RIME 重新部署..."
adb shell am broadcast -a com.osfans.trime.deploy 2>/dev/null || {
  echo "   ⚠️  广播命令失败，请手动部署："
  echo "      打开 Trime → 设置 → 部署 → 重新部署"
}
echo "   ✅ 部署指令已发送"
echo ""

# 5. 检查部署结果
echo "⏳ 步骤 5/5: 等待部署完成（30秒）..."
sleep 30

echo "🔍 检查部署结果..."
if adb shell ls /sdcard/rime/build/shengyun.prism.bin > /dev/null 2>&1; then
  echo "   ✅ 找到 shengyun.prism.bin"
else
  echo "   ⚠️  未找到编译产物，可能需要手动部署"
fi

if adb shell ls /sdcard/rime/build/shengyun.table.bin > /dev/null 2>&1; then
  echo "   ✅ 找到 shengyun.table.bin"
else
  echo "   ⚠️  未找到词库文件"
fi

echo ""
echo "================================"
echo "✅ 部署完成！"
echo "================================"
echo ""
echo "📝 测试步骤："
echo ""
echo "1. 打开任意应用（如备忘录、微信）"
echo "2. 点击输入框，调出键盘"
echo "3. 按 F4 切换到「声韵拼音」方案"
echo "4. 测试以下场景："
echo ""
echo "   ✅ 单字符声母："
echo "      - 点击 'b' → 应自动切换到韵母层"
echo "      - 点击 'a' → 应自动切换回声母层"
echo "      - 选择「吧」上屏"
echo ""
echo "   ✅ 双字符声母："
echo "      - 点击 'z' → 保持在当前层"
echo "      - 点击 'h' → 自动切换到韵母层（zh）"
echo "      - 点击 'ang' → 自动切换回声母层"
echo "      - 选择「张」上屏"
echo ""
echo "   ✅ 复杂韵母："
echo "      - 点击 'l' → 切换到韵母层"
echo "      - 点击 'i' → 韵母继续"
echo "      - 点击 'ang' → 切换回声母层（liang）"
echo "      - 选择「两」上屏"
echo ""
echo "   ✅ j/q/x + u(ü)："
echo "      - 点击 'j' → 切换到韵母层"
echo "      - 点击 'u' → 切换回声母层（实际发ü音）"
echo "      - 选择「居」上屏"
echo ""
echo "   ❌ 无效组合应无候选词："
echo "      - j + ang → 无结果"
echo "      - zh + ia → 无结果"
echo "      - g + i → 无结果"
echo ""
echo "📊 查看实时日志（可选）："
echo "   adb logcat | grep 'rime.trime'"
echo ""
echo "🐛 如遇问题，请检查日志中的错误信息"
echo ""
