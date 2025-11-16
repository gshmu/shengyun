#!/usr/bin/env python3
"""
根据配置文件生成24个声母的韵母层键盘布局

输入文件：
- finals_all.csv: 35个韵母的9列布局
- finals_mask_config.yaml: 每个声母的屏蔽韵母配置

输出：
- 直接更新 shengyun.trime.yaml 的第97-1246行（24个韵母层）
"""

import csv
import re
import sys
from pathlib import Path

# 配置
PROJECT_DIR = Path(__file__).parent
CSV_FILE = PROJECT_DIR / "finals_all.csv"
CONFIG_FILE = PROJECT_DIR / "finals_mask_config.yaml"
TRIME_YAML = PROJECT_DIR / "shengyun.trime.yaml"
OUTPUT_FILE = PROJECT_DIR / "finals_generated.yaml"

# 需要 ü→u 转换的声母层
U_CONVERT_INITIALS = {'j', 'q', 'x', 'y'}

def read_finals_layout():
    """从 CSV 读取35个韵母的9列布局"""
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = [row for row in reader if row]  # 过滤空行

    if len(rows) != 4:
        raise ValueError(f"CSV should have 4 rows, got {len(rows)}")

    return rows

def read_mask_config():
    """从 YAML 读取屏蔽配置（简单解析，不依赖 PyYAML）"""
    config = {}
    zero_initial_config = {'masked_finals': []}
    current_initial = None
    in_zero_initial = False

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()

            # 匹配零声母配置
            if re.match(r'^zero_initial:', line):
                in_zero_initial = True
                current_initial = None
                continue

            # 匹配 initials 开始
            if re.match(r'^initials:', line):
                in_zero_initial = False
                continue

            # 匹配声母定义（如 "  b:"）
            match = re.match(r'^  ([a-z]+):$', line)
            if match and not in_zero_initial:
                current_initial = match.group(1)
                config[current_initial] = {'masked_finals': []}
                continue

            # 匹配 masked_finals 列表（如 "    masked_finals: [er, e, ...]"）
            match = re.match(r'^\s+masked_finals:\s*\[(.*)\]$', line)
            if match:
                items = match.group(1)
                if items.strip():
                    finals = [item.strip() for item in items.split(',')]
                    if in_zero_initial:
                        zero_initial_config['masked_finals'] = finals
                    elif current_initial:
                        config[current_initial]['masked_finals'] = finals

    return config, zero_initial_config

def convert_u_display(text, initial):
    """j/q/x/y 层：ü→u 转换显示"""
    if initial in U_CONVERT_INITIALS:
        return text.replace('ü', 'u')
    return text

def convert_final_for_click(final, initial):
    """转换 CSV 中的韵母为实际 RIME 输入码

    互补分布规则：
    - ün 位置：j/q/x/y/n/l 用 ün（或 v），其他用 un
    - uan 位置：所有声母都用 uan
    """
    # ün/un 互补分布
    if final == 'ün':
        # j/q/x/y: jun (RIME识别为jün), n/l: nün/lün
        if initial in {'j', 'q', 'x', 'y'}:
            return 'un'  # j+un → jun，RIME自动识别为jün
        elif initial in {'n', 'l'}:
            return 'ün'  # n+ün → nün
        else:
            return 'un'  # k+un → kun

    # 其他韵母正常处理
    return final

def convert_label_for_display(final, initial):
    """转换韵母为显示标签

    显示规则：
    - j/q/x/y: ü→u 转换
    - n/l: 保留 ün
    - 其他: ün→un
    """
    if final == 'ün':
        if initial in U_CONVERT_INITIALS:  # j/q/x/y
            return 'un'
        elif initial in {'n', 'l'}:
            return 'ün'
        else:
            return 'un'

    # j/q/x/y 的其他 ü 转换
    if initial in U_CONVERT_INITIALS:
        return final.replace('ü', 'u')

    return final

def generate_keyboard_for_initial(initial, layout_rows, mask_config):
    """为单个声母生成键盘布局"""
    masked_finals = set(mask_config.get('masked_finals', []))

    lines = []
    lines.append(f"  # {initial} 的韵母层")
    lines.append(f"  shengyun_finals_{initial}:")
    lines.append(f"    name: 韵母层-{initial}")
    lines.append(f"    author: shengyun")
    lines.append(f"    ascii_mode: 0")
    lines.append(f"    width: 11.11")
    lines.append(f"    height: 70")
    lines.append(f"    lock: true")
    lines.append(f"    keys:")

    for row_idx, row in enumerate(layout_rows, 1):
        # 构建行注释
        row_comment = ', '.join(row)
        lines.append(f"      # 行{row_idx}：{initial} {row_comment}")

        for col_idx, final in enumerate(row, 1):
            # 第1列第1个按钮：显示声母（不可点击）
            if row_idx == 1 and col_idx == 1:
                lines.append(f"      - {{click: {initial}, select: shengyun_initials, label: \"{initial}\", width: 11.11}}")
                continue

            # 特殊控制键
            if final == '⇧':
                lines.append(f"      - {{click: Keyboard_shengyun_initials, label: \"⇧\", width: 11.11, send_bindings: false, hilited: true}}")
                continue
            elif final == '␣':
                lines.append(f"      - {{click: space, label: \"␣\", width: 11.11}}")
                continue
            elif final == '⌫':
                lines.append(f"      - {{click: BackSpace, label: \"⌫\", width: 11.11, repeat: true}}")
                continue

            # 普通韵母按钮
            # 检查是否被屏蔽
            if final in masked_finals:
                # 屏蔽：显示空格
                lines.append(f"      - {{click: space, label: \" \", width: 11.11}}")
            else:
                # 未屏蔽：正常显示
                display_label = convert_label_for_display(final, initial)
                click_final = convert_final_for_click(final, initial)
                click_value = f"{initial}{click_final}"
                lines.append(f"      - {{click: {click_value}, select: shengyun_initials, label: \"{display_label}\", width: 11.11}}")

    lines.append("")  # 空行分隔
    return '\n'.join(lines)

def generate_all_finals_layers():
    """生成所有24个韵母层"""
    layout_rows = read_finals_layout()
    mask_config, zero_config = read_mask_config()

    # 24个声母（按拼音顺序）
    initials = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h',
                'j', 'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w']

    all_lines = []
    for initial in initials:
        if initial not in mask_config:
            print(f"Warning: {initial} not in config, skipping", file=sys.stderr)
            continue

        keyboard_yaml = generate_keyboard_for_initial(initial, layout_rows, mask_config[initial])
        all_lines.append(keyboard_yaml)

    return '\n'.join(all_lines)

def generate_zero_initial_layer():
    """生成零声母层（shengyun_finals_all）"""
    layout_rows = read_finals_layout()
    _, zero_config = read_mask_config()

    masked_finals = set(zero_config.get('masked_finals', []))

    lines = []
    lines.append(f"  # 通用韵母层（显示所有35个韵母，西文模式专用，9列布局）")
    lines.append(f"  shengyun_finals_all:")
    lines.append(f"    name: 韵母层-全部")
    lines.append(f"    author: shengyun")
    lines.append(f"    ascii_mode: 0")
    lines.append(f"    width: 11.11")
    lines.append(f"    height: 70")
    lines.append(f"    lock: true")
    lines.append(f"    keys:")

    for row_idx, row in enumerate(layout_rows, 1):
        # 构建行注释
        row_comment = ' '.join(row)
        lines.append(f"      # 行{row_idx}：{row_comment}")

        for col_idx, final in enumerate(row, 1):
            # 特殊控制键
            if final == '⇧':
                lines.append(f"      - {{click: Keyboard_shengyun_initials, label: \"⇧\", width: 11.11, send_bindings: false, hilited: true}}")
                continue
            elif final == '␣':
                lines.append(f"      - {{click: space, label: \"␣\", width: 11.11}}")
                continue
            elif final == '⌫':
                lines.append(f"      - {{click: BackSpace, label: \"⌫\", width: 11.11, repeat: true}}")
                continue

            # 普通韵母按钮
            if final in masked_finals:
                # 屏蔽：显示空格
                lines.append(f"      - {{click: space, label: \" \", width: 11.11}}")
            else:
                # 未屏蔽：正常显示
                # ü 需要转换为 v（RIME 输入码）
                click_value = final.replace('ü', 'v')
                lines.append(f"      - {{click: {click_value}, select: shengyun_initials, label: \"{final}\", width: 11.11}}")

    lines.append("")
    return '\n'.join(lines)

def update_trime_yaml(new_finals_content, new_zero_initial_content):
    """更新 shengyun.trime.yaml 的韵母层部分（97-1246行）和零声母层（1247-1299行）"""
    with open(TRIME_YAML, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 提取三部分：
    # 1. 头部（1-96行）：声母层等
    # 2. 24个韵母层（97-1246行）：替换
    # 3. 零声母层（1247-1299行）：替换
    # 4. 尾部（1300行之后）：主键盘等
    header = lines[:96]
    footer = lines[1299:]

    # 组合新内容
    new_lines = header + [new_finals_content + '\n'] + [new_zero_initial_content + '\n'] + footer

    # 写回文件
    with open(TRIME_YAML, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✓ Updated {TRIME_YAML}")
    print(f"  - Replaced lines 97-1246 with new finals layers (24 initials)")
    print(f"  - Replaced lines 1247-1299 with new zero-initial layer")
    print(f"  - Total lines: {len(new_lines)}")

def main():
    """主函数"""
    print("=== 声韵韵母层生成器 ===")
    print(f"CSV: {CSV_FILE}")
    print(f"Config: {CONFIG_FILE}")
    print(f"Target: {TRIME_YAML}")
    print()

    # 生成24个韵母层
    print("Generating 24 finals layers...")
    finals_content = generate_all_finals_layers()
    print(f"✓ Generated 24 finals layers")

    # 生成零声母层
    print("Generating zero-initial layer...")
    zero_initial_content = generate_zero_initial_layer()
    print(f"✓ Generated zero-initial layer (shengyun_finals_all)")

    # 保存到临时文件（可选，用于查看）
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(finals_content)
        f.write('\n')
        f.write(zero_initial_content)
    print(f"✓ Saved to {OUTPUT_FILE} (for review)")

    # 更新主配置文件
    print()
    print("Updating shengyun.trime.yaml...")
    update_trime_yaml(finals_content, zero_initial_content)

    print()
    print("Done! You can now:")
    print("  git diff shengyun.trime.yaml  # Review changes")
    print("  adb push shengyun.trime.yaml /sdcard/rime/  # Deploy to phone")

if __name__ == '__main__':
    main()
