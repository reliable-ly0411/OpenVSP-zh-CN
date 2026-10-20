# OpenVSP 五版本族 rc1 技术验收报告

本报告记录 3.55.0、3.54.0、3.53.0、3.51.3、3.51.2 的 `zh-CN.rc.1` 原生构建、Linux GUI 审阅与发布核验。项目为非官方简体中文本地化；OpenVSP 原作者归属和 NOSA 1.3 许可不变。安装、构建及版本变化仍以各精确源码中的 `README_zh-CN.md` 为准。

**最终状态：2026-10-19 21:16:39 UTC。** 五族均已公开为新的 `zh-CN.rc.1` 预发布，25 个原生包、5 份原始清单和全部 30 项公开资产下载核验通过。

- 每族同一次原生构建的 8 个必要作业均终态成功：源码/维护回归、计划、五平台原生构建和组装。
- 晋级直接使用已审阅的原始 ZIP，不重新编译；五个新标签均读回指向下表精确源码。
- 五族原始 Linux AMD64 包均完成限定范围实际 GUI 操作与独立复核，共 80 张截图、2,188 个原包文件；其他平台 GUI 未做同范围实际操作验收。
- 原有 12 个 Release、46 项附件的指定元数据和正文保持不变，稳定版 Latest 保持不变。历史二进制未重复下载，不据此宣称逐字节重验了历史文件。

## 修复与验收对象

1. 显示文本与模型数据分离：固定中文界面标签可读，用户模型名、路径、API 标识和持久化材质值保持原义；机翼材料操作显示“自定义”，材料数据仍为字面值 `Custom`。
2. Windows UTF-8 STL 路径：`WriteSTLFile` 与 `WriteTaggedMSSTLFile` 使用宽字符文件接口；前者打开失败仍返回生成的网格标识，UTF-8 转换失败走正常打开失败处理。
3. UTF-8 文件匹配：目录通过 `fs::u8path` 构造，待匹配文件名通过 `.u8string()` 保持 UTF-8；通配符规则及用户数据未改变。五族最终 Windows 包均通过本轮 15 项生产检查，旧诊断构建不计入发布证据。
4. 原生运行资源、模型保存重开、中文 CLI、Python 扩展及新建 venv 安装均由精确源码构建的产物检查；中文帮助文件、官方示例和随包文档与对应源码进行字节比对。

全部修复以各精确源码为准；下表 PR 标识最后一轮 Windows Unicode 修复。构建与验收脚本固定于 [36889e39b463c0e1637e147d6dd6a87d7f84fa05](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/36889e39b463c0e1637e147d6dd6a87d7f84fa05)。五族均经普通双父合并进入各自 `develop/<版本>-zh-CN`，合并树与已验候选树一致；无压平历史或移动旧标签。

## 源码与构建追溯

| 版本族 | 最终源码 SHA | 产品 PR | 源 CI | 原生构建 run |
|---|---|---|---|---|
| 3.55.0 | [55a89b4d73223951a5d9cb692bcef7b050641fb3](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/55a89b4d73223951a5d9cb692bcef7b050641fb3) | [#62](https://github.com/reliable-ly0411/OpenVSP-zh-CN/pull/62) | [39312995554](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39312995554) 成功 | [39313632453](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39313632453) |
| 3.54.0 | [6215cd8d1513cb0fffd062b1b75b1073e1379b4b](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/6215cd8d1513cb0fffd062b1b75b1073e1379b4b) | [#61](https://github.com/reliable-ly0411/OpenVSP-zh-CN/pull/61) | [39312910362](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39312910362) 成功 | [39313735871](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39313735871) |
| 3.53.0 | [fd5feac3040c84c95b4f102a19010dc069515722](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/fd5feac3040c84c95b4f102a19010dc069515722) | [#60](https://github.com/reliable-ly0411/OpenVSP-zh-CN/pull/60) | [39312816028](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39312816028) 成功 | [39313842648](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39313842648) |
| 3.51.3 | [d35d66193f387f65f2d12e0bcd034a41bbe0ac84](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/d35d66193f387f65f2d12e0bcd034a41bbe0ac84) | [#59](https://github.com/reliable-ly0411/OpenVSP-zh-CN/pull/59) | [39312733848](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39312733848) 成功 | [39314173454](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39314173454) |
| 3.51.2 | [296a9e7c7c7e1c6b084381f527ca3a3ab3126855](https://github.com/reliable-ly0411/OpenVSP-zh-CN/commit/296a9e7c7c7e1c6b084381f527ca3a3ab3126855) | [#58](https://github.com/reliable-ly0411/OpenVSP-zh-CN/pull/58) | [39312650728](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39312650728) 成功 | [39314331149](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39314331149) |

源码 CI 全部终态成功。3.55.0 为 116 项 Python 维护回归、补包回归套件 58 项（57 项通过，1 项因轻量 CI 未安装 Noto CJK 而跳过）、8 项已配置 CTest；其本地开启 XML 文本选项后的 9 项 CTest 是另一组证据。3.54.0、3.53.0、3.51.3、3.51.2 分别为 86、74、73、74 项 Python 回归及各 10 项 CTest。

| 目标标签 | 晋级与公开状态 |
|---|---|
| [3.55.0-zh-CN.rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.55.0-zh-CN.rc.1) | [晋级 run 39320435103](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39320435103) 成功；公开预发布；6 项资产匿名完整下载核验完成 |
| [3.54.0-zh-CN.rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.54.0-zh-CN.rc.1) | [晋级 run 39322133316](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39322133316) 成功；公开预发布；6 项资产匿名完整下载核验完成 |
| [3.53.0-zh-CN.rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.53.0-zh-CN.rc.1) | [晋级 run 39322245346](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39322245346) 成功；公开预发布；6 项资产匿名完整下载核验完成 |
| [3.51.3-zh-CN.rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.51.3-zh-CN.rc.1) | [晋级 run 39324820991](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39324820991) 成功；公开预发布；6 项资产匿名完整下载核验完成 |
| [3.51.2-zh-CN.rc.1](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.51.2-zh-CN.rc.1) | [晋级 run 39325668209](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39325668209) 成功；公开预发布；6 项资产匿名完整下载核验完成 |

五个公开标签均读回指向上表精确源码；Release 均为 `draft=false`、`prerelease=true`。

## 平台验收矩阵

“通过”表示本族同一原生 run、同一 attempt 的原包与 15 项运行检查报告均核验通过；不包含该平台 GUI 实际操作验收。

| 版本族 | Ubuntu 24.04 AMD64 | Ubuntu 24.04 ARM64 | Windows x64 | macOS ARM64 | macOS Intel | 五包清单与组装证据 |
|---|---|---|---|---|---|---|
| 3.55.0 | 通过 | 通过 | 通过 | 通过 | 通过 | 通过 |
| 3.54.0 | 通过 | 通过 | 通过 | 通过 | 通过 | 通过 |
| 3.53.0 | 通过 | 通过 | 通过 | 通过 | 通过 | 通过 |
| 3.51.3 | 通过 | 通过 | 通过 | 通过 | 通过 | 通过 |
| 3.51.2 | 通过 | 通过 | 通过 | 通过 | 通过 | 通过 |

共核验 25/25 个平台包、5/5 份五包 SHA-256 清单及组装证据。所有原生构建均为 attempt 1；没有使用其他 run、旧轮或诊断包替代发布结果。

15 项检查包括：AngelScript 模型冒烟；中文 CLI 帮助；CompGeom 与 VSPAERO CLI 分析；Python 扩展导入与版本；Unicode STL 导出及三角形有效性；Unicode 文件名与持久化名称；ZIP 完整性；空工作目录自定义几何体；依赖闭包/RPATH；全新 requirements 安装与导入；模型名称往返；原生架构；隐私扫描；示例、帮助与文档源码字节一致性；受版本控制源码未改变。分析冒烟验证有限、非零等结果条件，不构成气动精度认证。

- Linux Python ABI 为 3.12；Windows/macOS 为 3.11。新 venv 实测 NumPy 1.26.4，子包约束 `<2`，不宣称 NumPy 2 支持。
- 已验 macOS ARM64 包的 所查 Mach-O 最低系统要求的最大值为 14.0，实际运行主机为 14.8.9；Intel 为 15.0，实际运行主机为 15.7.9。只声明已测主机结果，不推导更低系统兼容性。
- macOS 仅 ad-hoc 签名，未使用 Developer ID 签名，未 notarize。包名、最低系统与本轮目标保持一致。
- “受版本控制源码未改变”与整个工作区无生成文件是不同检查项，本文不宣称全部工作区为空净。

## Linux GUI 结果与边界

五个 Ubuntu 24.04 AMD64 原始包在 Debian 13 x86_64、X11、Noto CJK 字体及既有运行库环境中实际操作。3.55.0、3.54.0、3.53.0 使用随包 `vsp`；3.51.3、3.51.2 使用随包 `vsp-zh-CN`。每族 16 张截图均独立逐图复核，并核对源码、构建 run、ZIP 和可执行文件哈希。

- 主菜单、几何树、机翼 General/Planform 页的已查固定中文标签可读，未见阻断使用的固定标签裁切。
- 材料操作显示“自定义”，编辑器与已应用数据保持 `Custom`；菜单可见 10 个 CustomScripts，并实际创建和保存 Cone。界面仍有 `Disk` 等字面标签，不作“汉化绝对完整”结论。
- About 显示对应软件版本、精确 rc.1、仓库归属和 NASA/OpenVSP、NOSA 1.3 声明。
- 文件菜单和首次、重复使用的打开/确认/取消控件保留中文；通过 GUI 打开并保存 `Wing Design 100% 中文.vsp3`。
- 14 个英文、中文、同名与特殊字符模型名称在解析后的 XML 中保持精确；重复打开后取消，当前文件名、可见几何及保存文件 SHA-256 不变。
- GUI 操作后逐文件核对 2,188 个原包文件的字节、大小与权限；无新增、缺失或被改写的包文件。五族分别核对 436、436、436、439、441 个文件。

边界：长名称和完整路径会在固定宽度区域裁切，完整数据通过 XML 和文件系统复核。14 个名称的保留承诺以“上游 API 接受后的值”为准：既有 `SetGeomName` 会移除 `/`，不把任意原始输入逐字保留作为通过标准。Windows、macOS、Linux ARM64 GUI、运行时语言切换、本地帮助在浏览器中的渲染均未实际操作验证。帮助菜单文字已目视检查，帮助文件及链接另有静态/包内容检查。此项为限定 GUI 冒烟验收，不覆盖全部页面或全部硬件。

原生报告中的 `GUI review pending` 记录的是实际界面审阅前的阶段；本文 GUI 结论来自之后的实际操作与独立逐图视觉复核。

## 原始 ZIP 与清单哈希

以下是直接分发 ZIP 的 SHA-256 和字节数，不是 GitHub Actions 外层 artifact ZIP 的哈希。已核验包的外层传输摘要与 GitHub API 一致，内外 ZIP CRC、路径安全与成员清单均检查通过。五族 Linux AMD64 行同时标识实际 GUI 所验原包。 收尾重哈希的 35 份完整原始外层 ZIP 共 3,508,382,820 字节，均仍匹配 GitHub API 摘要；25 份完整成员清单（12,467 条记录）及 5 份 manifest 未变。

| 版本族 | 平台 | 字节数 | 原始 ZIP SHA-256 |
|---|---|---:|---|
| 3.55.0 | Linux AMD64（已验 GUI） | 76,777,668 | `d0eba534d167ec02aed29aa6ce3788e033745ccba26b6071b7e6311781a13b8a` |
| 3.55.0 | Linux ARM64 | 72,020,857 | `f57059d226d6b12b6886908aa1c15731781201f583ccf4dff3e18dafb15f8bfe` |
| 3.55.0 | Windows x64 | 53,181,524 | `d3f9ec8440697e61cdebc5ac67319331635ff0236c96c1e8b837bdce054bac08` |
| 3.55.0 | macOS ARM64 | 65,572,372 | `ec90ec9f962a1b9af965477c82ac6109ff2eb58d4aae81f7176d9c924c18afcb` |
| 3.55.0 | macOS Intel | 72,462,580 | `7d788d75a2f597df636441b65afb213fc33989d4d516f4f7574cac2ccecc6be7` |
| 3.54.0 | Linux AMD64（已验 GUI） | 76,048,236 | `65e0f6adb52278a8961cd4537fc0ca627c268dc1bd44503333e665d7e125c5d7` |
| 3.54.0 | Linux ARM64 | 71,359,211 | `7721d20a001fe2215a531bd0e83461b918a495d8f0f4c6e4caccbd4160098876` |
| 3.54.0 | Windows x64 | 52,387,424 | `0c0a18980e32ad82ea28fd382596612666fe7990f83c1ef60c4f722bcae35f15` |
| 3.54.0 | macOS ARM64 | 64,675,519 | `df0656c59c724459a3516c862f39232c7af36c667ebe073cf358f94d5dd39210` |
| 3.54.0 | macOS Intel | 71,453,484 | `b67f9a6138360303e599fac8d1ad97f4c39482d5f393e96fc22cb391a54e06fd` |
| 3.53.0 | Linux AMD64（已验 GUI） | 73,631,871 | `1e20f5382a5321b39653acfc0ba2300bb5089504fded2d4c0370d5b3aaf66206` |
| 3.53.0 | Linux ARM64 | 69,092,524 | `5fc395181f17020af56f947f70fcc933436f50242f4729f090ad2c774be258ff` |
| 3.53.0 | Windows x64 | 51,089,966 | `b798820de1c8827cd55d025e4eec1d5947fc91d990261c48bf9a9aaaa54035b3` |
| 3.53.0 | macOS ARM64 | 62,872,038 | `30be4bfa3d17c4e38b11a5ae554665a37c8a3eb0fefb105b15503352a686dc12` |
| 3.53.0 | macOS Intel | 69,483,133 | `d5a5449b092493d5d4a4ec52e5f6afa4fa82d5c355319dd74330d07d8663fd63` |
| 3.51.3 | Linux AMD64（已验 GUI） | 101,076,513 | `a25aa19f97fa410859cf9794cbc57d41e641cdb9fcf6acffa23e0d756e49ada0` |
| 3.51.3 | Linux ARM64 | 95,173,261 | `c53f59457f9cfdfa5a7da1dd7a6067569f96b583771a5fd8122db7debb5010ec` |
| 3.51.3 | Windows x64 | 51,190,876 | `bd06c8b1f585ab1f3b2bec54ef155ee1bd2d19a62c5702f703a1ef278b04681a` |
| 3.51.3 | macOS ARM64 | 61,819,412 | `7b8d28c09b0be4e5ec0486eab188ffdc2843a24569b5a70a234cde70e134b6d9` |
| 3.51.3 | macOS Intel | 68,332,971 | `e8ccd6b0dd7a01d89b438f572955d5b7615c3af00e6d538582b870854c30624b` |
| 3.51.2 | Linux AMD64（已验 GUI） | 100,402,190 | `49121df4fcba3ac327ad98a0a6d8d2e0c7fce5ef6ca1638d8c2a4253a8654cee` |
| 3.51.2 | Linux ARM64 | 94,551,547 | `0830bd6bb27e6a3ad66cc03e4bf6ebae1e28c3705ed494b92ba1c264ade08e8d` |
| 3.51.2 | Windows x64 | 50,529,711 | `6b1722c510b0e17c32caeed4d797c5ae40dca7c25a90b04173e96205ed4dd8e5` |
| 3.51.2 | macOS ARM64 | 61,193,373 | `915076a0606556c439d1796e5627ac93fc84099479ef9b3573abcd0fcabdf669` |
| 3.51.2 | macOS Intel | 67,612,186 | `f3ce41ff5cd8a513f0d99041d1e1f75dc017f0ac21f9a46f3d49031da8f2ddef` |

| 版本族 | 同 run 的 SHA256SUMS.txt 文件 SHA-256 |
|---|---|
| 3.55.0 | `844fd1dbc3aacc1dca60dad54a9a57c30c2f467752c83d4994bf863ef471f1dc` |
| 3.54.0 | `1d2f8b053bd515dc1c995410d6202843f000a307b158cd0e98d510bd99fb6831` |
| 3.53.0 | `19194357841c50ab4078f35d848e46ab0b56b857547e6b836a101a111bc78632` |
| 3.51.3 | `3970f1b22406cb1083131b161f3c228b71aa39889ea36f675314cc4c17db8884` |
| 3.51.2 | `257859096520922bc906b9016a52f075c88f92ac69bd4cacf8a5900552e9f572` |

[3.55.0 清单](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/download/3.55.0-zh-CN.rc.1/SHA256SUMS.txt)、[3.54.0 清单](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/download/3.54.0-zh-CN.rc.1/SHA256SUMS.txt)、[3.53.0 清单](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/download/3.53.0-zh-CN.rc.1/SHA256SUMS.txt)、[3.51.3 清单](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/download/3.51.3-zh-CN.rc.1/SHA256SUMS.txt)、[3.51.2 清单](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/download/3.51.2-zh-CN.rc.1/SHA256SUMS.txt)各自精确覆盖对应五个 ZIP。全部 25 个 ZIP 和 5 份清单均通过匿名 HTTPS 完整流式下载；完整字节数及 SHA-256 同时匹配原构建清单和公开资产 API。五族 Linux AMD64 下载值与上述 GUI 原包一致。

## 历史发布保持

五族全部公开并完成下载校验后，于 2026-10-19 21:16:39 UTC 重新读取发布列表。现共 17 个 Release；本轮新增 5 个预发布、30 项资产。原有 12 个 Release 的 ID、标签名、目标、标题、草稿/预发布状态、创建/更新/发布时间和完整正文，以及 46 项附件的 ID、文件名、标签、大小、摘要、创建/更新时间及公开下载 URL，均与发布前基线一致。可变化的下载计数不用于此比较。

Latest 仍为 [3.53.0 稳定版](https://github.com/reliable-ly0411/OpenVSP-zh-CN/releases/tag/3.53.0-Codex-AI-zh-CN)，未将本轮 rc 标为稳定最新版。历史文件未重新下载；本节是历史元数据及正文保持检查，不是历史二进制逐字节重新验收。五个新标签则分别读回核对了精确源码 SHA。

验收实现与后续复核入口：[固定构建工作流](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/36889e39b463c0e1637e147d6dd6a87d7f84fa05/.github/workflows/native-prerelease.yml)、[固定晋级工作流](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/36889e39b463c0e1637e147d6dd6a87d7f84fa05/.github/workflows/native-promote.yml)、[固定验收实现](https://github.com/reliable-ly0411/OpenVSP-zh-CN/blob/36889e39b463c0e1637e147d6dd6a87d7f84fa05/scripts/native_verify.py)。本报告仅记录验收证据，不替代各版本 README 的安装与使用说明。
