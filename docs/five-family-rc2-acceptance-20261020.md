# 五版本族 rc.2 原包验收

核验日期：2026-10-20 UTC。

## 当前状态

五族对应的 25 个原生构建均成功。已重新核验每族原始汇总工件内五个 ZIP 与原始 `SHA256SUMS.txt`，共 25 个包全部匹配。此检查没有重编译或改写包。另逐文件核对实际启动目录与原始 Linux ZIP 的字节，五族共 2234 个文件全部匹配，见 [解包字节核验](evidence/rc2-20261020/extracted-byte-identity.json)。

五族原始 Linux AMD64 ZIP 均已完成下述有限交互式桌面验收。3.55.0 使用 05:47:44 UTC 已保存的真实操作证据，恢复后重新核验全部原始字节并独立目视审阅；其余四族在本轮重新操作。共保留 51 张应用窗口截图及实际保存的合成模型文件。CI 的 `captured_not_reviewed` 图片没有被当作桌面通过证明。

截至本报告核验时，rc.2 尚未公开发布；桌面验收通过不等于发布成功，后续仅晋级绑定下列哈希的原包。

## 精确来源

- 3.55.0：源码 `85a1a1a2029d0ab35e1a5f685a117061fe89aa21`，[原始构建 39351908980](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39351908980)。
  - Linux ZIP SHA-256：`1220a109b037681fd77f468245f3300f78878fbd96561012ff8e41b24fbb5c5b`
  - 原始清单 SHA-256：`08ba2bf94d1f703f99e9b3e90f2dd93f650670e77da40128e08d9b712a6c9e34`
- 3.54.0：源码 `67f00f7567296d8a1e4088a1fb32e650967af7c2`，[原始构建 39351999591](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39351999591)。
  - Linux ZIP SHA-256：`a0534b9c5ad5767d787d7d509abc4c988588bbc8c7841e932c7ac6387f746d01`
  - 原始清单 SHA-256：`f9cebc1458ad820c90d6fc5fbbb6049ab7c2cb200e33b76c10285c13a653cc74`
- 3.53.0：源码 `219f6c0a7857d110e69116a21f314af3fc26ff46`，[原始构建 39352445023](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39352445023)。
  - Linux ZIP SHA-256：`8414b3751fe10976c1766483e97c6904899553463cd3b73c476e7378a8099e2a`
  - 原始清单 SHA-256：`684933ff6a160dfd3a53d20655fec6b9197fcce01eff6fcbfb1d4881646dc2f1`
- 3.51.3：源码 `0262336a4c17fe0931bba234ecae99073e089cc3`，[原始构建 39352626109](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39352626109)。
  - Linux ZIP SHA-256：`bc68f35be5849f19598490c169d0d6e52f80a8dd076078d2a3e698c537870cd8`
  - 原始清单 SHA-256：`661a0aeb38a85ba9009e866764b76d9325be79f688392819a5ea93d9e07b343b`
- 3.51.2：源码 `d71b88733805b87939a9a7337442d9f43125f43e`，[原始构建 39352805945](https://github.com/reliable-ly0411/OpenVSP-zh-CN/actions/runs/39352805945)。
  - Linux ZIP SHA-256：`3fc9417afab015607ad18c65fa09dd9ab80317d5c81cc32b9ab104db14d7c2b8`
  - 原始清单 SHA-256：`e4ca376c977b4659633a846d5aee349262ec05879e52cd5dd9426a6d320c7e64`

完整机器可读摘要见 [验收 JSON](five-family-rc2-acceptance-20261020.json)。

## 交互式证据

| 版本族 | 真实操作完成时间（UTC） | PNG 数量 | 证据 ZIP SHA-256 |
|---|---|---|---|
| [3.55.0](evidence/rc2-20261020/3.55.0/recovered-desktop-acceptance.zip) | 2026-10-20T05:47:44Z | 9 | `6f6dcf4a06115c44cd0ab3e345ff73cc4c309e257fafe9d81cc3275127137cb7` |
| [3.54.0](evidence/rc2-20261020/3.54.0/desktop-acceptance.zip) | 2026-10-20T05:58:30Z | 11 | `9e6841b9b6f98cc065e0311670864b93313ee5d21b5be60208d0d57b70334af6` |
| [3.53.0](evidence/rc2-20261020/3.53.0/desktop-acceptance.zip) | 2026-10-20T06:44:35Z | 10 | `e4cbfce5ff33279fb233530501af594608ca15d89b4444ba0a23ab59fac47527` |
| [3.51.3](evidence/rc2-20261020/3.51.3/desktop-acceptance.zip) | 2026-10-20T06:47:40Z | 11 | `2100cd1a7e3db7b7d1c7120c96e61397639016830397291d171a7325337e5a02` |
| [3.51.2](evidence/rc2-20261020/3.51.2/desktop-acceptance.zip) | 2026-10-20T06:50:40Z | 10 | `0df310d211e1611a050c6c928af0e6c7b26eed17b787fd96fe600c8dba382f7a` |

另对全部持久化 XML 参数按 ID 比较：五族分别为 1945、1944、1942、1931、1931 个参数，ID 无增删；每族仅 GUI 视图适配造成的六个视图/截图尺寸参数变化，其他参数值不变，详见 [参数往返结果](evidence/rc2-20261020/parameter-roundtrip.json)。这不声称模型文件逐字节一致。

各 ZIP 包含实际应用窗口 PNG 和 GUI 保存的模型 XML，不只是哈希清单。模型仅为固定脚本生成的机翼及机身测试件，用户自定义名称 `Wing & Body_100% 中文` 与 `Fuselage` 保持原样。截图只取相关 OpenVSP 窗口，不含整屏桌面或其他应用。

3.55.0 原记录及恢复说明见 [证据说明](evidence/rc2-20261020/3.55.0/README.md)；其原始时间不冒充本轮新操作时间。其他四族的 `gui-review.json` 分别列出截图哈希、实际保存文件名、模型 ID、审阅范围和未验平台。

发布工具离线回归：`test_native_release.py` 15 项、`test_native_promote.py` 11 项、`test_upstream_release_notes.py` 6 项全部通过。它们验证发布守卫，不替代原生构建或 GUI 证据。

## 范围与限制

- 原始五平台证据涵盖 CLI、模型边界、中文 STL、CompGeom、VSPAERO API/CLI、全新 Python 环境与依赖及包结构检查。这里记录原始构建结果，不把 Linux 本地检查扩展为其他系统的桌面结论。
- 本次使用 Debian 13 Linux x86_64 云桌面运行 Ubuntu 24.04 构建的原始 ZIP，逐族检查主界面、几何体树、机翼常规与平面形页、本地化关于窗口，以及含空格、百分号、中文文件名的实际 GUI 另存为和打开。两个模型的持久化 ID 和名称在保存重开后均一致。该环境不是 Ubuntu 桌面验收。
- 3.51.3 / 3.51.2 使用随包 `vsp-zh-CN` 启动器；其余三族使用 `vsp`。检查范围不覆盖全部专业页面或工程数值准确性。
- Windows、macOS 和 Linux ARM64 GUI 未完成同范围人工验收。macOS 仅 ad-hoc 签名，未公证。
- 全部八个整机示例保留，三个社区模型 CC BY-SA 版本待核实，见 [issue 16](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/16)。
- 发布仅可使用上述原包；新标签不得移动历史标签，旧附件字节和稳定 Latest 不变。
