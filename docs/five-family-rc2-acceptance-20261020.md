# 五版本族 rc.2 原包验收

核验日期：2026-10-20 UTC。

## 当前状态

五族对应的 25 个原生构建均成功。已重新核验每族原始汇总工件内五个 ZIP 与原始 `SHA256SUMS.txt`，共 25 个包全部匹配。此检查没有重编译或改写包。

Linux AMD64 交互式桌面验收尚在进行；本报告当前不构成 GUI 通过或发布结论。CI 的 `captured_not_reviewed` 图片不能替代实际操作与目视判读。

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

## 范围与限制

- 原始五平台证据涵盖 CLI、模型边界、中文 STL、CompGeom、VSPAERO API/CLI、全新 Python 环境与依赖及包结构检查。这里记录原始构建结果，不把 Linux 本地检查扩展为其他系统的桌面结论。
- 本次在 Linux x86_64 云桌面逐族检查主界面、机翼页、名称及含空格、百分号、中文路径保存重开；完成后追加真实结果及截图哈希。
- Windows、macOS 和 Linux ARM64 GUI 未完成同范围人工验收。macOS 仅 ad-hoc 签名，未公证。
- 全部八个整机示例保留，三个社区模型 CC BY-SA 版本待核实，见 [issue 16](https://github.com/reliable-ly0411/OpenVSP-zh-CN/issues/16)。
- 发布仅可使用上述原包；新标签不得移动历史标签，旧附件字节和稳定 Latest 不变。
