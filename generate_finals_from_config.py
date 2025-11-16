#!/usr/bin/env python3
"""
根据配置文件生成声韵输入法的韵母层键盘布局

输入文件：
- finals_all.csv: 35个韵母的9列布局
- finals_mask_config.yaml: 每个声母的屏蔽韵母配置

输出：
- 直接更新 shengyun.trime.yaml，生成以下内容：
  1. 24个声母的专用韵母层（shengyun_finals_b ~ shengyun_finals_w）
  2. 通用韵母全览层（shengyun_finals）- 显示所有35个韵母
  3. 零声母韵母层（shengyun_finals_zero）- 只显示独立可用的韵母
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

    显示规则（按汉语拼音标准写法）：
    - j/q/x/y 层的 ü 系韵母：转换为 u 写法（ü→u, üe→ue, ün→un, üan→uan）
    - 其他层的 ün：n/l 显示 ün，其他显示 un
    - 其他韵母：保持原样
    """
    # j/q/x/y 层：所有 ü 系韵母转换为 u 显示（拼音写法）
    if initial in U_CONVERT_INITIALS:
        return final.replace('ü', 'u')

    # ün 位置的互补分布（其他层）
    if final == 'ün':
        if initial in {'n', 'l'}:
            return 'ün'  # n/l 保留 ün
        else:
            return 'un'  # 其他显示 un

    # 其他韵母保持原样
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

def generate_finals_all_layer():
    """生成通用韵母全览层（shengyun_finals）- 显示所有35个韵母"""
    layout_rows = read_finals_layout()

    lines = []
    lines.append(f"  # 通用韵母层（显示所有韵母，用于所有声母的调试预览）")
    lines.append(f"  shengyun_finals:")
    lines.append(f"    name: 韵母全览")
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

            # 普通韵母按钮 - 全部显示
            # ü 需要转换为 v（RIME 输入码）
            click_value = final.replace('ü', 'v')
            lines.append(f"      - {{click: {click_value}, select: shengyun_initials, label: \"{final}\", width: 11.11}}")

    lines.append("")
    return '\n'.join(lines)

def generate_zero_initial_layer():
    """生成零声母层（shengyun_finals_zero）- 只显示独立可用的韵母"""
    layout_rows = read_finals_layout()
    _, zero_config = read_mask_config()

    masked_finals = set(zero_config.get('masked_finals', []))

    lines = []
    lines.append(f"  # 零声母韵母层（独立可用的韵母，不需要声母）")
    lines.append(f"  shengyun_finals_zero:")
    lines.append(f"    name: 零声母层")
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

def update_trime_yaml(new_finals_content, new_finals_all_content, new_zero_initial_content):
    """更新 shengyun.trime.yaml 的韵母层部分，保留头尾配置"""
    with open(TRIME_YAML, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 通过标记分割文件，避免硬编码行号
    header = []
    footer = []
    in_header = True
    in_footer = False

    for i, line in enumerate(lines):
        # 找到第一个韵母层标记（b 的韵母层）
        if '# b 的韵母层' in line:
            in_header = False
            continue

        # 找到主键盘标记（footer 开始）
        if '# 声韵主键盘（默认显示声母层）' in line:
            in_footer = True

        if in_header:
            header.append(line)
        elif in_footer:
            footer.append(line)

    # 组合新内容：24个声母层 + 通用韵母全览层 + 零声母层
    new_lines = header + [new_finals_content + '\n'] + [new_finals_all_content + '\n'] + [new_zero_initial_content + '\n'] + footer

    # 写回文件
    with open(TRIME_YAML, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✓ Updated {TRIME_YAML}")
    print(f"  - Replaced 24 finals layers + finals_all layer + zero-initial layer")
    print(f"  - Total lines: {len(new_lines)}")
    print(f"  - Header lines: {len(header)}, Footer lines: {len(footer)}")

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

    # 生成通用韵母全览层
    print("Generating finals-all layer (shengyun_finals)...")
    finals_all_content = generate_finals_all_layer()
    print(f"✓ Generated finals-all layer (shengyun_finals)")

    # 生成零声母层
    print("Generating zero-initial layer (shengyun_finals_zero)...")
    zero_initial_content = generate_zero_initial_layer()
    print(f"✓ Generated zero-initial layer (shengyun_finals_zero)")

    # 保存到临时文件（可选，用于查看）
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(finals_content)
        f.write('\n')
        f.write(finals_all_content)
        f.write('\n')
        f.write(zero_initial_content)
    print(f"✓ Saved to {OUTPUT_FILE} (for review)")

    # 更新主配置文件
    print()
    print("Updating shengyun.trime.yaml...")
    update_trime_yaml(finals_content, finals_all_content, zero_initial_content)

    print()
    print("Done! You can now:")
    print("  git diff shengyun.trime.yaml  # Review changes")
    print("  adb push shengyun.trime.yaml /sdcard/rime/  # Deploy to phone")

if __name__ == '__main__':
    main()
