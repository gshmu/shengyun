#!/usr/bin/env python3
"""
声韵输入法键盘配置生成器

【功能】根据声母-韵母映射表生成26个键盘配置
【输入】pinyin.tsv + finals_all.csv
【输出】rime/shengyun.trime.yaml
【使用】cd generator && python3 tools/gen_keyboards.py

核心逻辑：
- 从 pinyin.tsv 读取每个声母的可用韵母
- 从 finals_all.csv 读取韵母布局模板（4×11网格）
- 交叉生成23个韵母键盘（含once参数）
- 键位宽度自动计算：100 / 列数
"""

import csv
import yaml
from pathlib import Path

# 自定义格式化器：强制宽度保留两位小数
class WidthFloat(float):
    pass

def represent_width_float(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:float', f"{data:.2f}")

yaml.add_representer(WidthFloat, represent_width_float)

ROOT_DIR = Path(__file__).parent.parent.parent
TSV_FILE = Path(__file__).parent.parent / 'pinyin.tsv'
CSV_FILE = Path(__file__).parent.parent / 'finals_all.csv'
TRIME_FILE = ROOT_DIR / 'rime' / 'shengyun.trime.yaml'


def parse_pinyin_tsv():
    """解析 pinyin.tsv，提取每个声母的可用韵母"""
    with open(TSV_FILE, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]

    # 列索引
    INITIAL_START = 1
    INITIAL_END = 22
    Y_COL = 22
    W_COL = 23
    ZERO_COL = 24

    # 声母列表（从第一行提取）
    header = lines[0].split('\t')
    initials = [header[i] for i in range(INITIAL_START, INITIAL_END)]

    # 为每个声母收集可用韵母
    initial_finals = {}
    for initial in initials:
        initial_finals[initial] = []

    initial_finals['y'] = []
    initial_finals['w'] = []
    initial_finals['zero'] = []

    # 遍历每一行（从第二行开始，第一行是 er）
    for line_idx in range(1, len(lines)):
        cols = lines[line_idx].split('\t')
        final_name = cols[0]

        # 处理 22 个真声母
        for i, initial in enumerate(initials, start=INITIAL_START):
            if len(cols) > i and cols[i] and cols[i] != '-':
                initial_finals[initial].append(final_name)

        # 处理 y/w/zero
        if len(cols) > Y_COL and cols[Y_COL] and cols[Y_COL] != '-':
            initial_finals['y'].append(final_name)

        if len(cols) > W_COL and cols[W_COL] and cols[W_COL] != '-':
            initial_finals['w'].append(final_name)

        if len(cols) > ZERO_COL and cols[ZERO_COL] and cols[ZERO_COL] != '-':
            initial_finals['zero'].append(final_name)

    # 处理 er（第一行）
    first_cols = lines[0].split('\t')
    if len(first_cols) > ZERO_COL and first_cols[ZERO_COL] and first_cols[ZERO_COL] != '-':
        initial_finals['zero'].append('er')

    return initial_finals


def load_finals_layout():
    """加载韵母布局，处理换行分割的互斥韵母"""
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 处理互斥韵母：将 "un|vn" 分割为 ["un", "vn"]
    processed_rows = []
    for row in rows:
        processed_row = []
        for cell in row:
            if '|' in cell:
                processed_row.append(cell.split('|'))
            else:
                processed_row.append(cell)
        processed_rows.append(processed_row)

    return processed_rows


def select_final_for_initial(final_options, initial, available_finals):
    """从互斥韵母选项中选择适用于当前声母的韵母"""
    if isinstance(final_options, str):
        return final_options if final_options in available_finals else None

    # 互斥韵母：选择在 available_finals 中的那个
    for option in final_options:
        if option in available_finals:
            return option
    return None


def convert_final_for_click(final, initial):
    """转换韵母点击值：零声母直接用韵母，其他声母+韵母（ü→v）"""
    code = final.replace('ü', 'v')
    if initial == 'zero':
        return code
    return f"{initial}{code}"


def generate_keyboard_dict(initial, layout_rows, available_finals_set):
    """为单个声母生成键盘字典"""
    keys = []

    for row_idx, row in enumerate(layout_rows, 1):
        # 每行用自己的宽度（根据该行列数计算）
        width = f"{(10000 // len(row) / 100):g}"
        for col_idx, final_options in enumerate(row, 1):
            # 第1行第1个按钮：显示声母（零声母显示 er）
            if row_idx == 1 and col_idx == 1:
                if initial == 'zero':
                    keys.append({'click': 'er', 'select': 'shengyun_initials', 'label': 'er', 'width': width})
                else:
                    keys.append({'click': initial, 'select': 'shengyun_initials', 'label': initial, 'width': width, 'functional': True})
                continue

            # 特殊控制键
            if final_options == '⇧':
                if initial == 'zero':
                    keys.append({'click': 'Keyboard_shengyun_initials', 'label': '⇧', 'width': width, 'send_bindings': False, 'hilited': True})
                else:
                    keys.append({'click': 'Keyboard_shengyun_initials', 'label': '⇧', 'width': width, 'send_bindings': False, 'hilited': True})
                continue
            elif final_options == '␣':
                keys.append({'click': 'space', 'label': '␣', 'width': width})
                continue
            elif final_options == '⌫':
                keys.append({'click': 'BackSpace', 'label': '⌫', 'width': width, 'repeat': True})
                continue
            elif final_options == '':
                keys.append({'click': 'space', 'label': ' ', 'width': width})
                continue

            # 普通韵母按钮：选择适用的韵母
            selected_final = select_final_for_initial(final_options, initial, available_finals_set)

            if selected_final:
                click_value = convert_final_for_click(selected_final, initial)
                keys.append({'click': click_value, 'select': 'shengyun_initials', 'label': selected_final, 'width': width})
            else:
                # 不可用韵母：显示空格
                keys.append({'click': 'space', 'label': ' ', 'width': width})

    return {
        'name': f'韵母层-{initial}',
        'author': 'gshmu',
        'ascii_mode': 0,
        'width': 100,  # 总宽度 100%
        'height': 70,
        'lock': True,
        'once': True,  # 添加 once 参数
        'keys': keys
    }


def generate_universal_finals_dict(layout_rows):
    """生成通用韵母全览层字典"""
    keys = []

    for row_idx, row in enumerate(layout_rows, 1):
        # 每行用自己的宽度（根据该行列数计算）
        width = f"{(10000 // len(row) / 100):g}"
        for col_idx, final_options in enumerate(row, 1):
            if row_idx == 1 and col_idx == 1:
                keys.append({'click': 'er', 'label': 'er', 'width': width, 'functional': True})
                continue

            if final_options == '⇧':
                keys.append({'click': 'Keyboard_shengyun_initials', 'label': '⇧', 'width': width, 'send_bindings': False, 'hilited': True})
                continue
            elif final_options == '␣':
                keys.append({'click': 'space', 'label': '␣', 'width': width})
                continue
            elif final_options == '⌫':
                keys.append({'click': 'BackSpace', 'label': '⌫', 'width': width, 'repeat': True})
                continue
            elif final_options == '':
                keys.append({'click': 'space', 'label': ' ', 'width': width})
                continue

            # 互斥韵母
            if isinstance(final_options, list):
                long, short  = final_options
                keys.append({'click': short, 'long_click': long, 'label': short, 'width': width})
            else:
                click_value = final_options.replace('ü', 'v')
                keys.append({'click': click_value, 'select': 'shengyun_initials', 'label': final_options, 'width': width})

    return {
        'name': '韵母层-全部',
        'author': 'gshmu',
        'ascii_mode': 0,
        'width': 100,  # 总宽度 100%
        'height': 70,
        'lock': True,
        'once': True,  # 添加 once 参数
        'keys': keys
    }


def update_trime_yaml(initial_finals, layout_rows):
    """更新 shengyun.trime.yaml 中的韵母键盘部分"""

    # 读取现有配置
    with open(TRIME_FILE, 'r', encoding='utf-8') as f:
        trime = yaml.safe_load(f)

    # 过滤：保留非 shengyun_finals_* 键盘
    preset_keyboards = trime.get('preset_keyboards', {})
    filtered_keyboards = {k: v for k, v in preset_keyboards.items()
                         if not k.startswith('shengyun_finals')}

    # 生成并添加新键盘
    # 1. 零声母层
    zero_finals = set(initial_finals['zero'])
    filtered_keyboards['shengyun_finals_zero'] = generate_keyboard_dict('zero', layout_rows, zero_finals)

    # 2. 24个声母层（21真声母 + y + w）
    initials_order = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h',
                      'j', 'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c', 's', 'y', 'w']

    for initial in initials_order:
        available = set(initial_finals[initial])
        filtered_keyboards[f'shengyun_finals_{initial}'] = generate_keyboard_dict(initial, layout_rows, available)

    # 3. 通用韵母全览层
    filtered_keyboards['shengyun_finals'] = generate_universal_finals_dict(layout_rows)

    # 添加声母键盘（如果不存在则生成空壳，如果存在则保留）
    if 'shengyun_initials' not in filtered_keyboards:
        # 生成声母键盘（这里需要调用生成函数，为了简化先留空壳）
        filtered_keyboards['shengyun_initials'] = generate_initials_keyboard()

    # 更新配置
    trime['preset_keyboards'] = filtered_keyboards

    # 添加预设键盘切换键（Keyboard_*）
    preset_keys = trime.get('preset_keys', {})
    for initial in initials_order + ['zero', 'finals']:
        key_name = f'Keyboard_shengyun_finals_{initial}' if initial != 'finals' else 'Keyboard_shengyun_finals'
        preset_keys[key_name] = {
            'label': initial if initial != 'zero' else '⇧',
            'send': 'Eisu_toggle',
            'select': f'shengyun_finals_{initial}' if initial != 'finals' else 'shengyun_finals'
        }
    # 声母键盘切换
    preset_keys['Keyboard_shengyun_initials'] = {
        'label': '声母',
        'send': 'Eisu_toggle',
        'select': 'shengyun_initials'
    }
    trime['preset_keys'] = preset_keys

    # 转换所有宽度为 WidthFloat（强制保留两位小数）
    for kb in trime['preset_keyboards'].values():
        if 'width' in kb:
            kb['width'] = WidthFloat(kb['width'])
        for key in kb.get('keys', []):
            if 'width' in key:
                key['width'] = WidthFloat(key['width'])

    # 写回文件
    with open(TRIME_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(trime, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=200)

    print(f"✅ 已更新 {TRIME_FILE}")
    print(f"   - 零声母层: 1个")
    print(f"   - 声母层: {len(initials_order)}个")
    print(f"   - 通用层: 1个")


def main():
    print("=" * 80)
    print("声韵输入法键盘生成器")
    print("=" * 80)

    print("\n1. 解析 pinyin.tsv...")
    initial_finals = parse_pinyin_tsv()
    print(f"   ✅ 共 {sum(len(v) for v in initial_finals.values())} 个拼音组合")

    print("\n2. 加载键盘布局...")
    layout_rows = load_finals_layout()
    print(f"   ✅ 已加载: {CSV_FILE} ({len(layout_rows)}行)")

    print("\n3. 生成并更新键盘...")
    update_trime_yaml(initial_finals, layout_rows)

    print("\n" + "=" * 80)
    print("✅ 完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
