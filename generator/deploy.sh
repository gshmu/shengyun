#!/bin/bash
# 声韵输入法：一键部署（生成→打包→推送）
# 使用说明：./deploy.sh
# 功能：根据 pinyin.tsv + finals_all.csv 生成键盘配置，打包并推送到手机

set -e
cd "$(dirname "$0")"

DATE=$(date +%Y%m%d-%H%M%S)
ZIP_NAME="shengyun-${DATE}.zip"

echo "======================================="
echo "声韵输入法 - 一键部署"
echo "======================================="
echo "数据源：pinyin.tsv + finals_all.csv"
echo "生成器：tools/gen_keyboards.py"

# 1. 生成配置
echo ""
echo "📝 步骤 1/4: 生成配置..."
python3 tools/gen_keyboards.py
echo "✅ 配置生成完成"

# 2. 打包 zip
echo ""
echo "📦 步骤 2/4: 打包 release..."
rm -f ../*.zip 2>/dev/null || true
(cd ../rime && zip -q -r "../$ZIP_NAME" .)
echo "✅ 已打包: $ZIP_NAME"

# 3. 检查设备
echo ""
echo "📱 步骤 3/4: 检查设备连接..."
if ! adb devices | grep -q "device$"; then
  echo "⚠️  未检测到设备，跳过 ADB 推送"
  echo ""
  echo "======================================="
  echo "✅ 完成（仅生成和打包）"
  echo "📦 Release: $ZIP_NAME"
  echo "======================================="
  exit 0
fi

DEVICE=$(adb devices | grep "device$" | awk '{print $1}')
echo "✅ 设备: $DEVICE"

# 4. ADB 推送
echo ""
echo "📤 步骤 4/4: 推送配置到设备..."
adb shell rm -rf /sdcard/rime/build/* 2>/dev/null || true
adb push ../rime /sdcard/ > /dev/null
echo "✅ 推送完成"

# 触发部署
echo ""
echo "🔧 触发 RIME 部署..."
adb shell am broadcast -a com.osfans.trime.action.DEPLOY > /dev/null 2>&1 || true
echo "📢 开始部署，请在通知栏查看部署状态"

echo ""
echo "======================================="
echo "✅ 完成"
echo "📦 Release: $ZIP_NAME"
echo "📱 已推送到: $DEVICE"
echo "======================================="
