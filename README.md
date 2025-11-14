# 声韵拼音输入方案

> 专为幼儿园儿童设计的声韵分层拼音输入法

**开发状态**：🚧 v1.0.1 开发中 - Lua处理器自动键盘切换功能开发完成，等待测试验证

## 📖 简介

声韵拼音是一种创新的汉字输入方法，将每个汉字的拼音分为**声母**和**韵母**两层键盘，通过**两次点击**即可完成一个完整拼音的输入。

### 为什么选择声韵输入法？

- ✅ **符合教学规范**：与幼儿园拼音教学方法一致（声母+韵母）
- ✅ **简化操作**：每个拼音仅需2次点击（如：liang = l + iang）
- ✅ **自动切换**：点击声母自动切换到韵母层，点击韵母自动切回声母层
- ✅ **纯拼音界面**：清爽界面，无汉字干扰，专注拼音学习
- ✅ **智能过滤**：自动阻止无效声韵组合（如：j+ang、zh+ü）

---

## 🎯 核心特性

### 1. 两层键盘设计

| 层级 | 内容 | 按键数 |
|------|------|--------|
| **声母层** | b, p, m, f, d, t, n, l, g, k, h, j, q, x, zh, ch, sh, r, z, c, s, y, w | 23个 |
| **韵母层** | a, o, e, i, u, ü, ai, ei, ao, ou, ia, ie, iao, iu, ua, uo, uai, ui, üe, er, an, en, in, un, ün, ang, eng, ing, ong, ian, uan, üan, iang, uang, iong 等 | 39个 |

### 2. 自动切换流程

```
👆 点击声母（如：zh）
   ↓ 自动切换到韵母层
👆 点击韵母（如：ang）
   ↓ 自动切换回声母层
✅ 完成拼音：zhang（张）
```

### 3. 输入示例

| 汉字 | 拼音 | 输入方式 | 点击次数 |
|------|------|----------|----------|
| 两 | liang | l + iang | 2次 |
| 张 | zhang | zh + ang | 2次 |
| 居 | ju | j + u（实际发ü音） | 2次 |
| 一 | yi | y + i | 2次 |
| 五 | wu | w + u | 2次 |
| 学 | xue | x + ue（üe） | 2次 |

---

## 📥 安装方法

### 前提条件

1. 安装 **Trime 同文输入法**（官方版本）
   - [F-Droid 下载](https://f-droid.org/packages/com.osfans.trime/)
   - [Google Play 下载](https://play.google.com/store/apps/details?id=com.osfans.trime)
   - [GitHub Releases 下载](https://github.com/osfans/trime/releases)

### 方法1：文件管理器安装（推荐给家长）

#### 步骤1：下载方案文件

1. 访问 [Releases 页面](https://github.com/gshmu/shengyun/releases)
2. 下载最新版本的 `shengyun-v1.0.0.zip`（文件很小，约 50KB）

#### 步骤2：解压文件

1. 在手机上找到下载的 ZIP 文件（通常在"下载"文件夹）
2. 使用文件管理器解压，得到 3 个 `.yaml` 文件：
   - `shengyun.schema.yaml`
   - `shengyun.trime.yaml`
   - `default.custom.yaml`

#### 步骤3：复制到 Trime 目录

1. 打开文件管理器
2. 找到 `/内部存储/rime/` 目录
   - 如果找不到，先打开 Trime 输入法，它会自动创建
3. 将 3 个 `.yaml` 文件复制到 `/rime/` 目录

#### 步骤4：部署方案

1. 打开任意应用（如备忘录、微信）
2. 调出 Trime 输入法
3. 点击输入法界面上的 **设置图标**（齿轮⚙️）或长按空格键
4. 进入 **设置 → 部署**
5. 点击 **重新部署**
6. 等待 1-2 分钟（首次部署需要编译方案）
7. 看到"部署完成"提示

#### 步骤5：切换到声韵方案

1. 在输入法界面，按 **F4** 键（或点击输入法图标）
2. 在方案列表中选择 **"声韵拼音"**
3. 开始使用！

---

### 方法2：ADB 安装（开发者用）

如果您熟悉命令行工具，可以使用 ADB 快速安装：

```bash
# 1. 连接手机到电脑，启用 USB 调试

# 2. 推送文件
adb push shengyun.schema.yaml /sdcard/rime/
adb push shengyun.trime.yaml /sdcard/rime/
adb push default.custom.yaml /sdcard/rime/

# 3. 在手机 Trime 中点击"部署" → "重新部署"

# 4. 切换到声韵拼音方案（F4 键）
```

---

## 🎮 使用教程

### 基本操作

1. **输入声母**：点击声母层的任意声母（如：b, zh, q）
   - 键盘自动切换到韵母层

2. **输入韵母**：点击韵母层的任意韵母（如：a, ang, iang）
   - 键盘自动切换回声母层

3. **选择汉字**：在候选词列表中点击想要的汉字

### 特殊情况

#### 零声母音节（如：啊、一、五）

**方法1**：使用 y/w 作为声母
- 一（yi）= y + i
- 五（wu）= w + u
- 鹅（e）= 需要用零声母层

**方法2**：使用零声母层（点击声母层的"➔韵母"旁边的按钮切换）

#### ü 的输入

ü（迂）系列韵母会直接显示为 ü：
- 女（nü）= n + ü
- 去（qu）= q + u（显示为 u，但发 ü 音）
- 雨（yu）= y + u

### 键盘切换

- **声母 → 韵母**：点击任意声母，自动切换
- **韵母 → 声母**：点击任意韵母，自动切换
- **手动切换**：点击 "➔韵母" 或 "声母➔" 按钮
- **切换到零声母**：声母层点击零声母按钮

---

## ❓ 常见问题

### Q1: 找不到 `/rime/` 目录？

**答**：
1. 确保已安装 Trime 输入法
2. 打开 Trime 并切换到该输入法，它会自动创建目录
3. 使用文件管理器搜索 "rime" 文件夹
4. 完整路径通常是：`/storage/emulated/0/rime/` 或 `/sdcard/rime/`

### Q2: 部署后在方案列表中找不到"声韵拼音"？

**答**：
1. 检查是否正确复制了 3 个文件（特别是 `default.custom.yaml`）
2. 重新部署：设置 → 部署 → 重新部署
3. 查看部署日志，看是否有错误提示
4. 确保文件名正确（注意大小写和后缀 `.yaml`）

### Q3: 输入 j + ang 为什么没有候选词？

**答**：这是正确的！j/q/x 只能搭配 i 系和 ü 系韵母，不能搭配 a/o/e/ang 等。
- ✅ 正确：j + i = ji（鸡）
- ✅ 正确：j + u = ju（居，发 ü 音）
- ✅ 正确：j + iang = jiang（江）
- ❌ 错误：j + ang（无效组合）

这是汉语拼音的规则，声韵输入法会智能过滤无效组合。

### Q4: 如何更新到新版本？

**答**：
1. 下载新版本的 ZIP 文件
2. 解压并复制到 `/rime/` 目录（覆盖旧文件）
3. 在 Trime 中重新部署即可

### Q5: 可以和其他输入方案共存吗？

**答**：可以！声韵方案不会影响其他已安装的输入方案（如朙月拼音、五笔等）。您可以随时通过 F4 键切换不同方案。

### Q6: 键盘不会自动切换？

**答**：
1. 确保使用的是本项目提供的优化版 `shengyun.trime.yaml`
2. 检查文件是否完整复制到 `/rime/` 目录
3. 重新部署方案

---

## 🔄 更新日志

### v1.0.0 (2025-11-14)

- ✨ 首个正式版本发布
- ✅ 实现声母层（23个声母）
- ✅ 实现韵母层（39个韵母）
- ✅ 实现自动键盘切换功能
- ✅ 纯拼音界面（移除汉字助记）
- ✅ 智能过滤无效声韵组合
- ✅ 支持 ü 系韵母输入
- ✅ 儿童友好的大按键设计

---

## 🤝 贡献与反馈

### 反馈问题

如果您在使用过程中遇到问题，请：

1. 访问 [Issues 页面](https://github.com/gshmu/shengyun/issues)
2. 搜索是否已有相同问题
3. 如果没有，创建新 Issue，描述：
   - 您的设备型号和 Android 版本
   - Trime 版本
   - 具体问题和复现步骤
   - 截图（如果可以）

### 贡献代码

欢迎提交 Pull Request：

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

---

## 📜 许可证

本项目基于 [GPL-3.0-or-later](LICENSE) 许可证开源。

---

## 🙏 致谢

- [RIME](https://rime.im/) - 开源的中文输入法引擎
- [Trime](https://github.com/osfans/trime) - Android 平台的 RIME 前端
- 所有测试和反馈的家长、老师和小朋友们

---

## 📞 联系方式

- GitHub: https://github.com/gshmu/shengyun
- Issues: https://github.com/gshmu/shengyun/issues

---

<div align="center">

**声韵拼音输入方案** | 两步输入，轻松学拼音

Made with ❤️ for kindergarten children

</div>
