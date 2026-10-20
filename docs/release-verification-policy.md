# 发布校验：当前门禁与历史例外

核对日期：2026-10-20。本文说明校验范围和历史例外；安装与运行统一见
[README_zh-CN.md](../README_zh-CN.md)。不改写旧标签、旧二进制、旧附件名或旧清单。

## SHA-256 清单

### 新五族 rc.1

3.55.0、3.54.0、3.53.0、3.51.3、3.51.2 的 `zh-CN.rc.1` 每族均公开五个原生 ZIP 与一份
`SHA256SUMS.txt`。清单各有五行，文件名精确覆盖该 Release 的五个实际 ZIP，无别名映射
或漏项。五族共 30 项资产的完整匿名下载、字节数与 SHA-256 已于 2026-10-19 验证，见
[验收报告与原始摘要](five-family-rc1-acceptance-20261019.md#原始-zip-与清单哈希)。

门禁固定于 [`36889e39b463c0e1637e147d6dd6a87d7f84fa05`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/36889e39b463c0e1637e147d6dd6a87d7f84fa05)：

- [`native_release.py`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/36889e39b463c0e1637e147d6dd6a87d7f84fa05/scripts/native_release.py)
  从实际包名生成清单，要求完整五平台、精确文件集合、无重复条目及匹配哈希。
- 晋级下载远端资产后，以原构建字节为参照，再在下载目录实际执行
  `sha256sum -c SHA256SUMS.txt`。只有全部成功才允许从未公开草稿转为公开预发布。
- 文件名固定到软件版本和平台，rc 序号由 Release 标签区分；不同 rc 的同名包不得混放。
  SHA-256 证明与发布清单一致，不是独立数字签名或对发布者身份的额外认证。

### 旧 3.55.0 auto 的明确例外

[#17](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/17) 报告的
[`3.55.0-Codex-AI-zh-CN-auto.5240ef210f41`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.55.0-Codex-AI-zh-CN-auto.5240ef210f41)
仍保留其 268 字节历史清单。原清单采用以下两项旧名称：

| 原清单中的名称 | 该 Release 当前实际名称 |
|---|---|
| `OpenVSP-3.55.0-Codex-AI-zh-CN-auto.5240ef210f41-Ubuntu-24.04-x86_64.zip` | `OpenVSP-3.55.0-Ubuntu-24.04_amd64-zh-CN.zip` |
| `OpenVSP-3.55.0-Codex-AI-zh-CN-auto.5240ef210f41-Windows-x64.zip` | `OpenVSP-3.55.0-win64-zh-CN.zip` |

后来补充的 macOS ARM64、macOS Intel、Ubuntu ARM64 也不在该原清单中。因此按当前
附件名直接执行旧 `sha256sum -c` 仍会失败；这不是本轮已原地修复的对象。
该 Release 正文已列名称映射及五个包各自的哈希，必须逐项与实际文件比对，不能只重命名
两份文件就声称已验证全部五包。已有旧包用户需要重验时，应保存标签和实际文件名，使用
该页逐包摘要；没有匹配条目的文件应停止使用，不能跳过校验。

替代版本为 [`3.55.0-zh-CN.rc.1`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.55.0-zh-CN.rc.1)，
其完整清单修复的是新的分发链路。其他历史版本也可能保留旧名清单，以各自正文为准。
Latest 的历史稳定标签没有因新 rc 发布而改变。

## 路径与凭据扫描

### 威胁范围

扫描同时服务于两个不同目标：

1. 防止已识别的凭据形态、构建元数据、Git 凭据文件、越界符号链接或当前机器私有目录
   被随包分发。这类内容可能造成实际信息暴露，应阻断。
2. 统一减少当前构建机/工作区绝对前缀，以降低机器信息残留并避免不同平台采用不同门槛。
   公开仓库 Actions runner 的工作区名本身不等于密码或令牌，不能把命中公共 runner 路径
   自动称为“凭据泄漏”。中性源码路径、系统路径和预定安装路径可能仍存在。

这是有限模式扫描，不是对所有敏感数据的完整证明。它不会检测每一种秘密格式，也不
遍历任意压缩/编码负载；“通过”只能表述为按该精确实现和本次运行前缀扫描未命中。

### 五平台统一实现与实际结果

新原生五平台流程全部调用相同的
[`native_verify.py`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/36889e39b463c0e1637e147d6dd6a87d7f84fa05/scripts/native_verify.py)
及 [`privacy_scan`](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/36889e39b463c0e1637e147d6dd6a87d7f84fa05/scripts/backfill_verify.py)。
不是只对 macOS 实施。

- 对解压后的每个普通文件读取字节，检查 GitHub 令牌形态、私钥头、当前
  `GITHUB_WORKSPACE` 与主目录前缀，以及 `.env`、`.git-credentials`、`CMakeCache.txt`
  和 `.git` 路径；也拒绝指向包外的符号链接。
- 前缀覆盖当前运行提供的路径及斜杠/反斜杠变体，包含 UTF-8 与 UTF-16LE 编码。
  不声称可识别所有其他机器的任意用户名路径。
- Linux/macOS 使用 `-ffile-prefix-map` 与 `-fdebug-prefix-map` 将工作区映射为中性
  `/usr/src/openvsp`；Windows 使用中性 `O:` 驱动器别名进行编译。macOS 另有依赖闭包、
  调试符号处理和 libxml2 标准目录配置；不通过事后改写二进制来隐藏匹配。
- 匹配后停止，诊断只记类别/次数等受限信息，不打印匹配原值，不上传被拒包。

| 当前验收对象 | Linux AMD64 | Linux ARM64 | Windows x64 | macOS ARM64 | macOS Intel |
|---|---|---|---|---|---|
| 五族各自 `zh-CN.rc.1`（共25包） | 5/5通过 | 5/5通过 | 5/5通过 | 5/5通过 | 5/5通过 |

上表是本轮原生报告的扫描检查结果，精确包哈希与构建 run 见
[五族验收报告](five-family-rc1-acceptance-20261019.md#平台验收矩阵)。不会外推到任意后续包。

### 历史二进制的例外

[#24](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/24) 记录的旧 3.55.0 auto
Linux/Windows 二进制包含公共 runner 源码路径。该报告未命中其所查 GitHub 令牌和私钥头，
但这仅是当时列出的规则检查；不能推断所有秘密格式均不存在。

旧包及其字节保留不动，故不宣称这些旧路径已清除。历史 macOS 补包曾因为同类前缀被
拦截的开发记录也是历史阶段记录，新五族 rc.1 则在统一扫描之后才发布。旧包没有被追溯
赋予新门禁的“通过”状态；选择新 rc 可获得本轮统一范围的构建与验收证据。
