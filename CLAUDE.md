# Shengyun 声韵输入方案 - 开发文档

## 项目概述

Shengyun（声韵拼音）是基于 RIME/Trime 的声韵分层拼音输入方案，通过将汉语拼音分为声母和韵母两层键盘，实现两步输入完整拼音的创新交互方式。

**项目类型**：纯输入方案（YAML 配置文件），无需编译 APK
**目标用户**：幼儿园儿童学习拼音
**依赖**：官方 Trime 输入法 + RIME 引擎
**许可证**：GPL-3.0-or-later

---

## 项目架构

### 文件结构

```
shengyun/
├── shengyun.schema.yaml          # RIME 输入方案配置（133行）
├── shengyun.trime.yaml           # Trime 键盘布局（204行）
├── default.custom.yaml           # 激活配置（7行）
├── README.md                      # 用户文档
├── CLAUDE.md                      # 本文件（开发文档）
└── LICENSE                        # GPL-3.0 许可证
```

### 技术栈

- **RIME**：中州韵输入法引擎（librime）
  - 拼音处理、词库匹配、候选词生成
  - YAML 配置驱动

- **Trime**：同文输入法（Android 前端）
  - 键盘渲染、触摸事件处理
  - 调用 RIME 引擎 JNI 接口

- **配置语言**：YAML
  - `schema.yaml`：输入法逻辑
  - `trime.yaml`：键盘布局

---

## 汉语拼音完整系统

### 声母（Initials）- 23 个

| 类别 | 声母 | IPA | 说明 |
|------|------|-----|------|
| 双唇音 | b, p, m | [p], [pʰ], [m] | 玻、坡、摸 |
| 唇齿音 | f | [f] | 佛 |
| 舌尖中音 | d, t, n, l | [t], [tʰ], [n], [l] | 得、特、呢、勒 |
| 舌根音 | g, k, h | [k], [kʰ], [x] | 哥、科、喝 |
| 舌面音 | j, q, x | [tɕ], [tɕʰ], [ɕ] | 基、欺、希 |
| 舌尖后音 | zh, ch, sh, r | [ʈʂ], [ʈʂʰ], [ʂ], [ʐ] | 知、吃、诗、日 |
| 舌尖前音 | z, c, s | [ts], [tsʰ], [s] | 资、雌、思 |
| 零声母标记 | y, w | - | 用于零声母音节 |

### 韵母（Finals）- 39 个

#### 单韵母（7个）
```
a [a], o [o], e [ɤ], i [i], u [u], ü [y], er [ɚ]
```

#### 复韵母（13个）
```
ai [ai], ei [ei], ao [au], ou [ou]                # 基础
ia [ja], ie [jɛ], iao [jau], iu [jou]            # i系
ua [wa], uo [wo], uai [wai], ui [wei]            # u系
üe [yɛ]                                            # ü系
```

#### 鼻韵母 - 前鼻音（9个）
```
an [an], en [ən], in [in], un [wən], ün [yn]     # 单元音+n
ian [jɛn], uan [wan], üan [yɛn]                  # 复合+n
```

#### 鼻韵母 - 后鼻音（10个）
```
ang [aŋ], eng [əŋ], ing [iŋ], ong [uŋ]           # 单元音+ng
iang [jaŋ], uang [waŋ], iong [jʊŋ]               # 复合+ng
ueng [wəŋ] (rare)                                  # 罕见
```

### 声韵组合规则矩阵

| 声母类别 | 可用韵母 | 限制 |
|----------|----------|------|
| **j, q, x** | i, ia, ie, iao, iu, ian, in, iang, ing, iong, u(=ü), ue(=üe), uan(=üan), un(=ün) | **最严格**：仅 i/ü 系 |
| **zh, ch, sh, r** | i, a, e, ai, ei, ao, ou, an, en, ang, eng, u, ua, uo, uai, ui, uan, un, uang, ong | 不能配 i 复合韵母和 ü 系 |
| **z, c, s** | 同 zh/ch/sh/r | 不能配 i 复合韵母和 ü 系 |
| **g, k, h** | a, o, e, ai, ei, ao, ou, an, en, ang, eng, ua, uo, uai, ui, uan, un, uang, ueng, ong | 不能配 i 系和 ü 系 |
| **b, p, m, f** | 大部分韵母 | 不能配 ü 系和 iong |
| **d, t** | 大部分韵母 | 不能配 ü 系 |
| **n, l** | **所有韵母** | 特例：可配 ü（nü, lü） |
| **y, w** | 对应 i/u 系 | 零声母标记 |

**关键示例**：
- ✅ l + iang = liang（两）
- ✅ j + u = ju（居，实际发 jü）
- ✅ zh + ang = zhang（张）
- ❌ j + ang（j 只配 i/ü 系）
- ❌ zh + ü（翘舌音不配 ü）
- ❌ g + i（舌根音不配 i 系）

---

## 配置文件详解

### 1. shengyun.schema.yaml

#### 核心配置段

##### schema 元数据
```yaml
schema:
  schema_id: shengyun           # 方案唯一标识
  name: 声韵拼音                 # 显示名称
  version: "1.0.0"
  dependencies:
    - luna_pinyin               # 依赖朙月拼音词库
```

##### engine 引擎配置
```yaml
engine:
  processors:                   # 输入处理器（按顺序执行）
    - ascii_composer            # ASCII 模式处理
    - recognizer                # 模式识别
    - key_binder                # 按键绑定
    - speller                   # 拼写器（核心）
    - punctuator                # 标点处理
    - selector                  # 候选词选择
    - navigator                 # 导航
    - express_editor            # 编辑器

  translators:                  # 翻译器
    - script_translator         # 脚本翻译（拼音→汉字）

  filters:                      # 过滤器
    - simplifier                # 简繁转换
    - uniquifier                # 去重
```

##### speller 拼写规则（核心）
```yaml
speller:
  alphabet: zyxwvutsrqponmlkjihgfedcba
  algebra:
    # 1. 保留原始拼音
    - xform/^([a-z]+)$/$1/

    # 2. ü 的等价处理
    - derive/ü/v/               # ü 用 v 表示

    # 3. j/q/x + u = j/q/x + v（都是ü）
    - derive/^([jqx])u/$1v/
    - derive/^([jqx])v/$1u/

    # 4. 智能过滤无效组合
    - erase/^([jqx])([aoe]|a[oin]|[eo]u|[ae]ng|ong|u[ao]|uai|u[ae]ng?)$/
    - erase/^([zcs]h|r)(ia|iao|ie|iu|i[ae]ng?|iong)$/
    - erase/^([zcs]h?|r)v[aenu]?$/
    - erase/^([gkh])(i[aeou]?|i[ae]ng?|iong|v[aenu]?)$/
    - erase/^([bpmf])(v[aenu]?|iong)$/
    - erase/^([dt])v[aenu]?$/
```

**algebra 规则说明**：
- `xform/A/B/`：转换（A→B）
- `derive/A/B/`：派生（保留A，增加B）
- `erase/A/`：删除匹配A的组合
- `abbrev/A/B/`：简写（A简写为B）

**智能过滤原理**：
1. 用户输入 `j + ang`
2. RIME 尝试匹配 `jang`
3. 被 `erase/^([jqx])([aoe]|...)$/` 规则删除
4. 候选词列表为空
5. 用户自然学会规则

##### translator 翻译配置
```yaml
translator:
  dictionary: luna_pinyin       # 使用朙月拼音词库
  prism: shengyun               # 编译后的二进制文件名
  preedit_format:               # 输入区显示格式
    - xform/([nl])v/$1ü/        # nv→nü, lv→lü
    - xform/([jqxy])v/$1u/      # jv→ju (显示u但发ü音)
```

### 2. shengyun.trime.yaml

#### 键盘布局配置

##### 声母层（shengyun_initials）
```yaml
preset_keyboards:
  shengyun_initials:
    name: 声母层
    width: 10                   # 单位宽度（百分比）
    height: 70                  # 按键高度（像素）
    keys:
      # 每个声母键配置
      - click: b                # 点击发送字符
        select: shengyun_finals # 自动切换到韵母层
        label: "b"              # 显示标签（纯拼音）
        long_click: "1"         # 长按发送数字
        width: 12.5             # 宽度占比
```

**关键属性**：
- `click`：点击时输入的字符
- `select`：点击后切换到的键盘
- `label`：显示文本
- `width`：宽度百分比（总和=100）

**自动切换实现**：
每个声母键都有 `select: shengyun_finals`，实现点击后自动跳转到韵母层。

##### 韵母层（shengyun_finals）
```yaml
  shengyun_finals:
    keys:
      - click: a
        select: shengyun_initials  # 自动返回声母层
        label: "a"                 # 纯拼音 a（不是 ɑ）
```

**修正点**：
- 原版使用 IPA 符号 `ɑ`，优化版改为原生拼音 `a`
- 所有韵母都有 `select: shengyun_initials` 实现自动返回

##### 零声母层（shengyun_zero）
```yaml
  shengyun_zero:
    keys:
      - click: yi
        select: shengyun_initials
        label: "yi"
```

用于直接输入零声母音节（a, o, e, ai, yi, wu, yu 等）。

##### 配色方案
```yaml
preset_color_schemes:
  shengyun_kids:
    text_color: 0x000000        # 黑色文字
    back_color: 0xFFFFFF        # 白色背景
    hilited_candidate_back_color: 0xFF6B35  # 橙色高亮
    key_back_color: 0xF5F5F5    # 浅灰按键
```

儿童友好设计：
- 高对比度（黑白配）
- 大按键（height: 70px）
- 大字号（key_text_size: 28）
- 明亮色彩提示

### 3. default.custom.yaml

```yaml
patch:
  schema_list:
    - schema: shengyun          # 激活声韵方案
    - schema: luna_pinyin       # 保留其他方案
```

**作用**：
- 告诉 RIME 启用哪些输入方案
- 允许多个方案共存（F4 切换）
- 必需文件，否则部署时不会加载 shengyun

---

## 技术原理

### 输入流程

```
用户操作                 Trime                RIME 引擎
  |                       |                      |
  |-- 点击声母 "l" ------>|                      |
  |                       |-- 发送 "l" -------->|
  |                       |<-- 返回候选词列表 --|
  |                       |-- 切换到韵母层       |
  |                       |   (select 属性)      |
  |                       |                      |
  |-- 点击韵母 "iang" --->|                      |
  |                       |-- 发送 "iang" ----->|
  |                       |                      |-- 匹配 "liang"
  |                       |                      |-- 查询词库
  |                       |<-- 返回候选 --------|-- 两、亮、量...
  |                       |   ["两","亮"...]     |
  |                       |-- 切换回声母层       |
  |                       |   (select 属性)      |
  |                       |                      |
  |-- 选择 "两" ---------->|-- 发送 "两" ------->|-- 上屏
```

### RIME 编译过程

**用户侧**：
1. 复制 `.yaml` 文件到 `/sdcard/rime/`
2. 点击 Trime 的"部署"按钮

**RIME 引擎执行**：
1. 读取 `shengyun.schema.yaml`
2. 解析 speller/algebra 规则
3. 加载 luna_pinyin.dict.yaml 词库
4. 编译生成 `shengyun.prism.bin`（拼音索引）
5. 生成 `shengyun.table.bin`（词库索引）
6. 保存到 `/sdcard/rime/build/`

**首次部署时间**：1-2 分钟（后续更新更快）

### 智能过滤实现

#### erase 规则工作原理

```yaml
# 规则：j/q/x 只能配 i系和ü系
- erase/^([jqx])([aoe]|a[oin]|[eo]u|[ae]ng|ong|u[ao]|uai|u[ae]ng?)$/
```

**匹配示例**：
- `jang` → 匹配 `^j` 和 `ang` → **删除**
- `ja` → 匹配 `^j` 和 `a` → **删除**
- `ji` → 不匹配规则 → **保留**
- `ju` → 不匹配规则 → **保留**（u=ü）

**用户体验**：
- 输入 `j + ang` → 无候选词
- 自然引导用户学习拼音规则

#### ju = jv 等价处理

```yaml
# 派生规则
- derive/^([jqx])u/$1v/         # ju → jv
- derive/^([jqx])v/$1u/         # jv → ju
```

**效果**：
- 用户输入 `j + u` → 匹配 `ju` → 也匹配 `jv`
- 用户输入 `j + v(ü)` → 匹配 `jv` → 也匹配 `ju`
- 两者等价，都能输入"居"

---

## 发布与分发

### 为什么不需要编译 APK？

**RIME/Trime 架构设计**：
- **RIME 引擎**：负责输入法逻辑（C++ librime）
- **Trime 前端**：负责界面渲染（Kotlin/Java）
- **配置文件**：YAML（运行时加载）

**关键点**：
1. RIME 引擎在运行时读取 `.yaml` 文件
2. 用户可以自由添加/修改配置
3. 无需重新编译 APK

**对比**：
- 传统输入法：配置硬编码在 APK 中，修改需重新编译
- RIME/Trime：配置外置 YAML，热更新

### 发布流程

#### 1. 准备文件
```bash
cd /Users/gshmu/aoe/shengyun

# 检查文件
ls -lh
# shengyun.schema.yaml
# shengyun.trime.yaml
# default.custom.yaml
# README.md
# CLAUDE.md
# LICENSE
```

#### 2. 创建 Git 仓库
```bash
git init
git add .
git commit -m "feat: initial release of shengyun pinyin scheme v1.0.0"

# 创建 GitHub 仓库
gh repo create shengyun --public \
  --description "声韵分层拼音输入方案 - 适合幼儿园儿童学习拼音" \
  --source=.

# 推送代码
git branch -M main
git push -u origin main
```

#### 3. 创建 Release
```bash
# 创建 ZIP 包
zip shengyun-v1.0.0.zip \
  shengyun.schema.yaml \
  shengyun.trime.yaml \
  default.custom.yaml

# 创建 Release
gh release create v1.0.0 \
  --title "声韵拼音输入方案 v1.0.0" \
  --notes "首个正式版本，支持声韵分层两步输入

## 主要特性
- ✅ 声母层（23个声母）
- ✅ 韵母层（39个韵母）
- ✅ 自动键盘切换
- ✅ 纯拼音界面（无汉字助记）
- ✅ 智能过滤无效声韵组合
- ✅ 儿童友好的大按键设计

## 安装方法
详见 README.md

## 文件说明
- shengyun.schema.yaml: RIME 输入方案配置
- shengyun.trime.yaml: 键盘布局配置
- default.custom.yaml: 激活配置" \
  shengyun-v1.0.0.zip

# 查看 Release
gh release view v1.0.0
```

### 用户安装流程

```
用户操作                           系统操作
  |                                   |
  |-- 下载 shengyun-v1.0.0.zip        |
  |   (GitHub Releases)               |
  |                                   |
  |-- 解压到 /sdcard/rime/           |
  |                                   |
  |-- 打开 Trime → 部署               |
  |                                   |-- 读取 .yaml 文件
  |                                   |-- 解析 schema 配置
  |                                   |-- 编译 algebra 规则
  |                                   |-- 生成 .prism.bin
  |                                   |-- 生成 .table.bin
  |                                   |
  |-- 切换到声韵方案（F4）            |
  |                                   |
  |-- 开始使用！                      |
```

---

## 测试与验证

### 测试用例

#### 有效组合（必须成功）
```
✅ l + iang → liang（两、亮、量）
✅ zh + ang → zhang（张、长、章）
✅ j + i → ji（鸡、几、记）
✅ j + u → ju（居、举、句）[u 发 ü 音]
✅ j + v → ju（同上）[v = ü]
✅ n + v(ü) → nü（女）
✅ y + i → yi（一、衣、已）
✅ w + u → wu（五、无、舞）
✅ sh + ang → shang（上、商）
✅ q + u → qu（去、取）[显示u，发ü音]
✅ x + ian → xian（先、现、线）
```

#### 无效组合（应无候选词）
```
❌ j + ang → 无结果（j 只配 i/ü 系）
❌ j + a → 无结果
❌ j + o → 无结果
❌ q + ong → 无结果
❌ zh + v(ü) → 无结果（翘舌音不配 ü）
❌ zh + ia → 无结果
❌ g + i → 无结果（舌根音不配 i 系）
❌ g + ia → 无结果
❌ b + iong → 无结果
❌ d + v(ü) → 无结果
```

### 测试脚本

```bash
#!/bin/bash
# test_install.sh - 在干净设备上测试安装

# 1. 清理环境
adb shell rm -rf /sdcard/rime/shengyun.*
adb shell rm -rf /sdcard/rime/build/

# 2. 安装方案
adb push shengyun.schema.yaml /sdcard/rime/
adb push shengyun.trime.yaml /sdcard/rime/
adb push default.custom.yaml /sdcard/rime/

echo "请在手机上：打开 Trime → 设置 → 部署 → 重新部署"
echo "等待部署完成后，按回车继续..."
read

# 3. 验证文件
adb shell ls -l /sdcard/rime/build/shengyun.*

echo "请在手机上：按 F4 → 选择"声韵拼音" → 测试输入"
echo "测试用例："
echo "  - l + iang = liang（两）"
echo "  - j + ang = 无候选词"
```

### 调试方法

#### 查看 RIME 日志
```bash
# Trime 日志位置
adb logcat | grep -i rime

# 常见错误
# - "Cannot find schema": default.custom.yaml 缺失或配置错误
# - "Failed to build": schema.yaml 语法错误
# - "Dictionary not found": 词库依赖缺失
```

#### 检查部署结果
```bash
# 查看编译产物
adb shell ls -lh /sdcard/rime/build/

# 应该看到：
# shengyun.prism.bin
# shengyun.table.bin
# shengyun.schema.yaml (复制)
```

---

## 维护指南

### 修改键盘布局

#### 添加新按键
```yaml
# 在 shengyun.trime.yaml 中
keys:
  - click: newkey              # 输入字符
    select: target_keyboard    # 切换目标
    label: "显示"              # 标签
    width: 10                  # 宽度
```

#### 调整按键宽度
```yaml
# 确保每行宽度总和 = 100
# 第一行：8 × 12.5 = 100 ✓
- {click: b, label: "b", width: 12.5}
- {click: p, label: "p", width: 12.5}
...

# 第二行：如果有 10 个键，每个 10%
- {click: a, label: "a", width: 10}
...
```

### 修改组合规则

#### 添加模糊音支持
```yaml
# 在 shengyun.schema.yaml 的 speller/algebra 中
- derive/^zh/z/                # zh → z
- derive/^ch/c/                # ch → c
- derive/^sh/s/                # sh → s
- derive/ang$/an/              # ang → an
- derive/eng$/en/              # eng → en
- derive/ing$/in/              # ing → in
```

#### 调整过滤规则
```yaml
# 如果需要放宽某些限制
# 注释掉对应的 erase 规则
# - erase/^([gkh])(i...)$/    # 允许 g/k/h + i
```

### 更新词库

#### 使用自定义词库
```yaml
# 创建 shengyun.dict.yaml
---
name: shengyun
version: "1.0"
sort: by_weight
...

两	liang	100
张	zhang	100
...
```

然后在 schema.yaml 中：
```yaml
translator:
  dictionary: shengyun          # 使用自定义词库
  # 不再依赖 luna_pinyin
```

---

## 未来计划

### v1.1.0 计划
- [ ] 添加词频学习（根据用户输入优化候选词顺序）
- [ ] 添加键盘主题切换（明亮/暗黑模式）
- [ ] 优化按键布局（基于用户反馈）
- [ ] 添加声韵组合提示（在韵母层显示当前声母）

### v2.0.0 设想
- [ ] 支持声调输入（一声、二声、三声、四声）
- [ ] 图形化配置工具（无需手动编辑 YAML）
- [ ] 提交到 RIME Plum 官方仓库
- [ ] 多语言版本（繁体中文、英文说明）

---

## 参考资源

### 官方文档
- **RIME 官网**: https://rime.im/
- **RIME Schema 指南**: https://github.com/rime/home/wiki/RimeWithSchemata
- **Trime 文档**: https://github.com/osfans/trime/wiki
- **Trime 键盘配置**: https://github.com/osfans/trime/wiki/trime.yaml-詳解

### 汉语拼音资源
- **汉语拼音方案**: http://www.moe.gov.cn/
- **Pinyin Info**: https://pinyin.info/
- **拼音组合表**: https://en.wikipedia.org/wiki/Pinyin_table

### 类似项目
- **小鹤音形**: https://github.com/amorphobia/openfly
- **极点五笔**: https://github.com/KyleBing/rime-wubi86-jidian
- **Rimerc**: https://github.com/Bambooin/rimerc

### 工具
- **RIME Plum**: https://github.com/rime/plum（方案安装器）
- **YAML Validator**: https://www.yamllint.com/

---

## 常见开发问题

### Q: 如何调试 algebra 规则？

**A**: 使用 RIME 的调试模式：
1. 在 Trime 中启用日志：设置 → 高级 → 启用日志
2. 查看 `/sdcard/rime/rime.log`
3. 搜索 `[speller]` 相关日志
4. 查看哪些规则被应用

### Q: 为什么部署后方案不生效？

**A**: 常见原因：
1. `default.custom.yaml` 未正确配置
2. `schema_id` 不匹配
3. 词库依赖缺失（luna_pinyin）
4. YAML 语法错误（缩进、冒号）

### Q: 如何测试单个规则？

**A**: 创建最小测试方案：
```yaml
# test.schema.yaml
schema:
  schema_id: test
  name: Test

speller:
  algebra:
    - xform/^([a-z]+)$/$1/
    - erase/^([jqx])a$/      # 测试规则

translator:
  dictionary: luna_pinyin
```

### Q: 如何贡献代码？

**A**:
1. Fork 仓库
2. 创建特性分支
3. 修改并测试
4. 提交 Pull Request
5. 等待代码审查

---

## 项目历史

### 2025-11-14 - v1.0.0
- ✨ 首个正式版本发布
- ✅ 完成汉语拼音系统全面研究（23声母+39韵母）
- ✅ 建立声韵组合规则矩阵
- ✅ 验证复杂拼音输入（liang, zhang, ju 等）
- ✅ 实现自动键盘切换机制
- ✅ 实现智能过滤（erase 规则）
- ✅ 纯拼音界面设计（移除汉字助记）
- ✅ 完成完整文档（README + CLAUDE.md）
- ✅ 创建独立 GitHub 仓库（shengyun）
- ✅ 发布 v1.0.0 Release with ZIP 包

---

## 许可证

本项目基于 GPL-3.0-or-later 许可证开源。

---

## 联系方式

- **GitHub**: https://github.com/gshmu/shengyun
- **Issues**: https://github.com/gshmu/shengyun/issues
- **原项目**: https://github.com/gshmu/shengyun-rime（Trime fork）

---

**Claude Code 项目文档** | 声韵输入方案 | Generated: 2025-11-14
