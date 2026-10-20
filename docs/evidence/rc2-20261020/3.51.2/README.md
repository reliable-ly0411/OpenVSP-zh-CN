# OpenVSP 3.51.2 rc.2 交互式桌面验收

完成时间：2026-10-20T06:50:40Z。

[实际证据 ZIP](desktop-acceptance.zip)，471898 字节，SHA-256：`0df310d211e1611a050c6c928af0e6c7b26eed17b787fd96fe600c8dba382f7a`。

包内含 10 张 OpenVSP 应用窗口 PNG、原始合成模型和 GUI 保存后的模型 XML，以及 [审阅记录](gui-review.json)。测试模型来自固定 [生成脚本](../gui-fixture.as)，没有用户模型或其他应用截图。

原始 Linux ZIP SHA-256：`3fc9417afab015607ad18c65fa09dd9ab80317d5c81cc32b9ab104db14d7c2b8`。主界面、几何体树、机翼常规/平面形、关于版本与仓库、实际另存为及打开均通过有限检查。保存文件名为 `GUI Roundtrip 100% 中文.vsp3`，持久化名称和 ID 与原模型一致。

环境为 Debian 13 Linux x86_64 云桌面运行 Ubuntu 24.04 构建的原包；Windows、macOS 和 Linux ARM64 GUI 未作同范围验收，不是全部页面或工程数值准确性证明。
